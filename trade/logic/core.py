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

        owner_balance_in_trade_currency = owner.virtual_wallets.get(currency=trade.trade_currency)
        owner_balance_in_trade_currency.balance -= trade.amount
        owner_balance_in_trade_currency.save()

        cashflow_list.append(dict(
            user=owner,
            to=user,
            trade=trade,
            type_operation='transfer',
            amount=trade.amount,
            currency=trade.trade_currency
        ))

        user_balance_in_trade_currency = user.virtual_wallets.get(currency=trade.trade_currency)
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
            currency=trade.trade_currency
        ))

        owner_balance_in_payment_currency = owner.virtual_wallets.get(currency=trade.order.payment_currency)
        owner_balance_in_payment_currency.balance -= trade.price_trade
        owner_balance_in_payment_currency.save()

        owner_balance_in_trade_currency = owner.virtual_wallets.get(currency=trade.trade_currency)
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

        user_balance_in_trade_currency = user.virtual_wallets.get(currency=trade.trade_currency)
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
            currency=trade.trade_currency
        ))

        user_balance_in_trade_currency = user.virtual_wallets.get(currency=trade.trade_currency)
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
            currency=trade.trade_currency,
            tx_hash=trade.tx_hash
        ))

    CashFlow.objects.bulk_create([CashFlow(**q) for q in cashflow_list])
