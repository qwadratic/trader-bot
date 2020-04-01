from pyrogram import Filters

from model import User


class UserMessageFilter:

    create = Filters.create

    await_exchange_rate = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.flag == 1)

    await_amount = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.flag == 2)

    await_requisite_bip = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.purse_flag == 1)

    await_requisite_btc = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.purse_flag == 2)

    await_requisite_usdt = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.purse_flag == 3)

    await_requisite_etg = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.purse_flag == 4)

    await_requisite_usd = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.purse_flag == 5)

    await_requisite_rub = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.purse_flag == 6)

    await_requisite_uag = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.purse_flag == 7)

    requisites_for_trade = create(lambda _, m: User.get(tg_id=m.from_user.id).user_flag.flag == 3)

    requisites_for_start_deal = create(lambda _, m: User.get_or_none(tg_id=m.from_user.id).user_flag.flag == 4)