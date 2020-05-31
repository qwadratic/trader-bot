import sys
from decimal import Decimal, InvalidOperation
from re import search
from time import sleep
import datetime as dt

from mintersdk.shortcuts import to_pip, to_bip
from peewee import IntegrityError
from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot_tools import converter
from bot_tools.help import delete_msg, correct_name
from core import trade_core
from core.trade_core import announcement_list_kb, get_ad_info, hold_money, auto_transaction, close_trade, \
    start_semi_auto_trade
from filters.cb_filters import TradeFilter
from filters.m_filters import UserMessageFilter
from keyboard import trade_kb
from logs import trade_log
from model import User, TempAnnouncement, TempPaymentCurrency, UserPurse, Announcement, PaymentCurrency, \
    Trade, HoldMoney, VirtualWallet, Wallet
from text import trade_text
from trade_errors import InsufficientFundsAnnouncement, InsufficientFundsOwner


@Client.on_message(Filters.regex(r'💸 Обмен'))
def trade_menu(cli, m):
    tg_id = m.from_user.id
    msg_ids = User.get(tg_id=tg_id).msg
    user = User.get(tg_id=tg_id)

    delete_msg(cli, user.id, msg_ids.trade_menu)

    msg = m.reply(trade_text.trade_menu, reply_markup=trade_kb.menu)
    msg_ids.trade_menu = msg.message_id
    msg_ids.save()

    TempPaymentCurrency.delete().where(TempPaymentCurrency.user_id == user.id).execute()
    m.delete()


@Client.on_callback_query(TradeFilter.trade_menu)
def trade_menu_navi(cli, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)

    button = cb.data[6:]

    if button == 'new buy':
        try:
            TempAnnouncement.create(user_id=user.id, type_operation='buy')

        except IntegrityError:
            TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
            TempAnnouncement.create(user_id=user.id, type_operation='buy')

        cb.message.edit(trade_text.choice_trade_currency_for_buy, reply_markup=trade_kb.trade_currency)

    elif button == 'new sale':
        try:
            TempAnnouncement.create(user_id=user.id, type_operation='sale')

        except IntegrityError:
            TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
            TempAnnouncement.create(user_id=user.id, type_operation='sale')

        cb.message.edit(trade_text.choice_trade_currency_for_sell, reply_markup=trade_kb.trade_currency)

    elif button == 'announc':
        cb.message.edit('Меню объявлений', reply_markup=announcement_list_kb('sale', 0))

    elif button == 'my announc':
        pass
    elif button == 'my trade':
        pass
    elif button == 'notice':
        pass


@Client.on_callback_query(TradeFilter.announcement_menu)
def navi_announcement_menu(cli, cb):
    result = search(r'\s(?P<route>\w*)\s(?P<type_op>\w*)\s(?P<offset>\d*)', cb.data)
    route = result.group('route')
    type_operation = result.group('type_op')
    offset = int(result.group('offset'))

    if route == 'back':
        cb.message.edit(trade_text.trade_menu, reply_markup=trade_kb.menu)
        return

    if type_operation == 'buy':
        order_by = Announcement.exchange_rate.desc()
    else:
        order_by = Announcement.exchange_rate

    anc = Announcement
    all_announc = (Announcement
                   .select(anc.id,
                           anc.type_operation,
                           anc.amount,
                           anc.trade_currency)
                   .order_by(order_by))

    if route == 'left':
        if offset == 0:
            pass
        else:
            offset -= 7
    elif route == 'right':
        offset += 7

    cb.message.edit('Меню объявлений', reply_markup=announcement_list_kb(type_operation, offset))


@Client.on_callback_query(TradeFilter.choice_trade_currency)
def choice_trade_currency(_, cb):
    trade_currency = cb.data[6:]
    tg_id = cb.from_user.id
    temp_announcement = User.get(tg_id=tg_id).temp_announcement
    if trade_currency == 'back':
        cb.message.edit(trade_text.trade_menu, reply_markup=trade_kb.menu)

    else:
        temp_announcement.trade_currency = trade_currency
        temp_announcement.save()
        cb.message.edit(trade_text.choice_payment_currency(temp_announcement.user_id),
                        reply_markup=trade_kb.payment_currency(trade_currency))


