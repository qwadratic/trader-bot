from time import sleep

from mintersdk import MinterConvertor
from mintersdk.minterapi import MinterAPI
from mintersdk.sdk.transactions import MinterSendCoinTx, MinterMultiSendCoinTx
from mintersdk.sdk.wallet import MinterWallet
from mintersdk.shortcuts import to_bip, to_pip
from requests import ReadTimeout, ConnectTimeout, HTTPError

from bot_tools.misc import retry
from model import Wallet

API = MinterAPI('https://api.minter.one')

to_handle = ReadTimeout, ConnectTimeout, ConnectionError, HTTPError, ValueError, KeyError


def create_wallet(user_id):
    return MinterWallet.create()


def get_minter_wallet(mnemonic):
    wallet = MinterWallet.create(mnemonic=mnemonic)
    return wallet


@retry(to_handle, tries=3, delay=0.5, backoff=2)
def get_wallet_balance(address):
    r = API.get_balance(address)['result']

    return r['balance']['BIP']


# @retry(to_handle, tries=3, delay=0.5, backoff=2)
# def check_address(address):
#     try:
#         r = API.get_balance(address)['result']
#         return True
#     except KeyError:
#         return False
#
#
# @retry(to_handle, tries=3, delay=0.5, backoff=2)
# def check_coin(coin):
#     r = API.get_coin_info(coin)
#     try:
#         w = r['result']
#         return True
#     except KeyError:
#         return False


@retry(to_handle, tries=3, delay=0.5, backoff=2)
def create_transaction(wallet, address, amount):
    nonce = API.get_nonce(wallet.address)
    tx = MinterSendCoinTx('BIP', address, to_bip(amount), gas_coin='BIP', nonce=nonce)
    tx.sign(wallet.private_key)
    return tx.signed_tx


@retry(to_handle, tries=3, delay=0.5, backoff=2)
def get_commission(tx):
    fee = API.estimate_tx_commission(tx)
    return fee['result']['commission']
#
#
# @retry(to_handle, tries=3, delay=0.5, backoff=2)
# def create_multitransaction(wallet, user_expenses, gas_coin):
#     txs = []
#     for k in user_expenses:
#         chat_address = k.chat.settings.address
#         txs.append({'coin': k.coin, 'to': chat_address, 'value': to_bip(k.amount)})
#
#     nonce = API.get_nonce(wallet['address'])
#     tx = MinterMultiSendCoinTx(txs, gas_coin=gas_coin, nonce=nonce)
#
#     tx.sign(wallet['private_key'])
#     return tx.signed_tx
#
#

@retry(to_handle, tries=3, delay=0.5, backoff=2)
def send_transaction(tx):
    tx = API.send_transaction(tx)
    sleep(3)
    return tx
#
# def get_multicommission(txs_count):
#     commission_per_recipient = 5
#     fee_default_multipier = 1000000000000000
#     recipients_fee = ((txs_count - 1) * commission_per_recipient * fee_default_multipier)
#     base_fee = to_pip(0.01)
#     return recipients_fee + base_fee
#
#
# def find_gas_coin(address):
#     balances = API.get_balance(address, pip2bip=True)['result']['balance']
#     gas_coin = 'BIP'
#     if balances['BIP'] < 0.01 and len(balances) > 1:
#         for coin, balance in balances.items():
#             if coin == 'BIP':
#                 continue
#             if (balance - estimate_custom_send_fee(coin)) < 0:
#                 continue
#             return coin
#         gas_coin = None
#     return gas_coin
#
#
# def find_virtual_gas_coin(user):
#     virt_wallets = user.virt_wallets
#     balances = {}
#     for w in virt_wallets:
#         balances[w.coin] = w.balance
#
#     gas_coin = 'BIP'
#     if balances['BIP'] < to_pip(0.01) and len(balances) > 1:
#         for coin, balance in balances.items():
#             if coin == 'BIP':
#                 continue
#             if (to_bip(balance) - estimate_custom_send_fee(coin)) < 0:
#                 continue
#             return coin
#         gas_coin = None
#     return gas_coin
#
#
# def estimate_custom_send_fee(coin):
#     wallet = MinterWallet.create()
#     send_tx = MinterSendCoinTx(coin, wallet['address'], 0, nonce=0, gas_coin=coin)
#     send_tx.sign(wallet['private_key'])
#     return API.estimate_tx_commission(send_tx.signed_tx, pip2bip=True)['result']['commission']
