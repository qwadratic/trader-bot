from pyrogram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


choice_lang_kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇬🇧 English', callback_data=f'lang 1')],
                [InlineKeyboardButton('🇷🇺 Русский', callback_data=f'lang 2')]
            ]
        )


choice_currency_kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇺🇸 Американский доллар (USD)', callback_data=f'val 1')],
                [InlineKeyboardButton('🇺🇦 Украинская гривна (UAH)', callback_data=f'val 2')],
                [InlineKeyboardButton('🇷🇺 Российский рубль (RUB)', callback_data=f'val 3')]
            ]
        )


menu_kb = ReplyKeyboardMarkup(
            [
                ['💸 Обмен'],
                ['📁 Профиль', '💳 Кошелёк'],
                ['🤝 Партнёрская программа'],
                ['⚙️ Настройки']
            ],
            resize_keyboard=True,
        )
