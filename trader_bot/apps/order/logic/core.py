from decimal import Decimal

from ..models import Order

from ...bot.helpers import to_pip, to_bip, currency_in_user_currency, currency_in_usd


def get_order_info(order_id):
    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}
    status = {'open': '⚪️ Активно',
              'close': '🔴 Отключено'}

    order = Order.objects.get(order_id=order_id)
    user_currency = order.user.settings.currency
    type_operation = order.type_operation
    trade_currency = order.trade_currency
    currency_rate = to_bip(order.currency_rate)
    amount = to_bip(order.amount)

    payment_currency= order.payment_currency

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
    txt += f'\n**{payment_currency}**'

    return txt


def order_info_for_owner(order_id):
    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}
    status = {'open': '⚪️ Активно',
              'close': '🔴 Отключено'}

    orders = Order.objects.filter(order_id=order_id).exclude(mirror=True)

    if len(orders) == 1:
        user_currency = orders[0].user.settings.currency
        type_operation = orders[0].type_operation
        trade_currency = orders[0].trade_currency
        currency_rate = to_bip(orders[0].currency_rate)
        amount = to_bip(orders[0].amount)

        txt = orders[0].user.get_text(name='order-order_info').format(
            order_id=orders[0].id,
            type_operation=trade_direction[type_operation]["type"],
            trade_currency=trade_currency,
            icon_operation=trade_direction[type_operation]["icon"],
            cost=currency_rate * amount,
            user_currency=user_currency,
            amount=amount,
            currency_rate=currency_rate

        )
        txt += f'\n**{orders[0].payment_currency}**'
        txt += f'\n\n**Статус:** {status[orders[0].status]}'
        return txt

    if len(orders) > 1:
        user_currency = orders[0].user.settings.currency

        txt = orders[0].user.get_text(name='order-order_info').format(
            order_id=orders[0].id,
            type_operation=trade_direction[orders[0].type_operation]["type"],
            trade_currency=orders[0].trade_currency,
            icon_operation=trade_direction[orders[0].type_operation]["icon"],
            cost=to_bip(orders[0].currency_rate * orders[0].amount),
            user_currency=user_currency,
            amount=to_bip(orders[0].amount),
            currency_rate=to_bip(orders[0].currency_rate)

        )

        for order in orders:
            txt += f'\n**{order.payment_currency}**'

        txt += f'\n\n**Статус:** {status[orders[0].status]}'
        return txt


def create_order(temp_order):
    payment_currency_list = temp_order.payment_currency

    order_list = []
    for currency in payment_currency_list:

        order_list.append(dict(
            user=temp_order.user,
            order_id=temp_order.order_id,
            type_operation=temp_order.type_operation,
            trade_currency=temp_order.trade_currency,
            amount=temp_order.amount,
            currency_rate=temp_order.currency_rate,
            payment_currency=currency,
            requisites=temp_order.requisites[currency],
            status='close'

        ))

        type_operation = 'buy' if temp_order.type_operation == 'sale' else 'sale'

        amount = to_bip(temp_order.amount) * to_bip(temp_order.currency_rate) / Decimal(currency_in_usd(currency, 1))

        order_list.append(dict(
            user=temp_order.user,
            order_id=temp_order.order_id,
            type_operation=type_operation,
            trade_currency=currency,
            amount=to_pip(amount),
            currency_rate=to_pip(1/to_bip(temp_order.currency_rate)),
            payment_currency=temp_order.trade_currency,
            requisites=temp_order.requisites[currency],
            status='close',
            mirror=True

        ))
    Order.objects.bulk_create([Order(**r) for r in order_list])

