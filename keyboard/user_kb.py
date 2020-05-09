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
                ['💸 Обмен'],
                ['📁 Профиль', '💳 Кошелёк'],
                ['🤝 Партнёрская программа'],
                ['⚙️ Настройки']
            ],
            resize_keyboard=True,
        )
