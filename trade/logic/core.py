from mintersdk.shortcuts import to_bip
from web3 import Web3

from bot.blockchain.ethAPI import w3
from bot.blockchain.minterAPI import Minter
from bot.models import CashFlow
from trade.models import HoldMoney


def hold_money(trade):
    HoldMoney.objects.create(
        trade=trade,
        amount=trade.amount
    )


def update_order(parent_order, type_update, value):
    if type_update == 'amount':
        orders = parent_order.orders.all()

        for order in orders:
            order.amount = value
            order.save()


def auto_trade(trade):
    owner = trade.order.parent_order.user
    user = trade.user
    parent_order = trade.order.parent_order

    update_order(parent_order, 'amount', parent_order.amount - trade.amount)

    cashflow_list = []

    if trade.order.type_operation == 'sale':
        cashflow_list.append(dict(
            user=user,
            to=owner,
            trade=trade,
            type_operation='transfer',
            amount=trade.price_trade,
            currency=trade.payment_currency
        ))

        owner_balance_in_payment_currency = owner.virtual_wallets.get(currency=trade.payment_currency)
        owner_balance_in_payment_currency.balance += trade.price_trade
        owner_balance_in_payment_currency.save()

        owner_balance_in_trade_currency = owner.virtual_wallets.get(currency=trade.order.trade_currency)
        owner_balance_in_trade_currency.balance -= trade.amount
        owner_balance_in_trade_currency.save()

        cashflow_list.append(dict(
            user=owner,
            to=user,
            trade=trade,
            type_operation='transfer',
            amount=trade.amount,
            currency=trade.order.trade_currency
        ))

        user_balance_in_trade_currency = user.virtual_wallets.get(currency=trade.order.trade_currency)
        user_balance_in_trade_currency.balance += trade.amount
        user_balance_in_trade_currency.save()

        user_balance_in_payment_currency = user.virtual_wallets.get(currency=trade.payment_currency)
        user_balance_in_payment_currency.balance -= trade.price_trade
        user_balance_in_payment_currency.save()

    # покупка
    else:
        cashflow_list.append(dict(
            user=user,
            to=owner,
            trade=trade,
            type_operation='transfer',
            amount=trade.price_trade,
            currency=trade.order.trade_currency
        ))

        owner_balance_in_payment_currency = owner.virtual_wallets.get(currency=trade.order.payment_currency)
        owner_balance_in_payment_currency.balance -= trade.price_trade
        owner_balance_in_payment_currency.save()

        owner_balance_in_trade_currency = owner.virtual_wallets.get(currency=trade.order.trade_currency)
        owner_balance_in_trade_currency.balance += trade.amount
        owner_balance_in_trade_currency.save()

        cashflow_list.append(dict(
            user=owner,
            to=user,
            trade=trade,
            type_operation='transfer',
            amount=trade.amount,
            currency=trade.payment_currency
        ))

        user_balance_in_payment_currency = user.virtual_wallets.get(currency=trade.payment_currency)
        user_balance_in_payment_currency.balance -= trade.price_trade
        user_balance_in_payment_currency.save()

        user_balance_in_trade_currency = user.virtual_wallets.get(currency=trade.order.trade_currency)
        user_balance_in_trade_currency.balance += trade.amount
        user_balance_in_trade_currency.save()

    CashFlow.objects.bulk_create([CashFlow(**q) for q in cashflow_list])


def semi_auto_trade(trade):
    owner = trade.order.parent_order.user
    user = trade.user
    parent_order = trade.order.parent_order

    cashflow_list = []

    update_order(parent_order, 'amount', parent_order.amount - trade.amount)

    if trade.order.type_operation == 'sale':
        cashflow_list.append(dict(
            user=owner,
            to=user,
            trade=trade,
            type_operation='transfer',
            amount=trade.amount,
            currency=trade.order.trade_currency
        ))

        user_balance_in_trade_currency = user.virtual_wallets.get(currency=trade.order.trade_currency)
        user_balance_in_trade_currency.balance += trade.amount
        user_balance_in_trade_currency.save()

        cashflow_list.append(dict(
            user=user,
            to=owner,
            trade=trade,
            type_operation='external-transfer',
            amount=trade.price_trade,
            currency=trade.payment_currency,
            tx_hash=trade.tx_hash
        ))

    else:

        cashflow_list.append(dict(
            user=owner,
            to=user,
            trade=trade,
            type_operation='transfer',
            amount=trade.price_trade,
            currency=trade.payment_currency
        ))

        user_balance_in_payment_currency = user.virtual_wallets.get(currency=trade.payment_currency)
        user_balance_in_payment_currency.balance += trade.price_trade
        user_balance_in_payment_currency.save()

        cashflow_list.append(dict(
            user=user,
            to=owner,
            trade=trade,
            type_operation='external-transfer',
            amount=trade.amount,
            currency=trade.order.trade_currency,
            tx_hash=trade.tx_hash
        ))

    CashFlow.objects.bulk_create([CashFlow(**q) for q in cashflow_list])


# TODO::
#  - избавиться от ебаного to_bip.
#  - сделать функцию независимой от моделей: вместо (trade, tx_hash) будет (tx_hash, currency, amount, address)
#  - сделать ее более расширяемой или хотя бы красивой/читабельной (мультивалютность)
#  - после чего перекинуть в модуль blockchain
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
        tx = Minter.get_transaction(tx_hash[2:])

        if 'error' in tx:
            return False

        if tx['result']['data']['to'] == trade.order.requisites \
                and round(to_bip(tx['result']['data']['value']), 2) == round(to_bip(trade.price_trade), 2):
            return True
        return False

