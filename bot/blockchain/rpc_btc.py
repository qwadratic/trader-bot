from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from config.settings import BTC_USER, BTC_PASS

rpc_user = BTC_USER
rpc_password = BTC_PASS

tx_fee = 0.00015

rpc_connection = AuthServiceProxy("http://%s:%s@195.201.211.234:8878"%
                                  (rpc_user, rpc_password))

wallet_name = 'garry'


def get_block():
    best_block_hash = rpc_connection.getbestblockhash()
    block = rpc_connection.getblock(best_block_hash)
    block_height = block['height']
    return block_height


def create_new_wallet ():
    new_wallet = rpc_connection.createwallet(wallet_name)
    return new_wallet


def get_wallet_balance():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s" %
                                (rpc_user, rpc_password, uri_path_w))
    wallet_balance = rpc_conn.getbalance()
    return wallet_balance


def get_wallet_info():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s" %
                                (rpc_user, rpc_password, uri_path_w))
    wallet_info = rpc_conn.getwalletinfo()
    return print('Your wallet information:', wallet_info)


def get_all_transactions():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s" %
                                (rpc_user, rpc_password, uri_path_w))
    all_transactions = rpc_conn.listtransactions("*", 1000)
    all_tx = []

    for key in all_transactions:
        try:
            tx = {'address': key['address'], 'category': key['category'],
                  'amount': key['amount'], 'fee': key['fee'], 'confirmations': key['confirmations'], 'tx_id': key['txid']}
        except KeyError:
            tx = {'address': key['address'], 'category': key['category'],
                  'amount': key['amount'], 'fee': 'not set', 'confirmations': key['confirmations'], 'tx_id': key['txid']}
        all_tx.append(tx)
    return all_tx



def get_new_address():
    uri_path_w = '/wallet/%s' % (wallet_name)
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s" %
                                (rpc_user, rpc_password, uri_path_w))
    address_type = 'legacy'
    new_adr = rpc_conn.getnewaddress(wallet_name, address_type)
    return new_adr


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
