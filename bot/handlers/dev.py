from pyrogram import Client, Filters


@Client.on_message(Filters.regex(r'dev'), group=-10)
def dev(cli, m):
    m.reply('dev')
