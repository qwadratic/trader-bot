from json import loads as load_json
import requests
from config.settings import BH_API_KEY, BH_SECRET_KEY

DEPTH_URL = 'https://global-openapi.bithumb.pro/market/data/orderBook?symbol='
API_KEY = BH_API_KEY
SECRET_KEY = BH_SECRET_KEY

class BithumbGlobalError(RuntimeError):
    def __init__(self, code, msg):
        super().__init__('[%s] %s' % (code, msg))


SIDE_MAP = {
    'ask': 'sell',
    'bid': 'buy',
    'sell': 'sell',
    's': 'sell',
    'buy': 'buy',
    'a': 'sell',
    'b': 'buy',
}


def direction(direction):
    return SIDE_MAP[direction.lower()]


def depth(data):
    data = data['info']
    asks = [(float(row[0]), float(row[1])) for row in data['s']]
    bids = [(float(row[0]), float(row[1])) for row in data['b']]

    return {'asks': asks, 'bids': bids}

class Secret:
    def __init__(self, api_key, secret_code):
        self.__api_key = api_key
        self.__secret_code = secret_code.encode()

    @property
    def api_key(self):
        return self.__api_key


class BithumbGlobalRestAPI:
    def __init__(self, api_key, secret_code):
        if api_key and secret_code:
            self.__secret = Secret(api_key, secret_code)
        else:
            self.__secret = None
        self.__session = session = requests.session()
        session.headers.update({'content-Type': 'application/json'})

    def depth(self, symbol, count):
        url = DEPTH_URL + symbol.replace('/', '-')
        data = load_json(self.__session.get(url, timeout=5).text)
        return depth(data)