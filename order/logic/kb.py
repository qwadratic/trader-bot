import math
from decimal import Decimal

from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

from bot.helpers.converter import currency_in_usd
from bot.helpers.shortcut import to_units, round_currency, get_currency_rate
from order.logic.core import get_orders, button_orders
from order.models import Order
from user.logic.core import create_reflink


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


def market_depth_trade_currency(user):
    def _makerow(*ccy_list):
        prefix = 'select_currency_for_market_depth-trade_currency'
        return [InlineKeyboardButton(ccy, callback_data=f'{prefix}-{ccy}') for ccy in ccy_list]

    back_btn = InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='select_currency_for_market_depth-back_menu')

    return InlineKeyboardMarkup(
        [
            _makerow('BIP', 'BTC', 'USDT', 'ETH'),
            _makerow('USD', 'RUB', 'UAH'),
            [back_btn]
        ])


def market_depth_payment_currency(trade_currency, user):

    btn_back = InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='select_currency_for_market_depth-back_trade_currency')

    def _makerow(*ccy_list):
        prefix = 'select_currency_for_market_depth-payment_currency'
        return [InlineKeyboardButton(ccy, callback_data=f'{prefix}-{ccy}') for ccy in ccy_list]

    crypto = ['BIP', 'BTC', 'USDT', 'ETH']
    fiat = ['USD', 'RUB', 'UAH']

    if trade_currency in crypto:
        crypto.remove(trade_currency)
        kb_rows = [
            _makerow(*crypto),
            _makerow(*fiat),
            [btn_back]
        ]

    elif trade_currency in fiat:
        kb_rows = [
            _makerow(*crypto),
            [btn_back]
        ]

    return InlineKeyboardMarkup(kb_rows)


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

    kb.append([InlineKeyboardButton(
        user.get_text(name='order-kb-cancel_order'),
        callback_data='cancel_order_create')]
    )

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


def avarage_rate(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-average_rate'), callback_data=f'order_helper-average_rate')],
            [InlineKeyboardButton(user.get_text(name='order-kb-cancel_order'), callback_data=f'cancel_order_create')]
        ]
    )
    return kb


def max_amount(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-max_amount'), callback_data=f'order_helper-max_amount')],
            [InlineKeyboardButton(user.get_text(name='order-kb-cancel_order'), callback_data=f'cancel_order_create')]
        ]
    )
    return kb


def market_depth(user, trade_currency, payment_currency, offset, revers=False):

    sale_orders = get_orders('sale', trade_currency, payment_currency, offset, 5, 'open')
    buy_orders = get_orders('buy', trade_currency, payment_currency, offset, 5, 'open')

    trade_currency_rate_usd = to_units(trade_currency, get_currency_rate(trade_currency))
    payment_currency_rate_usd = to_units(payment_currency, get_currency_rate(payment_currency))

    trade_currency_rate = round_currency(payment_currency, Decimal(trade_currency_rate_usd / payment_currency_rate_usd), to_str=True)
    payment_currency_rate = round_currency(trade_currency, Decimal(payment_currency_rate_usd / trade_currency_rate_usd), to_str=True)

    kb_list = []

    exchange_rate_button = f'1 {trade_currency} {round_currency("USD", trade_currency_rate_usd)} USD | 1 {trade_currency} {trade_currency_rate} {payment_currency} | 1 {payment_currency} {payment_currency_rate} {trade_currency}'

    kb_list.append([InlineKeyboardButton(' 🔍 Смотреть глубже', callback_data='market_depth-look-sale')])
    kb_list = button_orders(user, sale_orders, kb_list, offset)

    kb_list.append([InlineKeyboardButton(exchange_rate_button, callback_data=f'wqwq')])

    kb_list = button_orders(user, buy_orders, kb_list, offset)
    kb_list.append([InlineKeyboardButton(' 🔍 Смотреть глубже', callback_data='market_depth-look-buy')])
    kb_list.append([InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_buy'), callback_data='trade_menu-new_buy'),
             InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_sale'), callback_data='trade_menu-new_sale')])

    kb_list.append([
        InlineKeyboardButton('☯️ 1\X', callback_data=f'market_depth-reverse-{revers}'),
        InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'market_depth-back')])

    return InlineKeyboardMarkup(kb_list)


def half_market_depth(user, type_orders, offset):
    revers = user.cache['clipboard']['market_depth']['revers']

    if revers:
        trade_currency = user.cache['clipboard']['market_depth']['payment_currency']
        payment_currency = user.cache['clipboard']['market_depth']['trade_currency']
    else:
        trade_currency = user.cache['clipboard']['market_depth']['trade_currency']
        payment_currency = user.cache['clipboard']['market_depth']['payment_currency']

    orders = get_orders(type_orders, trade_currency, payment_currency, offset, 10, 'open')

    all_orders = Order.objects.filter(type_operation=type_orders, trade_currency=trade_currency, payment_currency=payment_currency, status='open')

    kb_list = button_orders(user, orders, [], offset)

    if offset == 5 and len(all_orders) <= 15:
        kb_list.append([InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'market_depth-back_to_market_depth')])
        return InlineKeyboardMarkup(kb_list)

    elif offset == 5:

        kb_list.append([InlineKeyboardButton(f'⇒', callback_data=f'market_depth-move-right-{type_orders}-{offset}')])

    elif 0 < offset + 15 >= len(all_orders):

        kb_list.append([InlineKeyboardButton(f'⇐', callback_data=f'market_depth-move-left-{type_orders}-{offset}')])
    else:
        kb_list.append([InlineKeyboardButton(f'⇐', callback_data=f'market_depth-move-left-{type_orders}-{offset}'),
                        InlineKeyboardButton(f'⇒', callback_data=f'market_depth-move-right-{type_orders}-{offset}')])

    kb_list.append([InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'market_depth-back_to_market_depth')])

    return InlineKeyboardMarkup(kb_list)


