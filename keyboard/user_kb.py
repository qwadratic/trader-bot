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
                [InlineKeyboardButton('Портмоне', callback_data=f'portmone')],
                [InlineKeyboardButton('Партнёрская программа', callback_data=f'q')],
                [InlineKeyboardButton('Премиум подписка', callback_data=f'q')]
            ]
        )


hide_notification = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f'« cкрыть »', callback_data='hide notify')]
        ])