from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum

from bot.helpers.converter import currency_in_user_currency
from bot.helpers.shortcut import to_units, round_currency
from order.models import Order, ParentOrder


def choice_payment_currency_text(order):
    payment_currency_list = order.payment_currency
    user = order.user
    if order.type_operation == 'sale':
        type_op = user.get_text(name="order-type_operation_translate_sale_1")
    else:
        type_op = user.get_text(name="order-type_operation_translate_buy_1")

    txt = f'{order.user.get_text(name="order-select_payment_currency").format(type_operation=type_op, currency=order.trade_currency)}\n\n'
    if len(payment_currency_list) > 0:
        txt += f'{order.user.get_text(name="order-your_choice")}\n'
        for currency in payment_currency_list:
            txt += f'**{currency}**\n'

    return txt


def wallet_info(user):
    user_currency = user.settings.currency

    virt_wallets = user.virtual_wallets.exclude(currency__in=['UAH', 'RUB', 'USD', 'BONUS'])

    balance_txt = ''
    for w in virt_wallets:

        balance = user.get_balance(w.currency, cent2unit=True)

        if w.balance > 0:
            balance_in_user_currency = round_currency(user_currency, currency_in_user_currency(w.currency, user_currency, balance))
        else:
            balance_in_user_currency = 0

        balance_txt += f'{round_currency(w.currency, balance)} {w.currency} ≈ {balance_in_user_currency} {user_currency}\n'

    bonus_balance = to_units('BONUS', user.virtual_wallets.get(currency='BONUS').balance, round=True)
    txt = user.get_text(name='wallet-wallet_info').format(
        balances=balance_txt)

    if bonus_balance >= 0.01:
        txt += user.get_text(name='wallet-affiliate_bonus').format(balance=bonus_balance)

    hold_money = user.holdMoney.exclude(currency__in=['UAH', 'RUB', 'USD'])

    if hold_money.count() > 0:
        hm_dict = defaultdict(int)
        for hm in hold_money:
            hm_dict[hm.currency] += hm.amount

        hold_money_txt = ''

        for currency in hm_dict:
            amount = to_units(currency,  hm_dict[currency], round=True)
            hold_money_txt += f'{amount} {currency}\n'

        txt += f'\n{user.get_text(name="wallet-hold_money").format(hold_money=hold_money_txt)}'

    withdrawal_requests = user.withdrawalRequests.filter(status__in=['pending verification', 'verifed'])

    if withdrawal_requests.count() > 0:
        wr_dict = defaultdict(int)
        for wr in withdrawal_requests:
            wr_dict[wr.currency] += wr.amount

        wr_hold_money_txt = ''

        for currency in wr_dict:
            amount = to_units(currency, wr_dict[currency], round=True)
            wr_hold_money_txt += f'{amount} {currency}'

        txt += f'\n{user.get_text(name="wallet-hold_money_for_withdrawal").format(hold_money=wr_hold_money_txt)}'

    return txt


def get_lack_balance_text(order, deposit_currency):
    user = order.user
    amount = to_units(order.trade_currency, order.amount)
    text = ''

    if order.type_operation == 'sale':
        trade_currency = order.trade_currency
        balance = user.get_balance(trade_currency, cent2unit=True)
        to_deposit = amount - balance
        text += f'{trade_currency} {round_currency(trade_currency, to_deposit, to_str=True, round_up=True)}\n'
    else:
        for currency in deposit_currency:
            payment_currency_rate = to_units(currency, order.payment_currency_rate[currency])
            trade_currency_rate = to_units(order.trade_currency, order.currency_rate)
            balance = user.get_balance(currency, cent2unit=True)
            price_trade = Decimal(amount * trade_currency_rate / payment_currency_rate)
            to_deposit = price_trade - balance

            text += f'{currency} {round_currency(currency, to_deposit, to_str=True, round_up=True)}\n'

    return text


def order_operation(user, order_id, t_op):
    user_id = user.id
    parent_order = Order.objects.get(id=order_id)
    parent_order_id = parent_order.parent_order_id
    user_order = ParentOrder.objects.get(id=parent_order_id).user_id
    operation = parent_order.type_operation
    type_operation = ''
    if user_id == user_order:
        type_operation = t_op
    if user_id != user_order and operation == 'sale':
        type_operation = 'Покупка'
    if user_id != user_order and operation == 'buy':
        type_operation = 'Продажа'

    return type_operation
