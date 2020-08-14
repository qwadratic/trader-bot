from bot.blockchain.rpc_btc import get_block, get_wallet_balance

from bot.models.core import Service
from user.models import VirtualWallet


def check_refill_btc(cli):
    current_block = get_block()
    service = Service.objects.get_or_none(currency='BTC')
    update_wallet_balance()
    if not service:
        Service.objects.create(last_block=current_block, currency='BTC')
        return

    if current_block == service.last_block:
        pass
    else:
        service.last_block = current_block
        service.save()

def update_wallet_balance():
    user_wallets = VirtualWallet.objects.filter(currency='BTC')
    user_name = []
    user_name.append(user_wallets.user_id)

    for name in user_name:
        update_balance = []
        wallet_name = name
        actual_balance = get_wallet_balance(wallet_name)
        update_balance.append(actual_balance)


        # костыль
        try:
            VirtualWallet.objects.update(balance=update_balance)
            return
        except ValueError:
            VirtualWallet.objects.update(balance=0)
            return
