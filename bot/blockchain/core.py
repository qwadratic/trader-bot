from collections import defaultdict

from web3 import Web3
from web3.exceptions import TransactionNotFound

from bot.blockchain.ethAPI import w3, USDT_CONTRACT_ADDRESS
from bot.blockchain.minterAPI import Minter
from bot.helpers.shortcut import to_units


TOPIC_SEND_TOKENS = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'


def _get_usdt_transfer_params_from_tx_logs(tx_logs):
    """
    transfer params should be in first log record in 'topics' field
    :param tx_logs: transaction receipt logs
    :return: None or (address, amount)
    """
    first_log = tx_logs[0]

    # if no 'topics' - it is not a usdt transfer tx
    if not first_log['topics']:
        return None

    # if first 'topics' element != TOPIC_SEND_TOKENS - it is not a usdt transfer tx
    topic = Web3.toHex(first_log['topics'][0])
    if topic != TOPIC_SEND_TOKENS:
        return None

    # logic to get receiver address and amount from 'topics'
    # receiver address is "hidden" first_log['topics'][2]
    # amount is encoded as hex number in first_log['data']
    len_0x = 2
    len_gap = 24
    len_address = 40

    if len(first_log['topics']) < 3:
        second = len_0x + len_gap + len_address + len_gap
        receiver_address = '0x' + first_log['topics'][2].hex()[second:second + len_address]
    else:
        receiver_address = '0x' + first_log['topics'][2].hex()[len_0x + len_gap:]

    amount = Web3.toWei(int(first_log['data'], 16) / 1000000, 'ether')
    return receiver_address, amount


def get_eth_refill_txs(addresses, block_height):
    refill_txs = defaultdict(int)
    txs_in_block = w3.eth.getBlock(block_height).transactions

    for tx_hash in txs_in_block:
        try:
            tx = w3.eth.getTransactionReceipt(tx_hash)
        except TransactionNotFound:
            continue

        # skip rejected txs
        if tx.status == 0 or not tx.to:
            continue

        # handle ETH transaction
        if len(tx.logs) == 0:

            # skip transactions to other addresses
            if tx.to.lower() not in addresses:
                continue

            # add tx value to refill_txs dict
            to_and_currency = (tx.to.lower(), 'ETH')
            refill_tx = w3.eth.getTransaction(tx_hash)
            refill_txs[to_and_currency] += refill_tx.value
            continue

        # now handle only USDT transactions
        if tx.to.lower() != USDT_CONTRACT_ADDRESS:
            continue

        # analyze tx receipt 'topics' to extract receiver address and transaction value
        token_transfer_params = _get_usdt_transfer_params_from_tx_logs(tx.logs)
        if not token_transfer_params:
            continue
        recv_address, amount = token_transfer_params
        if recv_address.lower() in addresses:
            to_and_currency = (recv_address, 'USDT')
            refill_txs[to_and_currency] += amount

    return refill_txs


def get_bip_refill_txs(addresses, block_height):
    refill_txs = defaultdict(int)
    block_data = Minter.get_block(block_height)
    # only BIP txs to users addresses
    txs = list(
        filter(
            lambda t: t['type'] == 1 and t['data']['to'] in addresses and t['data']['coin'] == 'BIP',
            block_data['result']['transactions']))

    for tx in txs:
        value = tx['data']['value']
        coin = tx['data']['coin']
        refill_txs[tx['data']['to'], coin] += value
    return refill_txs


# TODO::
#  - сделать ее более расширяемой или хотя бы красивой/читабельной (мультивалютность)
#  - расширить возвращаемые логи
def check_tx_hash(tx_hash, currency, amount, address):
    if currency in ['ETH', 'USDT']:

        try:
            tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
            tx_status = tx_receipt['status']
            tx_address = tx_receipt['to'].lower()

            if tx_status != 1:
                return False

            if tx_address != address.lower():
                return False

        except Exception:
            return False

        tx_hash = w3.eth.getTransaction(tx_hash)

        # Проверка эфира
        if currency == 'ETH':
            tx_value = round(to_units('ETH', tx_hash['value']), 6)
            return True if tx_value == round(to_units('ETH', amount), 6) else False

        # Проверка юстд
        tx_value = 0
        for element in tx_receipt.logs:
            tx_value = round(to_units('USDT', to_units('USDT', int(element['data'], 16) / 1000000)), 3)

        return True if tx_value == round(to_units('USDT', amount), 3) else False

    if currency == 'BIP':
        tx = Minter.get_transaction(tx_hash[2:])
        tx_address = tx['result']['data']['to']
        tx_value = round(to_units('BIP', tx['result']['data']['value']))

        if 'error' in tx:
            return False

        if tx_address != address:
            return False

        if tx_value != round(to_units('BIP', amount), 2):
            return False

        return True

