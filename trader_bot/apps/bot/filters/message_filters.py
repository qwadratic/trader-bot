from pyrogram import Filters

from ..helpers import get_user


def _bot_menu(m):
    user = get_user(m.from_user.id)

