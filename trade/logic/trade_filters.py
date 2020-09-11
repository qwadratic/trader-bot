from time import sleep

from pyrogram import Filters

from bot.helpers.shortcut import get_user
from trade.logic import kb


def _in_trade(_, m):
    user = get_user(m.from_user.id)

    if not user:
        return False

    flags = user.flags
    if flags.in_trade:
        m.delete()

        msg = m.reply(user.get_text(name='trade-in_trade'), reply_markup=kb.cancel_trade(user))
        sleep(5)
        msg.delete()

        return False
    else:
        return True


in_trade = Filters.create(
    name='in trade filter',
    func=_in_trade
)


