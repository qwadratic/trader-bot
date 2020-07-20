from decimal import Decimal

from bot.helpers.converter import currency_in_usd
from bot.helpers.shortcut import to_units, to_cents
from order.models import Order, ParentOrder, OrderHoldMoney


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
    currency_rate = to_units(trade_currency, order.currency_rate)
    amount = to_units(trade_currency, order.amount)

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
    currency_rate = to_units(trade_currency, order.currency_rate)
    amount = to_units(trade_currency, order.amount)

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

            amount = to_units(order.trade_currency, order.amount) * to_units(order.trade_currency, order.currency_rate) / currency_in_usd(currency, 1)

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

            amount = to_units(currency, order.amount) * to_units(currency, order.currency_rate) / currency_in_usd(currency, 1)
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

    return order


def hold_money_order(order):

    user = order.user
    hold_list = []
    if order.type_operation == 'sale':
        wallet = user.virtual_wallets.get(currency=order.trade_currency)
        wallet.balance -= order.amount
        wallet.save()
        hold_list.append(dict(
            order=order,
            currency=order.trade_currency,
            amount=order.amount
        ))

    elif order.type_operation == 'buy':

        for currency in order.payment_currency:
            wallet = user.virtual_wallets.get(currency=currency)
            wallet.balance -= order.amount
            wallet.save()
            currency_rate = Decimal(order.currency_rate / order.payment_currency_rate[currency])
            amount = currency_rate * to_units(order.trade_currency, order.amount)
            hold_list.append(dict(
                order=order,
                currency=currency,
                amount=to_cents(currency, amount)
            ))

    OrderHoldMoney.objects.bulk_create([OrderHoldMoney(**r) for r in hold_list])
