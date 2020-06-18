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
