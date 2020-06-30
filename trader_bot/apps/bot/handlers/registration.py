from pyrogram import Client, Filters

from ...user.logic.filters import ref_link
from ...user.models import TelegramUser, UserMsg, UserSettings, UserFlag, UserRef
from ...order.models import Order
from trader_bot.apps.bot.helpers.shortcut import get_user
from ...user.logic import kb
from ...user.logic.core import create_wallets_for_user


@Client.on_message(Filters.command('start') & ~ref_link, group=-1)
def start_command(_, m):
    tg_user = m.from_user

    user = get_user(tg_user.id)

    if not user:  # register user
        user = TelegramUser.objects.create(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name

        )

        UserMsg.objects.create(user=user)
        UserFlag.objects.create(user=user)
        UserSettings.objects.create(user=user)
        create_wallets_for_user(user)

        choice_language = 'Hello!\n' \
                          'choose a language\n\n' \
                          'Привет!!\n' \
                          'Выбери язык'

        m.reply(choice_language, reply_markup=kb.choice_language)

        return

    m.reply(user.get_text(name='user-start'), reply_markup=kb.start_menu(user))


@Client.on_message(Filters.command('start') & ref_link, group=-1)
def ref_start(_, m):
    comm = m.command
    ref_type = comm[1][:1]
    tg_user = m.from_user

    user = get_user(m.from_user.id)

    choice_language = 'Hello!\n' \
                      'choose a language\n\n' \
                      'Привет!!\n' \
                      'Выбери язык'

    if not user:
        user = TelegramUser.objects.create(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name

        )

        UserMsg.objects.create(user=user)
        UserFlag.objects.create(user=user)
        create_wallets_for_user(user)

        if ref_type == 'u':  # user invite
            referrer = TelegramUser.objects.get_or_none(id=int(comm[1][1:]))

            if referrer:
                UserSettings.objects.create(
                    user=user,
                    language=referrer.settings.language,
                    currency=referrer.settings.currency)

                UserRef.objects.create(
                    user=user,
                    referrer=referrer
                )

                m.reply(user.get_text(name="user-start_ref"), reply_markup=kb.hide(user))
                m.reply(user.get_text(name="user-start"), reply_markup=kb.start_menu(user))
                return

            UserSettings.objects.create(user=user)
            m.reply(user.get_text(name="user-start"), reply_markup=kb.start_menu(user))
            return

        if ref_type == 't':  # trade
            order = Order.object.get_or_none(id=int(comm[1][1:]))

            if order:
                referrer = get_user(order.user)

                if referrer.id == user.id:
                    m.reply(user.get_text('Тут объявление'))
                    return

                UserSettings.objects.create(
                    user=user,
                    language=referrer.settings.language,
                    currency=referrer.settings.currency)

                UserRef.objects.create(
                    user=user,
                    referrer=referrer
                )

                m.reply(user.get_text(name="user-start_ref"), reply_markup=kb.hide(user))

                # TODO  допилить
                order_txt = 'None'
                m.reply(order_txt, reply_markup=None)
                return

            UserSettings.objects.create(user=user)
            m.reply(choice_language, reply_markup=kb.choice_language)

    if user:
        if ref_type == 'u':  # user invite
            referrer = TelegramUser.objects.get_or_none(id=int(comm[1][1:]))

            if referrer:
                if referrer.id == user.id:
                    m.reply(user.get_text(name="user-start"), reply_markup=kb.start_menu(user))
                    return
                # TODO TOFOD
                UserRef.objects.update_or_create(
                    user=user,
                    defaults=dict(
                        referrer=referrer
                    )
                )

                m.reply(user.get_text(name="user-start_ref"), reply_markup=kb.hide(user))
                m.reply(user.get_text(name="user-start"), reply_markup=kb.start_menu(user))
                return

            m.reply(user.get_text(name="user-start"), reply_markup=kb.start_menu(user))
            return

        if ref_type == 't':

            order = Order.object.get_or_none(id=int(comm[1][1:]))

            if order:
                referrer = get_user(order.user)
                if referrer.id == user.id:
                    m.reply(user.get_text('Тут объявление'))
                    return

                UserRef.objects.update_or_create(
                    user=user,
                    referrer=referrer
                )

                m.reply(user.get_text(name="user-start_ref"), reply_markup=kb.hide(user))

                # TODO  допилить
                order_txt = 'None'
                m.reply(order_txt, reply_markup=None)
                return

            m.reply(user.get_text(name="user-start"), reply_markup=kb.start_menu(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:14] == 'choicelanguage'))
def choice_language_cb(_, cb):
    user = get_user(cb.from_user.id)
    language = cb.data.split('-')[1]

    user_set = user.settings
    user_set.language = language
    user_set.save()

    cb.message.edit(user.get_text(name='user-registration-select_currency'), reply_markup=kb.select_currency(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:14] == 'choicecurrency'))
def choice_currency_cb(_, cb):
    user = get_user(cb.from_user.id)
    currency = cb.data.split('-')[1]

    user_set = user.settings
    user_set.currency = currency
    user_set.save()

    cb.message.delete()
    cb.message.reply(user.get_text(name='user-end_registration'), reply_markup=kb.start_menu(user))
