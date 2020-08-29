from pyrogram import Client
from requests import ReadTimeout

from bot.blockchain.core import get_eth_refill_txs, get_bip_refill_txs, order_deposit
from bot.blockchain.ethAPI import w3
from bot.blockchain.minterAPI import Minter, get_wallet_balance
from bot.blockchain.rpc_btc import get_all_transactions
from bot.helpers.misc import retry
from bot.helpers.shortcut import to_units, round_currency


from bot.models import CashFlow, Service
from config.settings import TG_API_ID, TG_API_HASH, TG_API_TOKEN
from user.models import Wallet, VirtualWallet

from user.logic import kb
from collections import defaultdict


@retry(Exception)
def check_refill_eth():
    current_block = w3.eth.blockNumber
    service = Service.objects.get_or_none(currency='ETH')
    if not service:
        Service.objects.create(currency='ETH', last_block=current_block)
        return

    last_block = service.last_block
    if current_block == service.last_block:
        return

    block_diff = current_block - last_block

    addresses = [w.address.lower() for w in Wallet.objects.filter(currency='ETH')]
    for block in range(last_block + 1, last_block + block_diff + 1):
        refill_txs = get_eth_refill_txs(addresses, block)
        update_balance(refill_txs)
        service.last_block = block
        service.save()


@retry(ReadTimeout)
def check_refill_bip():
    current_block = Minter.get_latest_block_height()
    service = Service.objects.get_or_none(currency='BIP')
    if not service:
        Service.objects.create(last_block=current_block, currency='BIP')
        return

    last_block = service.last_block
    if current_block == service.last_block:
        return

    block_diff = current_block - last_block

    addresses = [w.address for w in Wallet.objects.filter(currency='BIP')]
    for block in range(last_block + 1, last_block + block_diff + 1):
        refill_txs = get_bip_refill_txs(addresses, block)
        update_balance(refill_txs)
        service.last_block = block
        service.save()

@retry(ReadTimeout)
def check_refill_btc():
    tx_cash_flow = [w.tx_hash.lower() for w in CashFlow.objects.filter(currency='BTC')]
    addresses = [w.address.lower() for w in Wallet.objects.filter(currency='BTC')]
    refill_txs = defaultdict(list)

    sorted_txs = list(
        filter(
            lambda tx: tx['category'] == 'receive'
                       and tx['address'].lower() in addresses
                       and tx['txid'].lower() not in tx_cash_flow
                       and tx['confirmations'] != 0,  get_all_transactions()))

    for tx in sorted_txs:
            refill_txs[tx['address']] += [{'amount': tx['amount'], 'tx_hash': tx['txid'], 'currency': 'BTC'}]

    update_balance(refill_txs)


def update_balance(refill_txs):
    app = Client(
        'session_main',
        api_id=TG_API_ID, api_hash=TG_API_HASH, bot_token=TG_API_TOKEN,
        plugins={'root': 'bot/handlers'})

    refills_list = []

    user_balances = defaultdict(int)
    for address in refill_txs:
        user = Wallet.objects.get(address=address).user

        await_deposit_currency = user.cache['clipboard'].get('deposit_currency',
                                                             list())  # TODO Это костыль т.к deposit_currency должен создаться при регистрации

        for refill in refill_txs[address]:
            currency = refill['currency']
            refill_amount = refill['amount']
            tx_hash = refill['tx_hash']
            txt_refills = f''

            user_balances[(user, currency)] += refill_amount

            refills_list.append(
                dict(
                    user=user,
                    type_operation='deposit',
                    amount=refill_amount,
                    currency=currency,
                    tx_hash=tx_hash
                )
            )

            if user.flags.await_replenishment_for_order and currency in await_deposit_currency:
                order_deposit(app, user, refill_txs[address])
            else:
                txt_refills += f'\n**{round_currency(currency, to_units(currency, refill_amount))} {currency}**'

                try:
                    with app:
                        app.send_message(user.telegram_id, user.get_text(name='bot-balance_replinished') + txt_refills,
                                         reply_markup=kb.show_tx(user, currency, refill['tx_hash']))
                except Exception as e:
                    print('check_refill, line 155\n', e)

    instanse_wallet_list = []

    for (user, amount) in user_balances.items():
        wallet = user[0].virtual_wallets.get(currency=user[1])
        wallet.balance += amount
        instanse_wallet_list.append(wallet)

    VirtualWallet.objects.bulk_update(instanse_wallet_list, ['balance'])
    CashFlow.objects.bulk_create([CashFlow(**q) for q in refills_list])
