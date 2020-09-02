from requests import Session

from bot.helpers.shortcut import get_currency_rate, to_units

url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'e483e77c-d563-42c1-8f04-4b719ae1ff7a',
}
session = Session()
session.headers.update(headers)


def currency_in_usd(currency, amount):
    return to_units(currency, get_currency_rate(currency)) * amount


def currency_in_user_currency(currency, user_currency, amount):
    currency_rate = to_units('USD', get_currency_rate(currency))
    user_currency_rate = to_units('USD', get_currency_rate(user_currency))

    return currency_rate * amount * user_currency_rate
