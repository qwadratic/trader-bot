from bot.helpers.shortcut import create_record_cashflow
from trade.models.trade import TradeHoldMoney
from user.logic.core import update_wallet_balance


def update_order(parent_order, type_update, value):
    if type_update == 'amount':
        orders = parent_order.orders.all()

        for order in orders:
            order.amount = value
            order.save()

    if type_update == 'switch':
        orders = parent_order.orders.all()
        parent_order.status = value
        parent_order.save()

        for order in orders:
            order.status = value
            order.save()


def auto_trade(trade):
    owner = trade.order.parent_order.user
    user = trade.user
    parent_order = trade.order.parent_order

    update_order(parent_order, 'amount', parent_order.amount - trade.amount)

    if trade.order.type_operation == 'sale':
        create_record_cashflow(user, owner, 'transfer', trade.price_trade, trade.payment_currency, trade)

        update_wallet_balance(owner, trade.payment_currency, trade.price_trade, 'up')
        update_wallet_balance(owner, trade.trade_currency, trade.amount, 'down')

        create_record_cashflow(owner, user, 'transfer', trade.amount, trade.trade_currency, trade)
        update_wallet_balance(user, trade.trade_currency, trade.amount, 'up')
        update_wallet_balance(user, trade.payment_currency, trade.price_trade, 'down')

    # покупка
    else:

        create_record_cashflow(user, owner, 'transfer', trade.price_trade, trade.payment_currency, trade)

        update_wallet_balance(owner, trade.order.payment_currency, trade.price_trade, 'down')
        update_wallet_balance(owner, trade.trade_currency, trade.amount, 'up')

        create_record_cashflow(owner, user, 'transfer', trade.amount, trade.trade_currency, trade)

        update_wallet_balance(user, trade.payment_currency, trade.price_trade, 'down')
        update_wallet_balance(user, trade.trade_currency, trade.amount, 'up')

    close_trade(trade)


def semi_auto_trade(trade):
    owner = trade.order.parent_order.user
    user = trade.user
    parent_order = trade.order.parent_order

    update_order(parent_order, 'amount', parent_order.amount - trade.amount)

    if trade.order.type_operation == 'sale':
        create_record_cashflow(owner, user, 'transfer', trade.amount, trade.trade_currency, trade)
        update_wallet_balance(user, trade.trade_currency, trade.amount, 'up')
        create_record_cashflow(user, owner, 'external-transfer', trade.price_trade, trade.payment_currency, trade, tx_hash=trade.tx_hash)

    else:

        create_record_cashflow(owner, user, 'transfer', trade.price_trade, trade.payment_currency, trade)
        update_wallet_balance(user, trade.payment_currency, trade.price_trade, 'up')
        create_record_cashflow(user, owner, 'external-transfer', trade.amount, trade.trade_currency, trade,
                               tx_hash=trade.tx_hash)

    close_trade(trade)


def close_trade(trade):

    # if trade.order.type_operation == 'sale':
    #     hm = trade.order.parent_order.holdMoney.get(currency=trade.trade_currency)
    #     hm.amount -= trade.price_trade
    #     hm.save()
    #
    # if trade.order.type_operation == 'buy':
    #     hm = trade.order.parent_order.holdMoney.get(currency=trade.payment_currency)
    #     hm.amount -= trade.amount
    #     hm.save()

    trade.status = 'close'
    trade.save()


def hold_money_trade(trade):
    user = trade.user
    hold_list = []
    hold_list.append(dict(
        trader=trade,
        currency=trade.trade_currency,
        amount=trade.amount
    ))
    TradeHoldMoney.objects.bulk_create([TradeHoldMoney(**r) for r in hold_list])