from configparser import ConfigParser


BOT_CFG = 'bot.cfg'


def get_token():
    parser = ConfigParser()
    parser.read(BOT_CFG)
    return parser['pyrogram']['bot_token']


def get_session_name():
    parser = ConfigParser()
    parser.read(BOT_CFG)
    return parser['pyrogram']['session_name']


def get_db_settings():
    parser = ConfigParser()
    parser.read(BOT_CFG)
    return parser['db']


def get_keys_liqpey():
    parser = ConfigParser()
    parser.read(BOT_CFG)
    keys = {'public': parser['liqpay']['public_key'],
            'private': parser['liqpay']['private_key']}
    return keys



class PriceSeed:

    @classmethod
    def photo_1(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return int(parser['price_photo']['photo_1'])

    @classmethod
    def photo_20_100(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return int(parser['price_photo']['photo_20_100'])

    @classmethod
    def photo_100_500(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return float(parser['price_photo']['photo_100_500'])

    @classmethod
    def photo_500_1000(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return int(parser['price_photo']['photo_500_1000'])

    @classmethod
    def auto_1(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return int(parser['price_auto']['auto_1'])

    @classmethod
    def auto_20_100(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return float(parser['price_auto']['auto_20_100'])

    @classmethod
    def auto_100_500(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return int(parser['price_auto']['auto_100_500'])

    @classmethod
    def auto_500_1000(cls):
        parser = ConfigParser()
        parser.read(BOT_CFG)
        return int(parser['price_auto']['auto_500_1000'])


def get_price_deliv(country):
    parser = ConfigParser()
    parser.read(BOT_CFG)
    if country == 1:
        return int(parser['delprice']['ua'])
    else:
        return int(parser['delprice']['other'])
