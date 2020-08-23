from decimal import Decimal

from pyrogram import InlineKeyboardButton

from bot.helpers.converter import currency_in_usd
from bot.helpers.shortcut import to_units, to_cents, round_currency
from bot.models import CurrencyList
from order.models import Order, ParentOrder, OrderHoldMoney
from trade.logic.core import update_order


def get_order_info(user, order_id):
    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}

    order = Order.objects.get(id=order_id)
    type_operation = order.type_operation
    trade_currency = order.trade_currency
    payment_currency = order.payment_currency
    if not order.mirror:
        trade_currency_rate_usd = to_units(trade_currency, order.parent_order.currency_rate)
        payment_currency_rate = Decimal(
            to_units(payment_currency, order.parent_order.payment_currency_rate[payment_currency]) / to_units(
                trade_currency, order.parent_order.currency_rate))
    else:
        trade_currency_rate_usd = to_units(trade_currency, order.parent_order.payment_currency_rate[trade_currency])
        payment_currency_rate = Decimal(
            to_units(payment_currency, order.parent_order.currency_rate)) / trade_currency_rate_usd

    payment_currency = order.payment_currency

    trade_currency_rate = to_units(trade_currency, order.currency_rate)

    amount = to_units(trade_currency, order.amount)
    price_order = amount * trade_currency_rate

    txt = user.get_text(name='order-order_info').format(
        order_id=order.id,
        type_operation=trade_direction[type_operation]["type"],
        trade_currency=trade_currency,
        trade_currency_rate_usd=trade_currency_rate_usd,
        payment_currency=payment_currency,
        rate_1=round_currency(payment_currency, trade_currency_rate),
        rate_2=round_currency(trade_currency, payment_currency_rate),
        amount=round_currency(trade_currency, amount),
        price_order=round_currency(payment_currency, price_order)
    )

    return txt


def order_info_for_owner(order):
    #  TODO сделать логику

    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}

    status = {'open': '⚪️ Активно',
              'close': '🔴 Отключено'}

    user = order.user
    type_operation = order.type_operation
    trade_currency = order.trade_currency
    trade_currency_rate_usd = to_units(trade_currency, order.currency_rate)
    amount = to_units(trade_currency, order.amount)

    currency_pairs = ''
    max_amounts = ''
    payment_currency = ''
    for currency in order.payment_currency:
        trade_currency_rate = order.currency_rate / order.payment_currency_rate[currency]
        payment_currency_rate = round_currency(trade_currency,
                                               order.payment_currency_rate[currency] / order.currency_rate)

        currency_pairs += f'1 {trade_currency} – {round_currency(currency, trade_currency_rate)} {currency}\n' \
            f'1 {currency} – {payment_currency_rate} {trade_currency}\n'

        price_lot = round_currency(currency, amount * trade_currency_rate)
        max_amounts += f'{price_lot} {currency}\n'

        payment_currency += f'{currency}\n'

    txt = user.get_text(name='order-parent_order_info').format(
        order_id=order.id,
        type_operation=trade_direction[type_operation]["type"],
        trade_currency=trade_currency,
        trade_currency_rate_usd=round_currency(trade_currency, trade_currency_rate_usd),
        payment_currency=payment_currency,
        amount=round_currency(trade_currency, amount),
        currency_pairs=currency_pairs,
        max_amounts=max_amounts
    )

    return txt


def create_order(temp_order):
    payment_currency_list = temp_order.payment_currency
    order = ParentOrder.objects.create(
        user=temp_order.user,
        type_operation=temp_order.type_operation,
        trade_currency=temp_order.trade_currency,
        amount=temp_order.amount,
        currency_rate=temp_order.currency_rate,
        payment_currency_rate=temp_order.payment_currency_rate,
        payment_currency=temp_order.payment_currency,
        requisites=temp_order.requisites
    )

    order_list = []

    if order.type_operation == 'sale':
        for currency in payment_currency_list:
            currency_rate = Decimal(order.currency_rate / order.payment_currency_rate[currency])
            order_list.append(dict(
                parent_order=order,
                type_operation=order.type_operation,
                trade_currency=order.trade_currency,
                amount=order.amount,
                currency_rate=to_cents(currency, currency_rate),
                payment_currency=currency,
                requisites=order.requisites[currency]
            ))

            type_operation = 'buy' if temp_order.type_operation == 'sale' else 'sale'

            amount = to_units(order.trade_currency, order.amount) * to_units(order.trade_currency,
                                                                             order.currency_rate) / currency_in_usd(
                currency, 1)

            currency_rate_mirror = Decimal(order.payment_currency_rate[currency] / order.currency_rate)
            order_list.append(dict(
                parent_order=order,
                type_operation=type_operation,
                trade_currency=currency,
                amount=to_cents(currency, amount),
                currency_rate=to_cents(order.trade_currency, currency_rate_mirror),
                payment_currency=order.trade_currency,
                requisites=order.requisites[currency],
                mirror=True
            ))
    else:
        for currency in payment_currency_list:
            currency_rate = Decimal(order.currency_rate / order.payment_currency_rate[currency])

            order_list.append(dict(
                parent_order=order,
                type_operation=order.type_operation,
                trade_currency=order.trade_currency,
                amount=order.amount,
                currency_rate=to_cents(currency, currency_rate),
                payment_currency=currency,
                requisites=order.requisites[order.trade_currency]
            ))

            type_operation = 'buy' if temp_order.type_operation == 'sale' else 'sale'

            amount = to_units(currency, order.amount) * to_units(currency, order.currency_rate) / currency_in_usd(
                currency, 1)
            currency_rate_mirror = Decimal(order.payment_currency_rate[currency] / order.currency_rate)
            order_list.append(dict(
                parent_order=order,
                type_operation=type_operation,
                trade_currency=currency,
                amount=to_cents(currency, amount),
                currency_rate=to_cents(order.trade_currency, currency_rate_mirror),
                payment_currency=order.trade_currency,
                requisites=order.requisites[order.trade_currency],
                mirror=True
            ))

    Order.objects.bulk_create([Order(**r) for r in order_list])

    hold_money_order(order)
    return order


