
from web3.exceptions import TransactionNotFound

from ..blockchain import ethAPI, minterAPI
from ..helpers import to_pip, to_bip, retry, create_cash_flow_record

from ..models import CashFlowStatement, Service
from ...user.models import Wallet

from ...user.logic import kb

from hexbytes import HexBytes


def check_refill_eth(cli):

    usdt_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
    current_block = ethAPI.w3.eth.blockNumber
    addresses = [w.address.lower() for w in Wallet.objects.filter(currency='ETH')]
    service = Service.objects.get_or_none(currency='ETH')

    if not service:
        Service.objects.create(currency='ETH', last_block=current_block)
        return

    last_block = service.last_block
    if current_block == service.last_block:
        return

    block_diff = current_block - last_block

    refill_txs = {}

    if block_diff > 1:
        for block in range(1, block_diff + 1):
            txs_in_block = ethAPI.w3.eth.getBlock(last_block + block).transactions

            for tx_hash in txs_in_block:
                try:
                    tx = ethAPI.w3.eth.getTransactionReceipt(tx_hash)
                except TransactionNotFound:
                    continue

                if tx.status == 0:
                    continue

                if len(tx.logs) == 0:

                    try:
                        tx = ethAPI.w3.eth.getTransaction(tx_hash)
                    except TransactionNotFound:
                        continue

                    if tx.to and tx.to.lower() in addresses:
                        to_and_currency = (tx.to.lower(), 'ETH')
                        if to_and_currency in refill_txs:
                            continue

                        refill_txs[to_and_currency] = 1

                    continue

                if tx.to and tx.to.lower() != usdt_address.lower():
                    continue

                topics_flag = True
                for element in tx.logs:

                    if not element['topics']:
                        topics_flag = False
                        break

                    foo = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
                    bar = ethAPI.Web3.toHex(element['topics'][0])
                    if bar != foo:
                        topics_flag = False
                        break

                    len_0x = 2
                    len_gap = 24
                    len_address = 40

                    if len(element['topics']) < 3:
                        first = len_0x + len_gap
                        second = len_0x + len_gap + len_address + len_gap
                        receiver_address = '0x' + element['topics'][2].hex()[second:second + len_address]
                    else:
                        receiver_address = '0x' + element['topics'][2].hex()[len_0x + len_gap:]

                    #amount = Web3.toWei(int(element['data'], 16) / 1000000, 'ether')

                    if receiver_address in addresses:
                        to_and_currency = (receiver_address, 'USDT')
                        if to_and_currency in refill_txs:
                            continue

                        refill_txs[to_and_currency] = 1

                if not topics_flag:
                    continue
    else:
        txs_in_block = ethAPI.w3.eth.getBlock(current_block).transactions

        for tx_hash in txs_in_block:
            try:
                tx = ethAPI.w3.eth.getTransactionReceipt(tx_hash)
            except TransactionNotFound:
                continue

            if tx.status == 0:
                continue

            if len(tx.logs) == 0:

                try:
                    tx = ethAPI.w3.eth.getTransaction(tx_hash)
                except TransactionNotFound:
                    continue

                if tx.to and tx.to.lower() in addresses:
                    to_and_currency = (tx.to.lower(), 'ETH')
                    if to_and_currency in refill_txs:
                        continue

                    refill_txs[to_and_currency] = 1

                continue

            if tx.to and tx.to.lower() != usdt_address.lower():
                continue

            topics_flag = True
            for element in tx.logs:

                if not element['topics']:
                    topics_flag = False
                    break

                foo = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
                bar = ethAPI.Web3.toHex(element['topics'][0])
                if bar != foo:
                    topics_flag = False
                    break

                len_0x = 2
                len_gap = 24
                len_address = 40

                if len(element['topics']) < 3:
                    first = len_0x + len_gap
                    second = len_0x + len_gap + len_address + len_gap
                    receiver_address = '0x' + element['topics'][2].hex()[second:second + len_address]
                else:
                    receiver_address = '0x' + element['topics'][2].hex()[len_0x + len_gap:]

                amount = int(element['data'], 16) / 1000000

                if receiver_address.lower() in addresses:
                    to_and_currency = (receiver_address, 'USDT')
                    if to_and_currency in refill_txs:
                        continue

                    refill_txs[to_and_currency] = 1

            if not topics_flag:
                continue

    service.last_block = current_block
    service.save()
    update_eth_balance(cli, refill_txs)


