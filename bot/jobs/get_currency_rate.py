import json

from bot.helpers.shortcut import to_cents

from bot.models import ExchangeRate
from requests import Session
from bot.blockchain.bithumb_api import BithumbGlobalRestAPI
from binance.client import Client

from config.settings import BH_API_KEY, BH_SECRET_KEY, BIN_API_KEY, BIN_API_SECRET
import logging

import rollbar

from config.settings import POST_SERVER_ITEM_ACCESS_TOKEN

logger = logging.getLogger('TradeErrors')
rollbar.init(POST_SERVER_ITEM_ACCESS_TOKEN, 'production')

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
    try:
        coin = data['data']['quote']['USD']['price']
        return coin
    except KeyError:
        rollbar.report_message('You have exceeded your API Keys monthly credit limit. API info: %s'%(data))
        logger.warning('You have exceeded your API Keys monthly credit limit. API info: %s'%(data))


def bithumb_currency_usdt(currency):
    api = BithumbGlobalRestAPI(BH_API_KEY, BH_SECRET_KEY)
    symbol = '%s-USDT'%(currency)
    depth = api.depth(symbol, count=1)

    asks_usdt = depth['asks'][0][0]
    bids_usdt = depth['bids'][0][0]
    average_exchange_rate = (asks_usdt + bids_usdt)/2

    return average_exchange_rate

def binance_currency_usdt(currency):
    client = Client(api_key=BIN_API_KEY, api_secret=BIN_API_SECRET)

    currency_list = ['BTC', 'ETH']

    if currency in currency_list:
        depth = client.get_order_book(symbol='%sUSDT' % (currency))
        asks_usdt = float(depth['asks'][0][0])
        bids_usdt = float(depth['bids'][0][0])
    else:
        depth = client.get_order_book(symbol='USDT%s' % (currency))
        asks_usdt = 1 / float(depth['asks'][0][0])
        bids_usdt = 1 / float(depth['bids'][0][0])

    average_exchange_rate = (asks_usdt + bids_usdt) / 2
    return average_exchange_rate


def update_exchange_rates():
    currency_list = ['BIP', 'BTC', 'USDT', 'ETH', 'UAH', 'RUB']
    sources = {'coinmarketcup': coinmarket_currency_usd,
                'bithumb': bithumb_currency_usdt, 'binance': binance_currency_usdt}

    rate_list = []
    for currency in currency_list:
        for s in sources:
            try:
                rate = sources[s](currency)
                rate_list.append(dict(
                    currency=currency,
                    source=s,
                    value=to_cents('USD', rate)
                ))
            except:
                pass

    ExchangeRate.objects.bulk_create([ExchangeRate(**r) for r in rate_list])