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
        [InlineKeyboardButton('BIP', callback_data='tcurr BIP'),
         InlineKeyboardButton('BTC', callback_data='tcurr BTC'),
         InlineKeyboardButton('USDT', callback_data='tcurr USDT'),
         InlineKeyboardButton('ETH', callback_data='tcurr ETH')],
        [InlineKeyboardButton('USD', callback_data='tcurr USD'),
         InlineKeyboardButton('RUB', callback_data='tcurr RUB'),
         InlineKeyboardButton('UAH', callback_data='tcurr UAH')],
        [InlineKeyboardButton('🔙 Назад', callback_data='tcurr back')]

    ])


def payment_currency(trade_currency):
    if trade_currency == 1:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BTC', callback_data='paycurr BTC'),
                 InlineKeyboardButton('USDT', callback_data='paycurr USDT'),
                 InlineKeyboardButton('ETH', callback_data='paycurr ETH')],
                [InlineKeyboardButton('USD', callback_data='paycurr USD'),
                 InlineKeyboardButton('RUB', callback_data='paycurr RUB'),
                 InlineKeyboardButton('UAH', callback_data='paycurr UAH')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 2:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr BIP'),
                 InlineKeyboardButton('USDT', callback_data='paycurr USDT'),
                 InlineKeyboardButton('ETH', callback_data='paycurr ETH')],
                [InlineKeyboardButton('USD', callback_data='paycurr USD'),
                 InlineKeyboardButton('RUB', callback_data='paycurr RUB'),
                 InlineKeyboardButton('UAH', callback_data='paycurr UAH')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 3:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr BIP'),
                 InlineKeyboardButton('BTC', callback_data='paycurr BTC'),
                 InlineKeyboardButton('ETH', callback_data='paycurr ETH')],
                [InlineKeyboardButton('USD', callback_data='paycurr USD'),
                 InlineKeyboardButton('RUB', callback_data='paycurr RUB'),
                 InlineKeyboardButton('UAH', callback_data='paycurr UAH')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 4:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr BIP'),
                 InlineKeyboardButton('BTC', callback_data='paycurr BTC'),
                 InlineKeyboardButton('USDT', callback_data='paycurr USDT')],
                [InlineKeyboardButton('USD', callback_data='paycurr USD'),
                 InlineKeyboardButton('RUB', callback_data='paycurr RUB'),
                 InlineKeyboardButton('UAH', callback_data='paycurr UAH')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 5:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr BIP'),
                 InlineKeyboardButton('BTC', callback_data='paycurr BTC'),
                 InlineKeyboardButton('USDT', callback_data='paycurr USDT'),
                 [InlineKeyboardButton('ETH', callback_data='paycurr ETH')],
                 InlineKeyboardButton('RUB', callback_data='paycurr RUB'),
                 InlineKeyboardButton('UAH', callback_data='paycurr UAH')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    elif trade_currency == 6:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr BIP'),
                 InlineKeyboardButton('BTC', callback_data='paycurr BTC'),
                 InlineKeyboardButton('USDT', callback_data='paycurr USDT'),
                 InlineKeyboardButton('ETH', callback_data='paycurr ETH')],
                [InlineKeyboardButton('USD', callback_data='paycurr USD'),
                 InlineKeyboardButton('UAH', callback_data='paycurr UAH')],
                [InlineKeyboardButton('🔙 Назад', callback_data='paycurr back')]

            ])

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅ Подтвердить', callback_data='paycurr accept')],
                [InlineKeyboardButton('BIP', callback_data='paycurr BIP'),
                 InlineKeyboardButton('BTC', callback_data='paycurr BTC'),
                 InlineKeyboardButton('USDT', callback_data='paycurr USDT'),
                 InlineKeyboardButton('ETH', callback_data='paycurr ETH')],
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