def update_eth_balance(cli, refill_txs):
    address_refills = {}
    for (address, coin), refill_pip in refill_txs.items():
        address_refills.setdefault(address, {})
        address_refills[address][coin] = refill_pip

    refills_list = []
    for address in address_refills:
        user = Wallet.objects.get(address=address).user

        txt_refills = f''

        for currency in address_refills[address]:
            balance = ethAPI.get_balance(address, currency)

            refills_list.append(dict(user=user.id,
                                     type_operation='refill',
                                     amount=balance,
                                     currency=currency))

            virt_wallet = user.virtual_wallets.get(currency=currency)
            refill = balance - virt_wallet.balance
            virt_wallet.balance = balance
            virt_wallet.save()

            txt_refills += f'\n**{to_bip(refill)} {currency}**'
        try:

            cli.send_message(user.telegram_id, user.get_text(name='bot-balance_replinished') + txt_refills,
                             reply_markup=kb.hide_notification(user))
        except Exception as e:
            print('check_refill, line 197\n', e)

    CashFlowStatement.objects.bulk_create([CashFlowStatement(**q) for q in refills_list])



def check_refill_bip(cli):
    current_block = minterAPI.API.get_latest_block_height()

    service = Service.objects.get_or_none(currency='BIP')

    if not service:
        Service.objects.create(last_block=current_block, currency='BIP')
        return

    last_block = service.last_block
    if current_block == service.last_block:
        return

    service.last_block = current_block
    service.save()

    block_diff = current_block - last_block
    addresses = [w.address for w in Wallet.objects.filter(currency='BIP')]

    if block_diff > 1:
        refills = {}
        for i in range(1, block_diff + 1):
            txs = list(filter(lambda t: t['type'] == 1 and t['data']['to'] in addresses and t['data']['coin'] == 'BIP',
                              minterAPI.API.get_block(last_block + i)['result']['transactions']))

            for tx in txs:
                value = tx['data']['value']
                coin = tx['data']['coin']
                refills[tx['data']['to'], coin] = value

    else:
        refill_txs = list(filter(lambda t: t['type'] == 1 and t['data']['to'] in addresses and t['data']['coin'] == 'BIP',
                                 minterAPI.API.get_block(current_block)['result']['transactions']))

        refills = {}
        for tx in refill_txs:
            value = tx['data']['value']
            coin = tx['data']['coin']
            refills[tx['data']['to'], coin] = value

    update_balance(cli, refills)
    service.last_block = current_block
    service.save()


def update_balance(cli, refills):

    address_refills = {}
    for (address, coin), refill_pip in refills.items():
        address_refills.setdefault(address, {})
        address_refills[address][coin] = refill_pip

    refills_list = []

    for address in address_refills:

        user = Wallet.objects.get(address=address).user
        user_balance = minterAPI.get_wallet_balance(address)
        txt_refills = ''
        refill_in_pip = address_refills[address]['BIP']

        virt_wallet = user.virtual_wallets.get(currency='BIP')

        virt_wallet.balance += refill_in_pip
        if user_balance != virt_wallet.balance:
            virt_wallet.balance = user_balance

        virt_wallet.save()

        txt_refills += f'\n**{to_bip(refill_in_pip)} BIP**'

        refills_list.append(dict(user=user,
                                 type_operation='refill',
                                 amount=user_balance,
                                 currency='BIP'))

        try:
            cli.send_message(user.telegram_id, user.get_text(name='bot-balance_replinished') + txt_refills,
                             reply_markup=kb.hide_notification(user))
        except Exception as e:
            print('check_refill, line 272\n', e)

    CashFlowStatement.objects.bulk_create([CashFlowStatement(**q) for q in refills_list])

