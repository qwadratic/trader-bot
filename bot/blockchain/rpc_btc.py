from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_user = 'isheldon'
rpc_password = 'zAdmkhdRRkSI3XfqWXW9_08wOSaqwfVr_8ZEdGTl_1E='
uri_path_wallet = '/wallet/garry'
tx_fee = 0.00015

rpc_connection = AuthServiceProxy("http://%s:%s@195.201.211.234:8878%s"%
                                  (rpc_user, rpc_password, uri_path_wallet))

def create_new_wallet (wallet_name): #TODO to define wallet_name
    new_wallet = rpc_connection.createwallet(wallet_name)
    return print(new_wallet)

def get_wallet_balance():
    wallet_balance = rpc_connection.getbalance()
    return print('wallet_balance:', wallet_balance)

def get_wallet_info():
    wallet_info = rpc_connection.getwalletinfo()
    return print('Your wallet information:', wallet_info)

def get_all_transactions():
    all_transactions = rpc_connection.listtransactions("*", 1000)
    all_tx = []

    for key in all_transactions:
        try:
            tx = {'address': key['address'], 'category': key['category'],
                  'amount': key['amount'], 'fee': key['fee'], 'tx_id': key['txid']}
        except KeyError:
            tx = {'address': key['address'], 'category': key['category'],
                  'amount': key['amount'], 'fee': 'not set', 'tx_id': key['txid']}
        all_tx.append(tx)
    return print('Transactions of current wallet:', all_tx)

def get_new_adress(wallet): #TODO logic to identify
    address_type = 'legacy'
    new_adr = rpc_connection.getnewaddress(wallet, address_type)
    return new_adr

def create_transaction():
    received_address = ''
    sum_btc = None # integer
    new_transaction = None

    try:
        new_transaction = rpc_connection.sendtoaddress(received_address, sum_btc)
    except Exception:
        print('Smth wrong, please check the data')
        pass
    return new_transaction

def set_transaction_fee():
    tx_fee = None # integer
    transaction_fee = rpc_connection.settxfee(tx_fee)
    return transaction_fee
