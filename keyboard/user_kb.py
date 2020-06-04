from pyrogram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


choice_lang = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇬🇧 English', callback_data=f'lang en')],
                [InlineKeyboardButton('🇷🇺 Русский', callback_data=f'lang ru')]
            ]
        )


choice_currency = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇺🇸 Американский доллар (USD)', callback_data=f'currency USD')],
                [InlineKeyboardButton('🇺🇦 Украинская гривна (UAH)', callback_data=f'currency UAH')],
                [InlineKeyboardButton('🇷🇺 Российский рубль (RUB)', callback_data=f'currency RUB')]
            ]
        )


menu = ReplyKeyboardMarkup(
            [
                ['💼 Кошелёк', '💸 Обмен'],
                ['⚙️ Настройки']
            ],
            resize_keyboard=True,
        )


wallet_menu = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Пополнить', callback_data=f'q'),
                 InlineKeyboardButton('Вывести', callback_data=f'q')],
                [InlineKeyboardButton('Портмоне', callback_data=f'wm-portmone')],
                [InlineKeyboardButton('Партнёрская программа', callback_data=f'q')],
                [InlineKeyboardButton('Премиум подписка', callback_data=f'q')]
            ]
        )


hide_notification = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f'« cкрыть »', callback_data='hide notify')]
        ])


def purse(user):
    requisites = user.purse

    kb = [[InlineKeyboardButton('Назад', callback_data='purse-back')], [InlineKeyboardButton('Добавить реквизиты', callback_data='purse-add')]]

    for r in requisites:
        name = f'[{r.name}]' if r.name else ''
        kb.append([InlineKeyboardButton(f'{name}[{r.currency}] {r.address}', callback_data=f'purse-req-{r.id}')])

    return InlineKeyboardMarkup(kb)


def requisite(requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Назад', callback_data=f'wm-portmone')],
                [InlineKeyboardButton('Редактировать адрес', callback_data=f'editrequisite-address-{requisite_id}')],
                [InlineKeyboardButton('Изменить/добавить название', callback_data=f'editrequisite-name-{requisite_id}')],
                [InlineKeyboardButton('Удалить', callback_data=f'editrequisite-delete-{requisite_id}')]
            ]
        )

    return kb


choice_currency_for_wallet = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('BIP', callback_data='chcurr-BIP'),
         InlineKeyboardButton('BTC', callback_data='chcurr-BTC'),
         InlineKeyboardButton('USDT', callback_data='chcurr-USDT'),
         InlineKeyboardButton('ETH', callback_data='chcurr-ETH')],
        [InlineKeyboardButton('USD', callback_data='chcurr-USD'),
         InlineKeyboardButton('RUB', callback_data='chcurr-RUB'),
         InlineKeyboardButton('UAH', callback_data='chcurr-UAH')],
        [InlineKeyboardButton('🔙 Назад', callback_data='chcurr')]

    ])


cancel_add_requisites = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('« Отменить »', callback_data=f'cancaddreq')]
            ]
        )

skip_add_requisites_name = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Пропустить', callback_data=f'addreq-skip')],
                [InlineKeyboardButton('« Отменить »', callback_data=f'addreq-cancel')]
            ]
        )


def cancel_edit_requisite(requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('« Отменить »', callback_data=f'editrequisite-cancel-{requisite_id}')]
            ]
        )

    return kb


def edit_requisite_name(requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Удалить название', callback_data=f'editrequisite-delname-{requisite_id}')],
                [InlineKeyboardButton('« Отменить »', callback_data=f'editrequisite-cancel-{requisite_id}')]
            ]
        )

    return kb