@Client.on_callback_query(TradeFilter.choice_payment_instrument)
def choice_payment_instrument(cli, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)

    payment_currency = cb.data[8:]

    temp_announcement = user.temp_announcement
    trade_currency = user.temp_announcement.trade_currency
    if payment_currency == 'accept':
        temp_payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user.id)

        if not temp_payment_currency:
            cli.answer_callback_query(cb.id, trade_text.error_empty_trade_currency)
        else:
            if temp_announcement.type_operation == 'sale':
                for curr in temp_payment_currency:

                    requisite = UserPurse.select().where(
                        (UserPurse.user_id == user.id) & (UserPurse.currency == curr.payment_currency))
                    if not requisite:
                        user_flag = user.flags
                        user_flag.temp_currency = curr.payment_currency
                        user_flag.requisites_for_trade = True
                        user_flag.save()

                        msg_ids = user.msg
                        msg = cb.message.reply(trade_text.indicate_requisites(curr.payment_currency))
                        msg_ids.await_requisites = msg.message_id
                        msg_ids.save()

                        cli.delete_messages(cb.message.chat.id, msg_ids.trade_menu)

                        return

                user_flag = user.flags
                user_flag.temp_currency = None
                user_flag.requisites_for_trade = False
                user_flag.await_exchange_rate = True
                user_flag.save()

                msg = cb.message.reply(trade_text.enter_exchange_rate(trade_currency))
                user_msg = user.msg
                user_msg.await_exchange_rate = msg.message_id
                user_msg.save()
                return

            if temp_announcement.type_operation == 'buy':
                requisite = UserPurse.select().where(
                    (UserPurse.user_id == user.id) & (UserPurse.currency == temp_announcement.trade_currency))
                if not requisite:
                    user_flag = user.flags
                    user_flag.temp_currency = temp_announcement.trade_currency
                    user_flag.requisites_for_trade = False
                    user_flag.save()

                    msg_ids = user.msgid
                    msg = cb.message.reply(trade_text.indicate_requisites(temp_announcement.trade_currency))
                    msg_ids.await_requisites = msg.message_id
                    msg_ids.save()

                    cli.delete_messages(cb.message.chat.id, msg_ids.trade_menu)

                    return

                user_flag = user.flags
                user_flag.temp_currency = None
                user_flag.requisites_for_trade = False
                user_flag.await_exchange_rate = True
                user_flag.save()

                msg = cb.message.edit(trade_text.enter_exchange_rate(trade_currency))
                user_msg = user.msg
                user_msg.await_exchange_rate = msg.message_id
                user_msg.save()

    elif payment_currency == 'back':
        if temp_announcement.type_operation == 'sale':
            cb.message.edit(trade_text.choice_trade_currency_for_sell, reply_markup=trade_kb.trade_currency)
            TempPaymentCurrency.delete().where(TempPaymentCurrency.user_id == user.id).execute()
        else:
            cb.message.edit(trade_text.choice_trade_currency_for_buy, reply_markup=trade_kb.trade_currency)
            TempPaymentCurrency.delete().where(TempPaymentCurrency.user_id == user.id).execute()
    else:
        trade_currency = user.temp_announcement.trade_currency
        try:
            TempPaymentCurrency.create(user_id=user.id, payment_currency=payment_currency)
            cb.message.edit(trade_text.choice_payment_currency(user.id),
                            reply_markup=trade_kb.payment_currency(trade_currency))

        except IntegrityError:
            (TempPaymentCurrency
             .delete()
             .where(
                (TempPaymentCurrency.user_id == user.id) & (TempPaymentCurrency.payment_currency == payment_currency))
             .execute()
             )

            cb.message.edit(trade_text.choice_payment_currency(user.id),
                            reply_markup=trade_kb.payment_currency(trade_currency))


