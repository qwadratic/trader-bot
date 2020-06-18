from django.db.models import Manager

from trader_bot.apps.user.models import TelegramUser

def get_user(tg_id):
    return TelegramUser.objects.get_or_none(telegram_id=tg_id)


def delete_msg(cli, user_id, msg):
    try:
        cli.delete_messages(user_id, msg)
    except Exception:
        pass
