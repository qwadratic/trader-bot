from time import sleep
import math

from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

from model import Announcement, PaymentCurrency, Trade
from text import trade_text


def await_money_for_trade(user, cli, m):
    # TODO Настроить проверку платежа
    sleep(2)

    amount = 500
    commission = 5
    max_limit = amount * (1 - commission / 100)

    msg_ids = user.msgid
    cli.delete_messages(m.chat.id, msg_ids.await_payment_pending)
    msg = cli.send_message(m.chat.id, trade_text.enter_amount_for_sale(max_limit))
    msg_ids.await_limit = msg.message_id
    msg_ids.save()

    user_flag = user.user_flag
    user_flag.flag = 2
    user_flag.save()

    temp_anounc = user.temp_announcement
    temp_anounc.max_limit = max_limit
    temp_anounc.save()


def deal_info(announc_id):
    trade_direction = {1: {'type': 'Покупка',
                           'icon': '📈'},
                       2: {'type': 'Продажа',
                           'icon': '📉'}}
    status = {1: '⚪️ Активно'}

    announcement = Announcement.get(id=announc_id)
    type_operation = announcement.type_operation
    trade_currency = announcement.trade_currency.name
    announc_status = announcement.status
    amount = announcement.amount

    payment_currency = PaymentCurrency.select().where(PaymentCurrency.id == announc_id)

    txt = f'📰️  Объявление {announcement.id}\n\n' \
        f'**{trade_direction[type_operation]["type"]} {trade_currency} {trade_direction[type_operation]["icon"]}**\n\n' \
        f'**Стоимость:** 1\n' \
        f'**Сумма**: {amount}\n\n' \
        f'**Платёжные инструменты:**\n'

    for curr in payment_currency:
        txt += f'**{curr.payment_currency.name}**\n'

    txt += f'\n\n**Статус:** {status[announc_status]}'

    return txt


def announcement_list_kb(type_operation, offset):
    if type_operation == 1:
        order_by = Announcement.exchange_rate.desc()
    else:
        order_by = Announcement.exchange_rate

    # .join(Trade, on=(Announcement.id == Trade.announcement_id))
    # .where((Announcement.type_operation == type_operation) & (Trade.status != 2) & (Trade.status != 3))
    anc = Announcement
    announcs = (Announcement
                .select(anc.id,
                        anc.type_operation,
                        anc.amount,
                        anc.max_limit,
                        anc.trade_currency)
                .order_by(order_by)
                .offset(offset)
                .limit(7))

    all_announc = (Announcement
                   .select(anc.id,
                           anc.type_operation,
                           anc.amount,
                           anc.max_limit,
                           anc.trade_currency)
                   .order_by(order_by))

    # icon = {1: 'Ⓜ️', 2: '🏵',
    #         3: '💸', 4: '',
    #         5: '', 6: '',
    #         7: ''}

    buttons = {1: {'name': 'Смотреть список на продажу',
                   'cb': 2},
               2: {'name': 'Смотреть список на покупку',
                   'cb': 1}}

    kb_list = []
    kb_list.append([InlineKeyboardButton(buttons[type_operation]['name'],
                                         callback_data=f'annlist t {buttons[type_operation]["cb"]} {offset}')])
    for an in announcs:
        currency_trade = an.trade_currency.name
        amount = an.amount
        # pay_curr = an.payment_currency
        pay_curr = PaymentCurrency.select().where(PaymentCurrency.announcement_id == an.id)
        curs = ''
        for curr in pay_curr:
            curs += f'{curr.payment_currency.name} '
        name = f'{currency_trade} (1 USD): {amount} {curs}'

        kb_list.append([InlineKeyboardButton(name, callback_data=f'open announc {an.id}')])

    if len(all_announc) < 7:
        kb_list.append([InlineKeyboardButton('🔙 Назад', callback_data=f'annlist b')])

    else:
        numb_list_l = f'/{math.ceil(all_announc/7)}'
        numb_list_r = f'/{math.ceil(all_announc/7)}'
        kb_list.append([InlineKeyboardButton(f'⇐ {numb_list_l}', callback_data=f'annlist l {type_operation} {offset}'),
                        InlineKeyboardButton('🔙 Назад', callback_data=f'annlist b'),
                        InlineKeyboardButton(f'{numb_list_r} ⇒', callback_data=f'annlist r {type_operation} {offset}')])

    kb = InlineKeyboardMarkup(kb_list)

    return kb
