from django.core.management.base import BaseCommand

from bot.models import CurrencyList, Text


class Command(BaseCommand):

    def handle(self, **options):
        currency_list = [
            {'currency': 'ETH', 'type': 'crypto', 'accuracy': 6},
            {'currency': 'USDT', 'type': 'crypto', 'accuracy': 4},
            {'currency': 'BTC', 'type': 'crypto', 'accuracy': 8},
            {'currency': 'BIP', 'type': 'crypto', 'accuracy': 4},
            {'currency': 'USD', 'type': 'fiat', 'accuracy': 2},
            {'currency': 'UAH', 'type': 'fiat', 'accuracy': 2},
            {'currency': 'RUB', 'type': 'fiat', 'accuracy': 4},
            {'currency': 'BONUS', 'type': 'affiliate', 'accuracy': 2}
        ]

        if CurrencyList.objects.all().count() > 0:
            e = 'Таблица валют уже содержит данные\n'
            answ = input(
                f'{e}\nЖелаете перезаписать данные?\nВсе значения настроек валют в БД будут перезаписаны\nВведите Y/n: ')

            if answ == 'Y':
                CurrencyList.objects.all().delete()
                CurrencyList.objects.bulk_create([CurrencyList(**q) for q in currency_list])
                print('Successful installation of a package of currencies')
        else:
            CurrencyList.objects.bulk_create([CurrencyList(**q) for q in currency_list])
            print('Successful installation of a package of currencies')

        Text.objects.all().delete()
        txts = [{'name': 'wallet-select_currency_for_deposit', 'text': 'Выберите валюту для пополнения', 'text_ru': 'Выберите валюту для пополнения', 'text_en': ''}, {'name': 'trade-your_canceled_trade', 'text': '**Вы отменили обмен.**', 'text_ru': '**Вы отменили обмен.**', 'text_en': ''}, {'name': 'bot-balance_replinished', 'text': '💸 Ваш баланс пополнен на:\r\n{refill}', 'text_ru': '💸 Ваш баланс пополнен на:\r\n{refill}', 'text_en': 'цйуцй'}, {'name': 'trade-order_not_open', 'text': 'Объявление было закрыто', 'text_ru': 'Объявление было закрыто', 'text_en': ''}, {'name': 'trade-in_trade', 'text': 'Вы сейчас на стадии подготовки к обмену. Функционал бота ограничен.', 'text_ru': 'Вы сейчас на стадии подготовки к обмену. Функционал бота ограничен.', 'text_en': ''}, {'name': 'order-kb-share-go', 'text': 'Перейти', 'text_ru': 'Перейти', 'text_en': ''}, {'name': 'wallet-affiliate_bonus', 'text': 'ᅠ\r\n💎 **Бонусы**:\r\n{balance} USD\r\nᅠ', 'text_ru': 'ᅠ\r\n💎 **Бонусы**:\r\n{balance} USD\r\nᅠ', 'text_en': ''}, {'name': 'wallet-confirm_convert_bonus', 'text': 'Вы хотите перевести {amount} бонусных USD  в {amount_in_currency} {currency}', 'text_ru': 'Вы хотите перевести {amount} бонусных USD  в {amount_in_currency} {currency}', 'text_en': ''}, {'name': 'wallet-successful_convert_bonus', 'text': 'Вы конвертировали {amount} бонусных USD в {amount_in_currency} {currency}', 'text_ru': 'Вы конвертировали {amount} бонусных USD в {amount_in_currency} {currency}', 'text_en': ''}, {'name': 'purse-confirm_delete_requisite', 'text': 'Подтвердите удаление', 'text_ru': 'Подтвердите удаление', 'text_en': ''}, {'name': 'order-confirm_delete_order', 'text': 'Вы хотите удалить объявление?', 'text_ru': 'Вы хотите удалить объявление?', 'text_en': ''}, {'name': 'order-parent_order_info', 'text': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n{currency_pairs}\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: \r\n{max_amounts}', 'text_ru': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n{currency_pairs}\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: \r\n{max_amounts}', 'text_en': ''}, {'name': 'wallet-address_for_deposit', 'text': 'Адрес кошелька для пополнения {currency}:', 'text_ru': 'Адрес кошелька для пополнения {currency}:', 'text_en': ''}, {'name': 'wallet-kb-deposit', 'text': 'Пополнить', 'text_ru': 'Пополнить', 'text_en': 'йцуйц'}, {'name': 'order-not_enough_money_after_deposit', 'text': 'Но это не достаточно чтобы завершить создание объявления.\r\nЕсли хотите использовать бота как гаранта - надо пополнить:\r\n{deposit_currency}', 'text_ru': 'Но это не достаточно чтобы завершить создание объявления.\r\nЕсли хотите использовать бота как гаранта - надо пополнить:\r\n{deposit_currency}', 'text_en': ''}, {'name': 'order-continue_order_after_deposit', 'text': 'Баланса достаточно для завершения создания объявления. Желаете продолжить?', 'text_ru': 'Баланса достаточно для завершения создания объявления. Желаете продолжить?', 'text_en': ''}, {'name': 'wallet-kb-convert_bonus', 'text': 'Конвертировать бонусы', 'text_ru': 'Конвертировать бонусы', 'text_en': ''}, {'name': 'wallet-cancel_convert_bonus', 'text': 'Вы отменили конвертацию бонусов', 'text_ru': 'Вы отменили конвертацию бонусов', 'text_en': ''}, {'name': 'purse-requisite_name_is_already_exist', 'text': 'Под этим именем **{name}** у Вас уже существует реквизиты с валютой {currency}', 'text_ru': 'Под этим именем **{name}** у Вас уже существует реквизиты с валютой {currency}', 'text_en': ''}, {'name': 'order-not_enough_money', 'text': 'Балансы {balance} недостаточны. Если хотите использовать бота как гаранта - надо пополнить\r\n{deposit_amount}', 'text_ru': 'Балансы {balance} недостаточны. Если хотите использовать бота как гаранта - надо пополнить\r\n{deposit_amount}', 'text_en': ''}, {'name': 'order-order_deleted', 'text': '❌ Объявление удалено!', 'text_ru': '❌ Объявление удалено!', 'text_en': ''}, {'name': 'order-market_depth-select_trade_currency', 'text': 'Выберите валюту 1', 'text_ru': 'Выберите валюту 1', 'text_en': ''}, {'name': 'trade-not_enough_money_to_trade', 'text': 'У Вас недостаточно средств на внутреннем кошельке для проведения обмена.\r\n\r\nДля того, чтобы провести обмен пополните счёт на:\r\n**{amount} {currency}**', 'text_ru': 'У Вас недостаточно средств на внутреннем кошельке для проведения обмена.\r\n\r\nДля того, чтобы провести обмен пополните счёт на:\r\n**{amount} {currency}**', 'text_en': 'йцуцй'}, {'name': 'trade-kb-continue_trade', 'text': 'Завершить обмен', 'text_ru': 'Завершить обмен', 'text_en': ''}, {'name': 'trade-not_enough_money_after_deposit', 'text': 'Но этого не достаточно. Для завершения трейда необходимо пополнить на:\r\n{amount} {currency}', 'text_ru': 'Но этого не достаточно. Для завершения трейда необходимо пополнить на:\r\n{amount} {currency}', 'text_en': ''}, {'name': 'wallet-enter_amount_for_conver_bonus', 'text': 'Сколько хотите использовать бонусов?\r\n\r\nМинимальная сумма для конвертации: {min_amount} USD', 'text_ru': 'Сколько хотите использовать бонусов?\r\n\r\nМинимальная сумма для конвертации: {min_amount} USD', 'text_en': ''}, {'name': 'wallet-limit_convert_bonus', 'text': 'Вы не можете конвертировать больше чем {amount} бонусных USD', 'text_ru': 'Вы не можете конвертировать больше чем {amount} бонусных USD', 'text_en': ''}, {'name': 'purse-requisite_address_is_already_exist', 'text': 'Реквизиты с адресом **{address}** уже существуют', 'text_ru': 'Реквизиты с адресом **{address}** уже существуют', 'text_en': ''}, {'name': 'order-market_depth-select_payment_currency', 'text': 'Выберите валюту 2', 'text_ru': 'Выберите валюту 2', 'text_en': ''}, {'name': 'trade-kb-cancel_trade', 'text': 'Отменить обмен', 'text_ru': 'Отменить обмен', 'text_en': ''}, {'name': 'trade-continue_trade_after_deposit', 'text': 'Баланса достаточно для завершения трейда.\r\n\r\nВы желаете {type_operation} {amount} {trade_currency} за {price_trade} {payment_currency}', 'text_ru': 'Баланса достаточно для завершения трейда.\r\n\r\nВы желаете {type_operation} {amount} {trade_currency} за {price_trade} {payment_currency}', 'text_en': ''}, {'name': 'wallet-kb-cancel_convert_bonus', 'text': 'Отменить конвертацию', 'text_ru': 'Отменить конвертацию', 'text_en': ''}, {'name': 'wallet-wallet_info', 'text': '💼 **Кошелёк**\r\n\r\n💰 **Баланс**:\r\n{balances}', 'text_ru': '💼 **Кошелёк**\r\n\r\n💰 **Баланс**:\r\n{balances}', 'text_en': 'sd'}, {'name': 'purse-kb-edit_address', 'text': 'Изменить адрес', 'text_ru': 'Изменить адрес', 'text_en': 'вфвы'}, {'name': 'purse-kb-edit_add_name', 'text': 'Изменить/Добавить имя', 'text_ru': 'Изменить/Добавить имя', 'text_en': 'цйуцйуйц'}, {'name': 'order-enter_currency_rate', 'text': 'Введите желаемую стоимость {trade_currency} в долларах США (USD)\r\n\r\nСредняя цена за {trade_currency}: {price} USD', 'text_ru': 'Введите желаемую стоимость {trade_currency} в долларах США (USD)\r\n\r\nСредняя цена за {trade_currency}: {price} USD', 'text_en': 'asdasd'}, {'name': 'order-select_payment_currency', 'text': 'Выберите платёжный инструмент\r\n\r\nВы можете выбрать одну или несколько и нажмите "Подтвердить"', 'text_ru': 'Выберите платёжный инструмент\r\n\r\nВы можете выбрать одну или несколько и нажмите "Подтвердить"', 'text_en': 'выфвыф'}, {'name': 'order-your_choice', 'text': 'Ваш выбор:', 'text_ru': 'Ваш выбор:', 'text_en': 'уцйуйц'}, {'name': 'user-start', 'text': 'Добро пожаловать!', 'text_ru': 'Добро пожаловать!', 'text_en': 'уйцуйцу'}, {'name': 'user-start_ref', 'text': 'Тебя пригласил пользователь {name}', 'text_ru': 'Тебя пригласил пользователь {name}', 'text_en': 'dawdwad'}, {'name': 'user-end_registration', 'text': 'Поздравляю!\r\nРегистрация окончена, язык и валюту можно изменить в настройках\\n\r\n*какой-то еще текст*', 'text_ru': 'Поздравляю!\r\nРегистрация окончена, язык и валюту можно изменить в настройках\\n\r\n*какой-то еще текст*', 'text_en': 'oooo'}, {'name': 'user-kb-trade', 'text': '💸 Обмен', 'text_ru': '💸 Обмен', 'text_en': 'asdasd'}, {'name': 'user-kb-wallet', 'text': '💼 Кошелёк', 'text_ru': '💼 Кошелёк', 'text_en': 'adsds'}, {'name': 'user-kb-settings', 'text': '⚙️ Настройки', 'text_ru': '⚙️ Настройки', 'text_en': 'sadasd'}, {'name': 'user-hide', 'text': '« скрыть »', 'text_ru': '« скрыть »', 'text_en': 'уйцуйц'}, {'name': 'user-kb-usd', 'text': '🇺🇸 Американский доллар (USD)', 'text_ru': '🇺🇸 Американский доллар (USD)', 'text_en': 'ыфвфыв'}, {'name': 'user-kb-uah', 'text': '🇺🇦 Украинская гривна (UAH)', 'text_ru': '🇺🇦 Украинская гривна (UAH)', 'text_en': 'sadsad'}, {'name': 'user-kb-rub', 'text': '🇷🇺 Российский рубль (RUB)', 'text_ru': '🇷🇺 Российский рубль (RUB)', 'text_en': 'adsda'}, {'name': 'order-kb-trade_menu-new_buy', 'text': '📝 Новое на покупку', 'text_ru': '📝 Новое на покупку', 'text_en': 'dasdas'}, {'name': 'order-kb-trade_menu-new_sale', 'text': '📝 Новое на продажу', 'text_ru': '📝 Новое на продажу', 'text_en': 'dasdasd'}, {'name': 'order-kb-trade_menu-orders', 'text': '📜 Объявления', 'text_ru': '📜 Объявления', 'text_en': 'dasd'}, {'name': 'order-kb-trade_menu-my_orders', 'text': '📋 Мои объявления', 'text_ru': '📋 Мои объявления', 'text_en': 'asdasd'}, {'name': 'order-kb-trade_menu-my_trades', 'text': '📇 Мои сделки', 'text_ru': '📇 Мои сделки', 'text_en': 'dasd'}, {'name': 'order-kb-trade_menu-notifications', 'text': '📢 Уведомления', 'text_ru': '📢 Уведомления', 'text_en': 'sdasd'}, {'name': 'kb-accept', 'text': '✅ Подтвердить', 'text_ru': '✅ Подтвердить', 'text_en': 'adsdas'}, {'name': 'kb-back', 'text': '🔙 Назад', 'text_ru': '🔙 Назад', 'text_en': 'sadasd'}, {'name': 'order-orders_menu', 'text': 'Меню объявлений', 'text_ru': 'Меню объявлений', 'text_en': 'dasdas'}, {'name': 'user-trade_menu', 'text': '💸 **Обмен**\r\nЗдесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.', 'text_ru': '💸 **Обмен**\r\nЗдесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.', 'text_en': 'asdasd'}, {'name': 'order-error_no_selected_payment_instrument', 'text': 'Выберите хотя бы один платёжный инструмент', 'text_ru': 'Выберите хотя бы один платёжный инструмент', 'text_en': 'уйцуйц'}, {'name': 'order-kb-use_internal_wallet', 'text': '✅ Использовать внутренний кошелёк', 'text_ru': '✅ Использовать внутренний кошелёк', 'text_en': 'укцуку'}, {'name': 'order-type_operation_translate_buy_1', 'text': 'купить', 'text_ru': 'купить', 'text_en': 'вфыв'}, {'name': 'order-type_operation_translate_buy_2', 'text': 'купили', 'text_ru': 'купили', 'text_en': ''}, {'name': 'order-kb-open_purse', 'text': 'Использовать реквизиты из портмоне', 'text_ru': 'Использовать реквизиты из портмоне', 'text_en': 'выфв'}, {'name': 'order-kb-add_new_requisite', 'text': 'Добавить новые реквизиты', 'text_ru': 'Добавить новые реквизиты', 'text_en': 'вывфывы'}, {'name': 'order-select_requisite_from_purse', 'text': 'Ваши реквизиты {currency}', 'text_ru': 'Ваши реквизиты {currency}', 'text_en': 'wqeqw'}, {'name': 'order-kb-back_to_selection_requisite_menu', 'text': '🔙 Назад', 'text_ru': '🔙 Назад', 'text_en': 'dasdas'}, {'name': 'purse-enter_address', 'text': 'Введите адрес {currency} кошелька на который будут поступать средства от сделок.', 'text_ru': 'Введите адрес {currency} кошелька на который будут поступать средства от сделок.', 'text_en': 'уцйуйц'}, {'name': 'wallet-kb-withdrawal', 'text': 'Вывести', 'text_ru': 'Вывести', 'text_en': ''}, {'name': 'bot-you_choosed', 'text': 'Вы выбрали {foo}', 'text_ru': 'Вы выбрали {foo}', 'text_en': 'dasdas'}, {'name': 'bot-you_entered', 'text': 'Вы ввели {count}', 'text_ru': 'Вы ввели {count}', 'text_en': ''}, {'name': 'bot-type_error', 'text': 'Ошибка! Используйте только цифры', 'text_ru': 'Ошибка! Используйте только цифры', 'text_en': 'фвыфвыфв'}, {'name': 'order-type_operation_translate_sale_1', 'text': 'продать', 'text_ru': 'продать', 'text_en': ''}, {'name': 'order-type_operation_translate_sale_2', 'text': 'продали', 'text_ru': 'продали', 'text_en': ''}, {'name': 'wallet-kb-purse', 'text': 'Портмоне', 'text_ru': 'Портмоне', 'text_en': ''}, {'name': 'wallet-kb-affiliate_program', 'text': 'Партнёрская программа', 'text_ru': 'Партнёрская программа', 'text_en': 'к'}, {'name': 'wallet-kb-premium', 'text': 'Премиум подписка', 'text_ru': 'Премиум подписка', 'text_en': ''}, {'name': 'purse-kb-delete', 'text': 'Удалить', 'text_ru': 'Удалить', 'text_en': ''}, {'name': 'purse-requisite_info_with_name', 'text': '{name}\r\n{address}\r\n{currency}', 'text_ru': '{name}\r\n{address}\r\n{currency}', 'text_en': ''}, {'name': 'order-kb-share', 'text': '📣 Поделиться', 'text_ru': '📣 Поделиться', 'text_en': 'sad'}, {'name': 'purse-select_currency', 'text': 'Выберите валюту для кошелька', 'text_ru': 'Выберите валюту для кошелька', 'text_en': 'выфв'}, {'name': 'purse-purse_menu', 'text': '💼 Портмоне\r\n\r\nЗдесь вы можете хранить ваши реквизиты', 'text_ru': '💼 Портмоне\r\n\r\nЗдесь вы можете хранить ваши реквизиты', 'text_en': ''}, {'name': 'purse-enter_requisite_name', 'text': 'Введите имя реквизиты', 'text_ru': 'Введите имя реквизиты', 'text_en': 'выфвыф'}, {'name': 'bot-invalid_address', 'text': 'Некорректный адрес', 'text_ru': 'Некорректный адрес', 'text_en': 'цу'}, {'name': 'purse-requisite_info', 'text': '```{address}```\r\nВалюта: {currency}', 'text_ru': '```{address}```\r\nВалюта: {currency}', 'text_en': ''}, {'name': 'order-kb-off_order', 'text': '🌕 Выключить', 'text_ru': '🌕 Выключить', 'text_en': 'sads'}, {'name': 'order-kb-on_order', 'text': '🌑 Включить', 'text_ru': '🌑 Включить', 'text_en': 'dasd'}, {'name': 'kb-delete', 'text': '❌ Удалить', 'text_ru': '❌ Удалить', 'text_en': 'dasd'}, {'name': 'kb-cancel', 'text': '« Отменить »', 'text_ru': '« Отменить »', 'text_en': 'asdsa'}, {'name': 'kb-skip', 'text': 'Пропустить', 'text_ru': 'Пропустить', 'text_en': 'уы'}, {'name': 'kb-close', 'text': '« закрыть »', 'text_ru': '« закрыть »', 'text_en': 'уйц'}, {'name': 'order-select_trade_currency', 'text': 'Что хотите {type_operation}?', 'text_ru': 'Что хотите {type_operation}?', 'text_en': 'dasdas'}, {'name': 'order-select_requisite_for_order', 'text': 'Выберете кошелёк на который вы получите  {currency}', 'text_ru': 'Выберете кошелёк на который вы получите  {currency}', 'text_en': 'dasdas'}, {'name': 'kb-hide', 'text': '« скрыть »', 'text_ru': '« скрыть »', 'text_en': 'цйуц'}, {'name': 'user-settings', 'text': '⚙️ Настройки', 'text_ru': '⚙️ Настройки', 'text_en': 'dasda'}, {'name': 'user-kb-language', 'text': '🌎 Язык', 'text_ru': '🌎 Язык', 'text_en': 'dasdas'}, {'name': 'user-kb-currency', 'text': '💶 Валюта', 'text_ru': '💶 Валюта', 'text_en': 'dasdas'}, {'name': 'user-kb-service_info', 'text': '🌐 О сервисе', 'text_ru': '🌐 О сервисе', 'text_en': 'цйуцй'}, {'name': 'user-settings-select_currency', 'text': '💶 Валюта\r\n\r\nВыберите базовую валюту', 'text_ru': '💶 Валюта\r\n\r\nВыберите базовую валюту', 'text_en': 'ewrwe'}, {'name': 'user-settings-select_language', 'text': '🌍 Язык\r\n\r\nПожалуйста, выберите язык', 'text_ru': '🌍 Язык\r\n\r\nПожалуйста, выберите язык', 'text_en': 'ad'}, {'name': 'user-settings-selected_language', 'text': 'Вы выбрали {language} язык', 'text_ru': 'Вы выбрали {language} язык', 'text_en': ''}, {'name': 'user-settings-selected_currency', 'text': 'Вы выбрали {currency}', 'text_ru': 'Вы выбрали {currency}', 'text_en': 'dwadwa'}, {'name': 'order-my_orders', 'text': 'Ваши объявления', 'text_ru': 'Ваши объявления', 'text_en': 'уйцуйц'}, {'name': 'order-kb-look_at_the_sale', 'text': 'Смотреть на продажу', 'text_ru': 'Смотреть на продажу', 'text_en': ''}, {'name': 'order-kb-look_at_the_buy', 'text': 'Смотреть на покупку', 'text_ru': 'Смотреть на покупку', 'text_en': ''}, {'name': 'user-registration-select_currency', 'text': 'Выбери базовую валюту', 'text_ru': 'Выбери базовую валюту', 'text_en': 'уцйуйц'}, {'name': 'order-kb-start_trade', 'text': '🛎 Начать сделку', 'text_ru': '🛎 Начать сделку', 'text_en': 'цуйц'}, {'name': 'kb-yes', 'text': '✅ Да', 'text_ru': '✅ Да', 'text_en': 'выф'}, {'name': 'kb-no', 'text': '❌ Нет', 'text_ru': '❌ Нет', 'text_en': ''}, {'name': 'trade-select_type_trade', 'text': 'С какого кошелька Вы желаете произвести обмен?', 'text_ru': 'С какого кошелька Вы желаете произвести обмен?', 'text_en': 'цукцу'}, {'name': 'trade-kb-use_internal_wallet', 'text': 'Использовать внутренний кошелёк', 'text_ru': 'Использовать внутренний кошелёк', 'text_en': ''}, {'name': 'trade-kb-use_third_party_wallet', 'text': 'Использовать сторонний кошелёк', 'text_ru': 'Использовать сторонний кошелёк', 'text_en': ''}, {'name': 'trade-await_confirm_from_owner', 'text': 'Ожидайте подтверждение от владельца объявления', 'text_ru': 'Ожидайте подтверждение от владельца объявления', 'text_en': 'цйуйц'}, {'name': 'trade-kb-confirm_payment', 'text': '✅ Да, я получил деньги', 'text_ru': '✅ Да, я получил деньги', 'text_en': ''}, {'name': 'trade-kb-decline_payment', 'text': '❌ Я не получил денег', 'text_ru': '❌ Я не получил денег', 'text_en': 'уцуйц'}, {'name': 'trade-kb-view_on', 'text': 'Посмотреть на {name}', 'text_ru': 'Посмотреть на {name}', 'text_en': 'wqe'}, {'name': 'trade-confirm_transaction', 'text': 'С Вами начали сделку \r\n\r\nПользователь Вам отправил {amount} {currency}\r\nна ваш адрес \r\n```{address}```\r\n\r\nПроверьте пришло ли вам {amount} {currency}\r\nХэш транзакции для проверки\r\n```{tx_hash}```', 'text_ru': 'С Вами начали сделку \r\n\r\nПользователь Вам отправил {amount} {currency}\r\nна ваш адрес \r\n```{address}```\r\n\r\nПроверьте пришло ли вам {amount} {currency}\r\nХэш транзакции для проверки\r\n```{tx_hash}```', 'text_en': 'ewrwer'}, {'name': 'trade-semi_automatic_start', 'text': 'Переведите {amount} {currency} \r\nна адрес ```{address}```\r\n\r\nПосле оплаты, сбросьте в бота хэш-транзакции', 'text_ru': 'Переведите {amount} {currency} \r\nна адрес ```{address}```\r\n\r\nПосле оплаты, сбросьте в бота хэш-транзакции', 'text_en': ''}, {'name': 'order-kb-cancel_order', 'text': 'Отменить создание объявления', 'text_ru': 'Отменить создание объявления', 'text_en': ''}, {'name': 'trade-second_confirm_transaction', 'text': 'Вы точно уверены, что получили {amount} {currency} \r\n\r\nНа адрес {address}', 'text_ru': 'Вы точно уверены, что получили {amount} {currency} \r\n\r\nНа адрес {address}', 'text_en': ''}, {'name': 'trade-success_trade', 'text': 'Вы {type_operation} {amount} {trade_currency} \r\nза {price_trade} {payment_currency}', 'text_ru': 'Вы {type_operation} {amount} {trade_currency} \r\nза {price_trade} {payment_currency}', 'text_en': ''}, {'name': 'order-type_operation_translate_sale_3', 'text': 'Продажа {currency}', 'text_ru': 'Продажа {currency}', 'text_en': ''}, {'name': 'order-type_operation_translate_buy_3', 'text': 'Покупка {currency}', 'text_ru': 'Покупка {currency}', 'text_en': ''}, {'name': 'order-enter_amount_for_sale', 'text': 'Введите сумму {currency}, которую хотите продать\r\nВсего доступно к продаже: {amount} {currency}', 'text_ru': 'Введите сумму {currency}, которую хотите продать\r\nВсего доступно к продаже: {amount} {currency}', 'text_en': 'eter'}, {'name': 'trade-enter_amount_for_trade', 'text': 'Введите желаемую сумму для обмена\r\n\r\nВсего доступно: {amount} {currency}', 'text_ru': 'Введите желаемую сумму для обмена\r\n\r\nВсего доступно: {amount} {currency}', 'text_en': ''}, {'name': 'order-kb-average_rate', 'text': 'Выбрать средний курс', 'text_ru': 'Выбрать средний курс', 'text_en': ''}, {'name': 'order-kb-max_amount', 'text': 'Выбрать максимальную сумму', 'text_ru': 'Выбрать максимальную сумму', 'text_en': ''}, {'name': 'order-order_info', 'text': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n1 {trade_currency} – {rate_1} {payment_currency}\r\n1 {payment_currency} – {rate_2} {trade_currency}\r\n\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: {price_order} {payment_currency}', 'text_ru': '📰️ ID: #{order_id}\r\n**{type_operation} {trade_currency} за {payment_currency} **\r\n\r\n**Цена**: \r\n1 {trade_currency} – {trade_currency_rate_usd} USD\r\n1 {trade_currency} – {rate_1} {payment_currency}\r\n1 {payment_currency} – {rate_2} {trade_currency}\r\n\r\n**Доступный объем**: {amount}  {trade_currency}\r\n**На сумму**: {price_order} {payment_currency}', 'text_en': 'ikjj'}, {'name': 'wallet-hold_money', 'text': '\U0001f9ca **Заблокировано под торговлю**:\r\n{hold_money}', 'text_ru': '\U0001f9ca **Заблокировано под торговлю**:\r\n{hold_money}', 'text_en': ''}, {'name': 'order-enter_amount_for_buy', 'text': 'Введите сумму {currency}, которую хотите купить', 'text_ru': 'Введите сумму {currency}, которую хотите купить', 'text_en': ''}, {'name': 'order-kb-show_deposit_address', 'text': 'Адрес пополнения {currency}', 'text_ru': 'Адрес пополнения {currency}', 'text_en': ''}, {'name': 'order-kb-continue_with', 'text': 'Продолжить с {currency}', 'text_ru': 'Продолжить с {currency}', 'text_en': ''}, {'name': 'order-kb-back_to_select_payment_currency', 'text': '🔙 Вернуться к выбору платежной валюты', 'text_ru': '🔙 Вернуться к выбору платежной валюты', 'text_en': ''}, {'name': 'order-kb-create_order', 'text': 'Продолжить', 'text_ru': 'Продолжить', 'text_en': ''}, {'name': 'wallet-select_currency_withdrawal', 'text': 'Выберите валюту, которую желаете вывести', 'text_ru': 'Выберите валюту, которую желаете вывести', 'text_en': ''}, {'name': 'trade-confirm_amount_for_trade', 'text': 'Вы желаете {type_operation} **{amount} {trade_currency}** за **{price_trade} {payment_currency}** ?\r\n\r\nКомиссия за обмен составит: **{fee_amount} {currency}**', 'text_ru': 'Вы желаете {type_operation} **{amount} {trade_currency}** за **{price_trade} {payment_currency}** ?\r\n\r\nКомиссия за обмен составит: **{fee_amount} {currency}**', 'text_en': 'eqwewq'}, {'name': 'you_selected', 'text': 'Вы выбрали: {foo}', 'text_ru': 'Вы выбрали: {foo}', 'text_en': ''}, {'name': 'wallet-enter_amount_for_withdrawal', 'text': 'Введите сумму для вывода\r\n\r\nМаксимальная сумма для вывода: {max_amount} {currency}', 'text_ru': 'Введите сумму для вывода\r\n\r\nМаксимальная сумма для вывода: {max_amount} {currency}', 'text_en': ''}, {'name': 'wallet-select_requisite_for_withdrawal', 'text': 'Выберите реквизиты на которые желаете вывести {currency}', 'text_ru': 'Выберите реквизиты на которые желаете вывести {currency}', 'text_en': ''}, {'name': 'wallet-confirm_withdrawal', 'text': 'Вы желаете вывести {amount} {currency} на адрес {address} ?', 'text_ru': 'Вы желаете вывести {amount} {currency} на адрес {address} ?', 'text_en': ''}, {'name': 'admin-kb-withdrawal_requests', 'text': '📤 Заявки на вывод', 'text_ru': '📤 Заявки на вывод', 'text_en': ''}, {'name': 'bot-withdrawal_request_info', 'text': 'Заявка №{id}\r\n\r\nПользователь: {user}\r\nСумма вывода: {amount}\r\nВалюта вывода: {currency}\r\n\r\nАдрес:  ```{address}```', 'text_ru': 'Заявка №{id}\r\n\r\nПользователь: {user}\r\nСумма вывода: {amount}\r\nВалюта вывода: {currency}\r\n\r\nАдрес:  ```{address}```', 'text_en': ''}, {'name': 'admin-kb-withdrawal_send_tx', 'text': 'Отправить tx hash', 'text_ru': 'Отправить tx hash', 'text_en': ''}, {'name': 'admin-kb-withdrawal_cancel', 'text': 'Отказать в выводе', 'text_ru': 'Отказать в выводе', 'text_en': ''}, {'name': 'admin-await_withdrawal_tx_hash', 'text': 'Сбросьте tx hash', 'text_ru': 'Сбросьте tx hash', 'text_en': ''}, {'name': 'admin-kb-send_tx-hash', 'text': 'Отправить', 'text_ru': 'Отправить', 'text_en': ''}, {'name': 'admin-kb-edit_tx_hash', 'text': 'Изменить', 'text_ru': 'Изменить', 'text_en': ''}, {'name': 'wallet-hold_money_for_withdrawal', 'text': '📤 Заблокировано под вывод:\r\n{hold_money}', 'text_ru': '📤 Заблокировано под вывод:\r\n{hold_money}', 'text_en': ''}, {'name': 'wallet-kb-cancel_withdrawal', 'text': '🚫 Отменить вывод средств', 'text_ru': '🚫 Отменить вывод средств', 'text_en': ''}, {'name': 'wallet-confirm_refusal_withdrawal', 'text': 'Вы желаете отменить вывод {amount} {currency}', 'text_ru': 'Вы желаете отменить вывод {amount} {currency}', 'text_en': ''}, {'name': 'admin-confirm_tx_hash_withdrawal', 'text': 'Проверьте правильность указанных данных \r\n{tx_hash}', 'text_ru': 'Проверьте правильность указанных данных \r\n{tx_hash}', 'text_en': ''}, {'name': 'wallet-successful_withdrawal', 'text': 'Вы успешно вывели {amount} {currency}\r\n\r\nНа адрес: {address}', 'text_ru': 'Вы успешно вывели {amount} {currency}\r\n\r\nНа адрес: {address}', 'text_en': ''}, {'name': 'wallet-denied withdrawal', 'text': 'Вам отказано в выводе на сумму {amount} {currency}', 'text_ru': 'Вам отказано в выводе на сумму {amount} {currency}', 'text_en': ''}, {'name': 'trade-trade_amount_more_than_order_amount', 'text': 'Но у объявления закончился резерв', 'text_ru': 'Но у объявления закончился резерв', 'text_en': ''}, {'name': 'wallet-select_currency_for_convert_bonus', 'text': 'Выберите валюту на которую будут начислены бонусы', 'text_ru': 'Выберите валюту на которую будут начислены бонусы', 'text_en': ''}]

        Text.objects.bulk_create([Text(**q) for q in txts])

        print('Successful installation of texts')

