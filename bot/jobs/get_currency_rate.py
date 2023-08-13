import json
from decimal import Decimal

from bot.helpers.shortcut import to_cents

from bot.models import ExchangeRate
from requests import Session
from bot.blockchain.bithumb_api import BithumbGlobalRestAPI, BithumbGlobalError
from binance.client import Client, BinanceAPIException

from config.settings import BIN_API_KEY, BIN_API_SECRET # BH_API_KEY, BH_SECRET_KEY,
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
        rollbar.report_message(f'You have exceeded your API Keys monthly credit limit. API info: {data}')
        logger.warning(f'You have exceeded your API Keys monthly credit limit. API info: {data}')
        return None


# def bithumb_currency_usdt(currency):
#     try:
#         api = BithumbGlobalRestAPI(BH_API_KEY, BH_SECRET_KEY)
#         symbol = f'{currency}-USDT'
#         depth = api.depth(symbol, count=1)

#         asks_usdt = depth['asks'][0][0]
#         bids_usdt = depth['bids'][0][0]
#         average_exchange_rate = (asks_usdt + bids_usdt)/2

#         return average_exchange_rate
#     except BithumbGlobalError as info:
#         rollbar.report_message(f'Error bithumb API update data: {info}')
#         logger.warning(f'Error bithumb API update data: {info}')


def binance_currency_usdt(currency):
    client = Client(api_key=BIN_API_KEY, api_secret=BIN_API_SECRET)

    currency_list = ['BTC', 'ETH', 'USDT']

    try:
        if currency in currency_list:
            depth = client.get_order_book(symbol=f'{currency}USDT')
            asks_usdt = Decimal(depth['asks'][0][0])
            bids_usdt = Decimal(depth['bids'][0][0])
        else:
            depth = client.get_order_book(symbol=f'USDT{currency}')
            asks_usdt = 1 / Decimal(depth['asks'][0][0])
            bids_usdt = 1 / Decimal(depth['bids'][0][0])

        average_exchange_rate = (asks_usdt + bids_usdt) / 2
        return average_exchange_rate
    except BinanceAPIException as info:
        #rollbar.report_message(f'Error binance API update data: {info}')
        logger.warning(f'Error binance API update data: {info}')
        return None


def update_exchange_rates():
    currency_list = ['BIP', 'BTC', 'USDT', 'ETH', 'UAH', 'RUB']
    sources = {'coinmarketcup': coinmarket_currency_usd,
               'binance': binance_currency_usdt}

    rate_list = []
    for currency in currency_list:
        for s in sources:
            rate = sources[s](currency)
            if rate:
                    rate_list.append(dict(
                        currency=currency,
                        source=s,
                        value=to_cents(currency, rate)
                    ))

    ExchangeRate.objects.bulk_create([ExchangeRate(**r) for r in rate_list])
