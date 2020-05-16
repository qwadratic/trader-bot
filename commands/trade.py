from decimal import Decimal
from re import search
from time import sleep
import datetime as dt

from mintersdk.shortcuts import to_pip
from peewee import IntegrityError
from pyrogram import Client, Filters

from bot_tools.help import delete_msg
from core import trade_core
from core.trade_core import deal_info, announcement_list_kb, check_wallet_on_payment
from filters.cb_filters import TradeFilter
from filters.m_filters import UserMessageFilter
from keyboard import trade_kb
from model import User, TempAnnouncement, TempPaymentCurrency, UserFlag, UserPurse, Announcement, PaymentCurrency, Trade
from text import trade_text


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
    except TypeError:
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

    temp_announcement.amount = amount
    temp_announcement.save()

    user_flag = user.flags
    user_flag.await_amount_for_trade = False
    user_flag.save()

    announcement = trade_core.create_announcement(temp_announcement)

    deal = deal_info(announcement.id)

    m.reply(deal, reply_markup=trade_kb.deal_for_author(announcement, 1))

    cli.delete_messages(m.chat.id, user.msg.await_amount_for_trade)


@Client.on_callback_query(TradeFilter.open_announcement)
def open_announc(cli, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)
    announc_id = int(cb.data[13:])
    announcement = Announcement.get(id=announc_id)
    deal = deal_info(announcement.id)

    if announcement.user_id == user.id:

        cb.message.reply(deal, reply_markup=trade_kb.deal_for_author(announcement, 2))
    else:
        cb.message.reply(deal, reply_markup=trade_kb.deal_for_user(announcement.id))


@Client.on_callback_query(TradeFilter.deal_start)
def deal_start(cli, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)
    user_flag = user.user_flag
    announcement_id = int(cb.data[11:])
    user_flag.announcement_id = announcement_id
    user_flag.save()

    trade_currency = Announcement.get(id=announcement_id).trade_currency

    msg_ids = user.msg
    announcement = Announcement.get_by_id(announcement_id)
    payment_currency = PaymentCurrency.select().where(PaymentCurrency.announcement_id == announcement_id)

    if announcement.type_operation == 'buy':  # Покупка
        user_currency = None
        for curr in payment_currency:
            requisite = UserPurse.select().where(
                (UserPurse.user_id == user.id) & (UserPurse.currency == curr.payment_currency))

            if not requisite:  # имитация выбора валюты
                user_flag.purse_flag = curr.payment_currency
                user_flag.requisites_for_start_deal = True
                user_flag.save()

                msg_ids = user.msgid
                cli.delete_messages(cb.message.chat.id, msg_ids.await_requisites)

                msg = cb.message.edit(trade_text.indicate_requisites(curr.payment_currency))
                msg_ids.await_requisites = msg.message_id
                msg_ids.save()

                return

            user_currency = curr.payment_currency

            break

        trade = Trade.create(user_id=user.id, status='open', announcement_id=announcement_id, user_currency=user_currency)

        msg = cb.message.edit(trade_text.await_respond_from_buyer)
        msg_ids.await_respond_from_buyer = msg.message_id
        msg_ids.save()

        buyer_id = User.get_by_id(announcement.user_id).tg_id

        cli.send_message(buyer_id, trade_text.start_deal(announcement_id), reply_markup=trade_kb.start_deal(trade.id))

    elif announcement.type_operation == 'sale':  # Продажа
        buyer_requisite = UserPurse.select().where(
            (UserPurse.user_id == user.id) & (UserPurse.currency_id == announcement.trade_currency))

        if not buyer_requisite:
            user_flag.purse_flag = announcement.trade_currency
            user_flag.requisites_for_start_deal = True
            user_flag.save()

            msg = cb.message.reply(trade_text.indicate_requisites(announcement.trade_currency))
            msg_ids.await_requisites = msg.message_id
            msg_ids.save()

            cli.delete_messages(cb.message.chat.id, msg_ids.trade_menu)

            return

        payment_currency = PaymentCurrency.select().where(PaymentCurrency.announcement_id == announcement_id)
        user_currency = None
        for curr in payment_currency: # имитация выбора валюты на какую платить
            user_currency = curr.payment_currency
            break

        trade = Trade.create(user_id=user.id, announcement_id=announcement_id, user_currency=user_currency, status='open')

        msg = cb.message.edit(trade_text.await_respond_from_seller)
        msg_ids.await_respond_from_seller = msg.message_id
        msg_ids.save()

        seller_id = User.get_by_id(announcement.user_id).tg_id

        cli.send_message(seller_id, trade_text.start_deal(announcement_id), reply_markup=trade_kb.start_deal(trade.id))