@Client.on_message(UserMessageFilter.requisites_for_trade)
def requisite_for_trade(cli, m):
    m.delete()
    tg_id = m.from_user.id
    user = User.get(tg_id=tg_id)
    currency = user.flags.temp_currency
    address = m.text
    UserPurse.create(user_id=user.id, currency=currency, address=address)

    temp_payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user.id)

    msg_ids = user.msg
    user_flag = user.flags

    temp_announcement = user.temp_announcement
    trade_currency = user.temp_announcement.trade_currency
    if temp_announcement.type_operation == 'sale':
        for curr in temp_payment_currency:
            requisite = UserPurse.select().where(
                (UserPurse.user_id == user.id) & (UserPurse.currency == curr.payment_currency))

            if not requisite:
                user_flag.temp_currency = curr.payment_currency
                user_flag.save()

                msg_ids = user.msg
                cli.delete_messages(m.chat.id, msg_ids.await_requisites)

                msg = m.reply(trade_text.indicate_requisites(curr.payment_currency))
                msg_ids.await_requisites = msg.message_id
                msg_ids.save()

                return

        user_flag.temp_currency = None
        user_flag.requisites_for_trade = False
        user_flag.await_exchange_rate = True
        user_flag.save()

        delete_msg(cli, tg_id, msg_ids.await_requisites)

        msg = m.reply(trade_text.enter_exchange_rate(trade_currency))
        user_msg = user.msg
        user_msg.await_exchange_rate = msg.message_id
        user_msg.save()
    else:
        user_flag.temp_currency = None
        user_flag.requisites_for_trade = False
        user_flag.await_exchange_rate = True
        user_flag.save()

        delete_msg(cli, tg_id, msg_ids.await_requisites)

        msg = m.reply(trade_text.enter_exchange_rate(trade_currency))
        user_msg = user.msg
        user_msg.await_exchange_rate = msg.message_id
        user_msg.save()


@Client.on_message(UserMessageFilter.await_exchange_rate)
def enter_exch_rate(cli, m):
    tg_id = m.from_user.id
    user = User.get(tg_id=tg_id)

    try:
        rate = to_pip(Decimal(m.text))
    except (TypeError, InvalidOperation):
        msg = m.reply(trade_text.error_enter)
        sleep(5)
        cli.delete_messages(m.chat.id, msg.message_id)
        return

    temp_announcement = user.temp_announcement
    temp_announcement.exchange_rate = rate
    temp_announcement.save()

    msg = m.reply(trade_text.enter_count, reply_markup=trade_kb.cancel_ench_rate)
    msg_ids = user.msg
    msg_ids.await_amount_for_trade = msg.message_id
    msg_ids.save()

    user_flag = user.flags
    user_flag.await_exchange_rate = False
    user_flag.await_amount_for_trade = True
    user_flag.save()

    delete_msg(cli, user.tg_id, user.msg.await_exchange_rate)


#  Финальная часть создания объявления
@Client.on_message(UserMessageFilter.await_amount)
def await_amount_for_trade(cli, m):
    tg_id = m.from_user.id
    user = User.get(tg_id=tg_id)
    temp_announcement = user.temp_announcement

    try:
        amount = Decimal(m.text)

    except TypeError:
        m.delete()
        msg = m.reply(trade_text.error_enter)
        sleep(5)
        cli.delete_messages(m.chat.id, msg.message_id)
        return

    temp_announcement.amount = to_pip(amount)
    temp_announcement.save()

    user_flag = user.flags
    user_flag.await_amount_for_trade = False
    user_flag.save()

    announcement = trade_core.create_announcement(temp_announcement)

    ad_info = get_ad_info(announcement.id)

    m.reply(ad_info, reply_markup=trade_kb.deal_for_author(announcement, 1))

    cli.delete_messages(m.chat.id, user.msg.await_amount_for_trade)


