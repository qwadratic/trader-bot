from trader_bot.apps.bot.helpers import currency_in_user_currency, to_bip


def choice_payment_currency_text(order):
    payment_currency_list = order.payment_currency

    txt = f'{order.user.get_text(name="order-choice_payment_currency")}\n\n'
    if len(payment_currency_list) > 0:
        txt += f'{order.user.get_text(name="order-your_choice")}\n'
        for currency in payment_currency_list:
            txt += f'**{currency}**\n'

    return txt


def wallet_info(user):
    user_currency = user.settings.currency

    virt_wallets = user.virtual_wallets.exclude(currency__in=['UAH', 'RUB', 'USD'])
    txt = user.get_text(name='wallet-wallet_info')

    balance_in_user_currency = 0

    for w in virt_wallets:

        if w.balance > 0:
            balance_in_user_currency = currency_in_user_currency(w.currency, user_currency, to_bip(w.balance))

        txt += f'\n{round(to_bip(w.balance), 4)} {w.currency} ~{round(balance_in_user_currency, 2)} {user_currency}'

    return txt