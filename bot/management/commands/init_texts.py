from django.core.management.base import BaseCommand

from bot.models import Text


class Command(BaseCommand):

    def handle(self, **options):
        Text.objects.all().delete()
        # txts = [{'name': 'user-start', 'text': 'Добро пожаловать!', 'text_ru': 'Добро пожаловать!'},
        #         {'name': 'user-start_ref', 'text': 'Тебя пригласил пользователь {name}',
        #          'text_ru': 'Тебя пригласил пользователь {name}'}, {'name': 'user-end_registration',
        #                                                             'text': 'Поздравляю!\r\nРегистрация окончена, язык и валюту можно изменить в настройках\\n\r\n*какой-то еще текст*',
        #                                                             'text_ru': 'Поздравляю!\r\nРегистрация окончена, язык и валюту можно изменить в настройках\\n\r\n*какой-то еще текст*'},
        #         {'name': 'user-kb-trade', 'text': '💸 Обмен', 'text_ru': '💸 Обмен'},
        #         {'name': 'user-kb-wallet', 'text': '💼 Кошелёк', 'text_ru': '💼 Кошелёк'},
        #         {'name': 'user-kb-settings', 'text': '⚙️ Настройки', 'text_ru': '⚙️ Настройки'},
        #         {'name': 'user-hide', 'text': '« скрыть »', 'text_ru': '« скрыть »'},
        #         {'name': 'user-kb-usd', 'text': '🇺🇸 Американский доллар (USD)',
        #          'text_ru': '🇺🇸 Американский доллар (USD)'},
        #         {'name': 'user-kb-uah', 'text': '🇺🇦 Украинская гривна (UAH)',
        #          'text_ru': '🇺🇦 Украинская гривна (UAH)'},
        #         {'name': 'user-kb-rub', 'text': '🇷🇺 Российский рубль (RUB)',
        #          'text_ru': '🇷🇺 Российский рубль (RUB)'},
        #         {'name': 'order-kb-trade_menu-new_buy', 'text': '📝 Новое на покупку',
        #          'text_ru': '📝 Новое на покупку'},
        #         {'name': 'order-kb-trade_menu-new_sale', 'text': '📝 Новое на продажу',
        #          'text_ru': '📝 Новое на продажу'},
        #         {'name': 'order-kb-trade_menu-orders', 'text': '📜 Объявления', 'text_ru': '📜 Объявления'},
        #         {'name': 'order-kb-trade_menu-my_orders', 'text': '📋 Мои объявления', 'text_ru': '📋 Мои объявления'},
        #         {'name': 'order-kb-trade_menu-my_trades', 'text': '📇 Мои сделки', 'text_ru': '📇 Мои сделки'},
        #         {'name': 'order-kb-trade_menu-notifications', 'text': '📢 Уведомления', 'text_ru': '📢 Уведомления'},
        #         {'name': 'kb-accept', 'text': '✅ Подтвердить', 'text_ru': '✅ Подтвердить'},
        #         {'name': 'kb-back', 'text': '🔙 Назад', 'text_ru': '🔙 Назад'},
        #         {'name': 'order-orders_menu', 'text': 'Меню объявлений', 'text_ru': 'Меню объявлений'},
        #         {'name': 'user-trade_menu',
        #          'text': '💸 **Обмен**\r\nЗдесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.',
        #          'text_ru': '💸 **Обмен**\r\nЗдесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.'},
        #         {'name': 'order-your_choice', 'text': 'Ваш выбор:', 'text_ru': 'Ваш выбор:'},
        #         {'name': 'order-error_no_selected_payment_instrument',
        #          'text': 'Выберите хотя бы один платёжный инструмент',
        #          'text_ru': 'Выберите хотя бы один платёжный инструмент'},
        #         {'name': 'order-kb-use_internal_wallet', 'text': '✅ Использовать внутренний кошелёк',
        #          'text_ru': '✅ Использовать внутренний кошелёк'},
        #         {'name': 'order-type_operation_translate_buy_1', 'text': 'купить', 'text_ru': 'купить'},
        #         {'name': 'order-type_operation_translate_buy_2', 'text': 'купили', 'text_ru': 'купили'},
        #         {'name': 'order-kb-open_purse', 'text': 'Использовать реквизиты из портмоне',
        #          'text_ru': 'Использовать реквизиты из портмоне'},
        #         {'name': 'order-kb-add_new_requisite', 'text': 'Добавить новые реквизиты',
        #          'text_ru': 'Добавить новые реквизиты'},
        #         {'name': 'order-select_requisite_from_purse', 'text': 'Ваши реквизиты {currency}',
        #          'text_ru': 'Ваши реквизиты {currency}'},
        #         {'name': 'order-kb-back_to_selection_requisite_menu', 'text': '🔙 Назад', 'text_ru': '🔙 Назад'},
        #         {'name': 'purse-enter_address',
        #          'text': 'Введите адрес {currency} кошелька на который будут поступать средства от сделок.',
        #          'text_ru': 'Введите адрес {currency} кошелька на который будут поступать средства от сделок.'},
        #         {'name': 'order-select_payment_currency',
        #          'text': 'Какую валюту вы хотите получить за {currency}?\r\n\r\nВы можете выбрать одну или несколько и нажмите "Подтвердить"',
        #          'text_ru': 'Какую валюту вы хотите получить за {currency}?\r\n\r\nВы можете выбрать одну или несколько и нажмите "Подтвердить"'},
        #         {'name': 'bot-you_choosed', 'text': 'Вы выбрали {foo}', 'text_ru': 'Вы выбрали {foo}'},
        #         {'name': 'bot-you_entered', 'text': 'Вы ввели {count}', 'text_ru': 'Вы ввели {count}'},
        #         {'name': 'bot-type_error', 'text': 'Ошибка! Используйте только цифры',
        #          'text_ru': 'Ошибка! Используйте только цифры'},
        #         {'name': 'order-type_operation_translate_sale_1', 'text': 'продать', 'text_ru': 'продать'},
        #         {'name': 'order-enter_currency_rate',
        #          'text': 'Введите желаемую стоимость {trade_currency} в USD\r\n\r\nСредняя цена за {trade_currency}: {price} USD',
        #          'text_ru': 'Введите желаемую стоимость {trade_currency} в USD\r\n\r\nСредняя цена за {trade_currency}: {price} USD'},
        #         {'name': 'order-type_operation_translate_sale_2', 'text': 'продали', 'text_ru': 'продали'},
        #         {'name': 'wallet-kb-deposite', 'text': 'Пополнить', 'text_ru': 'Пополнить'},
        #         {'name': 'wallet-kb-withdraw', 'text': 'Вывести', 'text_ru': 'Вывести'},
        #         {'name': 'wallet-kb-purse', 'text': 'Портмоне', 'text_ru': 'Портмоне'},
        #         {'name': 'wallet-kb-affiliate_program', 'text': 'Партнёрская программа',
        #          'text_ru': 'Партнёрская программа'},
        #         {'name': 'wallet-kb-premium', 'text': 'Премиум подписка', 'text_ru': 'Премиум подписка'},
        #         {'name': 'wallet-wallet_info', 'text': '💼 Кошелёк\\n\\n\r\n\r\nБаланс:',
        #          'text_ru': '💼 Кошелёк\\n\\n\r\n\r\nБаланс:'},
        #         {'name': 'purse-kb-delete', 'text': 'Удалить', 'text_ru': 'Удалить'},
        #         {'name': 'purse-kb-edit_add_name', 'text': 'Редактировать/Добавить имя',
        #          'text_ru': 'Редактировать/Добавить имя'},
        #         {'name': 'purse-kb-edit_address', 'text': 'Редактировать адрес', 'text_ru': 'Редактировать адрес'},
        #         {'name': 'purse-requisite_info_with_name', 'text': '{name}\r\n{address}\r\n{currency}',
        #          'text_ru': '{name}\r\n{address}\r\n{currency}'},
        #         {'name': 'order-kb-share', 'text': '📣 Поделиться', 'text_ru': '📣 Поделиться'},
        #         {'name': 'purse-select_currency', 'text': 'Выберите валюту для кошелька',
        #          'text_ru': 'Выберите валюту для кошелька'},
        #         {'name': 'purse-purse_menu', 'text': '💼 Портмоне\r\n\r\nЗдесь вы можете хранить ваши реквизиты',
        #          'text_ru': '💼 Портмоне\r\n\r\nЗдесь вы можете хранить ваши реквизиты'},
        #         {'name': 'purse-enter_requisite_name', 'text': 'Введите имя реквизиты',
        #          'text_ru': 'Введите имя реквизиты'},
        #         {'name': 'bot-invalid_address', 'text': 'Некорректный адрес', 'text_ru': 'Некорректный адрес'},
        #         {'name': 'purse-requisite_info', 'text': '```{address}```\r\nВалюта: {currency}',
        #          'text_ru': '```{address}```\r\nВалюта: {currency}'},
        #         {'name': 'order-kb-off_order', 'text': '🌕 Выключить', 'text_ru': '🌕 Выключить'},
        #         {'name': 'order-kb-on_order', 'text': '🌑 Включить', 'text_ru': '🌑 Включить'},
        #         {'name': 'bot-balance_replinished', 'text': '💸 Ваш баланс пополнен на:',
        #          'text_ru': '💸 Ваш баланс пополнен на:'},
        #         {'name': 'kb-delete', 'text': '❌ Удалить', 'text_ru': '❌ Удалить'},
        #         {'name': 'kb-cancel', 'text': '« Отменить »', 'text_ru': '« Отменить »'},
        #         {'name': 'kb-skip', 'text': 'Пропустить', 'text_ru': 'Пропустить'},
        #         {'name': 'kb-close', 'text': '« закрыть »', 'text_ru': '« закрыть »'},
        #         {'name': 'order-select_trade_currency', 'text': 'Что хотите {type_operation}?',
        #          'text_ru': 'Что хотите {type_operation}?'}, {'name': 'order-select_requisite_for_order',
        #                                                       'text': 'Выберете кошелёк на который вы получите  {currency}',
        #                                                       'text_ru': 'Выберете кошелёк на который вы получите  {currency}'},
        #         {'name': 'kb-hide', 'text': '« скрыть »', 'text_ru': '« скрыть »'},
        #         {'name': 'user-settings', 'text': '⚙️ Настройки', 'text_ru': '⚙️ Настройки'},
        #         {'name': 'user-kb-language', 'text': '🌎 Язык', 'text_ru': '🌎 Язык'},
        #         {'name': 'user-kb-currency', 'text': '💶 Валюта', 'text_ru': '💶 Валюта'},
        #         {'name': 'user-kb-service_info', 'text': '🌐 О сервисе', 'text_ru': '🌐 О сервисе'},
        #         {'name': 'user-settings-select_currency', 'text': '💶 Валюта\r\n\r\nВыберите базовую валюту',
        #          'text_ru': '💶 Валюта\r\n\r\nВыберите базовую валюту'},
        #         {'name': 'user-settings-select_language', 'text': '🌍 Язык\r\n\r\nПожалуйста, выберите язык',
        #          'text_ru': '🌍 Язык\r\n\r\nПожалуйста, выберите язык'},
        #         {'name': 'user-settings-selected_language', 'text': 'Вы выбрали {language} язык',
        #          'text_ru': 'Вы выбрали {language} язык'},
        #         {'name': 'user-settings-selected_currency', 'text': 'Вы выбрали {currency}',
        #          'text_ru': 'Вы выбрали {currency}'},
        #         {'name': 'order-my_orders', 'text': 'Ваши объявления', 'text_ru': 'Ваши объявления'},
        #         {'name': 'order-kb-look_at_the_sale', 'text': 'Смотреть на продажу', 'text_ru': 'Смотреть на продажу'},
        #         {'name': 'order-kb-look_at_the_buy', 'text': 'Смотреть на покупку', 'text_ru': 'Смотреть на покупку'},
        #         {'name': 'user-registration-select_currency', 'text': 'Выбери базовую валюту',
        #          'text_ru': 'Выбери базовую валюту'},
        #         {'name': 'order-order_info',
        #          'text': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**:\r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n1 {trade_currency} – {rate_1} {payment_currency}\r\n1 {payment_currency} – {rate_2} {trade_currency}\r\n\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: {price_order} {payment_currency}',
        #          'text_ru': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**:\r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n1 {trade_currency} – {rate_1} {payment_currency}\r\n1 {payment_currency} – {rate_2} {trade_currency}\r\n\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: {price_order} {payment_currency}'},
        #         {'name': 'order-kb-start_trade', 'text': '🛎 Начать сделку', 'text_ru': '🛎 Начать сделку'},
        #         {'name': 'trade-enter_amount_for_trade', 'text': 'Введите желаемую сумму для обмена\r\n\r\nВсего доступно: {amount} {currency}',
        #          'text_ru': 'Введите желаемую сумму для обмена\r\n\r\nВсего доступно: {amount} {currency}'}, {'name': 'trade-confirm_amount_for_trade',
        #                                                            'text': 'Вы желаете {type_operation} {amount} {trade_currency} за {price_trade} {payment_currency}',
        #                                                            'text_ru': 'Вы желаете {type_operation} {amount} {trade_currency} за {price_trade} {payment_currency}'},
        #         {'name': 'kb-yes', 'text': '✅ Да', 'text_ru': '✅ Да'},
        #         {'name': 'kb-no', 'text': '❌ Нет', 'text_ru': '❌ Нет'},
        #         {'name': 'trade-select_type_trade', 'text': 'С какого кошелька Вы желаете произвести обмен?',
        #          'text_ru': 'С какого кошелька Вы желаете произвести обмен?'},
        #         {'name': 'trade-kb-use_internal_wallet', 'text': 'Использовать внутренний кошелёк',
        #          'text_ru': 'Использовать внутренний кошелёк'},
        #         {'name': 'trade-kb-use_third_party_wallet', 'text': 'Использовать сторонний кошелёк',
        #          'text_ru': 'Использовать сторонний кошелёк'}, {'name': 'trade-not_enough_money_to_trade',
        #                                                         'text': 'У Вас недостаточно средств на внутреннем кошельке для проведения обмена.\r\nВы можете пополнить баланс или оплатить с стороннего кошелька',
        #                                                         'text_ru': 'У Вас недостаточно средств на внутреннем кошельке для проведения обмена.\r\nВы можете пополнить баланс или оплатить с стороннего кошелька'},
        #         {'name': 'trade-await_confirm_from_owner', 'text': 'Ожидайте подтверждение от владельца объявления',
        #          'text_ru': 'Ожидайте подтверждение от владельца объявления'},
        #         {'name': 'trade-kb-confirm_payment', 'text': '✅ Да, я получил деньги',
        #          'text_ru': '✅ Да, я получил деньги'},
        #         {'name': 'trade-kb-decline_payment', 'text': '❌ Я не получил денег', 'text_ru': '❌ Я не получил денег'},
        #         {'name': 'trade-kb-view_on', 'text': 'Посмотреть на {name}', 'text_ru': 'Посмотреть на {name}'},
        #         {'name': 'trade-confirm_transaction',
        #          'text': 'С Вами начали сделку \r\n\r\nПользователь Вам отправил {amount} {currency}\r\nна ваш адрес \r\n```{address}```\r\n\r\nПроверьте пришло ли вам {amount} {currency}\r\nХэш транзакции для проверки\r\n```{tx_hash}```',
        #          'text_ru': 'С Вами начали сделку \r\n\r\nПользователь Вам отправил {amount} {currency}\r\nна ваш адрес \r\n```{address}```\r\n\r\nПроверьте пришло ли вам {amount} {currency}\r\nХэш транзакции для проверки\r\n```{tx_hash}```'},
        #         {'name': 'trade-semi_automatic_start',
        #          'text': 'Переведите {amount} {currency} \r\nна адрес ```{address}```\r\n\r\nПосле оплаты, сбросьте в бота хэш-транзакции',
        #          'text_ru': 'Переведите {amount} {currency} \r\nна адрес ```{address}```\r\n\r\nПосле оплаты, сбросьте в бота хэш-транзакции'},
        #         {'name': 'trade-second_confirm_transaction',
        #          'text': 'Вы точно уверены, что получили {amount} {currency} \r\n\r\nНа адрес {address}',
        #          'text_ru': 'Вы точно уверены, что получили {amount} {currency} \r\n\r\nНа адрес {address}'},
        #         {'name': 'trade-success_trade',
        #          'text': 'Вы {type_operation} {amount} {trade_currency} \r\nза {price_trade} {payment_currency}',
        #          'text_ru': 'Вы {type_operation} {amount} {trade_currency} \r\nза {price_trade} {payment_currency}'},
        #         {'name': 'order-type_operation_translate_sale_3', 'text': 'Продажа {currency}',
        #          'text_ru': 'Продажа {currency}'},
        #         {'name': 'order-type_operation_translate_buy_3', 'text': 'Покупка {currency}',
        #          'text_ru': 'Покупка {currency}'}, {'name': 'order-enter_amount',
        #                                             'text': 'Введите сумму {currency}, которую хотите {type_operation}\r\nВсего доступно: {amount} {currency}',
        #                                             'text_ru': 'Введите сумму {currency}, которую хотите {type_operation}\r\nВсего доступно: {amount} {currency}'},
        #         {'name': 'order-kb-cancel_order', 'text': 'Отменить создание объявления',
        #          'text_ru': 'Отменить создание объявления'}
        #        ]
        txts = [{'name': 'user-start', 'text': 'Добро пожаловать!', 'text_ru': 'Добро пожаловать!', 'text_en': 'уйцуйцу'}, {'name': 'user-start_ref', 'text': 'Тебя пригласил пользователь {name}', 'text_ru': 'Тебя пригласил пользователь {name}', 'text_en': 'dawdwad'}, {'name': 'user-end_registration', 'text': 'Поздравляю!\r\nРегистрация окончена, язык и валюту можно изменить в настройках\\n\r\n*какой-то еще текст*', 'text_ru': 'Поздравляю!\r\nРегистрация окончена, язык и валюту можно изменить в настройках\\n\r\n*какой-то еще текст*', 'text_en': 'oooo'}, {'name': 'user-kb-trade', 'text': '💸 Обмен', 'text_ru': '💸 Обмен', 'text_en': 'asdasd'}, {'name': 'user-kb-wallet', 'text': '💼 Кошелёк', 'text_ru': '💼 Кошелёк', 'text_en': 'adsds'}, {'name': 'user-kb-settings', 'text': '⚙️ Настройки', 'text_ru': '⚙️ Настройки', 'text_en': 'sadasd'}, {'name': 'user-hide', 'text': '« скрыть »', 'text_ru': '« скрыть »', 'text_en': 'уйцуйц'}, {'name': 'user-kb-usd', 'text': '🇺🇸 Американский доллар (USD)', 'text_ru': '🇺🇸 Американский доллар (USD)', 'text_en': 'ыфвфыв'}, {'name': 'user-kb-uah', 'text': '🇺🇦 Украинская гривна (UAH)', 'text_ru': '🇺🇦 Украинская гривна (UAH)', 'text_en': 'sadsad'}, {'name': 'user-kb-rub', 'text': '🇷🇺 Российский рубль (RUB)', 'text_ru': '🇷🇺 Российский рубль (RUB)', 'text_en': 'adsda'}, {'name': 'order-kb-trade_menu-new_buy', 'text': '📝 Новое на покупку', 'text_ru': '📝 Новое на покупку', 'text_en': 'dasdas'}, {'name': 'order-kb-trade_menu-new_sale', 'text': '📝 Новое на продажу', 'text_ru': '📝 Новое на продажу', 'text_en': 'dasdasd'}, {'name': 'order-kb-trade_menu-orders', 'text': '📜 Объявления', 'text_ru': '📜 Объявления', 'text_en': 'dasd'}, {'name': 'order-kb-trade_menu-my_orders', 'text': '📋 Мои объявления', 'text_ru': '📋 Мои объявления', 'text_en': 'asdasd'}, {'name': 'order-kb-trade_menu-my_trades', 'text': '📇 Мои сделки', 'text_ru': '📇 Мои сделки', 'text_en': 'dasd'}, {'name': 'order-kb-trade_menu-notifications', 'text': '📢 Уведомления', 'text_ru': '📢 Уведомления', 'text_en': 'sdasd'}, {'name': 'kb-accept', 'text': '✅ Подтвердить', 'text_ru': '✅ Подтвердить', 'text_en': 'adsdas'}, {'name': 'kb-back', 'text': '🔙 Назад', 'text_ru': '🔙 Назад', 'text_en': 'sadasd'}, {'name': 'order-orders_menu', 'text': 'Меню объявлений', 'text_ru': 'Меню объявлений', 'text_en': 'dasdas'}, {'name': 'user-trade_menu', 'text': '💸 **Обмен**\r\nЗдесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.', 'text_ru': '💸 **Обмен**\r\nЗдесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.', 'text_en': 'asdasd'}, {'name': 'order-error_no_selected_payment_instrument', 'text': 'Выберите хотя бы один платёжный инструмент', 'text_ru': 'Выберите хотя бы один платёжный инструмент', 'text_en': 'уйцуйц'}, {'name': 'order-kb-use_internal_wallet', 'text': '✅ Использовать внутренний кошелёк', 'text_ru': '✅ Использовать внутренний кошелёк', 'text_en': 'укцуку'}, {'name': 'order-type_operation_translate_buy_1', 'text': 'купить', 'text_ru': 'купить', 'text_en': 'вфыв'}, {'name': 'order-type_operation_translate_buy_2', 'text': 'купили', 'text_ru': 'купили', 'text_en': ''}, {'name': 'order-kb-open_purse', 'text': 'Использовать реквизиты из портмоне', 'text_ru': 'Использовать реквизиты из портмоне', 'text_en': 'выфв'}, {'name': 'order-kb-add_new_requisite', 'text': 'Добавить новые реквизиты', 'text_ru': 'Добавить новые реквизиты', 'text_en': 'вывфывы'}, {'name': 'order-select_requisite_from_purse', 'text': 'Ваши реквизиты {currency}', 'text_ru': 'Ваши реквизиты {currency}', 'text_en': 'wqeqw'}, {'name': 'order-kb-back_to_selection_requisite_menu', 'text': '🔙 Назад', 'text_ru': '🔙 Назад', 'text_en': 'dasdas'}, {'name': 'purse-enter_address', 'text': 'Введите адрес {currency} кошелька на который будут поступать средства от сделок.', 'text_ru': 'Введите адрес {currency} кошелька на который будут поступать средства от сделок.', 'text_en': 'уцйуйц'}, {'name': 'order-select_payment_currency', 'text': 'Какую валюту вы хотите получить за {currency}?\r\n\r\nВы можете выбрать одну или несколько и нажмите "Подтвердить"', 'text_ru': 'Какую валюту вы хотите получить за {currency}?\r\n\r\nВы можете выбрать одну или несколько и нажмите "Подтвердить"', 'text_en': 'выфвыф'}, {'name': 'bot-you_choosed', 'text': 'Вы выбрали {foo}', 'text_ru': 'Вы выбрали {foo}', 'text_en': 'dasdas'}, {'name': 'bot-you_entered', 'text': 'Вы ввели {count}', 'text_ru': 'Вы ввели {count}', 'text_en': ''}, {'name': 'bot-type_error', 'text': 'Ошибка! Используйте только цифры', 'text_ru': 'Ошибка! Используйте только цифры', 'text_en': 'фвыфвыфв'}, {'name': 'order-type_operation_translate_sale_1', 'text': 'продать', 'text_ru': 'продать', 'text_en': ''}, {'name': 'order-enter_currency_rate', 'text': 'Введите желаемую стоимость {trade_currency} в USD\r\n\r\nСредняя цена за {trade_currency}: {price} USD', 'text_ru': 'Введите желаемую стоимость {trade_currency} в USD\r\n\r\nСредняя цена за {trade_currency}: {price} USD', 'text_en': 'asdasd'}, {'name': 'order-type_operation_translate_sale_2', 'text': 'продали', 'text_ru': 'продали', 'text_en': ''}, {'name': 'wallet-kb-deposite', 'text': 'Пополнить', 'text_ru': 'Пополнить', 'text_en': 'йцуйц'}, {'name': 'wallet-kb-withdraw', 'text': 'Вывести', 'text_ru': 'Вывести', 'text_en': ''}, {'name': 'wallet-kb-purse', 'text': 'Портмоне', 'text_ru': 'Портмоне', 'text_en': ''}, {'name': 'wallet-kb-affiliate_program', 'text': 'Партнёрская программа', 'text_ru': 'Партнёрская программа', 'text_en': 'к'}, {'name': 'wallet-kb-premium', 'text': 'Премиум подписка', 'text_ru': 'Премиум подписка', 'text_en': ''}, {'name': 'wallet-wallet_info', 'text': '💼 Кошелёк\\n\\n\r\n\r\nБаланс:', 'text_ru': '💼 Кошелёк\\n\\n\r\n\r\nБаланс:', 'text_en': 'sd'}, {'name': 'purse-kb-delete', 'text': 'Удалить', 'text_ru': 'Удалить', 'text_en': ''}, {'name': 'purse-kb-edit_add_name', 'text': 'Редактировать/Добавить имя', 'text_ru': 'Редактировать/Добавить имя', 'text_en': 'цйуцйуйц'}, {'name': 'purse-kb-edit_address', 'text': 'Редактировать адрес', 'text_ru': 'Редактировать адрес', 'text_en': 'вфвы'}, {'name': 'purse-requisite_info_with_name', 'text': '{name}\r\n{address}\r\n{currency}', 'text_ru': '{name}\r\n{address}\r\n{currency}', 'text_en': ''}, {'name': 'order-kb-share', 'text': '📣 Поделиться', 'text_ru': '📣 Поделиться', 'text_en': 'sad'}, {'name': 'purse-select_currency', 'text': 'Выберите валюту для кошелька', 'text_ru': 'Выберите валюту для кошелька', 'text_en': 'выфв'}, {'name': 'purse-purse_menu', 'text': '💼 Портмоне\r\n\r\nЗдесь вы можете хранить ваши реквизиты', 'text_ru': '💼 Портмоне\r\n\r\nЗдесь вы можете хранить ваши реквизиты', 'text_en': ''}, {'name': 'purse-enter_requisite_name', 'text': 'Введите имя реквизиты', 'text_ru': 'Введите имя реквизиты', 'text_en': 'выфвыф'}, {'name': 'bot-invalid_address', 'text': 'Некорректный адрес', 'text_ru': 'Некорректный адрес', 'text_en': 'цу'}, {'name': 'purse-requisite_info', 'text': '```{address}```\r\nВалюта: {currency}', 'text_ru': '```{address}```\r\nВалюта: {currency}', 'text_en': ''}, {'name': 'order-kb-off_order', 'text': '🌕 Выключить', 'text_ru': '🌕 Выключить', 'text_en': 'sads'}, {'name': 'order-kb-on_order', 'text': '🌑 Включить', 'text_ru': '🌑 Включить', 'text_en': 'dasd'}, {'name': 'bot-balance_replinished', 'text': '💸 Ваш баланс пополнен на:', 'text_ru': '💸 Ваш баланс пополнен на:', 'text_en': 'цйуцй'}, {'name': 'kb-delete', 'text': '❌ Удалить', 'text_ru': '❌ Удалить', 'text_en': 'dasd'}, {'name': 'kb-cancel', 'text': '« Отменить »', 'text_ru': '« Отменить »', 'text_en': 'asdsa'}, {'name': 'kb-skip', 'text': 'Пропустить', 'text_ru': 'Пропустить', 'text_en': 'уы'}, {'name': 'kb-close', 'text': '« закрыть »', 'text_ru': '« закрыть »', 'text_en': 'уйц'}, {'name': 'order-select_trade_currency', 'text': 'Что хотите {type_operation}?', 'text_ru': 'Что хотите {type_operation}?', 'text_en': 'dasdas'}, {'name': 'order-select_requisite_for_order', 'text': 'Выберете кошелёк на который вы получите  {currency}', 'text_ru': 'Выберете кошелёк на который вы получите  {currency}', 'text_en': 'dasdas'}, {'name': 'order-your_choice', 'text': 'Ваш выбор:', 'text_ru': 'Ваш выбор:', 'text_en': 'уцйуйц'}, {'name': 'kb-hide', 'text': '« скрыть »', 'text_ru': '« скрыть »', 'text_en': 'цйуц'}, {'name': 'user-settings', 'text': '⚙️ Настройки', 'text_ru': '⚙️ Настройки', 'text_en': 'dasda'}, {'name': 'user-kb-language', 'text': '🌎 Язык', 'text_ru': '🌎 Язык', 'text_en': 'dasdas'}, {'name': 'user-kb-currency', 'text': '💶 Валюта', 'text_ru': '💶 Валюта', 'text_en': 'dasdas'}, {'name': 'user-kb-service_info', 'text': '🌐 О сервисе', 'text_ru': '🌐 О сервисе', 'text_en': 'цйуцй'}, {'name': 'user-settings-select_currency', 'text': '💶 Валюта\r\n\r\nВыберите базовую валюту', 'text_ru': '💶 Валюта\r\n\r\nВыберите базовую валюту', 'text_en': 'ewrwe'}, {'name': 'user-settings-select_language', 'text': '🌍 Язык\r\n\r\nПожалуйста, выберите язык', 'text_ru': '🌍 Язык\r\n\r\nПожалуйста, выберите язык', 'text_en': 'ad'}, {'name': 'user-settings-selected_language', 'text': 'Вы выбрали {language} язык', 'text_ru': 'Вы выбрали {language} язык', 'text_en': ''}, {'name': 'user-settings-selected_currency', 'text': 'Вы выбрали {currency}', 'text_ru': 'Вы выбрали {currency}', 'text_en': 'dwadwa'}, {'name': 'order-my_orders', 'text': 'Ваши объявления', 'text_ru': 'Ваши объявления', 'text_en': 'уйцуйц'}, {'name': 'order-kb-look_at_the_sale', 'text': 'Смотреть на продажу', 'text_ru': 'Смотреть на продажу', 'text_en': ''}, {'name': 'order-kb-look_at_the_buy', 'text': 'Смотреть на покупку', 'text_ru': 'Смотреть на покупку', 'text_en': ''}, {'name': 'user-registration-select_currency', 'text': 'Выбери базовую валюту', 'text_ru': 'Выбери базовую валюту', 'text_en': 'уцйуйц'}, {'name': 'order-kb-start_trade', 'text': '🛎 Начать сделку', 'text_ru': '🛎 Начать сделку', 'text_en': 'цуйц'}, {'name': 'kb-yes', 'text': '✅ Да', 'text_ru': '✅ Да', 'text_en': 'выф'}, {'name': 'kb-no', 'text': '❌ Нет', 'text_ru': '❌ Нет', 'text_en': ''}, {'name': 'trade-select_type_trade', 'text': 'С какого кошелька Вы желаете произвести обмен?', 'text_ru': 'С какого кошелька Вы желаете произвести обмен?', 'text_en': 'цукцу'}, {'name': 'trade-kb-use_internal_wallet', 'text': 'Использовать внутренний кошелёк', 'text_ru': 'Использовать внутренний кошелёк', 'text_en': ''}, {'name': 'trade-kb-use_third_party_wallet', 'text': 'Использовать сторонний кошелёк', 'text_ru': 'Использовать сторонний кошелёк', 'text_en': ''}, {'name': 'trade-not_enough_money_to_trade', 'text': 'У Вас недостаточно средств на внутреннем кошельке для проведения обмена.\r\nВы можете пополнить баланс или оплатить с стороннего кошелька', 'text_ru': 'У Вас недостаточно средств на внутреннем кошельке для проведения обмена.\r\nВы можете пополнить баланс или оплатить с стороннего кошелька', 'text_en': 'йцуцй'}, {'name': 'trade-await_confirm_from_owner', 'text': 'Ожидайте подтверждение от владельца объявления', 'text_ru': 'Ожидайте подтверждение от владельца объявления', 'text_en': 'цйуйц'}, {'name': 'trade-kb-confirm_payment', 'text': '✅ Да, я получил деньги', 'text_ru': '✅ Да, я получил деньги', 'text_en': ''}, {'name': 'trade-kb-decline_payment', 'text': '❌ Я не получил денег', 'text_ru': '❌ Я не получил денег', 'text_en': 'уцуйц'}, {'name': 'trade-kb-view_on', 'text': 'Посмотреть на {name}', 'text_ru': 'Посмотреть на {name}', 'text_en': 'wqe'}, {'name': 'trade-confirm_transaction', 'text': 'С Вами начали сделку \r\n\r\nПользователь Вам отправил {amount} {currency}\r\nна ваш адрес \r\n```{address}```\r\n\r\nПроверьте пришло ли вам {amount} {currency}\r\nХэш транзакции для проверки\r\n```{tx_hash}```', 'text_ru': 'С Вами начали сделку \r\n\r\nПользователь Вам отправил {amount} {currency}\r\nна ваш адрес \r\n```{address}```\r\n\r\nПроверьте пришло ли вам {amount} {currency}\r\nХэш транзакции для проверки\r\n```{tx_hash}```', 'text_en': 'ewrwer'}, {'name': 'trade-semi_automatic_start', 'text': 'Переведите {amount} {currency} \r\nна адрес ```{address}```\r\n\r\nПосле оплаты, сбросьте в бота хэш-транзакции', 'text_ru': 'Переведите {amount} {currency} \r\nна адрес ```{address}```\r\n\r\nПосле оплаты, сбросьте в бота хэш-транзакции', 'text_en': ''}, {'name': 'order-kb-cancel_order', 'text': 'Отменить создание объявления', 'text_ru': 'Отменить создание объявления', 'text_en': ''}, {'name': 'trade-second_confirm_transaction', 'text': 'Вы точно уверены, что получили {amount} {currency} \r\n\r\nНа адрес {address}', 'text_ru': 'Вы точно уверены, что получили {amount} {currency} \r\n\r\nНа адрес {address}', 'text_en': ''}, {'name': 'trade-success_trade', 'text': 'Вы {type_operation} {amount} {trade_currency} \r\nза {price_trade} {payment_currency}', 'text_ru': 'Вы {type_operation} {amount} {trade_currency} \r\nза {price_trade} {payment_currency}', 'text_en': ''}, {'name': 'order-type_operation_translate_sale_3', 'text': 'Продажа {currency}', 'text_ru': 'Продажа {currency}', 'text_en': ''}, {'name': 'order-type_operation_translate_buy_3', 'text': 'Покупка {currency}', 'text_ru': 'Покупка {currency}', 'text_en': ''}, {'name': 'order-enter_amount', 'text': 'Введите сумму {currency}, которую хотите {type_operation}\r\nВсего доступно: {amount} {currency}', 'text_ru': 'Введите сумму {currency}, которую хотите {type_operation}\r\nВсего доступно: {amount} {currency}', 'text_en': 'eter'}, {'name': 'trade-enter_amount_for_trade', 'text': 'Введите желаемую сумму для обмена\r\n\r\nВсего доступно: {amount} {currency}', 'text_ru': 'Введите желаемую сумму для обмена\r\n\r\nВсего доступно: {amount} {currency}', 'text_en': ''}, {'name': 'order-parent_order_info', 'text': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n{currency_pairs}\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: \r\n{max_amounts}', 'text_ru': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n{currency_pairs}\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: \r\n{max_amounts}', 'text_en': ''}, {'name': 'order-kb-average_rate', 'text': 'Выбрать средний курс', 'text_ru': 'Выбрать средний курс', 'text_en': ''}, {'name': 'order-kb-max_amount', 'text': 'Выбрать максимальную сумму', 'text_ru': 'Выбрать максимальную сумму', 'text_en': ''}, {'name': 'trade-confirm_amount_for_trade', 'text': 'Вы желаете {type_operation} {amount} {trade_currency} за {price_trade} {payment_currency}', 'text_ru': 'Вы желаете {type_operation} {amount} {trade_currency} за {price_trade} {payment_currency}', 'text_en': 'eqwewq'}, {'name': 'order-order_info', 'text': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n1 {trade_currency} – {rate_1} {payment_currency}\r\n1 {payment_currency} – {rate_2} {trade_currency}\r\n\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: {price_order} {payment_currency}', 'text_ru': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n1 {trade_currency} – {rate_1} {payment_currency}\r\n1 {payment_currency} – {rate_2} {trade_currency}\r\n\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: {price_order} {payment_currency}', 'text_en': 'ikjj'}]

        Text.objects.bulk_create([Text(**q) for q in txts])
