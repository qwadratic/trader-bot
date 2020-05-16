import datetime as dt

from peewee import IntegrityError
from pyrogram import Client, Filters

from bot_tools.help import create_wallets_for_user
from core import user_core
from core.trade_core import deal_info
from filters.cb_filters import UserCallbackFilter
from filters.m_filters import ref_link
from jobs.check_refill import check_refill_eth
from keyboard import trade_kb
from keyboard import user_kb
from model import User, UserSettings, UserRef, MsgId, UserFlag, Announcement
from text import basiq_texts


# @Client.on_message(Filters.regex('w'))
# def qwe(cli, m):
#     user = User.get(tg_id=m.from_user.id)
#     create_wallets_for_user(user)

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
        create_wallets_for_user(user)
        m.reply(basiq_texts.choice_language, reply_markup=user_kb.choice_lang)

        return

    m.reply(basiq_texts.start, reply_markup=user_kb.menu)


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
        create_wallets_for_user(user)

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
            return m.reply(basiq_texts.start, reply_markup=user_kb.menu)

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

            return m.reply(basiq_texts.start_ref(), reply_markup=user_kb.menu)

        return m.reply(basiq_texts.start, reply_markup=user_kb.menu)

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

            return m.reply(deal_info(trade_id), reply_markup=trade_kb.deal_for_user(trade_id))

        return m.reply(basiq_texts.start, reply_markup=user_kb.menu)


@Client.on_callback_query(UserCallbackFilter.choice_language)
def choice_lang_cb(_, cb):
    tg_id = cb.from_user.id
    user = User.get(tg_id=tg_id)
    language = cb.data[5:]

    user_set = user.settings
    user_set.language = language
    user_set.save()

    cb.message.edit(basiq_texts.choice_currency, reply_markup=user_kb.choice_currency)


@Client.on_callback_query(UserCallbackFilter.choice_currency)
def choice_curr_cb(_, cb):
    tg_id = cb.from_user.id
    currency = cb.data[9:]

    user_set = User.get(tg_id=tg_id).settings
    user_set.currency = currency
    user_set.save()

    cb.message.delete()
    cb.message.reply(basiq_texts.end_reg, reply_markup=user_kb.menu)


@Client.on_message(Filters.regex(r'💼 Кошелёк'))
def my_wallet(cli, m):
    user = User.get(tg_id=m.from_user.id)
    m.reply(user_core.wallet_info(user))


@Client.on_message(Filters.command(r'refill'))
def sda(cli, m):
    user = m.from_user
    name = f'[{user.first_name}](tg://user?id={int(1100783143)})'
    m.reply(name+' wadawdaw')
    #check_refill_eth(cli)