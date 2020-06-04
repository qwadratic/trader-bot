import datetime as dt
from time import sleep

from peewee import IntegrityError
from pyrogram import Client, Filters

from bot_tools.help import create_wallets_for_user, check_address, delete_msg
from core import user_core
from core.trade_core import get_ad_info, turn_off_announcement_and_inform
from filters.cb_filters import UserCallbackFilter
from filters.m_filters import ref_link, UserMessageFilter
from jobs.check_refill import check_refill_eth
from keyboard import trade_kb
from keyboard import user_kb
from model import User, UserSettings, UserRef, MsgId, UserFlag, Announcement, Wallet, VirtualWallet, UserPurse
from text import basiq_texts


@Client.on_message(Filters.regex(r'rrr'))
def create_fake_wallets(cli, m):
    users = User.select()

    for user in users:
        Wallet.create(user_id=user.id,
                      currency='BTC',
                      address='btc address',
                      private_key='btc key')

        Wallet.create(user_id=user.id,
                      currency='UAH',
                      address='uah address',
                      private_key='uah key')

        Wallet.create(user_id=user.id,
                      currency='RUB',
                      address='uah address',
                      private_key='uah key')

        Wallet.create(user_id=user.id,
                      currency='USD',
                      address='uah address',
                      private_key='uah key')
        currency = ['UAH', 'USD', 'RUB']
        for c in currency:
            VirtualWallet.create(user_id=user.id,
                                 currency=c)


    m.reply('complete')


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

            return m.reply(get_ad_info(trade_id), reply_markup=trade_kb.deal_for_user(trade_id))

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
    m.reply(user_core.wallet_info(user), reply_markup=user_kb.wallet_menu)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:2] == 'wm'))
def wallet_menu(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    user_msg = user.msg

    button = cb.data.split('-')[1]

    if button == 'portmone':
        txt = f'💼 Портмоне\n\n' \
            f'Здесь вы можете хранить ваши реквизиты'

        msg = cb.message.edit(txt, reply_markup=user_kb.purse(user))
        user_msg.wallet_menu = msg.message_id

    user_msg.save()


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:5] == 'purse'))
def purse_menu(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    action = cb.data.split('-')[1]

    if action == 'back':
        cb.message.edit(user_core.wallet_info(user), reply_markup=user_kb.wallet_menu)
        return

    if action == 'add':
        UserPurse.delete().where((UserPurse.user_id == user.id) & (UserPurse.status == 'invalid')).execute()
        txt = 'Выбери валюту кошелька'
        cb.message.edit(txt, reply_markup=user_kb.choice_currency_for_wallet)
        return

    requisite = UserPurse.get_by_id(int(cb.data.split('-')[2]))

    if requisite.name:
        txt = f'{requisite.name}\n' \
            f'```{requisite.address}```\n' \
            f'Валюта: {requisite.currency}'
    else:
        txt = f'Адрес: ```{requisite.address}```\n' \
            f'Валюта: {requisite.currency}'

    cb.message.edit(txt, reply_markup=user_kb.requisite(requisite.id))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:6] == 'chcurr'))
def add_requisite_currency(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    currency = cb.data.split('-')[1]

    UserPurse.delete().where((UserPurse.user_id == user.id) & (UserPurse.status == 'invalid')).execute()
    requisite = UserPurse.create(user_id=user.id, currency=currency)

    user_flag = user.flags
    user_flag.await_requisites_name = True
    user_flag.save()

    txt = f'Введите имя реквизиты'

    msg = cb.message.edit(txt, reply_markup=user_kb.skip_add_requisites_name)
    user_msg = user.msg
    user_msg.wallet_menu = msg.message_id
    user_msg.save()


@Client.on_message(UserMessageFilter.await_requisites_name)
def add_reqiusites_name(cli, m):
    m.delete()
    user = User.get(tg_id=m.from_user.id)
    user_msg = user.msg

    user_flag = user.flags

    if user_flag.edit_requisite:
        user_flag.await_requisites_name = False
        user_flag.edit_requisite = False
        user_flag.save()

        requisite = UserPurse.get(user_id=user.id, status='edit')

        requisite.name = m.text
        requisite.status = 'valid'
        requisite.save()

        delete_msg(cli, user.tg_id, user_msg.wallet_menu)

        if requisite.name:
            txt = f'{requisite.name}\n' \
                f'```{requisite.address}```\n' \
                f'Валюта: {requisite.currency}'
        else:
            txt = f'Адрес: ```{requisite.address}```\n' \
                f'Валюта: {requisite.currency}'

        msg = m.reply(txt, reply_markup=user_kb.requisite(requisite.id))
        user_msg.wallet_menu = msg.message_id
        user_msg.save()
        return

    requisite = UserPurse.get(user_id=user.id, status='invalid')
    requisite.name = m.text
    requisite.save()

    user_flag.await_requisites_name = False
    user_flag.await_requisites_address = True
    user_flag.save()

    txt = f'Введите адрес {requisite.currency} кошелька'
    msg = m.reply(txt, reply_markup=user_kb.cancel_add_requisites)

    delete_msg(cli, user.tg_id, user_msg.wallet_menu)

    user_msg.wallet_menu = msg.message_id
    user_msg.save()


@Client.on_message(UserMessageFilter.await_requisites_address)
def add_reqiusites_address(cli, m):
    m.delete()
    user = User.get(tg_id=m.from_user.id)
    user_flag = user.flags

    requisite = UserPurse.get_or_none(user_id=user.id, status='invalid')

    if user_flag.edit_requisite:
        requisite = UserPurse.get(user_id=user.id, status='edit')

    address = m.text if check_address(m.text, requisite.currency) else None
    if not address:
        msg = m.reply('Некорректный адрес')
        sleep(3)
        msg.delete()
        return

    if address:
        requisite.address = address
        requisite.status = 'valid'
        requisite.save()

    user_flag.await_requisites_address = False
    user_flag.edit_requisite = False
    user_flag.save()

    delete_msg(cli, user.tg_id, user.msg.wallet_menu)

    txt = f'💼 Портмоне\n\n' \
        f'Здесь вы можете хранить ваши реквизиты'

    m.reply(txt, reply_markup=user_kb.purse(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:6] == 'addreq'))
