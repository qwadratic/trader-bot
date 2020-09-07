import json

from bot.helpers.shortcut import to_cents

from bot.models import ExchangeRate, Settings
from requests import Session
from bot.blockchain.bithumb_api import BithumbGlobalRestAPI, \
    API_KEY, SECRET_KEY
from binance.client import Client

from config.settings import BIN_API_KEY, BIN_API_SECRET


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

def bithumb_currency_usdt(currency):
    api = BithumbGlobalRestAPI(API_KEY, SECRET_KEY)
    symbol = '%s-USDT'%(currency)
    depth = api.depth(symbol, count=1)

    asks_usdt = depth['asks'][0][0]
    bids_usdt = depth['bids'][0][0]
    average_exchange_rate = (asks_usdt + bids_usdt)/2

    return average_exchange_rate

def binance_currency_usdt(currency):
    client = Client(BIN_API_KEY, BIN_API_SECRET)
    depth = client.get_order_book(symbol='%sBTC'%(currency))

    return  depth


def update_exchange_rates():
    currency_list = ['BIP', 'BTC', 'USDT', 'ETH', 'UAH', 'RUB']
    currency_list_2 = ['USDT', 'UAH', 'RUB']
    source_c = {'coinmarketcup': coinmarket_currency_usd}
    source_b = {'bithumb': bithumb_currency_usdt}

    rate_list = []
    for currency in currency_list:
        for s in source_c:
            rate = source_c[s](currency)
            rate_list.append(dict(
                currency=currency,
                source=s,
                value=rate
            ))

        for s in source_b:  # TODO if exceeded API Key's monthly credit limit coinmarketcup - use bithumb
            for keys in rate_list:
                try:
                    rate = source_b[s](currency)
                    if keys['currency'] == currency and keys['source'] != s:
                        keys.update({'source': '%s/%s' % (keys['source'], s),
                                        'value': to_cents('USD', ((keys['value'] + rate) / 2))})

                except TypeError:
                    a = keys.values()
                    for i in a:
                        for currency in currency_list_2:
                            if i in currency_list_2:
                                i = to_cents('USD', keys['value'])
                                keys.update({'value': i})
                                currency_list_2.remove(currency)

    ExchangeRate.objects.bulk_create([ExchangeRate(**r) for r in rate_list])