def owner_order_list(user, type_orders, offset, wallet_menu=False):
    sort_orders = user.parentOrders.exclude(status__in=['completed', 'deleted'])[offset:offset+7]
    all_orders = user.parentOrders.exclude(status__in=['completed', 'deleted'])

    if wallet_menu:
        cbdata_back = 'owner_order-back-to_wallet'
    else:
        cbdata_back = 'owner_order-back-to_trade_menu'

    kb_list = [[InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=cbdata_back)],
               [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_buy'), callback_data='trade_menu-new_buy'),
                InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_sale'), callback_data='trade_menu-new_sale')]]

    for order in sort_orders:
        amount = round_currency(order.trade_currency, to_units(order.trade_currency, order.amount))
        currency_rate = round_currency(order.trade_currency, to_units(order.trade_currency, order.currency_rate))

        status_marker = '▶️' if order.status == 'open' else '⏸'
        operation_marker = '🟥' if order.type_operation == 'buy' else '🟩'

        button_name = f'{status_marker} {operation_marker} {order.trade_currency}/{", ".join(order.payment_currency)} | $ {currency_rate} | {amount} {order.trade_currency} |'
        kb_list.append([InlineKeyboardButton(button_name, callback_data=f'owner_order-open-{order.id}-{type_orders}-{offset}')])

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


def order_for_owner(order):
    user = order.user
    marker_status_button = {'open': user.get_text(name='order-kb-off_order'),
                            'close': user.get_text(name='order-kb-on_order')}

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-share'), callback_data=f'share_order-{order.id}')],
            [InlineKeyboardButton(f'{marker_status_button[order.status]}',
                                  callback_data=f'order_info-switch-{order.id}')],
            [InlineKeyboardButton(user.get_text(name='kb-close'), callback_data='close'),
             InlineKeyboardButton(user.get_text(name='kb-delete'), callback_data=f'order_info-delete-{order.id}')]

        ]
    )

    return kb


def order_for_user(user, order_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-close'), callback_data=f'close'),
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


def confirm_delete_order(user, order_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-yes'), callback_data=f'delete_order-yes-{order_id}'),
             InlineKeyboardButton(user.get_text(name='kb-no'), callback_data=f'delete_order-no-{order_id}')]
        ]
    )
    return kb


def deposit_from_order(user):

    order = user.temp_order
    if order.type_operation == 'sale':
        trade_currency = order.trade_currency
        kb = InlineKeyboardMarkup(
            [
                    [InlineKeyboardButton(user.get_text(name='order-kb-back_to_select_payment_currency'),
                                          callback_data='order_deposit-back')],
                    [InlineKeyboardButton(user.get_text(name='order-kb-show_deposit_address').format(currency=trade_currency),
                                          callback_data=f'order_deposit-show_address-{trade_currency}')],
                    [InlineKeyboardButton(user.get_text(name='order-kb-cancel_order'),
                                          callback_data=f'cancel_order_create-{order.id}')]
            ])

        return kb
    else:

        kb_list = [[InlineKeyboardButton(user.get_text(name='order-kb-back_to_select_payment_currency'),
                                         callback_data='order_deposit-back')]]

        underbalanced_currency = user.cache['clipboard']['deposit_currency']
        positive_currency = []

        for currency in order.payment_currency:
            if currency in underbalanced_currency:
                continue
            positive_currency.append(currency)

        if len(positive_currency) > 0:
            kb_list.append([InlineKeyboardButton(user.get_text(name='order-kb-continue_with').format(currency=', '.join(positive_currency)),
                                                 callback_data=f'order_deposit-continue-{", ".join(positive_currency)}')])

        for currency in underbalanced_currency:
            kb_list.append([InlineKeyboardButton(user.get_text(name='order-kb-show_deposit_address').format(currency=currency),
                                                 callback_data=f'order_deposit-show_address-{currency}')])

        kb_list.append([InlineKeyboardButton(user.get_text(name='order-kb-cancel_order'),
                                             callback_data=f'cancel_order_create-{order.id}')])
        return InlineKeyboardMarkup(kb_list)


def continue_order_after_deposit(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-create_order'), callback_data='complete_order_create')],
            [InlineKeyboardButton(user.get_text(name='order-kb-cancel_order'), callback_data=f'cancel_order_create')]
        ]
    )
    return kb


def share_url(user, order_id):
    url = create_reflink(order_id=order_id)

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-share-go'), url=url)]

        ]
    )
    return kb