#  Открыть объявление из списка
@Client.on_callback_query(TradeFilter.open_announcement)
def open_announc(cli, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)
    announc_id = int(cb.data[13:])
    announcement = Announcement.get(id=announc_id)
    ad_info = get_ad_info(announcement.id)

    if announcement.user_id == user.id:

        cb.message.reply(ad_info, reply_markup=trade_kb.deal_for_author(announcement, 2))
    else:
        cb.message.reply(ad_info, reply_markup=trade_kb.deal_for_user(announcement.id))


@Client.on_callback_query(TradeFilter.user_announcement)
def user_announc(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    # TODO тут добавить всю логику
    data = cb.data

    if data[:15] == 'dealauth status':
        announcement = Announcement.get_by_id(int(data[16:]))
        wallet = VirtualWallet.get(user_id=user.id, currency=announcement.trade_currency)

        if announcement.status == 'close':
            if wallet.balance < announcement.amount or announcement.amount == 0:
                return cli.answer_callback_query(cb.id, 'Недостаточно баланса для начала торговли', show_alert=True)

            announcement.status = 'open'

        elif announcement.status == 'open':
            announcement.status = 'close'

        announcement.save()
        ad_info = get_ad_info(announcement.id)
        return cb.message.edit(ad_info, reply_markup=trade_kb.deal_for_author(announcement, 1))


#  Начало сделки
@Client.on_callback_query(TradeFilter.deal_start)
def deal_start(cli, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)
    user_flag = user.flags
    user_set = user.settings
    announcement_id = int(cb.data[11:])
    user_set.announcement_id = announcement_id
    user_set.save()
    trade_currency = Announcement.get(id=announcement_id).trade_currency

    msg_ids = user.msg
    announcement = Announcement.get_by_id(announcement_id)
    payment_currency = PaymentCurrency.select().where(PaymentCurrency.announcement_id == announcement_id)

    if announcement.type_operation == 'buy':  # Покупка
        user_currency = None
        # for curr in payment_currency:
        #     requisite = UserPurse.select().where(
        #         (UserPurse.user_id == user.id) & (UserPurse.currency == curr.payment_currency))
        #
        #     if not requisite:  # имитация выбора валюты
        #         user_flag.purse_flag = curr.payment_currency
        #         user_flag.requisites_for_start_deal = True
        #         user_flag.save()
        #
        #         msg_ids = user.msgid
        #         cli.delete_messages(cb.message.chat.id, msg_ids.await_requisites)
        #
        #         msg = cb.message.edit(trade_text.indicate_requisites(curr.payment_currency))
        #         msg_ids.await_requisites = msg.message_id
        #         msg_ids.save()
        #
        #         return
        #
        #     user_currency = curr.payment_currency
        #
        #     break
        #
        # trade = Trade.create(user_id=user.id, status='open', announcement_id=announcement_id, user_currency=user_currency)
        #
        # msg = cb.message.edit(trade_text.await_respond_from_buyer)
        # msg_ids.await_respond_from_buyer = msg.message_id
        # msg_ids.save()
        #
        # buyer_id = User.get_by_id(announcement.user_id).tg_id
        #
        # cli.send_message(buyer_id, trade_text.start_deal(announcement_id), reply_markup=trade_kb.start_deal(trade.id))

    elif announcement.type_operation == 'sale':  # Продажа
        buyer_requisite = UserPurse.select().where(
            (UserPurse.user_id == user.id) & (UserPurse.currency == announcement.trade_currency))

        if not buyer_requisite:
            user_flag.temp_currency = announcement.trade_currency
            user_flag.requisites_for_start_deal = True
            user_flag.save()

            msg = cb.message.reply(trade_text.indicate_requisites(announcement.trade_currency))
            msg_ids.await_requisites = msg.message_id
            msg_ids.save()

            cli.delete_messages(cb.message.chat.id, msg_ids.trade_menu)

            return

        payment_currency = PaymentCurrency.select().where(PaymentCurrency.announcement_id == announcement_id)
        user_currency = None
        for curr in payment_currency:  # имитация выбора валюты на какую платить
            user_currency = curr.payment_currency
            break

        trade = Trade.create(user_id=user.id, announcement_id=announcement_id, user_currency=user_currency,
                             status='open')
        txt = f'Введите желаемую сумму для обмена\n'
        msg = cb.message.reply(txt, reply_markup=trade_kb.cancel_deal_before_start())
        msg_ids.await_amount_for_trade = msg.message_id
        msg_ids.save()

        user_flag.await_amount_for_deal = True
        user_flag.save()

        user_set.active_deal = trade.id
        user_set.save()


@Client.on_message(UserMessageFilter.requisites_for_start_deal)
def requisites_for_start_deal(cli, m):
    m.delete()
    tg_id = m.from_user.id
    user = User.get(tg_id=tg_id)
    msg_ids = user.msg
    currency = user.flags.temp_currency
    address = m.text
    UserPurse.create(user_id=user.id, currency=currency, address=address)

    user_flag = user.flags
    user_flag.temp_currency = None
    user_flag.requisites_for_start_deal = False
    user_flag.save()

    announcement_id = user.settings.announcement_id
    announcement = Announcement.get(id=announcement_id)

    if announcement.type_operation == 'buy':  # Покупка

        trade = Trade.create(user_id=user.id, announcement_id=announcement_id, user_currency=currency, status='open')

        msg = m.reply(trade_text.await_respond_from_buyer)
        msg_ids.await_respond_from_buyer = msg.message_id
        msg_ids.save()

        buyer_id = User.get_by_id(announcement.user_id).tg_id

        cli.send_message(buyer_id, trade_text.start_deal(announcement_id), reply_markup=trade_kb.start_deal(trade.id))

    elif announcement.type_operation == 'sale':
        payment_currency = PaymentCurrency.select().where(PaymentCurrency.announcement_id == announcement_id)
        user_currency = None
        for curr in payment_currency:  # имитация выбора валюты на какую платить
            user_currency = curr.payment_currency
            break

        trade = Trade.create(user_id=user.id, announcement_id=announcement_id, user_currency=user_currency,
                             status='open')

        msg = m.reply(trade_text.enter_amount_for_buy(user_currency))
        msg_ids.await_amount_for_trade = msg.message_id
        msg_ids.save()

        user_flag.await_amount_for_deal = True
        user_flag.save()
        user_set = user.settings
        user_set.active_deal = trade.id
        user_set.save()

        delete_msg(cli, user.tg_id, msg_ids.await_requisites)


@Client.on_message(UserMessageFilter.await_amount_for_deal)
def amount_for_deal(cli, m):
    user = User.get(tg_id=m.from_user.id)

    try:
        amount = Decimal(m.text)
        if amount == 0:
            raise TypeError
    except (TypeError, InvalidOperation):
        m.delete()
        msg = m.reply(trade_text.error_enter)
        sleep(5)
        msg.delete()
        return

    trade = Trade.get(user_id=user.id, id=user.settings.active_deal)
    trade_limit = trade.announcement.amount
    trade_currency = trade.announcement.trade_currency

    if to_pip(amount) > trade_limit:
        m.delete()
        txt = f'Вы не можете купить больше чем {to_bip(trade_limit)} {trade_currency}'
        msg = m.reply(txt)
        sleep(5)
        msg.delete()
        return

    trade.amount = to_pip(amount)
    trade.save()

    owner_trade_currency_price = trade.announcement.exchange_rate
    cost_user_currency_in_usd = Decimal(converter.currency_in_usd(trade.user_currency, 1))
    price_deal_in_usd = to_bip(trade.amount) * to_bip(owner_trade_currency_price)

    #  Сколько нужно юзеру заплатить
    price_deal_in_user_currency = price_deal_in_usd / cost_user_currency_in_usd

    type_operation = 'купить' if trade.announcement.type_operation == 'sale' else 'продать'
    trade_txt = f'Вы желаете {type_operation} {amount} {trade_currency}\n' \
        f'за {price_deal_in_user_currency} {trade.user_currency}?'
    m.reply(trade_txt, reply_markup=trade_kb.confirm_deal(trade.id))

    user_flag = user.flags
    user_flag.await_amount_for_deal = False
    user_flag.save()
    delete_msg(cli, user.id, user.msg.await_amount_for_trade)


@Client.on_callback_query(TradeFilter.finally_deal)
def finally_deal(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    user_name = correct_name(user)

    data = cb.data

    if data[:13] == 'trade confirm':
        trade = Trade.get_by_id(int(data[14:]))
        trade_currency_price = trade.announcement.exchange_rate
        trade_currency = trade.announcement.trade_currency
        owner = trade.announcement.user
        owner_name = correct_name(owner)

        owner_trade_currency_price = trade.announcement.exchange_rate
        cost_payment_currency_in_usd = Decimal(converter.currency_in_usd(trade.user_currency, 1))
        price_deal_in_usd = to_bip(trade.amount) * to_bip(owner_trade_currency_price)

        price_deal_in_payment_currency = price_deal_in_usd / cost_payment_currency_in_usd
        comission = to_pip(0)
        payment_currency = 'ETH' if trade.user_currency == 'USDT' else trade.user_currency

        user_wallet = VirtualWallet.get(user_id=user.id, currency=payment_currency)
        # Разветвление на полуавтоматический обмен
        if price_deal_in_payment_currency + comission > user_wallet.balance:
            cb.message.delete()

            trade_log.trade_start(cli, trade, owner_name, user_name, trade.announcement.type_operation,
                                  trade_currency_price, trade_currency, price_deal_in_usd, price_deal_in_payment_currency)

            owner_recipient_address = UserPurse.get(user_id=trade.announcement.user_id, currency=payment_currency).address
            start_semi_auto_trade(cli, trade, price_deal_in_payment_currency, owner_recipient_address)
            return

        cb.message.edit('Ожидайте')
        try:
            trade.deposite = True
            trade.save()
            trade_final = trade_core.start_trade(cli, trade)

        except ValueError as e:
            tb = sys.exc_info()[2]

            deposite = HoldMoney.get_or_none(trade_id=trade.id)
            if deposite:
                owner = trade.announcement.user
                hold_amount = deposite.amount

                owner_wallet = VirtualWallet.get(user_id=owner.id, currency=trade.announcement.trade_currency)
                owner_wallet.balance += hold_amount
                owner_wallet.save()

                HoldMoney.delete().where(HoldMoney.trade_id == trade.id).execute()
            err = e
            return cb.message.reply(f'Ошибка\n\n{err}')

        operation = 'Купили' if trade.announcement.type_operation == 'sale' else 'продали'
        txt = f'Вы {operation} {to_bip(trade.amount)} {trade.announcement.trade_currency} за {price_deal_in_payment_currency} {trade.user_currency}'
        cb.message.edit(txt)

        txt2 = f'Вы {trade.announcement.type_operation} {to_bip(trade.amount)} {trade.announcement.trade_currency} за {price_deal_in_payment_currency} {trade.user_currency}'
        return cli.send_message(trade.announcement.user.tg_id, txt2)

    if data[:12] == 'trade cancel':
        trade = Trade.get_by_id(int(cb.data[13:]))

        Trade.delete().where(Trade.id == trade.id).execute()

        deposite = HoldMoney.get_or_none(trade_id=trade.id)
        if deposite:
            owner = trade.announcement.user
            hold_amount = deposite.amount

            owner_wallet = VirtualWallet.get(user_id=owner.id, currency=trade.announcement.trade_currency)
            owner_wallet.balance += hold_amount
            owner_wallet.save()

            HoldMoney.delete().where(HoldMoney.trade_id == trade.id).execute()

        cb.message.edit('Сделка отменена')


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:7] == 'i payed'))
def user_confirm_payment(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    trade = Trade.get_by_id(int(cb.data[8:]))

    #  Валюта обмена
    trade_currency = trade.announcement.trade_currency

    #  Выбранный платёжный инструмент пользователя
    payment_currency = trade.user_currency

    #  Цена лота от владельца объявления
    trade_currency_price = trade.announcement.exchange_rate

    #  Цена выбранной валюты
    cost_payment_currency_in_usd = Decimal(converter.currency_in_usd(payment_currency, 1))

    #  Цена сделки в долларах
    price_deal_in_usd = to_bip(trade.amount) * to_bip(trade_currency_price)

    #  Сколько нужно юзеру заплатить
    price_deal_in_payment_currency = price_deal_in_usd / cost_payment_currency_in_usd

    # Депонирование средств
    try:
        hold_money(cli, trade)
    except InsufficientFundsAnnouncement:
        pass

    except InsufficientFundsOwner:
        pass

    txt = f'Сделка №{trade.id}\n\n' \
        f'Сумма обмена: {to_bip(trade.amount)} {trade_currency}\n' \
        f'Цена: {price_deal_in_payment_currency} {payment_currency}\n\n' \
        f'Пользователь подтвердил оплату'

    kb = InlineKeyboardMarkup([[InlineKeyboardButton('Я получил средства', callback_data=f'i got money {trade.id}')],
                               [InlineKeyboardButton('Подождать', callback_data=f'д {trade.id}')]])

    cli.send_message(trade.announcement.user.tg_id, txt, reply_markup=kb)
    cb.message.edit('Ожидайте подтверждения от второй стороны')


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:11] == 'i got money'))
def owner_confirm_trade(cli, cb):
    trade = Trade.get_by_id(int(cb.data[12:]))
    payment_currency = trade.user_currency
    trade_currency = trade.announcement.trade_currency

    user = trade.user
    owner = trade.announcement.user
    owner_wallet = VirtualWallet.get(user_id=owner.id, currency=trade_currency)

    user_recipient_address = UserPurse.get(user_id=trade.user_id, currency=trade_currency).address

    #  Цена выбранной валюты
    cost_payment_currency_in_usd = Decimal(converter.currency_in_usd(payment_currency, 1))

    #  Цена лота от владельца объявления
    trade_currency_price = trade.announcement.exchange_rate

    #  Цена сделки в долларах
    price_deal_in_usd = to_bip(trade.amount) * to_bip(trade_currency_price)

    #  Сколько нужно юзеру заплатить
    price_deal_in_payment_currency = price_deal_in_usd / cost_payment_currency_in_usd

    if payment_currency == 'USDT':
        user_currency_wallet = Wallet.get(user_id=user.id, currency='ETH')
        owner_currency_wallet = Wallet.get(user_id=owner.id, currency='ETH')
    else:
        user_currency_wallet = Wallet.get_or_none(user_id=user.id, currency=payment_currency)
        owner_currency_wallet = Wallet.get(user_id=owner.id, currency=trade_currency)

    try:
        tx = auto_transaction(trade_currency, owner_currency_wallet, user_recipient_address, trade.amount)
        if tx[1] == 'error':
            tx_hash = tx[0]
            err_txt = tx[2]
            trade_log.tx_error(cli, 'second', trade, owner_wallet.balance, owner_currency_wallet.address, user_recipient_address, trade_currency, trade.amount, err_txt, tx_hash)

    except Exception as e:
        print(e)
        return trade_log.tx_error(cli, 'second', trade, owner_wallet.balance, owner_currency_wallet.address, user_recipient_address, trade_currency, trade.amount, e)

    tx_hash_2 = tx[0]
    fee_2 = tx[1]

    trade_log.successful_tx(cli, 'second', trade, owner_currency_wallet.address, user_recipient_address, trade_currency,
                            trade.amount, fee_2, tx_hash_2)

    close_trade(cli, trade, fee_2, 0, price_deal_in_payment_currency)

    operation = 'Продали' if trade.announcement.type_operation == 'sale' else 'Купили'
    txt = f'Вы {operation} {to_bip(trade.amount)} {trade.announcement.trade_currency} за {price_deal_in_payment_currency} {trade.user_currency}'
    cb.message.edit(txt)

    operation = 'Продали' if operation == 'Купили' else 'Купили'
    txt2 = f'Вы {operation} {to_bip(trade.amount)} {trade.announcement.trade_currency} за {price_deal_in_payment_currency} {trade.user_currency}'
    cli.send_message(trade.user.tg_id, txt2)


