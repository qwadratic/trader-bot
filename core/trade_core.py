from decimal import Decimal
from time import sleep
import math

from mintersdk.shortcuts import to_bip, to_pip
from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

from blockchain import ethAPI, minterAPI
from bot_tools import converter
from bot_tools.converter import currency_in_usd
from bot_tools.help import correct_name, get_balance_from_currency
from logs import trade_log
from trade_errors import InsufficientFundsOwner, MinterErrorTransaction, InsufficientFundsAnnouncement, TransactionError
from keyboard import trade_kb
from model import Announcement, PaymentCurrency, Trade, User, VirtualWallet, TempPaymentCurrency, TempAnnouncement, \
    HoldMoney, Wallet, UserPurse
from text import trade_text

from datetime import datetime as dt


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


def get_ad_info(announc_id):
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
    amount = to_bip(announcement.amount)
    price_for_currency = currency_in_usd(trade_currency, 1)
    payment_currency = PaymentCurrency.select().where(PaymentCurrency.announcement_id == announc_id)

    txt = f'📰️  Объявление {announcement.id}\n\n' \
        f'**{trade_direction[type_operation]["type"]} {trade_currency} {trade_direction[type_operation]["icon"]}**\n\n' \
        f'**Стоимость:** {to_bip(announcement.exchange_rate) * amount} USD\n' \
        f'**Сумма**: {amount} {trade_currency}\n\n' \
        f'Цена за 1 {trade_currency}  {to_bip(announcement.exchange_rate)} USD\n\n' \
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
        name = f'{currency_trade} : {to_bip(amount)}'

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


def hold_money(cli, trade):
    announcement = trade.announcement

    trade_currency = announcement.trade_currency
    announc_owner = announcement.user

    owner_wallet = VirtualWallet.get(user_id=announc_owner.id, currency=trade_currency)

    if trade.amount > announcement.amount:
        raise InsufficientFundsAnnouncement('У объявления баланс меньше запрашиваемой суммы')

    if trade.amount > owner_wallet.balance:
        raise InsufficientFundsOwner('У владельца нет денег')

    HoldMoney.create(trade=trade.id, amount=trade.amount)
    trade_log.successful_hold(cli, trade, owner_wallet, trade_currency)

    announcement.amount -= trade.amount
    announcement.save()

    owner_wallet.balance -= trade.amount
    owner_wallet.save()


def start_trade(cli, trade):
    user = trade.user
    user_wallet = VirtualWallet.get(user_id=user.id, currency=trade.user_currency)
    user_name = correct_name(user)

    owner = trade.announcement.user
    owner_name = correct_name(owner)
    owner_wallet = VirtualWallet.get(user_id=user.id, currency=trade.announcement.trade_currency)
    #  Продажа или покупка
    type_operation = trade.announcement.type_operation

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

    if payment_currency == 'USDT':
        user_currency_wallet = Wallet.get(user_id=user.id, currency='ETH')
        owner_currency_wallet = Wallet.get(user_id=owner.id, currency='ETH')
    else:
        user_currency_wallet = Wallet.get(user_id=user.id, currency=payment_currency)
        owner_currency_wallet = Wallet.get(user_id=owner.id, currency=trade_currency)

    owner_recipient_address = UserPurse.get(user_id=owner.id, currency=payment_currency).address
    user_recipient_address = UserPurse.get(user_id=user.id, currency=trade_currency).address


    # Депонирование средств
    try:
        hold_money(cli, trade)
    except InsufficientFundsAnnouncement:
        pass

    except InsufficientFundsOwner:
        pass

    # Лог о начале сделки
    trade_log.trade_start(cli, trade, owner_name, user_name, type_operation, trade_currency_price, trade_currency, price_deal_in_usd, price_deal_in_payment_currency)

    # Первая транзакция, платит первый тот, кто начинает сделку
    try:
        tx_1 = auto_transaction(payment_currency, user_currency_wallet, owner_recipient_address, price_deal_in_payment_currency)
        if tx_1[1] == 'error':
            tx_hash = tx_1[0]
            err_txt = tx_1[2]
            trade_log.tx_error(cli, 'first', trade, user_wallet.balance, user_currency_wallet.address, owner_recipient_address, payment_currency, price_deal_in_payment_currency, err_txt, tx_hash)
    except MinterErrorTransaction as err:
        return trade_log.tx_error(cli, 'first', trade, user_wallet.balance, user_currency_wallet.address, owner_recipient_address, payment_currency, price_deal_in_payment_currency, err)

    except Exception as e:
        return trade_log.tx_error(cli, 'first', trade, user_wallet.balance, user_currency_wallet.address, owner_recipient_address, payment_currency, price_deal_in_payment_currency, e)

    tx_hash_1 = tx_1[0]
    fee_1 = tx_1[1]
    trade_log.successful_tx(cli, 'first', trade, user_currency_wallet.address, owner_recipient_address, payment_currency, price_deal_in_payment_currency, fee_1, tx_hash_1)


    # Вторая транзакция, платит владелец объявления
    try:
        tx_2 = auto_transaction(trade_currency, owner_currency_wallet, user_recipient_address, trade.amount)
        if tx_2[1] == 'error':
            tx_hash = tx_2[0]
            err_txt = tx_2[2]
            trade_log.tx_error(cli, 'second', trade, owner_wallet.balance, owner_currency_wallet.address, user_recipient_address, trade_currency, trade.amount, err_txt, tx_hash)

    except Exception as e:
        return trade_log.tx_error(cli, 'second', trade, owner_wallet.balance, owner_currency_wallet.address, user_recipient_address, trade_currency, trade.amount, e)

    tx_hash_2 = tx_2[0]
    fee_2 = tx_2[1]

    trade_log.successful_tx(cli, 'second', trade, owner_currency_wallet.address, user_recipient_address, trade_currency,
                            to_bip(trade.amount), fee_2, tx_hash_2)

    close_trade(cli, trade, fee_2, fee_1, price_deal_in_payment_currency)


