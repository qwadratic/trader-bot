from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('📝 Новое на покупку', callback_data='tmenu new buy'),
         InlineKeyboardButton('📝 Новое на продажу', callback_data='tmenu new sale')],
        [InlineKeyboardButton('📜 Объявления', callback_data='tmenu announc')],
        [InlineKeyboardButton('📋 Мои объявления', callback_data='tmenu my announc'),
         InlineKeyboardButton('📇 Мои сделки', callback_data='tmenu my trade')],
        [InlineKeyboardButton('📢 Уведомления', callback_data='tmenu notice')]

    ]
)

# menu = InlineKeyboardMarkup(
#     [
#         [InlineKeyboardButton('📈 Купить', callback_data='tmenu buy'),
#          InlineKeyboardButton('📉 Продать', callback_data='tmenu sale')],
#         [InlineKeyboardButton('📋 Мои объявления', callback_data='tmenu my announc')],
#         [InlineKeyboardButton('📇 Мои сделки', callback_data='tmenu my trade')],
#         [InlineKeyboardButton('📢 Уведомления', callback_data='tmenu notice')]
#
#     ]
# )
# buy_menu = InlineKeyboardMarkup(
#     [
#         [InlineKeyboardButton('📝 Новое на покупку', callback_data='buy new')],
#         [InlineKeyboardButton('📜 Список объявлений', callback_data='buy list')],
#         [InlineKeyboardButton('🔙 Назад', callback_data='buy back')]
#
#     ]
# )

trade_currency = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('BIP', callback_data='tcurr 1'),
         InlineKeyboardButton('BTC', callback_data='tcurr 2'),
         InlineKeyboardButton('USDT', callback_data='tcurr 3'),
         InlineKeyboardButton('ETH', callback_data='tcurr 4')],
        [InlineKeyboardButton('USD', callback_data='tcurr 5'),
         InlineKeyboardButton('RUB', callback_data='tcurr 6'),
         InlineKeyboardButton('UAH', callback_data='tcurr 7')],
        [InlineKeyboardButton('🔙 Назад', callback_data='tcurr 0')]

    ])


def payment_currency(trade_currency):
    if trade_currency == 1:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BTC', callback_data='paycurr 2'),
                 InlineKeyboardButton('USDT', callback_data='paycurr 3'),
                 InlineKeyboardButton('ETH', callback_data='paycurr 4')],
                [InlineKeyboardButton('USD', callback_data='paycurr 5'),
                 InlineKeyboardButton('RUB', callback_data='paycurr 6'),
                 InlineKeyboardButton('UAH', callback_data='paycurr 7')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 2:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr 1'),
                 InlineKeyboardButton('USDT', callback_data='paycurr 3'),
                 InlineKeyboardButton('ETH', callback_data='paycurr 4')],
                [InlineKeyboardButton('USD', callback_data='paycurr 5'),
                 InlineKeyboardButton('RUB', callback_data='paycurr 6'),
                 InlineKeyboardButton('UAH', callback_data='paycurr 7')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 3:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr 1'),
                 InlineKeyboardButton('BTC', callback_data='paycurr 2'),
                 InlineKeyboardButton('ETH', callback_data='paycurr 4')],
                [InlineKeyboardButton('USD', callback_data='paycurr 5'),
                 InlineKeyboardButton('RUB', callback_data='paycurr 6'),
                 InlineKeyboardButton('UAH', callback_data='paycurr 7')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 4:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr 1'),
                 InlineKeyboardButton('BTC', callback_data='paycurr 2'),
                 InlineKeyboardButton('USDT', callback_data='paycurr 3')],
                [InlineKeyboardButton('USD', callback_data='paycurr 5'),
                 InlineKeyboardButton('RUB', callback_data='paycurr 6'),
                 InlineKeyboardButton('UAH', callback_data='paycurr 7')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 5:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr 1'),
                 InlineKeyboardButton('BTC', callback_data='paycurr 2'),
                 InlineKeyboardButton('USDT', callback_data='paycurr 3'),
                 [InlineKeyboardButton('ETH', callback_data='paycurr 4')],
                 InlineKeyboardButton('RUB', callback_data='paycurr 6'),
                 InlineKeyboardButton('UAH', callback_data='paycurr 7')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 6:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr 1'),
                 InlineKeyboardButton('BTC', callback_data='paycurr 2'),
                 InlineKeyboardButton('USDT', callback_data='paycurr 3'),
                 InlineKeyboardButton('ETH', callback_data='paycurr 4')],
                [InlineKeyboardButton('USD', callback_data='paycurr 5'),
                 InlineKeyboardButton('UAH', callback_data='paycurr 7')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr 1'),
                 InlineKeyboardButton('BTC', callback_data='paycurr 2'),
                 InlineKeyboardButton('USDT', callback_data='paycurr 3'),
                 InlineKeyboardButton('ETH', callback_data='paycurr 4')],
                [InlineKeyboardButton('USD', callback_data='paycurr 5'),
                 InlineKeyboardButton('RUB', callback_data='paycurr 6')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    return kb


cancel_ench_rate = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('❌ Отменить', callback_data='cancel')]

    ])

sale_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('📝 Новое на продажу', callback_data='sale new')],
        [InlineKeyboardButton('📜 Список объявлений', callback_data='sale list')],
        [InlineKeyboardButton('🔙 Назад', callback_data='sale back')]

    ]
)


def deal_for_author(announcement, loc):
    marker_status_button = {1: '🌕 Выключить',
                            2: '🌑 Включить'}

    loc_d = {1: {'name': '✖️ Закрыть',
                 'cb': 'close'},
             2: {'name': '🔙 Назад', 'cb': 'backk'}}

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('📣 Поделиться', callback_data=f'deal share {announcement.id}')],
            [InlineKeyboardButton(f'{marker_status_button[announcement.status]}', callback_data=f'dealauth statu {announcement.id}')],
            [InlineKeyboardButton(loc_d[loc]["name"], callback_data=f'dealauth {loc_d[loc]["cb"]} {announcement.id}'),
             InlineKeyboardButton(f'❌ Удалить', callback_data=f'dealauth delet {announcement.id}')]

        ]
    )

    return kb


def deal_for_user(announcement_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('📣 Поделиться', callback_data=f'deal share {announcement_id}')],
            [InlineKeyboardButton('🔙 Назад', callback_data='deal back'),
             InlineKeyboardButton('🛎 Начать сделку', callback_data=f'deal start {announcement_id}')]

        ]
    )

    return kb


def start_deal(trade_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('❌ Отклонить', callback_data='start deal 2'),
             InlineKeyboardButton('🛎 Начать сделку', callback_data=f'start deal 1 {trade_id}')]

        ]
    )

    return kb


def confirm_paymend_from_buyer(trade_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('❌ Отклонить', callback_data='sss'),
             InlineKeyboardButton('✅ Подтверждаю', callback_data=f'conftrade {trade_id}')]

        ]
    )

    return kb