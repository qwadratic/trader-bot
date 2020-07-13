from requests import Session
from cachetools.func import ttl_cache
import json

from bot.helpers.shortcut import get_currency_rate, to_units

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
    return to_units(currency, get_currency_rate(currency)) * amount


def currency_in_user_currency(currency, user_currency, amount):
    currency_rate = to_units(currency, get_currency_rate(currency))
    user_currency_rate = to_units(user_currency, get_currency_rate(user_currency))

    return currency_rate * amount * user_currency_rate