# @Client.on_callback_query(TradeFilter.start_deal)
# def start_deal(cli, cb):
#     tg_id = cb.from_user.id
#     action = int(cb.data[11:12])
#     trade_id = int(cb.data[13:])
#
#     if action == 1:
#         deal = Trade.get_by_id(trade_id)
#         deal.status = 'in processing'
#         deal.created_at = dt.datetime.utcnow()
#         deal.save()
#
#         if deal.announcement.type_operation == 'buy':  # Покупка
#             buyer = User.get(tg_id=tg_id)
#             seller = deal.user
#             msgid = seller.msg
#             requisite = UserPurse.get(user_id=buyer.id, currency_id=deal.announcement.trade_currency_id)
#             cli.delete_messages(seller.tg_id, msgid.await_respond_from_buyer)
#             msg = cli.send_message(seller.tg_id, trade_text.payment_details(requisite.address))
#             msgid.await_payment_details = msg.message_id
#             msgid.save()
#
#             check_wallet_on_payment(cli, requisite, tg_id, trade_id)
#
#         else:
#             seller = User.get(tg_id=tg_id)
#             buyer = deal.user
#             msgid = buyer.msg
#
#             cli.delete_messages(buyer.tg_id, msgid.await_respond_from_seller)
#             seller_requisite = UserPurse.get(user_id=seller.id, currency_id=deal.user_currency)
#             msg = cli.send_message(buyer.tg_id, trade_text.payment_details(seller_requisite.address))
#             msgid.await_payment_details = msg.message_id
#             msgid.save()
#
#             check_wallet_on_payment(cli, seller_requisite, tg_id, trade_id)
#
#     cb.message.delete()


