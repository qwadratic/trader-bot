from requests import Request, Session
from cachetools.func import ttl_cache
import json

url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'e483e77c-d563-42c1-8f04-4b719ae1ff7a',
}
session = Session()
session.headers.update(headers)


@ttl_cache(ttl=60)
def bip_in_usd(amount):
    global session
    parameters = {
        'symbol': 'BIP',
        'amount': amount,
        'convert': 'USD'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    print(data)
    return data['data']['quote']['USD']['price']


@ttl_cache(ttl=60)
def eth_in_usd(amount):
    global session
    parameters = {
        'symbol': 'ETH',
        'amount': amount,
        'convert': 'USD'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['USD']['price']


@ttl_cache(ttl=60)
def usdt_in_usd(amount):
    global session
    parameters = {
        'symbol': 'USDT',
        'amount': amount,
        'convert': 'USD'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['USD']['price']
