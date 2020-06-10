from pyrogram import InlineKeyboardMarkup

from blockchain import minterAPI, ethAPI
from model import Wallet, VirtualWallet, CashFlowStatement


def delete_msg(cli, user_id, msg):
    try:
        cli.delete_messages(user_id, msg)
    except Exception as e:
        print(e)
        pass


def create_wallets_for_user(user):
    currency = ['BIP', 'ETH', 'BTC', 'USDT', 'UAH', 'USD', 'RUB']
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

    Wallet.create(user_id=user.id,
                  currency='BTC',
                  address='btc address',
                  private_key='btc key')

    Wallet.create(user_id=user.id,
                  currency='UAH',
                  address='uah address',
                  private_key='uah key')

    Wallet.create(user_id=user.id,
                  currency='RUB',
                  address='uah address',
                  private_key='uah key')

    Wallet.create(user_id=user.id,
                  currency='USD',
                  address='uah address',
                  private_key='uah key')

    for c in currency:
        VirtualWallet.create(user_id=user.id,
                             currency=c)


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


def create_cash_flow_record(**data):
    CashFlowStatement.insert(data).execute()


def check_address(address, currency):

    valid = False

    if currency == 'BIP':
        re = minterAPI.API.get_balance(address)
        if 'result' in re:
            valid = True

    if currency in ['ETH', 'USDT']:
        try:
            re = ethAPI.get_balance(address, currency)
            valid = True
        except ValueError:
            pass

    # TODO костыль
    if currency not in ['ETH', 'USDT', 'BIP']:
        valid = True

    return valid