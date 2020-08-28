from pyrogram import Client, Filters

from trade.logic.trade_filters import in_trade
from user.logic import kb
from bot.helpers.shortcut import get_user


@Client.on_message(Filters.create(lambda _, m: m.text == get_user(m.from_user.id).get_text(name='user-kb-settings')) & in_trade)
def setting_menu(cli, m):
    m.delete()

    m.reply(get_user(m.from_user.id).get_text(name='user-kb-settings'), reply_markup=kb.settings_menu(get_user(m.from_user.id)))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:7] == 'setuser'))
def settings(cli, cb):
    user = get_user(cb.from_user.id)

    set = cb.data.split('-')[1]
    if set == 'language':
        txt = user.get_text(name='user-settings-select_language')

        cb.message.edit(txt, reply_markup=kb.set_language(user))

    if set == 'currency':
        txt = user.get_text(name='user-settings-select_currency')

        cb.message.edit(txt, reply_markup=kb.set_currency(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:7] == 'userset'))
def set_setting(cli, cb):
    user = get_user(cb.from_user.id)
    user_set = user.settings

    set = cb.data.split('-')[1]
    value = cb.data.split('-')[2]

    if set == 'language':
        user_set.language = value
        txt = user.get_text(name='user-settings-selected_language').format(language=value)

        cb.message.reply(txt, reply_markup=kb.start_menu(user))

    if set == 'currency':
        user_set.currency = value
        currency_name = '🇺🇸 Американский доллар' if value == 'USD' else '🇺🇦 Украинскую гривну' if value == 'UAH' else '🇷🇺 Российский рубль'
        txt = user.get_text(name='user-settings-selected_currency').format(currency=currency_name)
        cli.answer_callback_query(cb.id, txt, show_alert=True)

    user_set.save()

    txt = user.get_text(name='user-settings')
    cb.message.edit(txt, reply_markup=kb.settings_menu(user))


@Client.on_callback_query(Filters.callback_data('close'))
def close_info(cli, cb):
    try:
        cb.message.delete()
    except:
        pass