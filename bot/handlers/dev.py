from pyrogram import Client, Filters


@Client.on_message(Filters.regex(r'dev'), group=-10)
def dev(cli, m):
    m.reply('dev')


@Client.on_message(Filters.regex(r'print texts'))
def qwe(cli, cb):
    from bot.models import Text
    t = Text.objects.all()
    s = []
    for tt in t:
        d = dict(name=tt.name, text=tt.text, text_ru=tt.text_ru, text_en=tt.text_en)
        s.append(d)

    print(s)