from pyrogram import Filters

ref_link = Filters.create(lambda _, m: len(m.command) > 1)

filter_admin = Filters.user([69062067, 373283223, 862797627])