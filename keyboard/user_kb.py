import math

from pyrogram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from model import Announcement

choice_lang = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇬🇧 English', callback_data=f'lang en')],
                [InlineKeyboardButton('🇷🇺 Русский', callback_data=f'lang ru')]
            ]
        )


choice_currency = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇺🇸 Американский доллар (USD)', callback_data=f'currency USD')],
                [InlineKeyboardButton('🇺🇦 Украинская гривна (UAH)', callback_data=f'currency UAH')],
                [InlineKeyboardButton('🇷🇺 Российский рубль (RUB)', callback_data=f'currency RUB')]
            ]
        )


menu = ReplyKeyboardMarkup(
            [
                ['💼 Кошелёк', '💸 Обмен'],
                ['⚙️ Настройки']
            ],
            resize_keyboard=True,
        )


wallet_menu = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Пополнить', callback_data=f'q'),
                 InlineKeyboardButton('Вывести', callback_data=f'q')],
                [InlineKeyboardButton('Портмоне', callback_data=f'wm-portmone')],
                [InlineKeyboardButton('Партнёрская программа', callback_data=f'q')],
                [InlineKeyboardButton('Премиум подписка', callback_data=f'q')]
            ]
        )


hide_notification = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f'« cкрыть »', callback_data='hide')]
        ])


def purse(user):
    requisites = user.purse

    kb = [[InlineKeyboardButton('🔙 Назад', callback_data='purse-back')], [InlineKeyboardButton('Добавить реквизиты', callback_data='purse-add')]]

    for r in requisites:
        name = f'[{r.name}]' if r.name else ''
        kb.append([InlineKeyboardButton(f'{name}[{r.currency}] {r.address}', callback_data=f'purse-req-{r.id}')])

    return InlineKeyboardMarkup(kb)


def requisite(requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🔙 Назад', callback_data=f'wm-portmone')],
                [InlineKeyboardButton('Редактировать адрес', callback_data=f'editrequisite-address-{requisite_id}')],
                [InlineKeyboardButton('Изменить/добавить название', callback_data=f'editrequisite-name-{requisite_id}')],
                [InlineKeyboardButton('Удалить', callback_data=f'editrequisite-delete-{requisite_id}')]
            ]
        )

    return kb


choice_currency_for_wallet = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('BIP', callback_data='chcurr-BIP'),
         InlineKeyboardButton('BTC', callback_data='chcurr-BTC'),
         InlineKeyboardButton('USDT', callback_data='chcurr-USDT'),
         InlineKeyboardButton('ETH', callback_data='chcurr-ETH')],
        [InlineKeyboardButton('USD', callback_data='chcurr-USD'),
         InlineKeyboardButton('RUB', callback_data='chcurr-RUB'),
         InlineKeyboardButton('UAH', callback_data='chcurr-UAH')],
        [InlineKeyboardButton('🔙 Назад', callback_data='chcurr')]

    ])


cancel_add_requisites = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('« Отменить »', callback_data=f'cancaddreq')]
            ]
        )

skip_add_requisites_name = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Пропустить', callback_data=f'addreq-skip')],
                [InlineKeyboardButton('« Отменить »', callback_data=f'addreq-cancel')]
            ]
        )


def cancel_edit_requisite(requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('« Отменить »', callback_data=f'editrequisite-cancel-{requisite_id}')]
            ]
        )

    return kb


def edit_requisite_name(requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Удалить название', callback_data=f'editrequisite-delname-{requisite_id}')],
                [InlineKeyboardButton('« Отменить »', callback_data=f'editrequisite-cancel-{requisite_id}')]
            ]
        )

    return kb


settings_menu = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🌎 Язык', callback_data=f'setuser-language'),
                 InlineKeyboardButton('💶 Валюта', callback_data=f'setuser-currency')],
                [InlineKeyboardButton('О сервисе', callback_data=f'setuser-about')],
                [InlineKeyboardButton('« Закрыть »', callback_data=f'hide')]
            ]
        )


set_language = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇬🇧 English', callback_data=f'userset-language-en')],
                [InlineKeyboardButton('🇷🇺 Русский', callback_data=f'userset-language-ru')],
                [InlineKeyboardButton('🔙 Назад', callback_data=f'userset-back-1')]
            ]
        )


set_currency = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇺🇸 Американский доллар (USD)', callback_data=f'userset-currency-USD')],
                [InlineKeyboardButton('🇺🇦 Украинская гривна (UAH)', callback_data=f'userset-currency-UAH')],
                [InlineKeyboardButton('🇷🇺 Российский рубль (RUB)', callback_data=f'userset-currency-RUB')],
                [InlineKeyboardButton('🔙 Назад', callback_data=f'userset-back-1')]
            ]
        )


def my_announcement(user, offset):
    kb_list = []

    kb_list.append([InlineKeyboardButton('🔙 Назад', callback_data=f'myannouncement-back-{offset}')])

    all_announcement = Announcement.select().where(Announcement.user_id == user.id)

    sort_announcement = Announcement.select().where(Announcement.user_id == user.id).offset(offset).limit(5)

    status = {'open': '⚪️',
              'close': '🔴'}
    if len(all_announcement) == 0:
        return InlineKeyboardMarkup(kb_list)
    else:
        for ad in sort_announcement:
            announcement_info = f'{status[ad.status]} [{ad.type_operation}][{ad.trade_currency}]'
            kb_list.append([InlineKeyboardButton(announcement_info, callback_data=f'open announc {ad.id}')])

        if offset == 0 and len(all_announcement) <= 5:
            return InlineKeyboardMarkup(kb_list)

        elif offset == 0:
            position = f'{int(offset + 2)}/{int(math.ceil(len(all_announcement) / 5))}'
            position_2 = f'{int(offset / 5 + 1)}'
            kb_list.append([InlineKeyboardButton(f'{position} ⇒', callback_data=f'myannouncement-right-{offset}')])

        elif 0 < offset + 5 >= len(all_announcement):
            position = f'{int(math.ceil(len(all_announcement) / 5)) - 1}/{int(math.ceil(len(all_announcement)/5))}'
            position_2 = f'{int(offset / 5)}'
            kb_list.append([InlineKeyboardButton(f'⇐ {position}', callback_data=f'myannouncement-left-{offset}')])

        else:
            position_1 = f'{int((offset + 5) / 5 - 1)}/{int(math.ceil(len(all_announcement) / 5))}'
            position_2 = f'{int(offset / 5 + 2)}/{int(math.ceil(len(all_announcement) / 5))}'
            position_3 = f'{int(offset / 5 + 1)}'
            kb_list.append([InlineKeyboardButton(f'⇐ {position_1}', callback_data=f'myannouncement-left-{offset}'),
                            InlineKeyboardButton(f'{position_2} ⇒', callback_data=f'myannouncement-right-{offset}')])

        return InlineKeyboardMarkup(kb_list)


