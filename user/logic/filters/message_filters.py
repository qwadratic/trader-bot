from pyrogram import Filters
from user.models.user import Text, TelegramUser

ref_link = Filters.create(lambda _, m: len(m.command) > 1)

filter_admin = Filters.user([69062067, 373283223, 862797627, 263425422])
