from bot.blockchain import minterAPI, ethAPI
from user.models import Wallet, VirtualWallet

from config.settings import env


def create_wallets_for_user(user):
    currency = ['BIP', 'ETH', 'BTC', 'USDT', 'UAH', 'USD', 'RUB']
    minter_wallet = minterAPI.create_wallet()
    eth_wallet = ethAPI.create_wallet()

    Wallet.objects.create(
        user_id=user.id,
        currency='BIP',
        address=minter_wallet['address'],
        mnemonic=minter_wallet['mnemonic'],
        private_key=minter_wallet['private_key']
    )

    Wallet.objects.create(
        user_id=user.id,
        currency='ETH',
        address=eth_wallet.address.lower(),
        private_key=ethAPI.Web3.toHex(eth_wallet.privateKey)
    )

    Wallet.objects.create(
        user_id=user.id,
        currency='BTC',
        address='btc address',
        private_key='btc key'
    )

    Wallet.objects.create(
        user_id=user.id,
        currency='UAH',
        address='uah address',
        private_key='uah key'
    )

    Wallet.objects.create(
        user_id=user.id,
        currency='RUB',
        address='uah address',
        private_key='uah key'
    )

    Wallet.objects.create(
        user_id=user.id,
        currency='USD',
        address='uah address',
        private_key='uah key')

    for c in currency:
        VirtualWallet.objects.create(user_id=user.id, currency=c)


def create_reflink(user_id, trade_id=None):
    # TODO  Возможно использовать шифрование

    bot_link = f'https://t.me/{env.str("BOT_USERNAME")}?start=u{user_id}'

    if trade_id:
        bot_link = f'https://t.me/{env.str("BOT_USERNAME")}?start=t{trade_id}'

    return bot_link
