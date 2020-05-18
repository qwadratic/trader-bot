from decimal import Decimal
from time import sleep
import math

from mintersdk.shortcuts import to_bip, to_pip
from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

from blockchain import ethAPI, minterAPI
from bot_tools import converter
from bot_tools.converter import currency_in_usd
from bot_tools.help import broadcast_action, correct_name
from trade_errors import InsufficientFundsUser, InsufficientFundsOwner, MinterErrorTransaction, EthErrorTransaction
from keyboard import trade_kb
from model import Announcement, PaymentCurrency, Trade, User, VirtualWallet, TempPaymentCurrency, TempAnnouncement, \
    HoldMoney, Wallet, UserPurse
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


def hold_money(trade):
    announcement = trade.announcement

    trade_currency = announcement.trade_currency
    announc_owner = announcement.user

    owner_wallet = VirtualWallet.get(user_id=announc_owner.id, currency=trade_currency)

    if trade.amount > announcement.amount:
        raise InsufficientFundsOwner('У объявления баланс меньше запрашиваемой суммы')

    HoldMoney.create(trade=trade.id, amount=trade.amount)
    owner_wallet.balance -= trade.amount
    owner_wallet.save()


def auto_trade(cli, trade):
    user = trade.user
    user_wallet = VirtualWallet.get(user_id=user.id, currency=trade.user_currency)

    owner = trade.announcement.user

    owner_trade_currency_price = trade.announcement.exchange_rate

    cost_user_currency_in_usd = Decimal(converter.currency_in_usd(trade.user_currency, 1))

    #  Цена сделки в долларах
    price_deal_in_usd = to_bip(trade.amount) * to_bip(owner_trade_currency_price)

    #  Сколько нужно юзеру заплатить
    price_deal_in_user_currency = price_deal_in_usd / cost_user_currency_in_usd

    owner_name = correct_name(owner)
    user_name = correct_name(user)
    log = dict(message='Начало сделки!', trade_id=trade.id, owner=owner_name, user_name=user_name, type_operation=trade.announcement.type_operation,
               trade_currency=trade.announcement.trade_currency, user_currency=trade.user_currency, amount=to_bip(trade.amount),
               price_for_user_in_usd=price_deal_in_usd, price_for_user_in_currency=price_deal_in_user_currency)
    broadcast_action(cli, log)

    if user_wallet.balance < to_pip(price_deal_in_user_currency):
        txt_error = f'Недостаточно средств для начала сделки\n\n' \
            f'Ваш баланс: {to_bip(user_wallet.balance)} {trade.user_currency}\n' \
            f'Сумма сделки: {price_deal_in_user_currency} {trade.user_currency}'
        log = dict(trade_id=trade.id, error='InsufficientFundsUser', user_balance=to_bip(user_wallet.balance), price_trade_in_user_currency=price_deal_in_user_currency,
                   currency=trade.user_currency)
        broadcast_action(cli, log)
        
        raise InsufficientFundsUser(txt_error)

    hold_money(trade)

    if trade.announcement.trade_currency == 'ETH':
        owner_eth_wallet = Wallet.get(user_id=owner.id, currency='ETH')
        user_currency_wallet = Wallet.get(user_id=user.id, currency=trade.user_currency)
        user_recipient_address = UserPurse.get(user_id=user.id, currency='ETH').address

        owner_recipient_address = UserPurse.get(user_id=owner.id, currency=trade.user_currency).address

        # Отправляет пользователь
        if trade.user_currency == 'BIP':

            signed_tx = minterAPI.create_transaction(user_currency_wallet, owner_recipient_address, to_pip(price_deal_in_user_currency))
            send_tx = minterAPI.send_transaction(signed_tx)
            if 'error' in send_tx and send_tx['error']['tx_result']['code'] == 107:
                err = send_tx['error']['tx_result']['code']['log']
                error_log = dict(trade_id=trade.id, action='error', error=err, from_address=user_currency_wallet.address, to=owner_recipient_address, amount=price_deal_in_user_currency,
                                 currency=trade.user_currency)
                broadcast_action(cli, error_log)
                raise MinterErrorTransaction(f"{err}\n")

            log = dict(trade_id=trade.id, action='successful transaction', from_address=user_currency_wallet.address,
                       to=owner_recipient_address, amount=price_deal_in_user_currency,
                       currency=trade.user_currency,
                       user_fee=0.02, tx_hash=send_tx.transactionHash.hex())

            broadcast_action(cli, log)

            gasPrice = ethAPI.w3.eth.gasPrice
            fee = gasPrice * 21000

            signed_tx2 = ethAPI.create_transaction(owner_eth_wallet.address, user_recipient_address, to_bip(trade.amount), owner_eth_wallet.private_key)

            try:
                send_tx2 = ethAPI.send_tx(signed_tx2)
                log = dict(trade_id=trade.id, action='successful transaction', from_address=owner_eth_wallet.address, to=user_recipient_address, amount=to_bip(trade.amount),
                           currency=trade.announcement.trade_currency, owner_fee=to_bip(fee), tx_hash=send_tx2.transactionHash.hex())

                broadcast_action(cli, log)
            except ValueError as e:
                error_log = dict(trade_id=trade.id, action='error', error=e, from_address=owner_eth_wallet.address, to=user_recipient_address, amount=to_bip(trade.amount),
                                 currency='ETH', owner_balance=to_bip(ethAPI.get_balance(owner_eth_wallet.address, 'ETH')))
                broadcast_action(cli, error_log)
                raise ValueError('У владельца сделки не хватает средств')

            if send_tx2.status == 0:
                error_log = dict(trade_id=trade.id, action='error', error='status == 0', from_address=owner_eth_wallet.address, to=user_recipient_address, amount=to_bip(trade.amount),
                                 currency='ETH', tx_hash=send_tx2.transactionHash.hex())
                broadcast_action(cli, error_log)
                raise EthErrorTransaction('Статус сделки 0')

            close_trade(cli, user, owner, trade, send_tx2.transactionHash.hex(), fee, to_pip(0.02), price_deal_in_user_currency)
            return price_deal_in_user_currency

    if trade.announcement.trade_currency == 'BIP':
        owner_bip_wallet = Wallet.get(user_id=owner.id, currency='BIP')
        user_currency_wallet = Wallet.get(user_id=user.id, currency=trade.user_currency)
        user_recipient_address = UserPurse.get(user_id=user.id, currency='BIP').address

        owner_recipient_address = UserPurse.get(user_id=owner.id, currency=trade.user_currency).address

        # Отправляет пользователь
        if trade.user_currency == 'ETH':

            signed_tx = ethAPI.create_transaction(user_currency_wallet.address, owner_recipient_address,
                                                   price_deal_in_user_currency, user_currency_wallet.private_key)

            gasPrice = ethAPI.w3.eth.gasPrice
            fee = gasPrice * 21000
            try:
                send_tx = ethAPI.send_tx(signed_tx)
                log = dict(trade_id=trade.id, action='successful transaction', from_address=user_currency_wallet.address,
                           to=owner_recipient_address, amount=price_deal_in_user_currency,
                           currency='ETH', user_fee=fee, tx_hash=send_tx.transactionHash.hex())
                broadcast_action(cli, log)

            except ValueError as e:
                error_log = dict(trade_id=trade.id, action='error', error=e, from_address=user_currency_wallet.address,
                                 to=owner_recipient_address, amount=price_deal_in_user_currency,
                                 currency='ETH', user_balance=to_bip(ethAPI.get_balance(user_currency_wallet.address, 'ETH')))
                broadcast_action(cli, error_log)

                raise ValueError('У юзера не хватило средств')

            if send_tx.status == 0:
                error_log = dict(trade_id=trade.id, action='error', error='status == 0',
                                 from_address=user_currency_wallet.address, to=owner_recipient_address,
                                 amount=to_bip(trade.amount),
                                 currency='ETH', tx_hash=send_tx.transactionHash.hex())
                broadcast_action(cli, error_log)
                raise EthErrorTransaction('Статус сделки 0')

            signed_tx2 = minterAPI.create_transaction(owner_bip_wallet, user_recipient_address,
                                                      trade.amount)
            send_tx2 = minterAPI.send_transaction(signed_tx2)
            if 'error' in send_tx2 and send_tx2['error']['tx_result']['code'] == 107:
                error = f"{send_tx2['error']['tx_result']['code']['log']}"
                error_log = dict(trade_id=trade.id, action='error', error=error,
                                 from_address=user_currency_wallet.address, to=owner_recipient_address,
                                 amount=price_deal_in_user_currency,
                                 currency=trade.user_currency)
                broadcast_action(cli, error_log)
                raise MinterErrorTransaction(f"{error}\n")

            close_trade(cli, user, owner, trade, send_tx.transactionHash.hex(), to_pip(0.02), fee, price_deal_in_user_currency)
            return price_deal_in_user_currency


def close_trade(cli, user, owner, trade, eth_hash,  owner_fee, user_fee, price_deal_in_user_currency):

    HoldMoney.delete().where(HoldMoney.trade_id == trade.id).execute()

    announcement = trade.announcement
    announcement.amount -= trade.amount
    announcement.save()

    owner_wallet = VirtualWallet.get(user_id=owner.id, currency=trade.announcement.trade_currency)
    owner_wallet.balance -= owner_fee
    owner_wallet.save()

    user_wallet = VirtualWallet.get(user_id=user.id, currency=trade.user_currency)
    user_wallet.balance -= to_pip(price_deal_in_user_currency) + user_fee
    user_wallet.save()

    log = dict(message='Сделка прошла успешно!', trade_id=trade.id)
    broadcast_action(cli, log)