from requests import Session
from cachetools.func import ttl_cache
import json

url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'e483e77c-d563-42c1-8f04-4b719ae1ff7a',
}
session = Session()
session.headers.update(headers)


@ttl_cache(ttl=3600)
def bip_in_usd(amount):
    global session
    parameters = {
        'symbol': 'BIP',
        'amount': amount,
        'convert': 'USD'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    return data['data']['quote']['USD']['price']


@ttl_cache(ttl=3600)
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


@ttl_cache(ttl=3600)
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


@ttl_cache(ttl=3600)
def uah_in_usd(amount):
    global session
    parameters = {
        'symbol': 'UAH',
        'amount': amount,
        'convert': 'USD'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['USD']['price']


@ttl_cache(ttl=3600)
def rub_in_usd(amount):
    global session
    parameters = {
        'symbol': 'RUB',
        'amount': amount,
        'convert': 'USD'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['USD']['price']


@ttl_cache(ttl=3600)
def bip_in_uah(amount):
    global session
    parameters = {
        'symbol': 'BIP',
        'amount': amount,
        'convert': 'UAH'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    return data['data']['quote']['UAH']['price']


@ttl_cache(ttl=3600)
def eth_in_uah(amount):
    global session
    parameters = {
        'symbol': 'ETH',
        'amount': amount,
        'convert': 'UAH'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['UAH']['price']


@ttl_cache(ttl=3600)
def usdt_in_uah(amount):
    global session
    parameters = {
        'symbol': 'USDT',
        'amount': amount,
        'convert': 'UAH'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['UAH']['price']


@ttl_cache(ttl=3600)
def bip_in_rub(amount):
    global session
    parameters = {
        'symbol': 'BIP',
        'amount': amount,
        'convert': 'RUB'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    return data['data']['quote']['RUB']['price']


@ttl_cache(ttl=3600)
def eth_in_rub(amount):
    global session
    parameters = {
        'symbol': 'ETH',
        'amount': amount,
        'convert': 'RUB'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['RUB']['price']


@ttl_cache(ttl=3600)
def usdt_in_rub(amount):
    global session
    parameters = {
        'symbol': 'USDT',
        'amount': amount,
        'convert': 'RUB'
    }
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    return data['data']['quote']['UAH']['price']


def currency_in_usd(currency, amount):
    price = amount

    if currency == 'BIP':
        price = bip_in_usd(amount)

    elif currency == 'ETH':
        price = eth_in_usd(amount)

    elif currency == 'USDT':
        price = usdt_in_usd(amount)

    elif currency == 'UAH':
        price = uah_in_usd(amount)

    elif currency == 'RUB':
        price = rub_in_usd(amount)

    return price


def currency_in_user_currency(currency, user_currency, amount):

    d = {('BIP', 'USD'): bip_in_usd,
         ('BIP', 'UAH'): bip_in_uah,
         ('BIP', 'RUB'): bip_in_rub,
         ('ETH', 'USD'): eth_in_usd,
         ('ETH', 'UAH'): eth_in_uah,
         ('ETH', 'RUB'): eth_in_rub,
         ('USDT', 'USD'): usdt_in_usd,
         ('USDT', 'UAH'): usdt_in_uah,
         ('USDT', 'RUB'): usdt_in_rub
         }

    return d[currency, user_currency](amount)