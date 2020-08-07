from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_user = 'isheldon'
rpc_password = 'zAdmkhdRRkSI3XfqWXW9_08wOSaqwfVr_8ZEdGTl_1E='
uri_path_wallet = '/wallet/garry'
tx_fee = 0.00015

rpc_connection = AuthServiceProxy("http://%s:%s@195.201.211.234:8878"%
                                  (rpc_user, rpc_password))

def create_new_wallet (rpc_connection, wallet_name):
    new_wallet = rpc_connection.createwallet(wallet_name)
    return new_wallet

def get_wallet_balance(rpc_user, rpc_password, uri_path_wallet):
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s"%
                                  (rpc_user, rpc_password, uri_path_wallet))
    wallet_balance = rpc_conn.getbalance()
    return print('wallet_balance:', wallet_balance)

def get_wallet_info(rpc_user, rpc_password, uri_path_wallet):
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s"%
                                (rpc_user, rpc_password, uri_path_wallet))
    wallet_info = rpc_conn.getwalletinfo()
    return print('Your wallet information:', wallet_info)

def get_all_transactions(rpc_user, rpc_password, uri_path_wallet):
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s"%
                                (rpc_user, rpc_password, uri_path_wallet))
    all_transactions = rpc_conn.listtransactions("*", 1000)
    all_tx = []

    for key in all_transactions:
        try:
            tx = {'adress': key['address'], 'category': key['category'],
                  'amount': key['amount'], 'fee': key['fee'], 'tx_id': key['txid']}
        except KeyError:
            tx = {'adress': key['address'], 'category': key['category'],
                  'amount': key['amount'], 'fee': 'not set', 'tx_id': key['txid']}
        all_tx.append(tx)
    return print('Transactions of current wallet:', all_tx)

def get_new_adress(rpc_user, rpc_password, uri_path_wallet, wallet):
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s"%
                                (rpc_user, rpc_password, uri_path_wallet))
    adress_type = 'legacy'
    new_adr = rpc_conn.getnewaddress(wallet, adress_type)
    return print('New adress is:', new_adr)

def create_transaction(rpc_user, rpc_password, uri_path_wallet, received_adress, sum_btc):
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s"%
                                (rpc_user, rpc_password, uri_path_wallet))
    new_transaction = None

    try:
        new_transaction = rpc_conn.sendtoaddress(received_adress, sum_btc)
    except Exception:
        print('Smth wrong, please check the data')
        pass
    return new_transaction

def set_transaction_fee(rpc_user, rpc_password, uri_path_wallet ,tx_fee):
    rpc_conn = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s"%
                                (rpc_user, rpc_password, uri_path_wallet))
    transaction_fee = rpc_conn.settxfee(tx_fee)
    return transaction_fee
