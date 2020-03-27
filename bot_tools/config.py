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
