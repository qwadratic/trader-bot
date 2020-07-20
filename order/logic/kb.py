import math
from decimal import Decimal

from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

from bot.helpers.converter import currency_in_usd
from bot.helpers.shortcut import to_units
from order.models import Order


def trade_menu(user):

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_buy'), callback_data='trade_menu-new_buy'),
             InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_sale'), callback_data='trade_menu-new_sale')],
            [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-orders'), callback_data='trade_menu-orders')],
            [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-my_orders'), callback_data='trade_menu-my_orders'),
             InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-my_trades'), callback_data='trade_menu-my_trades')],
            # [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-notifications'), callback_data='trade_menu-notifications')]
        ]
    )

    return kb


def trade_currency(user):

    def _makerow(*ccy_list):
        prefix = 'trade_currency'
        return [InlineKeyboardButton(ccy, callback_data=f'{prefix}-{ccy}') for ccy in ccy_list]

    back_btn = InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='trade_currency-back')

    return InlineKeyboardMarkup(
        [
            _makerow('BIP', 'BTC', 'USDT', 'ETH'),
            _makerow('USD', 'RUB', 'UAH'),
            [back_btn]
        ])


def payment_currency(trade_currency, user):
    btn_ok = InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')
    btn_back = InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')

    def _makerow(*ccy_list):
        prefix = 'order_payment_currency'
        return [InlineKeyboardButton(ccy, callback_data=f'{prefix}-{ccy}') for ccy in ccy_list]

    crypto = ['BIP', 'BTC', 'USDT', 'ETH']
    fiat = ['USD', 'RUB', 'UAH']

    if trade_currency in crypto:
        crypto.remove(trade_currency)
        kb_rows = [
            [btn_ok],
            _makerow(*crypto),
            _makerow(*fiat),
            [btn_back]
        ]

    elif trade_currency in fiat:
        kb_rows = [
            [btn_ok],
            _makerow(*crypto),
            [btn_back]
        ]

    return InlineKeyboardMarkup(kb_rows)


def choice_requisite_for_order(order, currency):
    user = order.user

    kb = []
    if currency not in ['USD', 'UAH', 'RUB']:

        kb .append([InlineKeyboardButton(
            user.get_text(name='order-kb-use_internal_wallet'),
            callback_data='requisite_for_order-use_wallet')
        ])

    current_currency = user.cache['clipboard']['requisites'][0]

    if len(user.requisites.filter(currency=current_currency)) == 1:
        requisite = user.requisites.get(currency=currency)

        button_name = requisite.address

        if requisite.name:
            button_name = f'{requisite.name}{requisite.address}'

        kb.append([InlineKeyboardButton(
            button_name,
            callback_data=f'requisite_for_order-use-{requisite.id}')]
        )

    if len(user.requisites.filter(currency=current_currency)) > 1:
        kb.append([InlineKeyboardButton(
            user.get_text(name='order-kb-open_purse'),
            callback_data=f'requisite_for_order-open_purse')]
        )


    kb.append([InlineKeyboardButton(
        user.get_text(name='order-kb-add_new_requisite'),
        callback_data='requisite_for_order-add_new')])

    return InlineKeyboardMarkup(kb)


def requisites_from_purse(user):
    current_currency = user.cache['clipboard']['currency']

    requisites = user.requisites.filter(currency=current_currency)

    kb = [[InlineKeyboardButton(user.get_text(name='order-kb-back_to_selection_requisite_menu'), callback_data='requisite_from_purse-back')]]

    for i in requisites:
        button_name = f'[{i.currency}]{i.address}'

        if i.name:
            button_name = f'[{i.name}][{i.currency}]{i.address}'

        kb.append([InlineKeyboardButton(button_name, callback_data=f'requisite_from_purse-use-{i.id}')])

    return InlineKeyboardMarkup(kb)


