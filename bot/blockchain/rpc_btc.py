from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from bot.helpers.shortcut import to_cents
from config.settings import BTC_USER, BTC_PASS

from constance import config

rpc_user = BTC_USER
rpc_password = BTC_PASS

tx_fee = 0.00015

btc_node = config.BTC_NODE

rpc_connection = AuthServiceProxy(btc_node%(rpc_user, rpc_password))

wallet_name = config.BTC_WALLET_NAME


def get_block():
    best_block_hash = rpc_connection.getbestblockhash()
    block = rpc_connection.getblock(best_block_hash)
    block_height = block['height']
    return block_height


def get_new_address():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy(btc_node %
                                (rpc_user, rpc_password, uri_path_w))
    address_type = 'legacy'
    new_adr = rpc_conn.getnewaddress('', address_type)
    return new_adr


def get_wallet_balance():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy(btc_node %
                                (rpc_user, rpc_password, uri_path_w))
    wallet_balance = rpc_conn.getbalance()
    return wallet_balance


def get_wallet_info():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy(btc_node %
                                (rpc_user, rpc_password, uri_path_w))
    wallet_info = rpc_conn.getwalletinfo()
    return print('Your wallet information:', wallet_info)


def get_all_transactions():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy(btc_node %
                                (rpc_user, rpc_password, uri_path_w))
    all_transactions = rpc_conn.listtransactions("*", 1000)

    all_tx = [{**key, 'amount': to_cents('BTC', key['amount']), 'fee': to_cents('BTC', key.get('fee', 0))} for key in all_transactions]

    return all_tx


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


def check_address(wallet_address):
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy(btc_node %
                                (rpc_user, rpc_password, uri_path_w))
    try:
        check_address = rpc_conn.getaddressinfo(wallet_address)
    except JSONRPCException:
        check_address = 'Invalid address'

    return  check_address


def check_transaction(tx_hash):
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy(btc_node %
                                (rpc_user, rpc_password, uri_path_w))
    try:
        tx = rpc_conn.gettransaction(tx_hash)
    except JSONRPCException:
        tx = 'error'
    return tx
