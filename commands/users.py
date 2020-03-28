import datetime as dt

from pyrogram import Client, Filters

from filters.cb_filters import UserCallbackFilter
from jobs.ref import job_check_ref
from keyboard.user_kb import choice_lang_kb, choice_currency_kb, menu_kb
from model import User, UserSettings, UserRef
from text.basiq_texts import choice_lang, choice_currency_txt, end_reg_txt, start_ref_txt, start_txt, end_reg_ref_txt


@Client.on_message(Filters.regex(r'q'))
def qew(_, m):
    job_check_ref()

@Client.on_message(Filters.command('start'))
def reg_user(_, m):
    tg_user = m.from_user
    user = User.get_or_none(tg_id=tg_user.id)
    comm = m.command
    if user:
        if len(comm) == 1:
            m.reply(start_txt, reply_markup=menu_kb)

        elif len(comm) > 1:

            ref_type = comm[1][:1]

            if ref_type == 'u':
                ref_user = User.get_or_none(id=int(comm[1][1:]))

                if ref_user:
                    user_ref = user.ref
                    user_ref.ref_user_id = ref_user.id
                    user_ref.ref_created_at = dt.datetime.utcnow()
                    user_ref.save()

                    m.reply(start_ref_txt(user.settings.lang), reply_markup=menu_kb)

                else:
                    m.reply(start_txt, reply_markup=menu_kb)

            elif ref_type == 't':
                trade_id = int(comm[1][1:])
                trade = True  # TODO  изменить на модель сделок

                if trade:
                    user_ref = 1
                    # user_ref = user.ref
                    # user_ref.ref_user_id = ref_user.id
                    # user_ref.ref_created_at = dt.datetime.utcnow()
                    # user_ref.save()

                    m.reply('Тут сделка c и кнопки под ней')
                else:
                    m.reply(start_txt, reply_markup=menu_kb)
            else:
                m.reply(start_txt, reply_markup=menu_kb)
    else:
        # TODO дописать создание профиля и кошелька
        user = User.create(tg_id=tg_user.id,
                           user_name=tg_user.username,
                           first_name=tg_user.first_name,
                           last_name=tg_user.last_name,
                           date_reg=dt.datetime.utcnow()
                           )

        user_set = UserSettings.create(user_id=user.id)

        if len(comm) == 1:
            m.reply(choice_lang, reply_markup=choice_lang_kb)

        elif len(comm) > 1:
            ref_type = comm[1][:1]

            if ref_type == 'u':
                ref_user = User.get_or_none(int(comm[1][1:]))

                if ref_user:
                    user_set.lang = ref_user.settings.lang
                    user_set.currency = ref_user.settings.currency
                    user_set.save()

                    UserRef.create(user_id=user.id,
                                   ref_user_id=ref_user.id,
                                   ref_created_at=dt.datetime.utcnow()
                                   )

                    m.reply(start_ref_txt(user_set.lang))
                    m.reply(end_reg_ref_txt(user_set.lang), reply_markup=menu_kb)

                else:
                    m.reply(choice_lang, reply_markup=choice_lang_kb)

            elif ref_type == 't':

                trade_id = int(comm[1][1:])
                trade = True #  TODO  изменить на модель сделок

                if trade:
                    # ref_user = trade.user_id
                    #
                    # user_set.lang = ref_user.settings.lang
                    # user_set.currency = ref_user.settings.currency
                    # user_set.save()
                    #
                    # UserRef.create(user_id=user.id,
                    #                ref_user_id=ref_user.id,
                    #                ref_created_at=dt.datetime.utcnow()
                    #                )

                    m.reply(start_ref_txt(user_set.lang))
                    m.reply('Тут сделка c и кнопки под ней')

                else:
                    m.reply(choice_lang, reply_markup=choice_lang_kb)

            else:
                print(7)
                m.reply(choice_lang, reply_markup=choice_lang_kb)


@Client.on_callback_query(UserCallbackFilter.choice_lang)
def choice_lang_cb(_, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)
    choice = int(cb.data[5:])

    user_set = user.settings
    user_set.lang = choice
    user_set.save()

    cb.message.edit(choice_currency_txt(user_set.lang), reply_markup=choice_currency_kb)


@Client.on_callback_query(UserCallbackFilter.choice_currency)
def choice_curr_cb(_, cb):
    tg_id = cb.from_user.id
    choice = int(cb.data[4:])

    user_set = User.get(tg_id=tg_id).settings
    user_set.currency = choice
    user_set.save()

    cb.message.delete()
    cb.message.reply(end_reg_txt, reply_markup=menu_kb)
