from time import sleep
import datetime as dt

from peewee import IntegrityError
from pyrogram import Client, Filters

from core.trade_core import await_money_for_trade, deal_info, announcement_list_kb, check_seller_wallet_on_payment
from filters.cb_filters import TradeFilter
from filters.m_filters import UserMessageFilter
from keyboard import trade_kb
from model import User, TempAnnouncement, TempPaymentCurrency, UserFlag, UserPurse, Announcement, PaymentCurrency, Trade
from text import trade_text


@Client.on_message(Filters.regex(r'💸 Обмен'))
def trade_menu(cli, m):
    tg_id = m.from_user.id
    msg_ids = User.get(tg_id=tg_id).msgid
    user = User.get(tg_id=tg_id)

    try:
        cli.delete_messages(m.chat.id, [msg_ids.trade_menu])
    except:
        pass

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
            TempAnnouncement.create(user_id=user.id, type_operation=1)

        except IntegrityError:
            TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
            TempAnnouncement.create(user_id=user.id, type_operation=1)

        cb.message.edit(trade_text.choice_trade_currency_for_sell, reply_markup=trade_kb.trade_currency)

    elif button == 'new sale':
        try:
            TempAnnouncement.create(user_id=user.id, type_operation=2)

        except IntegrityError:
            TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
            TempAnnouncement.create(user_id=user.id, type_operation=2)

        cb.message.edit(trade_text.choice_trade_currency_for_buy, reply_markup=trade_kb.trade_currency)

    elif button == 'announc':
        cb.message.edit('Меню объявлений', reply_markup=announcement_list_kb(2, 0))

    elif button == 'my announc':
        pass
    elif button == 'my trade':
        pass
    elif button == 'notice':
        pass


@Client.on_callback_query(TradeFilter.announcement_menu)
def navi_announcement_menu(cli, cb):
    act = cb.data[8:9]

    if act == 'b':
        cb.message.edit(trade_text.trade_menu, reply_markup=trade_kb.menu)
        return

    type_operation = int(cb.data[10:11])
    offset = int(cb.data[12:])

    if type_operation == 1:
        order_by = Announcement.exchange_rate.desc()
    else:
        order_by = Announcement.exchange_rate

    anc = Announcement
    all_announc = (Announcement
                   .select(anc.id,
                           anc.type_operation,
                           anc.amount,
                           anc.max_limit,
                           anc.trade_currency)
                   .order_by(order_by))

    if act == 'l':
        if offset == 0:
            pass
        else:
            offset -= 7
    else:
        offset += 7

    cb.message.edit('Меню объявлений', reply_markup=announcement_list_kb(type_operation, offset))


# @Client.on_callback_query(TradeFilter.buy_menu)
# def buy_menu(_, cb):
#     tg_id = cb.from_user.id
#     user = User.get(tg_id=tg_id)
#     action = cb.data[4:]
#
#     if action == 'new':
#         try:
#             TempAnnouncement.create(user_id=user.id, type_operation=1)
#
#         except IntegrityError:
#             TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
#             TempAnnouncement.create(user_id=user.id, type_operation=1)
#
#         cb.message.edit(trade_text.choice_trade_currency, reply_markup=trade_kb.trade_currency)
#
#     elif action == 'list':
#         pass
#     else:
#         cb.message.edit(trade_text.trade_menu, reply_markup=trade_kb.menu)


# @Client.on_callback_query(TradeFilter.sale_menu)
# def sale_menu(_, cb):
#     tg_id = cb.from_user.id
#     user = User.get(tg_id=tg_id)
#     action = cb.data[5:]
#     if action == 'new':
#         try:
#             TempAnnouncement.create(user_id=user.id, type_operation=2)
#
#         except IntegrityError:
#             TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
#             TempAnnouncement.create(user_id=user.id, type_operation=2)
#
#         cb.message.edit(trade_text.choice_trade_currency, reply_markup=trade_kb.trade_currency)
#
#     elif action == 'list':
#         pass
#     else:
#         cb.message.edit(trade_text.trade_menu, reply_markup=trade_kb.menu)


