import datetime as dt

from pyrogram import Client, Filters

from filters.cb_filters import UserCallbackFilter
from filters.m_filters import UserMessageFilter
from keyboard.user_kb import choice_lang_kb, choice_currency_kb, menu_kb
from models.db_models import User, UserSet
from text.basiq_texts import new_user_txt, choice_currency_txt, end_reg_txt


@Client.on_message(Filters.command('start') & UserMessageFilter.new_user)
def reg_user(_, m):
    user = m.from_user

    UserSet.create(user_id=user.id)

    # TODO дописать создание профиля и кошелька

    m.reply(new_user_txt, reply_markup=choice_lang_kb)


@Client.on_message(Filters.command('start') & ~UserMessageFilter.new_user)
def start_kb(_, m):
    m.reply('txt', reply_markup=menu_kb)


@Client.on_callback_query(UserCallbackFilter.choice_lang)
def choice_lang_cb(_, cb):
    user_id = cb.from_user.id
    choice = int(cb.data[5:])

    user_set = UserSet.get_by_id(user_id)
    user_set.lang = choice
    user_set.save()

    cb.message.edit(choice_currency_txt(user_id), reply_markup=choice_currency_kb)


@Client.on_callback_query(UserCallbackFilter.choice_currency)
def choice_curr_cb(_, cb):
    user = cb.from_user
    choice = int(cb.data[4:])

    user_set = UserSet.get_by_id(user.id)
    user_set.currency = choice
    user_set.save()

    User.create(tg_id=user.id,
                user_name=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                date_reg=dt.datetime.utcnow()
                )

    cb.message.delete()
    cb.message.reply(end_reg_txt, reply_markup=menu_kb)

