from pyrogram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


choice_language = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇬🇧 English', callback_data=f'choicelanguage-en')],
                [InlineKeyboardButton('🇷🇺 Русский', callback_data=f'choicelanguage-ru')]
            ]
        )


def choice_currency(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='user-kb-usd'), callback_data=f'choicecurrency-USD')],
                [InlineKeyboardButton(user.get_text(name='user-kb-uah'), callback_data=f'choicecurrency-UAH')],
                [InlineKeyboardButton(user.get_text(name='user-kb-rub'), callback_data=f'choicecurrency-RUB')]
            ]
        )

    return kb


def start_menu(user):
    kb = ReplyKeyboardMarkup(
        [
            [user.get_text(name='user-kb-wallet'), user.get_text(name='user-kb-trade')],
            [user.get_text(name='user-kb-settings')]
        ],
        resize_keyboard=True,
    )

    return kb


def hide(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='user-hide'), callback_data=f'hide')]
            ]
        )

    return kb


def wallet_menu(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='wallet-kb-deposite'), callback_data=f'wallet_menu-deposite'),
             InlineKeyboardButton(user.get_text(name='wallet-kb-withdraw'), callback_data=f'wallet_menu-withdraw')],
            [InlineKeyboardButton(user.get_text(name='wallet-kb-purse'), callback_data=f'wallet_menu-purse')],
            [InlineKeyboardButton(user.get_text(name='wallet-kb-affiliate_program'), callback_data=f'wallet_menu-afiliate_program')],
            [InlineKeyboardButton(user.get_text(name='wallet-kb-premium'), callback_data=f'wallet_menu-premium')]
        ]
    )

    return kb


def purse_menu(user):
    requisites = user.requisites.all()

    kb = [[InlineKeyboardButton('🔙 Назад', callback_data='purse-back')],
          [InlineKeyboardButton('Добавить реквизиты', callback_data='purse-add')]]

    for r in requisites:
        name = f'[{r.name}]' if r.name else ''
        kb.append([InlineKeyboardButton(f'{name}[{r.currency}] {r.address}', callback_data=f'purse-req-{r.id}')])

    return InlineKeyboardMarkup(kb)


choice_currency_for_wallet = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('BIP', callback_data='chcurr-BIP'),
         InlineKeyboardButton('BTC', callback_data='chcurr-BTC'),
         InlineKeyboardButton('USDT', callback_data='chcurr-USDT'),
         InlineKeyboardButton('ETH', callback_data='chcurr-ETH')],
        [InlineKeyboardButton('USD', callback_data='chcurr-USD'),
         InlineKeyboardButton('RUB', callback_data='chcurr-RUB'),
         InlineKeyboardButton('UAH', callback_data='chcurr-UAH')],
        [InlineKeyboardButton('🔙', callback_data='chcurr-back')]

    ])


def requisite(user, requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🔙 Назад', callback_data=f'wallet_menu-purse')],

                [InlineKeyboardButton(
                    user.get_text(name='purse-kb-edit_address'),
                    callback_data=f'requisite-address-{requisite_id}')],

                [InlineKeyboardButton(
                    user.get_text(name='purse-kb-edit_add_name'),
                    callback_data=f'requisite-name-{requisite_id}')],

                [InlineKeyboardButton(
                    user.get_text(name='purse-kb-delete'),
                    callback_data=f'requisite-delete-{requisite_id}')]
            ]
        )

    return kb


def skip_add_requisites_name(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-skip'), callback_data=f'addreq-skip')],
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'addreq-cancel')]
            ]
        )

    return kb


def cancel_add_requisites(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'addreq-cancel')]
            ]
        )

    return kb


def cancel_edit_requisite(user, requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'requisite-cancel-{requisite_id}')]
            ]
        )

    return kb


def edit_requisite_name(user, requisite_id):
    requisite = user.requisites.get(id=requisite_id)

    if requisite.name:
        kb = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(user.get_text(name='purse-kb-delete'), callback_data=f'requisite-delname-{requisite_id}')],
                    [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'requisite-cancel-{requisite_id}')]
                ]
            )

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'requisite-cancel-{requisite_id}')]
            ]
        )

    return kb


def hide_notification(user):
    return InlineKeyboardMarkup([[InlineKeyboardButton(user.get_text(name='kb-hide'), callback_data='hide')]])