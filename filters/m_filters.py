from pyrogram import Filters

from models.db_models import User


class UserMessageFilter:

    create = Filters.create

    new_user = create(lambda _, m: User.get_or_none(User.user_id == m.from_user.id) is None)
