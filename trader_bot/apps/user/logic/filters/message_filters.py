from pyrogram import Filters

ref_link = Filters.create(lambda _, m: len(m.command) > 1)