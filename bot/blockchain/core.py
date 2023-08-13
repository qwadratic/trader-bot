from web3 import Web3
from web3.exceptions import TransactionNotFound

from bot.blockchain.ethAPI import w3, USDT_CONTRACT_ADDRESS
from bot.blockchain.minterAPI import Minter
from bot.blockchain.rpc_btc import check_transaction
from bot.helpers.shortcut import to_units, round_currency, delete_inline_kb, send_message, update_cache_msg
from order.logic import kb as order_kb
from order.logic.core import check_balance_from_order, get_order_info
from order.logic.text_func import get_lack_balance_text
from trade.logic.core import check_balance_from_trade, close_trade
from trade.logic import kb as trade_kb

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
    #refill_txs = defaultdict(int)
    refill_txs = {}
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
            refill_tx = w3.eth.getTransaction(tx_hash)
            try:
                refill_txs[tx.to.lower()] += [{'tx_hash': tx_hash, 'currency': 'ETH', 'amount': refill_tx.value}]
            except KeyError:
                refill_txs[tx.to.lower()] = [{'tx_hash': tx_hash, 'currency': 'ETH', 'amount': refill_tx.value}]

            continue

        # now handle only USDT transactions
        if tx.to.lower() != USDT_CONTRACT_ADDRESS.lower():
            continue

        # analyze tx receipt 'topics' to extract receiver address and transaction value
        token_transfer_params = _get_usdt_transfer_params_from_tx_logs(tx.logs)
        if not token_transfer_params:
            continue
        recv_address, amount = token_transfer_params
        if recv_address.lower() in addresses:
            try:
                refill_txs[recv_address] += [{'tx_hash': tx_hash, 'currency': 'USDT', 'amount': refill_tx.value}]
            except KeyError:
                refill_txs[recv_address] = [{'tx_hash': tx_hash, 'currency': 'USDT', 'amount': amount}]

    return refill_txs


def get_bip_refill_txs(addresses, block_height):
    #refill_txs = defaultdict(int)
    refill_txs = {}
    block_data = Minter.get_block(block_height)
    # only BIP txs to users addresses
    txs = list(
        filter(
            lambda t: t['type'] == 1 and t['data']['to'] in addresses and t['data']['coin'] == 'BIP',
            block_data['result']['transactions']))

    for tx in txs:

        value = tx['data']['value']

        try:
            refill_txs[tx['data']['to']] += [{'tx_hash': tx['hash'], 'currency': 'BIP', 'amount': value}]
        except KeyError:
            refill_txs[tx['data']['to']] = [{'tx_hash': tx['hash'], 'currency': 'BIP', 'amount': value}]

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

    # Проверка бтс
    if currency == 'BTC':
        tx = check_transaction(tx_hash)
        tx_status = tx['confirmations']
        tx_address = [ad['address'] for ad in tx['details']]
        tx_value = tx['amount']

        if 'error' in tx:
            return False

        if tx_status == 0:
            return False

        if tx_address != address:
            return False

        if tx_value != round(to_units('BTC', amount), 8):
            return False

        return True


def order_deposit(cli, user, refill_txs):
    order = user.temp_order
    flags = user.flags
    is_good_balance = check_balance_from_order(user, order)
    user_msg = user.cache['msg']
    refill_currency = ''
    for refill in refill_txs:
        currency = refill['currency']
        amount = round_currency(currency, to_units(currency, refill['amount']))
        refill_currency += f'{amount} {currency}\n'

    txt_refill = user.get_text(name='bot-balance_replinished').format(refill=refill_currency)
    delete_inline_kb(cli, user.telegram_id, user_msg['last_temp_order'])

    if is_good_balance:
        flags.await_replenishment_for_order = False
        flags.save()

        send_message(cli, user.telegram_id, txt_refill, kb=None)
        send_message(cli, user.telegram_id, user.get_text(name='order-continue_order_after_deposit'),
                              kb=order_kb.continue_order_after_deposit(user))

    else:
        deposit_currency = user.cache['clipboard']['deposit_currency']
        lack_balance_txt = get_lack_balance_text(order, deposit_currency)
        txt_refill += f'\n{user.get_text(name="order-not_enough_money_after_deposit").format(deposit_currency=lack_balance_txt)}'

        delete_inline_kb(cli, user.telegram_id, user_msg['last_temp_order'])
        msg = send_message(cli, user.telegram_id, txt_refill, kb=order_kb.deposit_from_order(user))

        if msg:
            update_cache_msg(user, 'last_temp_order', msg.message_id)


def trade_deposit(cli, user, refill_txs):
    trade = user.trade.get(id=user.cache['clipboard']['active_trade'])
    flags = user.flags
    msg = user.cache['msg']
    amount = to_units(trade.trade_currency, trade.amount)

    if trade.order.type_operation == 'sale':
        currency = trade.payment_currency
        balance = user.get_balance(currency, cent2unit=True)
        price_trade = to_units(trade.payment_currency, trade.price_trade)
    else:
        currency = trade.trade_currency
        balance = user.get_balance(currency, cent2unit=True)
        price_trade = amount

    is_good_balance = check_balance_from_trade(currency, price_trade, balance)

    refill_currency = ''
    for refill in refill_txs:
        currency = refill['currency']
        amount_refill = round_currency(currency, to_units(currency, refill['amount']))
        refill_currency += f'{amount_refill} {currency}\n'

    txt_refill = user.get_text(name='bot-balance_replinished').format(refill=refill_currency)

    delete_inline_kb(cli, user.telegram_id, msg['last_trade'])

    if is_good_balance[0]:
        flags.await_replenishment_for_trade = False
        flags.save()
        order_amount = trade.order.amount

        if trade.order.status != 'open':
            msg = txt_refill + f'\n\n{user.get_text(name="trade-order_not_open")}'
            send_message(cli, user.telegram_id, msg, kb=None)
            trade.status = 'canceled'
            trade.save()
            return

        if trade.amount > order_amount:
            msg = txt_refill + f'\n\n{user.get_text(name="trade-trade_amount_more_than_order_amount")}'
            trade.status = 'canceled'
            trade.save()
            send_message(cli, user.telegram_id, msg, kb=None)
            send_message(cli, user.telegram_id, get_order_info(user, trade.order.id), kb=order_kb.order_for_user(user, trade.order.id))
            return

        if trade.order.type_operation == 'sale':
            type_translate = user.get_text(name='order-type_operation_translate_buy_1')
        else:
            type_translate = user.get_text(name='order-type_operation_translate_sale_1')

        txt = user.get_text(name='trade-continue_trade_after_deposit').format(
            type_operation=type_translate,
            amount=round_currency(trade.trade_currency, amount),
            payment_currency=trade.payment_currency,
            price_trade=to_units(trade.payment_currency, trade.price_trade, round=True),
            trade_currency=trade.trade_currency
        )

        msg = send_message(cli, user.telegram_id, f'{txt_refill}\n\n{txt}', kb=trade_kb.continue_trade_after_deposit(user))
        if msg:
            update_cache_msg(user, 'last_trade', msg.message_id)
    else:
        currency = is_good_balance[1]
        amount_deposit = is_good_balance[2]

        msg = send_message(cli,
            user.telegram_id,
            user.get_text(name='trade-not_enough_money_after_deposit').format(amount=amount_deposit, currency=currency),
            kb=trade_kb.not_enough_money_to_trade(user, currency))

        if msg:
            update_cache_msg(user, 'last_trade', msg.message_id)


