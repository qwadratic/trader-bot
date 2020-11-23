from pyrogram import Filters
from user.models.user import Text, TelegramUser
from user.models.user import TelegramUser
from bot.helpers.shortcut import get_user
from django.utils.translation import activate
from bot.models.text import Text

ref_link = Filters.create(lambda _, m: len(m.command) > 1)

filter_admin = Filters.user([69062067, 373283223, 862797627, 263425422])


def _unknown_command(_, m):
    user = get_user(m.from_user.id)
    activate(user.settings.language)
    query = Text.objects.filter(name__regex="-kb-")
    texts = [t.text for t in query]
    if m.text in texts:
        return False

    return True


unknown_command = Filters.create(
    name='unknwn comm',
    func=_unknown_command
)


def _active_flag(_, m):
    user = get_user(m.from_user.id)

    flags = user.flags

    if flags.in_trade \
        or flags.await_requisites_for_order \
        or flags.await_currency_rate \
        or flags.await_requisite_for_order \
        or flags.await_amount_for_order \
        or flags.await_amount_for_trade \
        or flags.await_tx_hash \
        or flags.await_requisites_address \
        or flags.await_requisites_name \
        or flags.edit_requisite \
        or flags.await_replenishment_for_order \
        or flags.await_amount_for_withdrawal \
        or flags.await_tx_hash_for_withdrawal \
        or flags.await_replenishment_for_trade \
        or flags.await_amount_for_convert_bonus \
        or flags.await_requisites_for_order \
        or flags.await_currency_rate \
        or flags.await_requisite_for_order \
        or flags.await_amount_for_order \
        or flags.await_amount_for_trade \
        or flags.await_tx_hash \
        or flags.await_requisites_address \
        or flags.edit_requisite \
        or flags.await_requisites_name \
        or flags.await_replenishment_for_order \
        or flags.await_amount_for_withdrawal \
        or flags.await_tx_hash_for_withdrawal \
        or flags.await_replenishment_for_trade \
        or flags.await_amount_for_convert_bonus:
        return True


active_flag = Filters.create(
    name='active flag',
    func=_active_flag
)

