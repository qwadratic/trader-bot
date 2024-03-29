from pyrogram import Client, Filters

from user.logic import kb
from user.logic.filters import ref_link
from user.logic.registration import register_user
from order.models import Order
from bot.helpers.shortcut import get_user


@Client.on_message(Filters.command('start') & ~ref_link, group=-1)
def start_command(_, m):
    tg_user = m.from_user
    user = get_user(tg_user.id)

    if not user:
        user = register_user(tg_user)
        text_name, markup = 'user-settings-select_language', kb.choice_language
    else:
        text_name, markup = 'user-start', kb.start_menu(user)

    m.reply(user.get_text(text_name), reply_markup=markup)


@Client.on_message(Filters.command('start') & ref_link, group=-1)
def ref_start(_, m):
    ref_str = m.command[1]
    ref_type, ref_user_or_order_id = ref_str[:1], int(ref_str[1:])

    tg_user = m.from_user
    user = get_user(tg_user.id)

    order, referrer = None, None
    # обычная рефка
    if ref_type == 'u':
        referrer = get_user(ref_user_or_order_id)
    # рефка сразу на объявление
    elif ref_type == 't':
        order = Order.objects.get_or_none(id=ref_user_or_order_id)
        referrer = order.parent_order.user if order else None

    # флаги:
    #  - новый юзер
    #  - новый/старый юзер, которого пригласили в трейд по рефке
    is_new_user = user is None
    is_ref_order = referrer is not None and order is not None
    if is_new_user:
        # Новый юзер переходит на объявление по рефке
        # В этом случае устанавливаем такой же язык/валюту, как у нашего реферера
        # (Ибо сделка важнее чем диалог выбора языка/валюты)
        reg_params = {
            'auto_language': referrer.setttings.language,
            'auto_currency': referrer.setttings.currency
        } if is_ref_order else {}

        user = register_user(tg_user, **reg_params)

    # Уведомление о том что мы прошли по партнерской ссылке (если сработала)
    is_ref_updated = user.update_referrer(referrer)
    if is_ref_updated:
        m.reply(user.get_text(name='user-start_ref'), reply_markup=kb.hide(user))

    # Мы попали в объявление.
    # TODO:: заимплементить этот кусок
    if is_ref_order:
        # Перешли по своей же ссылке
        if referrer.id == user.id:
            m.reply('TODO:: Интерфейс редактирования объявления (посетили свое по рефке)', reply_markup=kb.hide(user))
        else:
            m.reply('TODO:: Интерфейс просмотра объявления (возможно доп. логика, т. к. перешли по рефке)', reply_markup=kb.hide(user))
        return

    # Переход на объявление по валидной рефке мы уже обработали - значит мы в главном меню
    # Если юзер новый - выбор языка -> главное меню
    # Если старый - главное меню
    if is_new_user:
        text_name, markup = 'user-settings-select_language', kb.choice_language
    else:
        text_name, markup = 'user-start', kb.start_menu(user)

    m.reply(user.get_text(name=text_name), reply_markup=markup)


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
