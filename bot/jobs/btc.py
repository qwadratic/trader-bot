from bot.blockchain.rpc_btc import create_new_wallet, get_wallet_balance, set_transaction_fee, get_wallet_info, \
    get_all_transactions, get_new_adress, create_transaction, rpc_connection, rpc_user, rpc_password, uri_path_wallet, tx_fee


#new_wallet = create_new_wallet(rpc_connection, wallet_name)

wallet_balance = get_wallet_balance(rpc_user, rpc_password, uri_path_wallet)

#transaction_fee = set_transaction_fee(rpc_user, rpc_password, uri_path_wallet ,tx_fee)

wallet_info = get_wallet_info(rpc_user, rpc_password, uri_path_wallet)

wallet_transactions = get_all_transactions(rpc_user, rpc_password, uri_path_wallet)

#new_adress = get_new_adress(rpc_user, rpc_password, uri_path_wallet, wallet)

#new_transaction = create_transaction(rpc_user, rpc_password, uri_path_wallet, received_adress, sum_btc)