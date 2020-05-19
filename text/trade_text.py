from bot_tools import converter
from model import TempPaymentCurrency

trade_menu = '💸 **Обмен**\n\n' \
               'Здесь Вы совершаете сделки с людьми, а бот выступает в качестве гаранта безопасности при проведении сделки.'


#buy = '📋 Доступны объявления на продажу в следующих категориях платёжных инструментов'

choice_trade_currency_for_sell = 'Выберите какую валюту Вы хотите Продать:'

choice_trade_currency_for_buy = 'Выберите какую валюту Вы хотите Купить:'

error_empty_trade_currency = 'Сначала выбери валюту'

enter_exchange_rate2 = 'Введите стоимость'

error_enter = 'Некорректные данные'

enter_count = 'Введите точное количество валюты, которую желаете купить/продать'


sale = '📋 Доступны объявления на покупку в следующих категориях платёжных инструментов'

await_respond_from_seller = 'Ожидайте подтверждения продавца'

await_respond_from_buyer = 'Ожадайте подтверждения покупателя'


def start_deal(announcement_id):
    from core.trade_core import deal_info
    txt = '**Пользователь хочет начать с Вами сделку по этому объявлению**\n\n'
    txt += deal_info(announcement_id)
    return txt


def error_limit(limit):
    txt = f'Ошибка. Превышен лимит.\n' \
        f'Ваш лимит {limit}'

    return txt


def choice_payment_currency(user_id):
    payment_currency = TempPaymentCurrency.select().where(TempPaymentCurrency.user_id == user_id)

    txt = '**Выберите свой платёжный инструмент**\n\n'
    if payment_currency:
        txt += 'Ваш выбор:\n'
        for curr in payment_currency:
            txt += f'**{curr.payment_currency}**\n'

    return txt


def indicate_requisites(currency):
    txt = f'В портмоне у вас отсутствуют реквизиты для **{currency}**\n\n' \
        f'Введите, пожалуйста, реквизиты'

    return txt


def pending_payment_for_sale(trade_currency):
    #  TODO реальные адреса
    bot_addresses = {'BIP': 'bip address',
                     'BTC': 'btc address',
                     'USDT': 'usdt address',
                     'ETH': 'eth address',
                     'USD': 'usd address',
                     'RUB': 'rub address',
                     'UAH': 'uah address'}

    txt = f'Сбросьте сюда денюжку {bot_addresses[trade_currency]}\n\n' \
        f'Подтверждение платежа в автоматическом режиме'

    return txt


def pending_payment_for_buy(temp_payment_currency):
    bot_addresses = {'BIP': 'bip address',
                     'BTC': 'btc address',
                     'USDT': 'usdt address',
                     'ETH': 'eth address',
                     'USD': 'usd address',
                     'RUB': 'rub address',
                     'UAH': 'uah address'}
    txt = 'Сбросьте сюда денюжку\n\n'
    for curr in temp_payment_currency:
        txt += f'{bot_addresses[curr.payment_currency_id]}\n'

    txt += 'Подтверждение платежа в автоматическом режиме'

    return txt


def enter_amount_for_sale(limit):
    txt = f'Введите точную сумму сколько желаете продать\n' \
        f'Или диапазон от 0 до {limit}'

    return txt


def enter_amount_for_buy(user_currency):
    currency_in_usd = converter.currency_in_usd(user_currency, 1)


    txt = f'Введите сумму сколько желаете купить\n' \
        f'Цена за '

    return txt


def payment_details(requisites):

    txt = f'Переведите на этот счёт {requisites}\n\n' \
        f'Сумму денег'

    return txt


def enter_exchange_rate(trade_currency):
    txt = f'Введите желаемую стоимость криптовалюты в долларах\n\n'
    price = converter.currency_in_usd(trade_currency, 1)

    txt += f'Средняя цена за {trade_currency}: {price} USD'

    return txt