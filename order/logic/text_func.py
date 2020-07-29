from decimal import Decimal

from django.db.models import Sum

from bot.helpers.converter import currency_in_user_currency
from bot.helpers.shortcut import to_units, round_currency


def choice_payment_currency_text(order):
    payment_currency_list = order.payment_currency

    txt = f'{order.user.get_text(name="order-select_payment_currency").format(currency=order.trade_currency)}\n\n'
    if len(payment_currency_list) > 0:
        txt += f'{order.user.get_text(name="order-your_choice")}\n'
        for currency in payment_currency_list:
            txt += f'**{currency}**\n'

    return txt


def wallet_info(user):
    user_currency = user.settings.currency

    virt_wallets = user.virtual_wallets.exclude(currency__in=['UAH', 'RUB', 'USD'])

    balance_txt = ''
    for w in virt_wallets:

        balance = user.get_balance(w.currency, cent2unit=True)

        if w.balance > 0:
            balance_in_user_currency = round_currency(user_currency, currency_in_user_currency(w.currency, user_currency, balance))
        else:
            balance_in_user_currency = 0

        balance_txt += f'{round_currency(w.currency, balance)} {w.currency} ~{balance_in_user_currency} {user_currency}\n'

    txt = user.get_text(name='wallet-wallet_info').format(balances=balance_txt)

    hold_money = user.holdMoney.all()

    if hold_money.count() > 0:
        hm_dict = {}
        for hm in hold_money:
            try:
                hm_dict[hm.currency] += hm.amount
            except KeyError:
                hm_dict[hm.currency] = hm.amount

        hold_money_txt = ''

        for currency in hm_dict:
            hold_money_txt += f'{round_currency(currency, to_units(currency, hm_dict[currency]))} {currency}\n'

        txt += f'\n{user.get_text(name="wallet-hold_money").format(hold_money=hold_money_txt)}'
    return txt


def get_lack_balance_text(order, deposit_currency):
    user = order.user
    amount = to_units(order.trade_currency, order.amount)
    text = ''
    for currency in deposit_currency:
        payment_currency_rate = to_units(currency, order.payment_currency_rate[currency])
        trade_currency_rate = to_units(order.trade_currency, order.currency_rate)
        balance = user.get_balance(currency, cent2unit=True)
        price_trade = Decimal(amount * trade_currency_rate / payment_currency_rate)
        to_deposit = price_trade - balance

        text += f'{currency} {to_deposit}\n'

    return text