@Client.on_message(UserMessageFilter.requisites_for_start_deal)
def requisites_for_start_deal(cli, m):
    m.delete()
    tg_id = m.from_user.id
    user = User.get(tg_id=tg_id)
    msg_ids = user.msg
    currency = user.flags.temp_currency
    address = m.text
    UserPurse.create(user_id=user.id, currency_id=currency, address=address)

    user_flag = user.flags
    user_flag.temp_currency = None
    user_flag.requisites_for_start_deal = False
    user_flag.save()

    announcement_id = user_flag.announcement_id
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

        trade = Trade.create(user_id=user.id, announcement_id=announcement_id, user_currency=user_currency, status='open')

        msg = m.reply(trade_text.await_respond_from_seller)
        msg_ids.await_respond_from_seller = msg.message_id
        msg_ids.save()

        seller_id = User.get_by_id(announcement.user_id).tg_id

        cli.send_message(seller_id, trade_text.start_deal(announcement_id), reply_markup=trade_kb.start_deal(trade.id))

    cli.delete_messages(m.chat.id, msg_ids.await_requisites)


@Client.on_callback_query(TradeFilter.start_deal)
def start_deal(cli, cb):
    tg_id = cb.from_user.id
    action = int(cb.data[11:12])
    trade_id = int(cb.data[13:])

    if action == 1:
        deal = Trade.get_by_id(trade_id)
        deal.status = 'in processing'
        deal.created_at = dt.datetime.utcnow()
        deal.save()

        if deal.announcement.type_operation == 'buy':  #  Покупка
            buyer = User.get(tg_id=tg_id)
            seller = deal.user
            msgid = seller.msg
            requisite = UserPurse.get(user_id=buyer.id, currency_id=deal.announcement.trade_currency_id)
            cli.delete_messages(seller.tg_id, msgid.await_respond_from_buyer)
            msg = cli.send_message(seller.tg_id, trade_text.payment_details(requisite.address))
            msgid.await_payment_details = msg.message_id
            msgid.save()

            check_wallet_on_payment(cli, requisite, tg_id, trade_id)

        else:
            seller = User.get(tg_id=tg_id)
            buyer = deal.user
            msgid = buyer.msg

            cli.delete_messages(buyer.tg_id, msgid.await_respond_from_seller)
            seller_requisite = UserPurse.get(user_id=seller.id, currency_id=deal.user_currency)
            msg = cli.send_message(buyer.tg_id, trade_text.payment_details(seller_requisite.address))
            msgid.await_payment_details = msg.message_id
            msgid.save()

            check_wallet_on_payment(cli, seller_requisite, tg_id, trade_id)

    cb.message.delete()


@Client.on_callback_query(TradeFilter.confirm_trade)
def conf_trade(cli, cb):
    trade_id = int(cb.data[10:])
    deal = Trade.get_by_id(trade_id)
    deal.status = 'payed'
    deal.save()

    sleep(5)
    deal.status = 'close'
    deal.save()

    cb.message.edit('Сделка прошла успешно!')
    tg_user_id = User.get_by_id(deal.user_id).tg_id
    msgid = User.get(tg_id=tg_user_id).msgid
    cli.delete_messages(tg_user_id, msgid.await_payment_details)
    cli.send_message(tg_user_id, 'Сделка прошла успешно!')
