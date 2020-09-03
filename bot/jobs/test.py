from decimal import Decimal

from bot.blockchain.bithumb_api import BithumbGlobalRestAPI, API_KEY, SECRET_KEY



def bithumb_currency_usd():
    a = BithumbGlobalRestAPI(API_KEY, SECRET_KEY)
    return a

b = bithumb_currency_usd()
currency = 'BTC'
def bithumb_currency_usdt(currency):
    api = BithumbGlobalRestAPI(API_KEY, SECRET_KEY)
    symbol = '%s-USDT'%(currency)
    depth = api.depth(symbol, count=0)
    asks_usdt = depth['asks'][0][0]
    bids_usdt = depth['bids'][0][0]
    #a = (asks_usdt + bids_usdt)/2
    return bids_usdt, asks_usdt
n = bithumb_currency_usdt(currency)

if __name__=='__main__':
        print(n)