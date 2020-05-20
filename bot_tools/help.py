from pyrogram import InlineKeyboardMarkup

from blockchain import minterAPI, ethAPI
from model import Wallet, VirtualWallet


def delete_msg(cli, user_id, msg):
    try:
        cli.delete_messages(user_id, msg)
    except Exception:
        pass


def create_wallets_for_user(user):

    minter_wallet = minterAPI.create_wallet(user.id)
    eth_wallet = ethAPI.create_wallet()

    Wallet.create(user_id=user.id,
                  currency='BIP',
                  address=minter_wallet['address'],
                  mnemonic=minter_wallet['mnemonic'],
                  private_key=minter_wallet['private_key'])

    Wallet.create(user_id=user.id,
                  currency='ETH',
                  address=eth_wallet.address.lower(),
                  private_key=ethAPI.Web3.toHex(eth_wallet.privateKey))

    VirtualWallet.create(user_id=user.id,
                         currency='BIP')
    VirtualWallet.create(user_id=user.id,
                         currency='ETH')


def broadcast_action(cli, log, kb=None):
    channel_id = '-1001376981650'

    if kb:
        try:
            cli.send_message(-1001376981650, log, reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            print(e)
        return
    try:
        cli.send_message(-1001376981650, log)
    except Exception as e:
        print(e)


def correct_name(user):
    name = None

    if user.first_name and not user.last_name:

        name = f'[{user.first_name}](tg://user?id={int(user.tg_id)})'

    elif user.first_name and user.last_name:
        name = f'[{user.first_name} {user.last_name}](tg://user?id={int(user.tg_id)})'
    return name


def get_balance_from_currency(address, currency):

    if currency == 'BIP':
        return minterAPI.get_wallet_balance(address)

    if currency == 'ETH' or currency == 'USDT':
        return ethAPI.get_balance(address, currency)
