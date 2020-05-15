from mintersdk.shortcuts import to_bip
from web3.exceptions import TransactionNotFound

from blockchain.ethAPI import w3, Web3
from model import Service, Wallet
from hexbytes import HexBytes


def check_refill_eth():
    usdt_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
    current_block = w3.eth.blockNumber
    addresses = [w.address.lower() for w in Wallet.select().where(Wallet.currency == 'ETH')]
    service = Service.get_or_none(currency='ETH')

    if not service:
        Service.create(currency='ETH', last_block=current_block)
        return

    last_block = service.last_block
    if current_block == service.last_block:
        return

    block_diff = current_block - last_block

    refill_txs = []
    if block_diff > 1:
        for block in range(1, block_diff + 1):
            txs_in_block = w3.eth.getBlock(last_block + block).transactions

            for tx_hash in txs_in_block:
                try:
                    tx = w3.eth.getTransactionReceipt(tx_hash)
                except TransactionNotFound:
                    continue

                if tx.status == 0:
                    continue

                if len(tx.logs) == 0:

                    try:
                        tx = w3.eth.getTransaction(tx_hash)
                    except TransactionNotFound:
                        continue

                    if tx.to and tx.to.lower() in addresses:

                        refill_txs.append(dict(to=tx.to.lower(), amount=tx.value, currency='ETH'))

                    continue

                if tx.to and tx.to.lower() != usdt_address.lower():
                    continue

                topics_flag = True
                for element in tx.logs:

                    if not element['topics']:
                        topics_flag = False
                        break

                    foo = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
                    bar = Web3.toHex(element['topics'][0])
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

                    amount = Web3.toWei(int(element['data'], 16) / 1000000, 'ether')

                    if receiver_address in addresses:
                        print(receiver_address)
                        refill_txs.append(dict(to=receiver_address, amount=amount, currency='USDT'))

                if not topics_flag:
                    continue
    else:
        txs_in_block = w3.eth.getBlock(current_block).transactions

        for tx_hash in txs_in_block:
            try:
                tx = w3.eth.getTransactionReceipt(tx_hash)
            except TransactionNotFound:
                continue

            if tx.status == 0:
                continue

            if len(tx.logs) == 0:

                try:
                    tx = w3.eth.getTransaction(tx_hash)
                except TransactionNotFound:
                    continue

                if tx.to and tx.to.lower() in addresses:
                    refill_txs.append(dict(to=tx.to.lower(), amount=tx.value, currency='ETH'))

                continue

            if tx.to and tx.to.lower() != usdt_address.lower():
                continue

            topics_flag = True
            for element in tx.logs:

                if not element['topics']:
                    topics_flag = False
                    break

                foo = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
                bar = Web3.toHex(element['topics'][0])
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
                    refill_txs.append(dict(to=receiver_address, amount=amount, currency='USDT'))

            if not topics_flag:
                continue

    service.last_block = current_block
    service.save()
    update_eth_balance(refill_txs)


def update_eth_balance(refill_txs):
    print(refill_txs)
    return refill_txs

