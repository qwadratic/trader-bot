from pyrogram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from ...order.models import Order


def trade_menu(user):

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_buy'), callback_data='trade_menu-new_buy'),
             InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-new_sale'), callback_data='trade_menu-new_sale')],
            [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-orders'), callback_data='trade_menu-orders')],
            [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-my_orders'), callback_data='trade_menu-my_orders'),
             InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-my_trades'), callback_data='trade_menu-my_trades')],
            [InlineKeyboardButton(user.get_text(name='order-kb-trade_menu-notifications'), callback_data='trade_menu-notifications')]

        ]
    )

    return kb


def trade_currency(user):

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('BIP', callback_data='trade_currency-BIP'),
             InlineKeyboardButton('BTC', callback_data='trade_currency-BTC'),
             InlineKeyboardButton('USDT', callback_data='trade_currency-USDT'),
             InlineKeyboardButton('ETH', callback_data='trade_currency-ETH')],
            [InlineKeyboardButton('USD', callback_data='trade_currency-USD'),
             InlineKeyboardButton('RUB', callback_data='trade_currency-RUB'),
             InlineKeyboardButton('UAH', callback_data='trade_currency-UAH')],
            [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='trade_currency-back')]

        ])

    return kb


def payment_currency(trade_currency, user):

    if trade_currency == 'BIP':
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')],
                [InlineKeyboardButton('BTC', callback_data='order_payment_currency-BTC'),
                 InlineKeyboardButton('USDT', callback_data='order_payment_currency-USDT'),
                 InlineKeyboardButton('ETH', callback_data='order_payment_currency-ETH')],
                [InlineKeyboardButton('USD', callback_data='order_payment_currency-USD'),
                 InlineKeyboardButton('RUB', callback_data='order_payment_currency-RUB'),
                 InlineKeyboardButton('UAH', callback_data='order_payment_currency-UAH')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')]

            ])

    elif trade_currency == 'BTC':
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')],
                [InlineKeyboardButton('BIP', callback_data='order_payment_currency-BIP'),
                 InlineKeyboardButton('USDT', callback_data='order_payment_currency-USDT'),
                 InlineKeyboardButton('ETH', callback_data='order_payment_currency-ETH')],
                [InlineKeyboardButton('USD', callback_data='order_payment_currency-USD'),
                 InlineKeyboardButton('RUB', callback_data='order_payment_currency-RUB'),
                 InlineKeyboardButton('UAH', callback_data='order_payment_currency-UAH')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')]

            ])

    elif trade_currency == 'USDT':
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')],
                [InlineKeyboardButton('BIP', callback_data='order_payment_currency-BIP'),
                 InlineKeyboardButton('BTC', callback_data='order_payment_currency-BTC'),
                 InlineKeyboardButton('ETH', callback_data='order_payment_currency-ETH')],
                [InlineKeyboardButton('USD', callback_data='order_payment_currency-USD'),
                 InlineKeyboardButton('RUB', callback_data='order_payment_currency-RUB'),
                 InlineKeyboardButton('UAH', callback_data='order_payment_currency-UAH')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')]

            ])

    elif trade_currency == 'ETH':
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')],
                [InlineKeyboardButton('BIP', callback_data='order_payment_currency-BIP'),
                 InlineKeyboardButton('BTC', callback_data='order_payment_currency-BTC'),
                 InlineKeyboardButton('USDT', callback_data='order_payment_currency-USDT')],
                [InlineKeyboardButton('USD', callback_data='order_payment_currency-USD'),
                 InlineKeyboardButton('RUB', callback_data='order_payment_currency-RUB'),
                 InlineKeyboardButton('UAH', callback_data='order_payment_currency-UAH')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')]

            ])

    elif trade_currency == 'USD':
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')],
                [InlineKeyboardButton('BIP', callback_data='order_payment_currency-BIP'),
                 InlineKeyboardButton('BTC', callback_data='order_payment_currency-BTC'),
                 InlineKeyboardButton('USDT', callback_data='order_payment_currency-USDT'),
                 [InlineKeyboardButton('ETH', callback_data='order_payment_currency-ETH')]],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')]

            ])

    elif trade_currency == 'RUB':
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')],
                [InlineKeyboardButton('BIP', callback_data='order_payment_currency-BIP'),
                 InlineKeyboardButton('BTC', callback_data='order_payment_currency-BTC'),
                 InlineKeyboardButton('USDT', callback_data='order_payment_currency-USDT'),
                 InlineKeyboardButton('ETH', callback_data='order_payment_currency-ETH')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')]

            ])

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-accept'), callback_data='order_payment_currency-accept')],
                [InlineKeyboardButton('BIP', callback_data='order_payment_currency-BIP'),
                 InlineKeyboardButton('BTC', callback_data='order_payment_currency-BTC'),
                 InlineKeyboardButton('USDT', callback_data='order_payment_currency-USDT'),
                 InlineKeyboardButton('ETH', callback_data='order_payment_currency-ETH')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data='order_payment_currency-back')]

            ])

    return kb


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