@Client.on_callback_query(TradeFilter.choice_trade_currency)
def choice_trade_currency(_, cb):
    trade_currency = int(cb.data[6:])
    tg_id = cb.from_user.id
    temp_announcement = User.get(tg_id=tg_id).temp_announcement
    if trade_currency == 0:
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

    try:
        payment_currency = int(cb.data[8:])
    except ValueError:
        payment_currency = cb.data[8:]

    temp_announcement = user.temp_announcement
    if payment_currency == 'accept':
        temp_payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user.id)

        if not temp_payment_currency:
            cli.answer_callback_query(cb.id, trade_text.error_empty_trade_currency)
        else:
            if temp_announcement.type_operation == 2:
                for curr in temp_payment_currency:

                    requisite = UserPurse.select().where((UserPurse.user_id == user.id) & (UserPurse.currency_id == curr.payment_currency_id))
                    if not requisite:
                        user_flag = user.user_flag
                        user_flag.purse_flag = curr.payment_currency
                        user_flag.flag = 3
                        user_flag.save()

                        msg_ids = user.msgid
                        msg = cb.message.reply(trade_text.indicate_requisites(curr.payment_currency))
                        msg_ids.await_requisites = msg.message_id
                        msg_ids.save()

                        cli.delete_messages(cb.message.chat.id, msg_ids.trade_menu)

                        return

                user_flag = user.user_flag
                user_flag.purse_flag = None
                user_flag.flag = 0
                user_flag.save()

                trade_currency = user.temp_announcement.trade_currency_id

                msg_ids = user.msgid
                msg = cb.message.reply(trade_text.pending_payment_for_sale(trade_currency))
                msg_ids.await_payment_pending = msg.message_id
                msg_ids.save()

                cb.message.delete()
                await_money_for_trade(user, cli, cb.message)
            else:
                requisite = UserPurse.select().where((UserPurse.user_id == user.id) & (UserPurse.currency_id == temp_announcement.trade_currency))
                if not requisite:
                    user_flag = user.user_flag
                    user_flag.purse_flag = temp_announcement.trade_currency
                    user_flag.flag = 3
                    user_flag.save()

                    msg_ids = user.msgid
                    msg = cb.message.reply(trade_text.indicate_requisites(temp_announcement.trade_currency))
                    msg_ids.await_requisites = msg.message_id
                    msg_ids.save()

                    cli.delete_messages(cb.message.chat.id, msg_ids.trade_menu)

                    return

                user_flag = user.user_flag
                user_flag.purse_flag = None
                user_flag.flag = 0
                user_flag.save()

                msg_ids = user.msgid
                msg = cb.message.reply(trade_text.pending_payment_for_buy(temp_payment_currency))
                msg_ids.await_payment_pending = msg.message_id
                msg_ids.save()

                cb.message.delete()
                await_money_for_trade(user, cli, cb.message)

    elif payment_currency == 'back':
        if temp_announcement.type_operation == 2:
            cb.message.edit(trade_text.choice_trade_currency_for_sell, reply_markup=trade_kb.trade_currency)
            TempPaymentCurrency.delete().where(TempPaymentCurrency.user_id == user.id).execute()
        else:
            cb.message.edit(trade_text.choice_trade_currency_for_buy, reply_markup=trade_kb.trade_currency)
            TempPaymentCurrency.delete().where(TempPaymentCurrency.user_id == user.id).execute()
    else:
        trade_currency = user.temp_announcement.trade_currency_id
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
    currency_id = user.user_flag.purse_flag
    address = m.text
    UserPurse.create(user_id=user.id, currency_id=currency_id, address=address)

    temp_payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user.id)

    msg_ids = user.msgid
    user_flag = user.user_flag

    temp_announcement = user.temp_announcement

    if temp_announcement.type_operation == 2:
        for curr in temp_payment_currency:
            requisite = UserPurse.select().where(
                (UserPurse.user_id == user.id) & (UserPurse.currency_id == curr.payment_currency_id))

            if not requisite:
                user_flag.purse_flag = curr.payment_currency
                user_flag.save()

                msg_ids = user.msgid
                cli.delete_messages(m.chat.id, msg_ids.await_requisites)

                msg = m.reply(trade_text.indicate_requisites(curr.payment_currency.name))
                msg_ids.await_requisites = msg.message_id
                msg_ids.save()

                return

        user_flag.purse_flag = None
        user_flag.flag = 0
        user_flag.save()

        cli.delete_messages(m.chat.id, msg_ids.await_requisites)

        trade_currency = user.temp_announcement.trade_currency_id

        msg = m.reply(trade_text.pending_payment_for_sale(trade_currency))
        msg_ids.await_payment_pending = msg.message_id
        msg_ids.save()

        await_money_for_trade(user, cli, m)
    else:
        user_flag.purse_flag = None
        user_flag.flag = 0
        user_flag.save()

        cli.delete_messages(m.chat.id, msg_ids.await_requisites)

        msg = m.reply(trade_text.pending_payment_for_buy(temp_payment_currency))
        msg_ids.await_payment_pending = msg.message_id
        msg_ids.save()

        await_money_for_trade(user, cli, m)


