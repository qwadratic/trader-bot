from pyrogram import Filters


class UserCallbackFilter:

    create = Filters.create

    choice_lang = create(lambda _, cb: cb.data[:4] == 'lang')

    choice_currency = create(lambda _, cb: cb.data[:3] == 'val')