def start_semi_auto_trade(cli, trade, amount, recipient_address):
    user = trade.user
    txt = f'Отправьте {amount} {trade.user_currency} на счёт:\n' \
        f'{recipient_address}'

    kb = InlineKeyboardMarkup([[InlineKeyboardButton('Я оплатил', callback_data=f'i payed {trade.id}')],
                               [InlineKeyboardButton('Отменить сделку', callback_data=f'trade cancel {trade.id}')]])
    cli.send_message(user.tg_id, txt, reply_markup=kb)


def auto_transaction(payment_currency, wallet, recipient_address, amount):
    if payment_currency == 'BIP':
        signed_tx = minterAPI.create_transaction(wallet, recipient_address, amount)
        send_tx = minterAPI.send_transaction(signed_tx)

        if 'error' in send_tx:
            err = str(send_tx['error'])
            raise MinterErrorTransaction(err)

        tx_hash = 'Mt' + send_tx['result']['hash'].lower()
        return [tx_hash, to_pip(0.01)]

    if payment_currency == 'ETH':
        gasPrice = ethAPI.w3.eth.gasPrice
        fee = gasPrice * 21000
        signed_tx = ethAPI.create_transaction(wallet.address, recipient_address, amount, wallet.private_key, gasPrice)
        send_tx = ethAPI.send_tx(signed_tx)
        tx_hash = send_tx.transactionHash.hex()
        if send_tx.status == 0:
            err = str(send_tx)
            return [tx_hash, 'error', err]

        return [tx_hash, fee]

    if payment_currency == 'USDT':
        gasPrice = ethAPI.w3.eth.gasPrice
        signed_tx = ethAPI.create_usdt_tx(wallet.address, recipient_address, amount, wallet.private_key, gasPrice)
        send_tx = ethAPI.send_tx(signed_tx)
        tx_hash = send_tx.transactionHash.hex()

        if send_tx.status == 0:
            err = str(send_tx)
            return [tx_hash, 'error', err]

        fee = gasPrice * send_tx.gasUsed
        return [tx_hash, fee]


def close_trade(cli, trade, owner_fee, user_fee, price_deal_in_payment_currency):
    HoldMoney.delete().where(HoldMoney.trade_id == trade.id).execute()

    user = trade.user
    owner = trade.announcement.user

    announcement = trade.announcement

    owner_wallet = VirtualWallet.get(user_id=owner.id, currency=trade.announcement.trade_currency)
    owner_wallet.balance -= owner_fee
    owner_wallet.save()

    user_wallet = VirtualWallet.get(user_id=user.id, currency=trade.user_currency)

    if trade.deposite:
        user_wallet.balance -= to_pip(price_deal_in_payment_currency) + user_fee
        user_wallet.save()

    if announcement.amount == 0:
        turn_off_announcement_and_inform(cli, announcement.id)

    trade_log.successful_trade(cli, trade, price_deal_in_payment_currency)


def turn_off_announcement_and_inform(cli, announcement_id):
    # TODO комиссию боту
    announcement = Announcement.get(id=announcement_id)

    user = announcement.user

    trade_currency = 'ETH' if announcement.trade_currency == 'USDT' else announcement.trade_currency
    user_balance = VirtualWallet.get(user_id=user.id, currency=trade_currency).balance
    txt = '❗️ Ваши следующие объявления были деактивированы:\n\n'
    announcements = Announcement.select().where((Announcement.user_id == user.id) & (Announcement.trade_currency == trade_currency) & (Announcement.type_operation == announcement.type_operation))
    for ad in announcements:
        if ad.amount > user_balance or ad.amount == 0:
            ad.status = 'close'
            txt += f'№{announcement.id}\n'

        ad.save()

    try:
        cli.send_message(user.tg_id, txt)
    except Exception as e:
        print(f'error 332 trade core {e}')