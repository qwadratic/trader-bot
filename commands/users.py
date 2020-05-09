import datetime as dt

from peewee import IntegrityError
from pyrogram import Client, Filters

from core.trade_core import deal_info
from filters.m_filters import ref_link
from keyboard import trade_kb2
from keyboard.user_kb import choice_lang_kb, menu_kb
from model import User, UserSettings, UserRef, MsgId, UserFlag, Announcement
from text.basiq_texts import choice_language, start_ref_txt, start_txt


@Client.on_message(Filters.command('start') & ~ref_link)
def start_command(_, m):
    tg_user = m.from_user

    user = User.get_or_none(tg_id=tg_user.id)

    if not user:  # register user
        user = User.create(tg_id=tg_user.id,
                           user_name=tg_user.username,
                           first_name=tg_user.first_name,
                           last_name=tg_user.last_name,
                           date_reg=dt.datetime.utcnow()
                           )

        MsgId.create(user_id=user.id)
        UserFlag.create(user_id=user.id)
        UserSettings.create(user_id=user.id)

        m.reply(choice_language, reply_markup=choice_lang_kb)

        return

    m.reply(start_txt, reply_markup=menu_kb)


@Client.on_message(Filters.command('start') & ref_link)
def ref_start(_, m):
    comm = m.command
    ref_type = comm[1][:1]
    tg_user = m.from_user

    user = User.get_or_none(tg_id=tg_user.id)

    if not user:  # Регистрация пользователя
        user = User.create(tg_id=tg_user.id,
                           user_name=tg_user.username,
                           first_name=tg_user.first_name,
                           last_name=tg_user.last_name,
                           date_reg=dt.datetime.utcnow()
                           )

        MsgId.create(user_id=user.id)
        UserFlag.create(user_id=user.id)

        if ref_type == 'u':  # user invite
            ref = User.get_or_none(id=int(comm[1][1:]))
            if ref:
                UserSettings.create(user_id=user.id,
                                    language=ref.settings.language,
                                    currency=ref.settings.currency)
            else:
                UserSettings.create(user_id=user.id)
        elif ref_type == 't':
            trade_id = int(comm[1][1:])

            ref = Announcement.get_or_none(id=trade_id).user

            if ref:

                UserSettings.create(user_id=user.id,
                                    language=ref.settings.language,
                                    currency=ref.settings.currency)
            else:
                UserSettings.create(user_id=user.id)
        else:
            UserSettings.create(user_id=user.id)

    if ref_type == 'u':  # user invite
        ref = User.get_or_none(id=int(comm[1][1:]))

        if ref == user.id:
            return m.reply(start_txt, reply_markup=menu_kb)

        if ref:

            try:
                UserRef.create(user_id=user.id,
                               ref_user_id=ref.id,
                               ref_created_at=dt.datetime.utcnow()
                               )

            except IntegrityError:
                UserRef.update(user_id=user.id,
                               ref_user_id=ref.id,
                               ref_created_at=dt.datetime.utcnow()
                               ).execute()

            return m.reply(start_ref_txt(), reply_markup=menu_kb)

        return m.reply(start_txt, reply_markup=menu_kb)

    if ref_type == 't':  # trade ref link
        trade_id = int(comm[1][1:])

        trade = Announcement.get_or_none(id=trade_id)

        if trade:
            ref = trade.user

            try:
                UserRef.create(user_id=user.id,
                               ref_user_id=ref.id,
                               ref_created_at=dt.datetime.utcnow()
                               )

            except IntegrityError:
                UserRef.update(user_id=user.id,
                               ref_user_id=ref.id,
                               ref_created_at=dt.datetime.utcnow()
                               ).execute()

            return m.reply(deal_info(trade_id), reply_markup=trade_kb2.deal_for_user(trade_id))

        return m.reply(start_txt, reply_markup=menu_kb)

