from trader_bot.apps.bot.blockchain.ethAPI import w3, Web3
from trader_bot.apps.bot.blockchain.minterAPI import API
from ...trade.models import HoldMoney

from ...bot.helpers import to_bip, CashFlow


def hold_money(trade):
    HoldMoney.objects.create(
        trade=trade,
        amount=trade.amount
    )


def auto_trade(trade):
    owner = trade.order.parent_order.user
    user = trade.user

    cashflow_list = []

    cashflow_list.append(dict(
        user=user,
        to=owner,
        trade=trade,
        type_operation='transfer',
        amount=trade.price_trade,
        currency=trade.payment_currency,
        tx_hahs=trade.tx_hash
    ))

    owner_balance = owner.virtual_wallets.get(currency=trade.order.payment_currency)
    owner_balance.balance += trade.price_trade
    owner_balance.save()

    cashflow_list.append(dict(
        user=owner,
        to=user,
        trade=trade,
        type_operation='transfer',
        amount=trade.order.amount,
        currency=trade.order.trade_currency
    ))

    user_balance = user.vitual_wallets.get(currency=trade.order.trade_currency)
    user_balance.balance += trade.amount
    user_balance.save()

    CashFlow.objects.bulk_create([CashFlow(**q) for q in cashflow_list])


def semi_auto_trade(trade):
    owner = trade.order.parent_order.user
    user = trade.user

    cashflow_list = []

    cashflow_list.append(dict(
        user=owner,
        to=user,
        trade=trade,
        type_operation='transfer',
        amount=trade.order.amount,
        currency=trade.order.trade_currency
    ))

    user_balance = user.virtual_wallets.get(currency=trade.order.trade_currency)
    user_balance.balance += trade.amount
    user_balance.save()

    trade_currency = trade.order.trade_currency
    if trade.order.trade_currency == 'USDT':
        trade_currency = 'ETH'

    owner_internal_wallet = owner.wallets.get(currency=trade_currency)

    if trade.order.requisites.lower() == owner_internal_wallet.address.lower():
        cashflow_list.append(dict(
            user=user,
            to=owner,
            trade=trade,
            type_operation='transfer',
            amount=trade.price_trade,
            currency=trade.payment_currency,
            tx_hahs=trade.tx_hash
        ))

        owner_balance = owner.virtual_wallets.get(currency=trade.order.payment_currency)
        owner_balance.balance += trade.price_trade
        owner_balance.save()

    CashFlow.objects.bulk_create([CashFlow(**q) for q in cashflow_list])


def check_tx_hash(trade, tx_hash):

    if trade.payment_currency in ['ETH', 'USDT']:
        owner_address = trade.order.requisites
        try:
            tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        except Exception:
            return False

        if tx_receipt['status'] == 1 and tx_receipt['to'].lower() == owner_address.lower():
            tx_hash = w3.eth.getTransaction(tx_hash)

            # Проверка эфира
            if trade.payment_currency == 'ETH':

                if round(to_bip(tx_hash['value']), 6) == round(to_bip(trade.price_trade), 6):
                    return True
                return False

            # Проверка юстд
            amount = 0
            for element in tx_receipt.logs:
                amount = Web3.toWei(int(element['data'], 16) / 1000000, 'ether')

            if round(to_bip(amount), 3) == round(to_bip(trade.price_trade), 3):
                return True
            return False
        else:
            return False

    if trade.payment_currency == 'BIP':
        tx = API.get_transaction(tx_hash[2:])

        if 'error' in tx:
            return False
        print(tx)
        if tx['result']['data']['to'] == trade.order.requisites \
                and round(to_bip(tx['result']['data']['value']), 2) == round(to_bip(trade.price_trade), 2):
            return True
        return False