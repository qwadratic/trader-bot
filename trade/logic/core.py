from constance import config

from bot.helpers.shortcut import create_record_cashflow, to_units, to_cents, round_currency, get_fee_amount
from order.logic.core import update_order, close_order
from trade.models.trade import TradeHoldMoney
from user.logic.core import update_wallet_balance
from user.models import UserRef
import logging

logger = logging.getLogger('TradeOperations')


def pay_commssion(user):
    user_refferer = user.ref.get_or_none()

    if user_refferer:
        pass


def auto_trade(trade):
    owner = trade.order.parent_order.user
    owner_ref = UserRef.objects.get_or_none(user=owner)
    user = trade.user
    user_ref = UserRef.objects.get_or_none(user=user)

    parent_order = trade.order.parent_order
    
    new_amount = parent_order.amount - trade.amount

    new_parent_order = update_order(parent_order, 'set amount', new_amount)

    trade_currency = trade.trade_currency
    payment_currency = trade.payment_currency
    maker_fee = trade.maker_fee
    taker_fee = trade.taker_fee

    if trade.order.type_operation == 'sale':
        update_wallet_balance(owner, payment_currency, trade.price_trade - maker_fee, 'up')
        if owner_ref:
            owner_referrer = owner_ref.referrer

            maker_affiliate_fee = to_cents(trade_currency, get_fee_amount(config.AFFILIATE_FEE, to_units(trade_currency, maker_fee)))
            maker_affiliate_fee_usd = to_cents('BONUS', to_units(trade_currency, maker_affiliate_fee) * to_units(trade_currency, trade.order.parent_order.currency_rate))
            maker_fee -= maker_affiliate_fee

            update_wallet_balance(owner_referrer, 'BONUS', maker_affiliate_fee_usd, 'up')
            create_record_cashflow(owner, owner_referrer, 'affiliate_fee', maker_affiliate_fee_usd, 'USD', trade)

        update_wallet_balance(owner, trade_currency, trade.amount, 'down')
        create_record_cashflow(owner, user, 'transfer', trade.amount, trade_currency, trade)
        create_record_cashflow(owner, None, 'trade_fee', maker_fee, trade_currency, trade)

        update_wallet_balance(user, trade_currency, trade.amount - taker_fee, 'up')
        if user_ref:
            user_referrer = user_ref.referrer

            taker_affiliate_fee = to_cents(payment_currency, get_fee_amount(config.AFFILIATE_FEE, to_units(payment_currency, taker_fee)))
            taker_affiliate_fee_usd = to_cents('BONUS', to_units(payment_currency, taker_affiliate_fee) * to_units(payment_currency, trade.order.parent_order.payment_currency_rate[payment_currency]))

            taker_fee -= taker_affiliate_fee

            update_wallet_balance(user_referrer, 'BONUS', taker_affiliate_fee_usd, 'up')
            create_record_cashflow(user, user_referrer, 'affiliate_fee', taker_affiliate_fee_usd, 'USD', trade)

        update_wallet_balance(user, payment_currency, trade.price_trade, 'down')
        create_record_cashflow(user, owner, 'transfer', trade.price_trade, payment_currency, trade)
        create_record_cashflow(user, None, 'trade_fee', taker_fee, payment_currency, trade)

    # покупка
    else:
        update_wallet_balance(owner, trade_currency, trade.amount - maker_fee, 'up')

        if owner_ref:
            owner_referrer = owner_ref.referrer

            maker_affiliate_fee = to_cents(payment_currency, get_fee_amount(config.AFFILIATE_FEE, to_units(trade_currency, maker_fee)))
            maker_affiliate_fee_usd = to_cents('BONUS', to_units(payment_currency, maker_affiliate_fee) * to_units(payment_currency, trade.order.parent_order.payment_currency_rate[payment_currency]))
            maker_fee -= maker_affiliate_fee

            update_wallet_balance(owner_referrer, 'BONUS', maker_affiliate_fee_usd, 'up')
            create_record_cashflow(owner, owner_referrer, 'affiliate_fee', maker_affiliate_fee_usd, 'USD', trade)

        update_wallet_balance(owner, payment_currency, trade.price_trade, 'down')
        create_record_cashflow(owner, user, 'transfer', trade.price_trade, payment_currency, trade)
        create_record_cashflow(owner, None, 'trade_fee', maker_fee, payment_currency, trade)

        update_wallet_balance(user, payment_currency, trade.price_trade - taker_fee, 'up')

        if user_ref:
            user_referrer = user_ref.referrer

            taker_affiliate_fee = to_cents(trade_currency, get_fee_amount(config.AFFILIATE_FEE, to_units(trade_currency, taker_fee)))
            taker_affiliate_fee_usd = to_cents('USD', to_units(trade_currency, taker_affiliate_fee) * to_units(trade_currency, trade.order.parent_order.currency_rate))
            taker_fee -= taker_affiliate_fee

            update_wallet_balance(user_referrer, 'BONUS', taker_affiliate_fee_usd, 'up')
            create_record_cashflow(user, user_referrer, 'affiliate_fee', taker_affiliate_fee_usd, 'USD', trade)

        update_wallet_balance(user, trade_currency, trade.amount, 'down')
        create_record_cashflow(user, owner, 'transfer', trade.amount, trade_currency, trade)
        create_record_cashflow(user, None, 'trade_fee', taker_fee, trade_currency, trade)

    close_trade(trade)

# def semi_auto_trade(trade):
#     owner = trade.order.parent_order.user
#     user = trade.user
#     parent_order = trade.order.parent_order
#
#     update_order(parent_order, 'amount', parent_order.amount - trade.amount)
#
#     if trade.order.type_operation == 'sale':
#         create_record_cashflow(owner, user, 'transfer', trade.amount, trade.trade_currency, trade)
#         update_wallet_balance(user, trade.trade_currency, trade.amount, 'up')
#         create_record_cashflow(user, owner, 'external-transfer', trade.price_trade, trade.payment_currency, trade, tx_hash=trade.tx_hash)
#
#     else:
#
#         create_record_cashflow(owner, user, 'transfer', trade.price_trade, trade.payment_currency, trade)
#         update_wallet_balance(user, trade.payment_currency, trade.price_trade, 'up')
#         create_record_cashflow(user, owner, 'external-transfer', trade.amount, trade.trade_currency, trade,
#                                tx_hash=trade.tx_hash)
#
#     close_trade(trade)


def close_trade(trade):
    parent_order = trade.order.parent_order
    if trade.order.type_operation == 'sale':
        hm = parent_order.holdMoney.get(currency=trade.trade_currency)
        hm.amount -= trade.amount
        hm.save()

    if trade.order.type_operation == 'buy':
        hm = parent_order.holdMoney.get(currency=trade.payment_currency)
        hm.amount -= trade.price_trade
        hm.save()

    trade.status = 'close'
    trade.save()

    if parent_order.amount == 0:
        close_order(parent_order, 'completed')


def hold_money_trade(trade):
    hold_list = []
    hold_list.append(dict(
        trader=trade,
        currency=trade.trade_currency,
        amount=trade.amount
    ))
    TradeHoldMoney.objects.bulk_create([TradeHoldMoney(**r) for r in hold_list])


def check_balance_from_trade(currency, price_trade, balance):
    amount_deposit = price_trade - balance

    if to_cents(currency, balance) >= to_cents(currency, price_trade):
        return True, price_trade
    else:
        return False, currency, round_currency(currency, amount_deposit), price_trade
