from time import sleep

from pyrogram import Client, Filters

from bot.helpers.shortcut import get_user, delete_msg, check_address
from order.logic.text_func import wallet_info

from user.logic import kb
from user.models import UserPurse


@Client.on_message(Filters.create(lambda _, m: m.text == get_user(m.from_user.id).get_text(name='user-kb-wallet')))
def my_wallet(cli, m):
    user = get_user(m.from_user.id)
    msg = m.reply(wallet_info(user), reply_markup=kb.wallet_menu(user))

    user_msg = user.msg

    delete_msg(cli, user.telegram_id, user_msg.wallet_menu)

    user_msg.wallet_menu = msg.message_id
    user_msg.save()


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:11] == 'wallet_menu'))
def wallet_menu(cli, cb):
    user = get_user(cb.from_user.id)

    button = cb.data.split('-')[1]

    if button == 'purse':
        cb.message.edit(user.get_text(name='purse-purse_menu'), reply_markup=kb.purse_menu(user))

    if button == 'deposit':

        wallets = user.wallets.exclude(currency__in=['UAH', 'RUB', 'USD', 'BTC'])

        for w in wallets:
            wal = f'{w.currency}\n' \
                f'```{w.address}```'
            cb.message.reply(wal)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:5] == 'purse'))
def purse_menu(cli, cb):
    user = get_user(cb.from_user.id)
    action = cb.data.split('-')[1]

    if action == 'back':
        cb.message.edit(wallet_info(user), reply_markup=kb.wallet_menu(user))
        return

    if action == 'add':
        purse = user.requisites.filter(status='invalid').delete()

        cb.message.edit(user.get_text(name='purse-select_currency'), reply_markup=kb.choice_currency_for_wallet)
        return

    requisite = user.requisites.get(id=int(cb.data.split('-')[2]))

    # TODO:: создать в UserPurse функцию get_display_text и заюзать в трех местах этого модуля (1)
    if requisite.name:
        txt = user.get_text(name='purse-requisite_info_with_name').format(
            name=requisite.name,
            address=requisite.address,
            currency=requisite.currency
        )

    else:
        txt = user.get_text(name='purse-requisite_info').format(
            address=requisite.address,
            currency=requisite.currency
        )

    cb.message.edit(txt, reply_markup=kb.requisite(user, requisite.id))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:9] == 'requisite'))
def requisites_menu(cli, cb):
    user = get_user(cb.from_user.id)
    user_flag = user.flags

    set = cb.data.split('-')[1]

    requisite = user.requisites.get(id=int(cb.data.split('-')[2]))

    if set == 'address':
        txt = user.get_text(name='purse-enter_address').format(currency=requisite.currency)

        cb.message.edit(txt, reply_markup=kb.cancel_edit_requisite(user, requisite.id))
        requisite.status = 'edit'

        user_flag.await_requisites_address = True
        user_flag.edit_requisite = True

    if set == 'name':
        user_flag.await_requisites_name = True
        user_flag.edit_requisite = True
        requisite.status = 'edit'

        cb.message.edit(user.get_text(name='purse-enter_requisite_name'), reply_markup=kb.edit_requisite_name(user, requisite.id))

    if set == 'delete':
        requisite.delete()

        cb.message.edit(user.get_text(name='purse-purse_menu'), reply_markup=kb.purse_menu(user))
        return

    if set == 'cancel':
        user_flag.edit_requisite = False
        user_flag.await_requisites_name = False
        user_flag.await_requisites_address = False
        requisite.status = 'valid'

        # TODO:: создать в UserPurse функцию get_display_text и заюзать в трех местах этого модуля (2)
        if requisite.name:
            txt = user.get_text(name='purse-requisite_info_with_name').format(
                name=requisite.name,
                address=requisite.address,
                currency=requisite.currency
            )
        else:
            txt = user.get_text(name='purse-requisite_info').format(
                address=requisite.address,
                currency=requisite.currency
            )

        cb.message.edit(txt, reply_markup=kb.requisite(user, requisite.id))

    if set == 'delname':
        user_flag.edit_requisite = False
        requisite.name = None
        requisite.status = 'valid'
        requisite.save()

        txt = user.get_text(name='purse-requisite_info').format(
            address=requisite.address,
            currency=requisite.currency
        )

        cb.message.edit(txt, reply_markup=kb.requisite(user, requisite.id))

    requisite.save()
    user_flag.save()


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:6] == 'chcurr'))
def add_requisites_currency(cli, cb):
    user = get_user(cb.from_user.id)
    currency = cb.data.split('-')[1]

    if currency == 'back':
        cb.message.edit(user.get_text(name='purse-purse_menu'), reply_markup=kb.purse_menu(user))
        return

    requisite = UserPurse.objects.create(user_id=user.id, currency=currency)

    flags = user.flags
    flags.await_requisites_name = True
    flags.save()

    cb.message.edit(user.get_text(name='purse-enter_requisite_name'), reply_markup=kb.skip_add_requisites_name(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:6] == 'addreq'))
