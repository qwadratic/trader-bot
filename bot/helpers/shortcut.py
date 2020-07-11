from bot.blockchain import minterAPI, ethAPI
from user.models import TelegramUser


def get_user(tg_id):
    return TelegramUser.objects.get_or_none(telegram_id=tg_id)


def delete_msg(cli, user_id, msg):
    try:
        cli.delete_messages(user_id, msg)
    except Exception:
        pass


def check_address(address, currency):

    valid = False

    if currency == 'BIP':
        re = minterAPI.Minter.get_balance(address)
        if 'result' in re:
            valid = True

    if currency in ['ETH', 'USDT']:
        try:
            re = ethAPI.get_balance(address, currency)
            valid = True
        except ValueError:
            pass

    # TODO костыль
    if currency not in ['ETH', 'USDT', 'BIP']:
        valid = True

    return valid