# @Client.on_message(UserMessageFilter.await_exchange_rate)
# def enter_exch_rate(cli, m):
#     tg_id = m.from_user.id
#     user = User.get(tg_id=tg_id)
#
#     try:
#         rate = float(m.text)
#         temp_anounc = user.temp_announcement
#         temp_anounc.exchange_rate = rate
#         temp_anounc.save()
#
#         msg = m.reply(trade_text.enter_count, reply_markup=trade_kb.cancel_ench_rate)
#         msg_ids = user.msgid
#         msg_ids.await_count = msg.message_id
#         msg_ids.save()
#
#         user_flag = user.user_flag
#         user_flag.flag = 2
#         user_flag.save()
#
#         cli.delete_messages(m.chat.id, user.msgid.await_exchange_rate)
#
#     except TypeError:
#         msg = m.reply(trade_text.error_enter)
#         sleep(5)
#         cli.delete_messages(m.chat.id, msg.message_id)


@Client.on_message(UserMessageFilter.await_amount)
def await_amount(cli, m):
    tg_id = m.from_user.id
    user = User.get(tg_id=tg_id)
    temp_anounc = user.temp_announcement

    try:
        amount = int(m.text)
        limit = temp_anounc.max_limit

        if amount > limit or amount <= 0:
            msg = m.reply(trade_text.error_limit(limit))
            sleep(5)
            cli.delete_messages(m.chat.id, msg.message_id)
            return

    except TypeError:
        m.delete()
        msg = m.reply(trade_text.error_enter)
        sleep(5)
        cli.delete_messages(m.chat.id, msg.message_id)
        return

    temp_anounc.amount = amount
    temp_anounc.save()

    user_flag = user.user_flag
    user_flag.flag = 0
    user_flag.save()

    announcement = Announcement.create(user_id=user.id,
                                       type_operation=temp_anounc.type_operation,
                                       trade_currency=temp_anounc.trade_currency,
                                       amount=amount,
                                       max_limit=limit,
                                       status=1
                                       )

    temp_payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user.id)

    for curr in temp_payment_currency:
        PaymentCurrency.create(announcement=announcement.id,
                               payment_currency=curr.payment_currency)

    TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
    TempPaymentCurrency.delete().where(TempPaymentCurrency.user_id == user.id)

    deal = deal_info(announcement.id)
    if announcement.user_id == user.id:
        m.reply(deal, reply_markup=trade_kb.deal_for_author(announcement, 1))

    else:
        m.reply(deal, reply_markup=trade_kb.deal_for_user(announcement.id))

    cli.delete_messages(m.chat.id, user.msgid.await_limit)


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
def start_deal(cli, cb):
    print('dasd')
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)
    announcement_id = int(cb.data[11:])

    trade_currency = Announcement.get(id=announcement_id).trade_currency_id
    requisite = UserPurse.select().where((UserPurse.user_id == user.id) & (UserPurse.currency_id == trade_currency))

    msg_ids = user.msgid
    if not requisite:
        user_flag = user.user_flag
        user_flag.purse_flag = trade_currency
        user_flag.flag = 4
        user_flag.announcemen_id = announcement_id
        user_flag.save()

        msg = cb.message.reply(trade_text.indicate_requisites(trade_currency))
        msg_ids.await_requisites = msg.message_id
        msg_ids.save()

        cli.delete_messages(cb.message.chat.id, msg_ids.trade_menu)
        return

    cli.delete_messages(cb.message.chat.id, msg_ids.await_requisites)

    trade = Trade.create(user_id=user.id, announcement_id=announcement_id, status=1)

    msg = cb.message.reply(trade_text.await_respond_from_seller)

    msg_ids.await_requisites_from_seller = msg.message_id
    msg_ids.save()

    seller_id = User.get_by_id(Announcement.get(id=announcement_id).user_id).tg_id

    cli.send_message(seller_id, trade_text.start_deal_for_seller(announcement_id),
                     reply_markup=trade_kb.start_deal_for_seller(trade.id))


