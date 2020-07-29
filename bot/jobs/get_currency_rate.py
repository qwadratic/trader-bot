import json

from bot.helpers.shortcut import to_cents

from bot.models import ExchangeRate, Settings
from requests import Session


def coinmarket_currency_usd(currency):
    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'e483e77c-d563-42c1-8f04-4b719ae1ff7a',
    }
    session = Session()
    session.headers.update(headers)

    parameters = {
        'symbol': currency,
        'amount': 1,
        'convert': 'USD'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['USD']['price']


def update_exchange_rates():
    currency_list = ['BIP', 'BTC', 'USDT', 'ETH', 'UAH', 'RUB']
    sources = {'coinmarketcup': coinmarket_currency_usd}

    rate_list = []
    for currency in currency_list:
        for s in sources:
            rate = to_cents(currency, sources[s](currency))

            rate_list.append(dict(
                currency=currency,
                source=s,
                value=rate
            ))

    ExchangeRate.objects.bulk_create([ExchangeRate(**r) for r in rate_list])


def get_update_exchange_rates_interval():
    try:
        interval = Settings.objects.get().update_rate_interval
    except Exception:
        set = Settings.objects.create()
        interval = set.update_rate_interval

    return interval