import json

from bot.helpers.shortcut import to_cents

from bot.models import ExchangeRate, Settings
from requests import Session
import logging

import rollbar

from config.settings import POST_SERVER_ITEM_ACCESS_TOKEN

logger = logging.getLogger('TradeJobs')
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
        logging.warning('You have exceeded your API Keys monthly credit limit. API info: %s'%(data))



def update_exchange_rates():
    currency_list = ['BIP', 'BTC', 'USDT', 'ETH', 'UAH', 'RUB']
    sources = {'coinmarketcup': coinmarket_currency_usd}

    rate_list = []
    try:
        for currency in currency_list:
            for s in sources:
                rate = to_cents(currency, sources[s](currency))

                rate_list.append(dict(
                    currency=currency,
                    source=s,
                    value=rate
                ))

        ExchangeRate.objects.bulk_create([ExchangeRate(**r) for r in rate_list])
    except Exception as ex:
        rollbar.report_message('ExchangeRate doesn`t update. Exception: %s'%(ex))
        logger.warning('ExchangeRate doesn`t update. Exception: %s'%(ex))


def get_update_exchange_rates_interval():
    try:
        interval = Settings.objects.get().update_rate_interval
    except Exception:
        set = Settings.objects.create()
        interval = set.update_rate_interval

    return interval