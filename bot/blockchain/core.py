from bot.blockchain.ethAPI import w3
from bot.blockchain.minterAPI import Minter
from bot.helpers.shortcut import to_units


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

