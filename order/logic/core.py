from decimal import Decimal

from bot.helpers.converter import currency_in_usd
from bot.helpers.shortcut import to_units, to_cents
from order.models import Order, ParentOrder, OrderHoldMoney


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
        payment_currency_rate = round(
            Decimal(to_units(payment_currency, order.parent_order.payment_currency_rate[payment_currency])
                    / to_units(trade_currency, order.parent_order.currency_rate)), 6)
    else:
        trade_currency_rate_usd = to_units(trade_currency, order.parent_order.payment_currency_rate[trade_currency])
        payment_currency_rate = round(
            Decimal(to_units(payment_currency, order.parent_order.currency_rate))
                    / trade_currency_rate_usd, 6)

    payment_currency = order.payment_currency

    trade_currency_rate = to_units(trade_currency, order.currency_rate)

    amount = round(to_units(trade_currency, order.amount), 6)
    price_order = round(amount * trade_currency_rate, 6)

    txt = user.get_text(name='order-order_info').format(
        order_id=order.id,
        type_operation=trade_direction[type_operation]["type"],
        trade_currency=trade_currency,
        trade_currency_rate_usd=trade_currency_rate_usd,
        payment_currency=payment_currency,
        rate_1=trade_currency_rate,
        rate_2=payment_currency_rate,
        amount=amount,
        price_order=price_order
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
    payment_currency = order.payment_currency
    trade_currency_rate_usd = to_units(trade_currency, order.currency_rate)
    trade_currency_rate = to_units(trade_currency, order.currency_rate)
    payment_currency_rate = round(
        Decimal(to_units(payment_currency, order.payment_currency_rate[payment_currency])
                / to_units(trade_currency, order.currency_rate)), 6)
    amount = to_units(trade_currency, order.amount)
    price_order = amount * trade_currency_rate

    txt = user.get_text(name='order-order_info').format(
        order_id=order.id,
        type_operation=trade_direction[type_operation]["type"],
        trade_currency=trade_currency,
        trade_currency_rate_usd=trade_currency_rate_usd,
        payment_currency=payment_currency,
        rate_1=trade_currency_rate,
        rate_2=payment_currency_rate,
        amount=amount,
        price_order=price_order
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