def order_list(type_operation, offset):
    # TODO Решить здесь задачку

    if type_operation == 'buy':
        order_by = 'currency_rate'
    else:
        order_by = '-currency_rate'

    sort_orders = Order.objects.filter(status='open', type_operation=type_operation).order_by(order_by)[offset:offset+7]
    print(sort_orders)

    all_orders = Order.objects.filter(status='open')
    kb = []
    # for order in sort_orders:
    #     kb.append([InlineKeyboardButton()])


    # # icon = {1: 'Ⓜ️', 2: '🏵',
    # #         3: '💸', 4: '',
    # #         5: '', 6: '',
    # #         7: ''}
    #
    # buttons = {'buy': {'name': 'Смотреть список на продажу',
    #                    'cb': 'sale'},
    #            'sale': {'name': 'Смотреть список на покупку',
    #                     'cb': 'buy'}}
    #
    # kb_list = []
    # kb_list.append([InlineKeyboardButton(buttons[type_operation]['name'],
    #                                      callback_data=f'annlist t {buttons[type_operation]["cb"]} {offset}')])
    # for an in announcs:
    #     currency_trade = an.trade_currency
    #     amount = an.amount
    #     # pay_curr = an.payment_currency
    #     pay_curr = PaymentCurrency.select().where(PaymentCurrency.announcement_id == an.id)
    #     curs = ''
    #     for curr in pay_curr:
    #         curs += f'{curr.payment_currency} '
    #     name = f'{currency_trade} : {to_bip(amount)}'
    #
    #     kb_list.append([InlineKeyboardButton(name, callback_data=f'open announc {an.id}')])
    #
    # if len(all_announc) < 7:
    #     kb_list.append([InlineKeyboardButton('🔙 Назад', callback_data=f'annlist back {type_operation} {offset}')])
    #
    # else:
    #     numb_list_l = f'/{math.ceil(len(all_announc) / 7)}'
    #     numb_list_r = f'/{math.ceil(len(all_announc) / 7)}'
    #     kb_list.append(
    #         [InlineKeyboardButton(f'⇐ {numb_list_l}', callback_data=f'annlist left {type_operation} {offset}'),
    #          InlineKeyboardButton('🔙 Назад', callback_data=f'annlist back {type_operation} {offset}'),
    #          InlineKeyboardButton(f'{numb_list_r} ⇒', callback_data=f'annlist right {type_operation} {offset}')])
    #
    # kb = InlineKeyboardMarkup(kb_list)
    #
    # return kb


def order_for_owner(order, location):
    user = order.user
    marker_status_button = {'open': user.get_text(name='order-kb-off_order'),
                            'close': user.get_text(name='order-kb-on_order')}

    if location == 1:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='order-kb-share'), callback_data=f'order_info-share')],
                [InlineKeyboardButton(f'{marker_status_button[order.status]}',callback_data=f'order_info-switch')],
                [InlineKeyboardButton(user.get_text(name='kb-close'), callback_data=f'order_info-close'),
                 InlineKeyboardButton(user.get_text(name='kb-delete'), callback_data=f'order_info-delete')]

            ]
        )

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='order-kb-share'), callback_data=f'order_info-share')],
                [InlineKeyboardButton(f'{marker_status_button[order.status]}', callback_data=f'order_info-switch')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'order_info-back'),
                 InlineKeyboardButton(user.get_text(name='kb-delete'), callback_data=f'order_info-delete')]

            ]
        )

    return kb