def skip_requisite_name(cli, cb):
    user = get_user(cb.from_user.id)
    user_flag = user.flags

    action = cb.data.split('-')[1]
    requisite = user.requisites.get(status='invalid')

    if action == 'skip':
        user_flag.await_requisites_name = False
        user_flag.await_requisites_address = True
        user_flag.save()

        txt = user.get_text(name='purse-enter_address').format(currency=requisite.currency)

        cb.message.edit(txt, reply_markup=kb.cancel_add_requisites(user))

        return

    if action == 'cancel':
        user_flag.await_requisites_name = False
        user_flag.await_requisites_address = False
        user_flag.save()

        user.requisites.filter(status='invalid').delete()

        cb.message.edit(user.get_text(name='purse-purse_menu'), reply_markup=kb.purse_menu(user))


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id) and
                                               get_user(m.from_user.id).flags.await_requisites_name))
def add_reqiusites_name(cli, m):
    user = get_user(m.from_user.id)
    user_msg = user.msg

    user_flag = user.flags

    if user_flag.edit_requisite:
        user_flag.await_requisites_name = False
        user_flag.edit_requisite = False
        user_flag.save()

        requisite = user.requisites.get(status='edit')

        requisite.name = m.text
        requisite.status = 'valid'
        requisite.save()

        delete_msg(cli, user.telegram_id, user_msg.wallet_menu)

        # TODO:: создать в UserPurse функцию get_display_text и заюзать в трех местах этого модуля (3)
        if requisite.name:
            txt = user.get_text(name='purse-requisite_info_with_name').format(
                name=requisite.name,
                address=requisite.address,
                currency=requisite.currency
            )
        else:
            txt = user.get_text(name='purse-requisite_info').format(
                address=requisite.address,
                currency=requisite.currency
            )

        msg = m.reply(txt, reply_markup=kb.requisite(user, requisite.id))
        user_msg.wallet_menu = msg.message_id
        user_msg.save()
        return

    requisite = user.requisites.get(status='invalid')
    requisite.name = m.text
    requisite.save()

    user_flag.await_requisites_name = False
    user_flag.await_requisites_address = True
    user_flag.save()

    txt = user.get_text(name='purse-enter_address').format(currency=requisite.currency)
    msg = m.reply(txt, reply_markup=kb.cancel_add_requisites(user))

    delete_msg(cli, user.telegram_id, user_msg.wallet_menu)

    user_msg.wallet_menu = msg.message_id
    user_msg.save()


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id) and
                                               get_user(m.from_user.id).flags.await_requisites_address))
def add_reqiusites_address(cli, m):
    user = get_user(m.from_user.id)
    user_flag = user.flags

    if user_flag.edit_requisite:
        requisite = user.requisites.get(status='edit')
    else:
        requisite = user.requisites.get(status='invalid')

    address = m.text if check_address(m.text, requisite.currency) else None
    if not address:
        msg = m.reply(user.get_text(name='bot-invalid_address'))
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

    delete_msg(cli, user.telegram_id, user.msg.wallet_menu)

    msg = m.reply(user.get_text(name='purse-purse_menu'), reply_markup=kb.purse_menu(user))
    user_msg = user.msg
    user_msg.wallet_menu = msg.message_id
    user_msg.save()