def order_list(user, type_orders, offset):
    # TODO статус поставить
    if type_orders == 'buy':
        order_by = 'currency_rate'

    else:
        order_by = '-currency_rate'

    orders = Order.objects.filter(type_operation=type_orders).exclude(parent_order__user=user).order_by(order_by)[offset:offset+7]
    all_orders = Order.objects.filter(type_operation=type_orders).exclude(parent_order__user=user)

    kb_list = [[InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'order_list-back')]]
    if type_orders == 'sale':
        kb_list.append([InlineKeyboardButton(user.get_text(name='order-kb-look_at_the_buy'), callback_data=f'order_list-switch-buy')])
    else:
        kb_list.append([InlineKeyboardButton(user.get_text(name='order-kb-look_at_the_sale'), callback_data=f'order_list-switch-sale')])

    for order in orders:
        payment_currency_in_trade_currency = to_units(order.trade_currency, order.currency_rate) / Decimal(currency_in_usd(order.payment_currency, 1))
        button_name = f'{round(payment_currency_in_trade_currency, 6)} {order.payment_currency} ({round(to_units("USD", order.currency_rate), 2)} USD): ' \
            f'{to_units(order.trade_currency, order.amount)} {order.trade_currency}'
        kb_list.append([InlineKeyboardButton(button_name, callback_data=f'order_list-open-{order.id}-{type_orders}-{offset}')])

    if offset == 0 and len(all_orders) <= 7:
        return InlineKeyboardMarkup(kb_list)

    elif offset == 0:
        position = f'{int(offset + 2)}/{int(math.ceil(len(all_orders) / 7))}'
        kb_list.append([InlineKeyboardButton(f'{position} ⇒', callback_data=f'order_list-move-right-{type_orders}-{offset}')])

    elif 0 < offset + 7 >= len(all_orders):
        position = f'{int(math.ceil(len(all_orders) / 7)) - 1}/{int(math.ceil(len(all_orders) / 7))}'

        kb_list.append([InlineKeyboardButton(f'⇐ {position}', callback_data=f'order_list-move-left-{type_orders}-{offset}')])

    else:
        position_1 = f'{int((offset + 7) / 7 - 1)}/{int(math.ceil(len(all_orders) / 7))}'
        position_2 = f'{int(offset / 7 + 2)}/{int(math.ceil(len(all_orders) / 7))}'

        kb_list.append([InlineKeyboardButton(f'⇐ {position_1}', callback_data=f'order_list-move-left-{type_orders}-{offset}'),
                        InlineKeyboardButton(f'{position_2} ⇒', callback_data=f'order_list-move-right-{type_orders}-{offset}')])

    return InlineKeyboardMarkup(kb_list)


def owner_order_list(user, offset):
    sort_orders = user.parent_orders.all()[offset:offset+7]
    all_orders = user.parent_orders.all()

    kb_list = [[InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='owner_order-back')]]

    for order in sort_orders:
        button_name = f'[{order.type_operation}]{order.trade_currency}'
        kb_list.append([InlineKeyboardButton(button_name, callback_data=f'owner_order-open-{order.id}')])

    if offset == 0 and len(all_orders) <= 7:
        return InlineKeyboardMarkup(kb_list)

    elif offset == 0:
        position = f'{int(offset + 2)}/{int(math.ceil(len(all_orders) / 7))}'
        kb_list.append([InlineKeyboardButton(f'{position} ⇒', callback_data=f'owner_order-move-right-{offset}')])

    elif 0 < offset + 7 >= len(all_orders):
        position = f'{int(math.ceil(len(all_orders) / 7)) - 1}/{int(math.ceil(len(all_orders) / 7))}'

        kb_list.append([InlineKeyboardButton(f'⇐ {position}', callback_data=f'owner_order-move-left-{offset}')])

    else:
        position_1 = f'{int((offset + 7) / 7 - 1)}/{int(math.ceil(len(all_orders) / 7))}'
        position_2 = f'{int(offset / 7 + 2)}/{int(math.ceil(len(all_orders) / 7))}'

        kb_list.append([InlineKeyboardButton(f'⇐ {position_1}', callback_data=f'owner_order-move-left-{offset}'),
                        InlineKeyboardButton(f'{position_2} ⇒', callback_data=f'owner_order-move-right-{offset}')])

    return InlineKeyboardMarkup(kb_list)


def order_for_owner(order, location):
    user = order.user
    marker_status_button = {'open': user.get_text(name='order-kb-off_order'),
                            'close': user.get_text(name='order-kb-on_order')}

    if location == 1:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='order-kb-share'), callback_data=f'order_info-share-{order.id}')],
                [InlineKeyboardButton(f'{marker_status_button[order.status]}',callback_data=f'order_info-switch-{order.id}')],
                [InlineKeyboardButton(user.get_text(name='kb-close'), callback_data=f'order_info-close-{order.id}'),
                 InlineKeyboardButton(user.get_text(name='kb-delete'), callback_data=f'order_info-delete-{order.id}')]

            ]
        )

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='order-kb-share'), callback_data=f'order_info-share-{order.id}')],
                [InlineKeyboardButton(f'{marker_status_button[order.status]}', callback_data=f'order_info-switch-{order.id}')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'order_info-back-my_orders'),
                 InlineKeyboardButton(user.get_text(name='kb-delete'), callback_data=f'order_info-delete-{order.id}')]

            ]
        )

    return kb


def order_for_user(user, order_id, type_orders, offset):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-share'), callback_data=f'order_info-share-{order_id}')],
            [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'order_info-back-order_list-{type_orders}-{offset}'),
             InlineKeyboardButton(user.get_text(name='order-kb-start_trade'), callback_data=f'start_trade-{order_id}')]

        ]
    )
    return kb


def cancel_order(user, order_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-cancel_order'), callback_data=f'cancel_order_create-{order_id}')]
        ]
    )
    return kb