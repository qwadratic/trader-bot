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
                  address=eth_wallet.address,
                  private_key=ethAPI.Web3.toHex(eth_wallet.privateKey))

    VirtualWallet.create(user_id=user.id,
                         currency='BIP')
    VirtualWallet.create(user_id=user.id,
                         currency='ETH')
