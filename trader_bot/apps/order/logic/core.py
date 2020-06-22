from ..models import Order, OrderMirror

from ...bot.helpers import to_pip, to_bip, currency_in_user_currency, currency_in_usd


def get_order_info(order_id):
    trade_direction = {'buy': {'type': 'Покупка',
                               'icon': '📈'},
                       'sale': {'type': 'Продажа',
                                'icon': '📉'}}
    status = {'open': '⚪️ Активно',
              'close': '🔴 Отключено'}

    order = Order.objects.get(id=order_id)
    user_currency = order.user.settings.currency
    type_operation = order.type_operation
    trade_currency = order.trade_currency
    currency_rate = to_bip(order.currency_rate)
    amount = to_bip(order.amount)

    payment_currency_list = order.payment_currency

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

    for currency in payment_currency_list:
        txt += f'\n**{currency}**'
    txt += f'\n\n**Статус:** {status[order.status]}'

    return txt


def create_order(temp_order):
    user = temp_order.user
    order = Order.objects.create(
        user=user,
        type_operation=temp_order.type_operation,
        trade_currency=temp_order.trade_currency,
        amount=temp_order.amount,
        currency_rate=temp_order.currency_rate,
        payment_currency=temp_order.payment_currency,
        requisites=temp_order.requisites,
        status='close'
    )

    type_operation = 'buy' if order.type_operation == 'sale' else 'sale'
    payment_currency_list = order.payment_currency

    for currency in payment_currency_list:

        OrderMirror.objects.create(
            order=order,
            type_operation=type_operation,
            trade_currency=currency,
            amount=order.amount,
            currency_rate=order.currency_rate,
            payment_currency=order.trade_currency,
            requisites={currency: order.requisites[currency]},
            status='close'

        )

    return order