def navigation_in_create_requisite(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    user_flag = user.flags
    action = cb.data.split('-')[1]
    requisite = UserPurse.get(user_id=user.id, status='invalid')

    if action == 'skip':
        user_flag.await_requisites_name = False
        user_flag.await_requisites_address = True
        user_flag.save()

        txt = f'Введите адрес {requisite.currency} кошелька'
        msg = cb.message.edit(txt, reply_markup=user_kb.cancel_add_requisites)
        user_msg = user.msg
        delete_msg(cli, user.tg_id, user_msg.wallet_menu)

        user_msg.wallet_menu = msg.message_id
        user_msg.save()
        return

    if action == 'cancel':
        user_flag.await_requisites_name = False
        user_flag.await_requisites_address = False
        user_flag.save()

        UserPurse.delete().where((UserPurse.user_id == user.id) & (UserPurse.status == 'invalid')).execute()

        txt = f'💼 Портмоне\n\n' \
            f'Здесь вы можете хранить ваши реквизиты'

        cb.message.edit(txt, reply_markup=user_kb.purse(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:13] == 'editrequisite'))
def edit_requisite(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    user_flag = user.flags
    set = cb.data.split('-')[1]

    requisite = UserPurse.get_by_id(int(cb.data.split('-')[2]))

    if set == 'address':
        txt = f'Введите адрес {requisite.currency} кошелька'
        cb.message.edit(txt, reply_markup=user_kb.cancel_edit_requisite(requisite.id))
        requisite.status = 'edit'

        user_flag.await_requisites_address = True
        user_flag.edit_requisite = True

    if set == 'name':
        user_flag.await_requisites_name = True
        user_flag.edit_requisite = True
        requisite.status = 'edit'

        txt = f'Введите имя реквизиты'

        cb.message.edit(txt, reply_markup=user_kb.edit_requisite_name(requisite.id))

    if set == 'delete':
        UserPurse.delete_by_id(requisite.id)
        txt = f'💼 Портмоне\n\n' \
            f'Здесь вы можете хранить ваши реквизиты'

        cb.message.edit(txt, reply_markup=user_kb.purse(user))

    if set == 'cancel':
        user_flag.edit_requisite = False
        user_flag.await_requisites_name = False
        user_flag.await_requisites_address = False
        requisite.status = 'valid'

        if requisite.name:
            txt = f'{requisite.name}\n' \
                f'```{requisite.address}```\n' \
                f'Валюта: {requisite.currency}'
        else:
            txt = f'Адрес: ```{requisite.address}```\n' \
                f'Валюта: {requisite.currency}'

        cb.message.edit(txt, reply_markup=user_kb.requisite(requisite.id))

    if set == 'delname':
        user_flag.edit_requisite = False
        requisite.name = None
        requisite.status = 'valid'
        requisite.save()

        txt = f'```{requisite.address}```\n' \
            f'Валюта: {requisite.currency}'

        cb.message.edit(txt, reply_markup=user_kb.requisite(requisite.id))

    requisite.save()
    user_flag.save()


@Client.on_message(Filters.regex(r'⚙️ Настройки'))
def setting_menu(cli, m):
    m.delete()

    txt = f'⚙️ Настройки'

    m.reply(txt, reply_markup=user_kb.settings_menu)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:7] == 'setuser'))
def settings(cli, cb):
    set = cb.data.split('-')[1]
    if set == 'language':
        txt = f'🌍 Язык\n\n' \
            f'Пожалуйста, выберите язык:'

        cb.message.edit(txt, reply_markup=user_kb.set_language)

    if set == 'currency':
        txt = '💶 Валюта\n\n' \
              'Выберите Вашу базовую валюту'

        cb.message.edit(txt, reply_markup=user_kb.set_currency)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:7] == 'userset'))
def set_setting(cli, cb):
    user = User.get(tg_id=cb.from_user.id)
    user_set = user.settings

    set = cb.data.split('-')[1]
    value = cb.data.split('-')[2]

    if set == 'language':
        user_set.language = value
        lang_name = 'You have chosen 🇬🇧 English' if value == 'en' else 'Вы выбрали 🇷🇺 русский язык'
        cli.answer_callback_query(cb.id, lang_name, show_alert=True)

    if set == 'currency':
        user_set.currency = value
        currency_name = '🇺🇸 Американский доллар' if value == 'USD' else '🇺🇦 Украинскую гривну' if value == 'UAH' else '🇷🇺 Российский рубль'
        txt = f'Вы выбрали {currency_name}'
        cli.answer_callback_query(cb.id, txt, show_alert=True)

    user_set.save()

    txt = f'⚙️ Настройки'
    cb.message.edit(txt, reply_markup=user_kb.settings_menu)


