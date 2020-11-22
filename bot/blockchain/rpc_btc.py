from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from bot.helpers.shortcut import to_cents
from config.settings import BTC_USER, BTC_PASS

from constance import config

rpc_user = BTC_USER
rpc_password = BTC_PASS

tx_fee = 0.00015

btc_node = config.BTC_NODE

wallet_name = config.BTC_WALLET_NAME
url = btc_node.format(user=rpc_user, password=rpc_password) + '/wallet/' + wallet_name
rpc_connection = AuthServiceProxy(url)#btc_node.format(user=rpc_user, password=rpc_password))#%(rpc_user, rpc_password))


def get_block():
    best_block_hash = rpc_connection.getbestblockhash()
    block = rpc_connection.getblock(best_block_hash)
    block_height = block['height']
    return block_height


def get_new_address():
    address_type = 'legacy'
    new_adr = rpc_connection.getnewaddress('', address_type)
    return new_adr


def get_wallet_balance():
    wallet_balance = rpc_connection.getbalance()
    return wallet_balance


def get_wallet_info():

    wallet_info = rpc_connection.getwalletinfo()
    return wallet_info


def get_all_transactions():
    all_transactions = rpc_connection.listtransactions("*", 1000)

    all_tx = [{**key, 'amount': to_cents('BTC', key['amount']), 'fee': to_cents('BTC', key.get('fee', 0))} for key in all_transactions]

    return all_tx


def check_address_btc(wallet_address):
    try:
        result_address = rpc_connection.getaddressinfo(wallet_address)
    except JSONRPCException:
        result_address = 'Invalid address'

    return result_address


# def get_private_key(address):
#     uri_path_w = '/wallet/%s' % (wallet_name)
#     rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s" %
#                                 (rpc_user, rpc_password, uri_path_w))
#     privkey = rpc_conn.dumpprivkey(address)
#     return privkey


# def get_wallet_list():
#     wallet_dict = rpc_connection.listwalletdir()
#     wallet_list = wallet_dict['wallets']
#     w_names = []
#     for names in wallet_list:
#         w_names.append(names['name'])
#     return w_names


def create_transaction(receiver_address, amount):
    new_transaction = None

    try:
        new_transaction = rpc_connection.sendtoaddress(receiver_address, amount)
    except Exception:  #  TODO:: нужно сделать обработку ошибок
        print('Smth wrong, please check the data')
        pass

    return new_transaction


def set_transaction_fee():
    tx_fee = None # integer
    transaction_fee = rpc_connection.settxfee(tx_fee)
    return transaction_fee


def check_transaction(tx_hash):
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy(btc_node %
                                (rpc_user, rpc_password, uri_path_w))
    try:
        tx = rpc_conn.gettransaction(tx_hash)
    except JSONRPCException:
        tx = 'error'
    return tx
