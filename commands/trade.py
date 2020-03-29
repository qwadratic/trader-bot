from pyrogram import Client, Filters


@Client.on_message(Filters.regex(r'💸 Обмен'))
def trade_kb(cli, m):
    tg_id = m.from_user.id
    m.reply('')