from decimal import Decimal

from ..models import Order, ParentOrder

from ...bot.helpers import to_pip, to_bip, currency_in_user_currency, currency_in_usd


def get_order_info(user, order_id):
    #  TODO учесть валюту юзера

    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}

    order = Order.objects.get(id=order_id)
    user_currency = user.settings.currency
    type_operation = order.type_operation
    trade_currency = order.trade_currency
    currency_rate = to_bip(order.currency_rate)
    amount = to_bip(order.amount)

    payment_currency = order.payment_currency

    txt = user.get_text(name='order-order_info').format(
        order_id=order.id,
        type_operation=trade_direction[type_operation]["type"],
        trade_currency=trade_currency,
        icon_operation=trade_direction[type_operation]["icon"],
        cost=currency_rate * amount,
        user_currency=user_currency,
        amount=amount,
        currency_rate=currency_rate

    )
    txt += f'\n**{payment_currency}**'

    return txt


def order_info_for_owner(order):
    #  TODO сделать здесь интернационализацию

    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}

    status = {'open': '⚪️ Активно',
              'close': '🔴 Отключено'}

    user_currency = order.user.settings.currency
    type_operation = order.type_operation
    trade_currency = order.trade_currency
    currency_rate = to_bip(order.currency_rate)
    amount = to_bip(order.amount)

    txt = order.user.get_text(name='order-order_info').format(
        order_id=order.id,
        type_operation=trade_direction[type_operation]["type"],
        trade_currency=trade_currency,
        icon_operation=trade_direction[type_operation]["icon"],
        cost=currency_rate * amount,
        user_currency=user_currency,
        amount=amount,
        currency_rate=currency_rate

    )

    for currency in order.payment_currency:
        txt += f'\n**{currency}**'

    txt += f'\n\n{status[order.status]}'

    return txt


def create_order(temp_order):
    payment_currency_list = temp_order.payment_currency

    order = ParentOrder.objects.create(
        user=temp_order.user,
        type_operation=temp_order.type_operation,
        trade_currency=temp_order.trade_currency,
        amount=temp_order.amount,
        currency_rate=temp_order.currency_rate,
        payment_currency=temp_order.payment_currency,
        requisites=temp_order.requisites
    )

    order_list = []
    for currency in payment_currency_list:

        order_list.append(dict(
            parent_order=order,
            type_operation=order.type_operation,
            trade_currency=order.trade_currency,
            amount=order.amount,
            currency_rate=order.currency_rate,
            payment_currency=currency,
            requisites=order.requisites[currency]
        ))

        type_operation = 'buy' if temp_order.type_operation == 'sale' else 'sale'

        amount = to_bip(order.amount) * to_bip(order.currency_rate) / Decimal(currency_in_usd(currency, 1))

        order_list.append(dict(
            parent_order=order,
            type_operation=type_operation,
            trade_currency=currency,
            amount=to_pip(amount),
            currency_rate=to_pip(1/to_bip(order.currency_rate)),
            payment_currency=order.trade_currency,
            requisites=order.requisites[currency],
            mirror=True
        ))

    Order.objects.bulk_create([Order(**r) for r in order_list])

    return order


def get_owner_orders(user):
    orders = user.orders.exclude(mirror=True)