#
# @Client.on_callback_query(TradeFilter.confirm_trade)
# def conf_trade(cli, cb):
#     trade_id = int(cb.data[10:])
#     deal = Trade.get_by_id(trade_id)
#     deal.status = 'payed'
#     deal.save()
#
#     sleep(5)
#     deal.status = 'close'
#     deal.save()
#
#     cb.message.edit('Сделка прошла успешно!')
#     tg_user_id = User.get_by_id(deal.user_id).tg_id
#     msgid = User.get(tg_id=tg_user_id).msgid
#     cli.delete_messages(tg_user_id, msgid.await_payment_details)
#     cli.send_message(tg_user_id, 'Сделка прошла успешно!')


@Client.on_message(Filters.command('my_wallets'))
def walles(cli, m):
    user = User.get(tg_id=m.from_user.id)

    wallets = user.wallets

    for w in wallets:
        wal = f'{w.currency}\n' \
            f'```{w.address}```'
        m.reply(wal)


@Client.on_callback_query(Filters.callback_data('trcel'))
def tr_cel(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    user_flag = user.flags
    user_flag.await_amount_for_deal = False
    user_flag.save()
    cb.message.delete()
    announcement = Announcement.get_by_id(user.settings.announcement_id)
    ad_info = get_ad_info(announcement.id)
    cb.message.reply(ad_info, reply_markup=trade_kb.deal_for_user(announcement.id))