@Client.on_message(UserMessageFilter.requisites_for_start_deal)
def requisites_for_start_deal(cli, m):
    m.delete()
    tg_id = m.from_user.id
    user = User.get(tg_id=tg_id)
    currency_id = user.user_flag.purse_flag
    address = m.text
    UserPurse.create(user_id=user.id, currency_id=currency_id, address=address)

    user_flag = user.user_flag
    user_flag.purse_flag = None
    user_flag.flag = 0
    user_flag.save()
    announcement_id = user_flag.announcement_id

    msg_ids = user.msgid
    cli.delete_messages(m.chat.id, msg_ids.await_requisites)

    trade = Trade.create(user_id=user.id, status=1)

    msg = m.reply(trade_text.await_respond_from_seller)

    msg_ids.await_requisites_from_seller = msg.message_id
    msg_ids.save()

    seller_id = User.get_by_id(Announcement.get(id=announcement_id).user_id).tg_id

    cli.send_message(seller_id, trade_text.start_deal_for_seller(announcement_id),
                     reply_markup=trade_kb.start_deal_for_seller(trade.id))


@Client.on_callback_query(TradeFilter.start_deal_from_seller)
def start_deal_from_seller(cli, cb):
    action = int(cb.data[18:19])
    trade_id = int(cb.data[20:])

    if action == 1:
        deal = Trade.get_by_id(trade_id)
        deal.status = 2
        deal.created_at = dt.datetime.utcnow()
        deal.save()

        user_currency = PaymentCurrency.get(announcement_id=deal.announcement_id).payment_currency
        requisite = UserPurse.get(currency=user_currency).address
        tg_user_id = User.get_by_id(deal.user_id).tg_id
        cli.send_message(tg_user_id, trade_text.payment_details(deal, requisite))

        check_seller_wallet_on_payment(cli, requisite, deal.announcement.user_id, trade_id)


@Client.on_callback_query(TradeFilter.confirm_trade)
def conf_trade(cli, cb):
    trade_id = int(cb.data[10:])
    deal = Trade.get_by_id(trade_id)
    deal.status = 3
    deal.save()

    sleep(5)
    deal.status = 4
    deal.save()

    cb.message.edit('Сделка прошла успешно!')
    tg_user_id = User.get_by_id(deal.user_id).tg_id
    cli.send_message(tg_user_id, 'Сделка прошла успешно!')






