from requests import ReadTimeout

from bot.blockchain.core import get_eth_refill_txs, get_bip_refill_txs, order_deposit
from bot.blockchain.ethAPI import w3
from bot.blockchain.minterAPI import Minter, get_wallet_balance
from bot.blockchain.rpc_btc import get_all_transactions
from bot.helpers.misc import retry
from bot.helpers.shortcut import to_units, round_currency


from bot.models import CashFlow, Service
from user.models import Wallet, VirtualWallet

from user.logic import kb
from collections import defaultdict

@retry(Exception)
def check_refill_eth(cli):
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
        update_balance(cli, refill_txs)
        service.last_block = block
        service.save()


@retry(ReadTimeout)
def check_refill_bip(cli):
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
        update_balance(cli, refill_txs)
        service.last_block = block
        service.save()



def check_refill_btc(cli):
    all_tx = get_all_transactions()
    tx_cash_flow = [w.tx_hash for w in CashFlow.objects.filter(currency='BTC')]
    refill_txs = {}

    for key in all_tx:
        if key['category'] == 'send': # не удаляет tx 7f67de1688194def202777671ef4a904ed171b620c459933bea008c79ed3be5e
            all_tx.remove(key)
        else:
            pass
            continue

    for tx in all_tx:
        if tx['tx_id'] not in tx_cash_flow and tx['confirmations'] != 0:
            recieved = [tx['address']]
            txs_list = {'amount': tx['amount'], 'fee': tx['fee'], 'tx_id': tx['tx_id']}
            for i in recieved:
                try:
                    refill_txs[i] += [{'amount': txs_list['amount'], 'currency': 'BTC', 'fee': txs_list['fee'], 'tx_hash': txs_list['tx_id']}]
                except KeyError:
                    refill_txs[i] = [{'amount': txs_list['amount'], 'currency': 'BTC', 'fee': txs_list['fee'], 'tx_hash': txs_list['tx_id']}]
                continue
        else:
            pass
            continue
    #return refill_txs
    update_balance(cli, refill_txs)


def update_balance(cli, refill_txs):
    refills_list = []

    user_balances = {}
    for address in refill_txs:
        user = Wallet.objects.get(address=address).user

        txt_refills = f''
        await_deposit_currency = user.cache['clipboard']['deposit_currency']

        for refill in refill_txs[address]:
            currency = refill['currency']
            virt_wallet = user.virtual_wallets.get(currency=currency)
            refill_amount = refill['amount']
            tx_hash = refill['tx_hash']

            try:
                user_balances[(user, currency)] += refill_amount
            except KeyError:
                user_balances[(user, currency)] = refill_amount

            refills_list.append(dict(user=user,
                                     type_operation='deposit',
                                     amount=refill_amount,
                                     currency=currency,
                                     tx_hash=tx_hash))

            if user.flags.await_replenishment_for_order and currency in await_deposit_currency:
                order_deposit(cli, user, refill_txs[address])
            else:
                txt_refills += f'\n**{round_currency(currency, to_units(currency, refill_amount))} {currency}**'

                try:
                    cli.send_message(user.telegram_id, user.get_text(name='bot-balance_replinished') + txt_refills,
                                     reply_markup=kb.show_tx(user, currency, refill['tx_hash']))
                except Exception as e:
                    print('check_refill, line 155\n', e)

    instanse_wallet_list = []
    for (user, amount)in user_balances.items():

        wallet = user[0].virtual_wallets.get(currency=user[1])
        wallet.balance += amount
        instanse_wallet_list.append(wallet)

    VirtualWallet.objects.bulk_update(instanse_wallet_list, ['balance'])
    CashFlow.objects.bulk_create([CashFlow(**q) for q in refills_list])
