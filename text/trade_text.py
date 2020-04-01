from model import TempPaymentCurrency

trade_menu = '💸 **Обмен**\n\n' \
               'Здесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.'


#buy = '📋 Доступны объявления на продажу в следующих категориях платёжных инструментов'

choice_trade_currency = 'Выберите какую валюту Вы хотите обменять:'

error_empty_trade_currency = 'Сначала выбери валюту'

enter_exchange_rate = 'Введите стоимость'

error_enter = 'Некорректные данные'

enter_count = 'Введите точное количество валюты, которую желаете купить/продать'


sale = '📋 Доступны объявления на покупку в следующих категориях платёжных инструментов'


def error_limit(limit):
    txt = f'Ошибка. Превышен лими.\n' \
        f'Ваш лимит {limit}'

    return txt


def choice_payment_currency(user_id):
    payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user_id)

    txt = '**Выберите свой платёжный инструмент**\n\n'
    if payment_currency:
        txt += 'Ваш выбор:\n'
        for curr in payment_currency:
            txt += f'**{curr.payment_currency.name}**\n'

    return txt


def indicate_requisites(currency_name):
    txt = f'В портмоне у вас отсутствуют реквизиты для **{currency_name}**\n\n' \
        f'Введите, пожалуйста, реквизиты'

    return txt


def pending_payment(trade_currency):
    bot_addresses = {1: 'bip address',
                     2: 'btc address',
                     3: 'usdt address',
                     4: 'eth address',
                     5: 'usd address',
                     6: 'rub address'}

    txt = f'Сбросьте сюда денюжку {bot_addresses[trade_currency]}\n\n' \
        f'Подтверждение платежа в автоматическом режиме'

    return txt


def enter_amount_for_sale(limit):
    txt = f'Введите точную сумму сколько желаете продать\n' \
        f'Или диапазон от 0 до {limit}'

    return txt