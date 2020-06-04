from pyrogram import Filters

from model import User

ref_link = Filters.create(lambda _, m: len(m.command) > 1)


class UserMessageFilter:

    create = Filters.create

    await_currency_value = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id) and User.get_or_none(tg_id=m.from_user.id).flags.await_currency_value)

    await_amount = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id) and User.get_or_none(tg_id=m.from_user.id).flags.await_amount_for_trade)

    requisites_for_trade = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id) and User.get_or_none(tg_id=m.from_user.id).flags.requisites_for_trade)

    requisites_for_start_deal = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id) and User.get_or_none(tg_id=m.from_user.id).flags.requisites_for_start_deal)

    await_amount_for_deal = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id) and User.get_or_none(tg_id=m.from_user.id).flags.await_amount_for_deal)

    await_requisites_address = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id) and User.get_or_none(tg_id=m.from_user.id).flags.await_requisites_address)

    await_requisites_name = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id) and User.get_or_none(tg_id=m.from_user.id).flags.await_requisites_name)