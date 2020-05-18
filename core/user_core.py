from bot_tools.converter import bip_in_usd, eth_in_usd, usdt_in_usd
from mintersdk.shortcuts import to_bip, to_pip


def create_reflink(user_id, trade_id=None):
    bot_link = f'https://t.me/bankertest_bot?start=u{user_id}'

    if trade_id:
        bot_link = f'https://t.me/bankertest_bot?start=t{trade_id}'

    return bot_link


def wallet_info(user):
    virt_wallets = user.virt_wallets
    txt = '💼 Кошелёк\n\n' \
          'Баланс:\n'
    for w in virt_wallets:
        balance_in_usd = 0

        if w.balance > 0:

            if w.currency == 'BIP':
                balance_in_usd = bip_in_usd(to_bip(w.balance))

            if w.currency == 'ETH':
                balance_in_usd = eth_in_usd(to_bip(w.balance))

            if w.currency == 'USDT':
                balance_in_usd = usdt_in_usd(to_bip(w.balance))

        txt += f'{to_bip(w.balance)} {w.currency} ~{balance_in_usd} USD\n'

    return txt
