from bot.blockchain import minterAPI, ethAPI, rpc_btc
from bot.helpers.shortcut import create_record_cashflow, get_user, delete_msg
from bot.models import WithdrawalRequest

from user.models import Wallet, VirtualWallet

from config.settings import env
import logging

logger = logging.getLogger('TradeEvent')


def create_wallets_for_user(user):
    currency = ['BIP', 'ETH', 'USDT', 'UAH', 'USD', 'RUB', 'BONUS']
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

    # # add btc_wallet
    # Wallet.objects.create(
    #     user_id=user.id,
    #     currency='BTC',
    #     address=rpc_btc.get_new_address(),
    #     private_key='private key'
    # )

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

    logger.info('New user registered: %s, name: %s. New Wallets created'%(user.telegram_id, user.first_name))


def create_reflink(user_id=None, order_id=None):
    # TODO  Возможно использовать шифрование

    bot_link = f'https://t.me/{env.str("BOT_USERNAME")}?start=u{user_id}'

    if order_id:
        bot_link = f'https://t.me/{env.str("BOT_USERNAME")}?start=t{order_id}'

    return bot_link


def update_wallet_balance(user, currency, amount, operation):
    wallet = user.virtual_wallets.get(currency=currency)
    if operation == 'up':
        wallet.balance += amount
    elif operation == 'down':
        wallet.balance -= amount

    wallet.save()


def finish_withdraw(withdrawal_request_id, tx_hash):
    withdrawal_request = WithdrawalRequest.objects.get(id=withdrawal_request_id)
    withdrawal_request.tx_hash = tx_hash
    withdrawal_request.status = 'done'
    withdrawal_request.save()

    user = withdrawal_request.user
    amount = withdrawal_request.amount - withdrawal_request.fee
    currency = withdrawal_request.currency

    update_wallet_balance(user, withdrawal_request.currency, amount, 'down')

    create_record_cashflow(user, None, 'withdrawal', amount, currency, tx_hash=tx_hash)


def check_commands_requisite(cli, txt, user):
    commands = [
        user.get_text(name='user-kb-wallet'),
        user.get_text(name='user-kb-trade'),
        user.get_text(name='user-kb-settings')
    ]

    if txt in commands:
        flags = user.flags
        flags.await_requisites_name = False
        flags.edit_requisite = False
        flags.await_requisites_address = False
        flags.save()
        delete_msg(cli, user.telegram_id, user.cache['msg']['wallet_menu'])
        return True

    return False


def check_requisite_uniq_name(user, currency, req_name):
    req = user.requisites.get_or_none(currency=currency, name__in=[req_name.lower(), req_name])

    if req:
        return False

    return True


def check_requisite_uniq_address(user, currency, req_address):
    req = user.requisites.get_or_none(currency=currency, address__in=[req_address.lower(), req_address])

    if req:
        return False

    return True

