from time import sleep
import math

from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

from bot_tools.converter import currency_in_usd
from keyboard import trade_kb
from model import Announcement, PaymentCurrency, Trade, User, VirtualWallet, TempPaymentCurrency, TempAnnouncement
from text import trade_text


#


def check_wallet_on_payment(cli, wallet, user_tg_id, trade_id):
    # tg_id = User.get_by_id(user_id).tg_id
    transaction = True

    if transaction:
        cli.send_message(user_tg_id, 'Оплата пришла, проверьте кошелек!',
                         reply_markup=trade_kb.confirm_paymend_from_buyer(trade_id))


def create_announcement(temp_announcement):
    user = temp_announcement.user
    trade_currency = temp_announcement.trade_currency
    announcement = Announcement.create(user_id=user.id,
                                       type_operation=temp_announcement.type_operation,
                                       trade_currency=trade_currency,
                                       amount=temp_announcement.amount,
                                       exchange_rate=temp_announcement.exchange_rate,
                                       status='close')

    temp_payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user.id)

    for curr in temp_payment_currency:
        PaymentCurrency.create(announcement=announcement.id,
                               payment_currency=curr.payment_currency)

    TempAnnouncement.delete().where(TempAnnouncement.user_id == user.id).execute()
    TempPaymentCurrency.delete().where(TempPaymentCurrency.user_id == user.id).execute()

    return announcement

def get_max_limit(temp_announcement):
    user = temp_announcement.user

    if temp_announcement.type_operation_id == 'sale':
        trade_currency = temp_announcement.trade_currency
        trade_amount = temp_announcement.amount
        rate = temp_announcement.exchange_rate

        virt_balance = VirtualWallet.get(user_id=user.id, currency=trade_currency)


def deal_info(announc_id):
    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}
    status = {'open': '⚪️ Активно',
              'close': '🔴 Отключено'}

    announcement = Announcement.get(id=announc_id)
    type_operation = announcement.type_operation
    trade_currency = announcement.trade_currency
    announc_status = announcement.status
    amount = announcement.amount
    price_for_currency = currency_in_usd(trade_currency, 1)
    payment_currency = PaymentCurrency.select().where(PaymentCurrency.announcement_id == announc_id)

    txt = f'📰️  Объявление {announcement.id}\n\n' \
        f'**{trade_direction[type_operation]["type"]} {trade_currency} {trade_direction[type_operation]["icon"]}**\n\n' \
        f'**Стоимость:** {price_for_currency} USD\n' \
        f'**Сумма**: {amount} {trade_currency}\n\n' \
        f'**Платёжные инструменты:**\n'

    for curr in payment_currency:
        txt += f'**{curr.payment_currency}**\n'

    txt += f'\n\n**Статус:** {status[announc_status]}'

    return txt


def announcement_list_kb(type_operation, offset):
    if type_operation == 'buy':
        order_by = Announcement.exchange_rate.desc()
    else:
        order_by = Announcement.exchange_rate

    anc = Announcement
    announcs = (Announcement
                .select()
                .where(
        (Announcement.id.not_in(Trade.select(Trade.announcement_id).where(Trade.status == 'in processing')))
        & (Announcement.type_operation == type_operation)
        & (Announcement.status == 'open'))
                .order_by(order_by)
                .offset(offset)
                .limit(7))

    all_announc = (Announcement
                   .select()
                   .where(
        (Announcement.id.not_in(Trade.select(Trade.announcement_id).where(Trade.status == 'in processing')))
        & (Announcement.type_operation == type_operation)
        & (Announcement.status == 'open'))
                   .order_by(order_by)
                   )

    # icon = {1: 'Ⓜ️', 2: '🏵',
    #         3: '💸', 4: '',
    #         5: '', 6: '',
    #         7: ''}

    buttons = {'buy': {'name': 'Смотреть список на продажу',
                       'cb': 'sale'},
               'sale': {'name': 'Смотреть список на покупку',
                        'cb': 'buy'}}

    kb_list = []
    kb_list.append([InlineKeyboardButton(buttons[type_operation]['name'],
                                         callback_data=f'annlist t {buttons[type_operation]["cb"]} {offset}')])
    for an in announcs:
        currency_trade = an.trade_currency
        amount = an.amount
        # pay_curr = an.payment_currency
        pay_curr = PaymentCurrency.select().where(PaymentCurrency.announcement_id == an.id)
        curs = ''
        for curr in pay_curr:
            curs += f'{curr.payment_currency} '
        name = f'{currency_trade} (1 USD): {amount} {curs}'

        kb_list.append([InlineKeyboardButton(name, callback_data=f'open announc {an.id}')])

    if len(all_announc) < 7:
        kb_list.append([InlineKeyboardButton('🔙 Назад', callback_data=f'annlist back {type_operation} {offset}')])

    else:
        numb_list_l = f'/{math.ceil(len(all_announc) / 7)}'
        numb_list_r = f'/{math.ceil(len(all_announc) / 7)}'
        kb_list.append(
            [InlineKeyboardButton(f'⇐ {numb_list_l}', callback_data=f'annlist left {type_operation} {offset}'),
             InlineKeyboardButton('🔙 Назад', callback_data=f'annlist back {type_operation} {offset}'),
             InlineKeyboardButton(f'{numb_list_r} ⇒', callback_data=f'annlist right {type_operation} {offset}')])

    kb = InlineKeyboardMarkup(kb_list)

    return kb