def hold_money_order(order):
    user = order.user
    hold_list = []
    if order.type_operation == 'sale':
        hold_list.append(dict(
            order=order,
            user=user,
            currency=order.trade_currency,
            amount=order.amount
        ))

    elif order.type_operation == 'buy':

        for currency in order.payment_currency:
            currency_rate = Decimal(order.currency_rate / order.payment_currency_rate[currency])
            amount = currency_rate * to_units(order.trade_currency, order.amount)
            hold_list.append(dict(
                order=order,
                user=user,
                currency=currency,
                amount=to_cents(currency, amount)
            ))

    OrderHoldMoney.objects.bulk_create([OrderHoldMoney(**r) for r in hold_list])


def switch_order_status(order):
    hold_money = order.holdMoney.all()
    hold_money.delete()
    update_order(order, 'switch', 'close')


def close_order(order):
    hold_money = order.holdMoney.all()
    hold_money.delete()
    update_order(order, 'switch', 'completed')


def check_balance_from_order(user, order):
    is_good_balance = True
    amount = to_units(order.trade_currency, order.amount)

    deposit_currency = {}
    for currency in order.payment_currency:
        inst_currency = CurrencyList.objects.get(currency=currency)
        if inst_currency.type == 'fiat':
            continue

        payment_currency_rate = to_units(currency, order.payment_currency_rate[currency])
        trade_currency_rate = to_units(order.trade_currency, order.currency_rate)
        price_trade = Decimal(amount * trade_currency_rate / payment_currency_rate)
        balance = user.get_balance(currency, cent2unit=True)

        if price_trade > balance:
            is_good_balance = False

            if currency == 'USDT':
                deposit_address = user.wallets.get(currency='USDT').address
            else:
                deposit_address = user.wallets.get(currency=currency).address

            deposit_currency[currency] = dict(
                address=deposit_address
            )

    if is_good_balance:
        return True
    else:
        user_cache = user.cache
        user_cache['clipboard']['deposit_currency'] = deposit_currency
        user.save()

        return False


def get_orders(type_operation, trade_currency, payment_currency, offset, limit, status):

    if type_operation == 'buy':
        order_by = 'currency_rate'
    else:
        order_by = '-currency_rate'

    orders = Order.objects.filter(type_operation=type_operation, status=status, trade_currency=trade_currency, payment_currency=payment_currency).order_by(order_by)[offset:offset + limit]

    return orders


def button_orders(user, orders, kb_list, offset):

    for order in orders:
        type_operation = order.type_operation
        trade_currency = order.trade_currency
        payment_currency = order.payment_currency

        if order.mirror:
            currency_rate_usd = to_units(payment_currency, order.parent_order.payment_currency_rate[order.trade_currency], round=True)
        else:
            currency_rate_usd = to_units(trade_currency, order.parent_order.currency_rate, round=True)

        if type_operation == 'sale':
            icon = '🟥'
        else:
            icon = '🟩'

        trade_currency_rate = to_units(trade_currency, order.currency_rate, round=True)
        payment_currency_rate = round_currency(trade_currency, 1 / trade_currency_rate)

        amount = to_units(order.trade_currency, order.amount, round=True)
        button_name = f'{icon} {payment_currency_rate} {trade_currency}/{payment_currency} | {currency_rate_usd}$ {trade_currency} | {amount} {order.trade_currency} |'

        if order.parent_order.user_id == user.id:
            button_name += ' 👤'

        kb_list.append([InlineKeyboardButton('{:ᅠ<100}'.format(button_name), callback_data=f'market_depth-open-{order.id}-{type_operation}-{offset}')])

    return kb_list
