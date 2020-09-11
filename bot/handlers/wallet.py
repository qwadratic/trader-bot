from decimal import Decimal, InvalidOperation
from time import sleep

from constance import config
from pyrogram import Client, Filters

from bot.helpers.shortcut import get_user, delete_msg, check_address, get_max_amount_withdrawal, get_currency_rate, \
    to_units, round_currency, to_cents, update_cache_msg, delete_inline_kb
from bot.jobs.get_currency_rate import coinmarket_currency_usd
from bot.models import WithdrawalRequest
from order.logic.core import convert_bonus
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
        cb.message.edit(user.get_text(name='wallet-select_currency_for_deposit'), reply_markup=kb.select_currency_for_deposit(user))

    if button == 'withdrawal':
        withdrawal_requests = user.withdrawalRequests.filter(status__in=['pending verification', 'verifed'])
        if withdrawal_requests.count() > 0:
            cli.answer_callback_query(cb.id, 'У вас есть уже активная заявка на вывод')
            return

        cb.message.edit(user.get_text(name='wallet-select_currency_withdrawal'), reply_markup=kb.select_currency_for_withdrawal)

    if button == 'cancel_withdrawal':
        withdrawal_requests = user.withdrawalRequests.filter(status__in=['pending verification', 'verifed'])
        currency = withdrawal_requests[0].currency
        amount = to_units(currency, withdrawal_requests[0].amount, round=True)
        cb.message.reply(user.get_text(name='wallet-confirm_refusal_withdrawal').format(
            amount=amount,
            currency=currency
        ), reply_markup=kb.confirm_cancel_withdrawal(user))

    if button == 'convert_bonus':
        flags = user.flags
        flags.await_amount_for_convert_bonus = True
        flags.save()

        msg = cb.message.edit(user.get_text(name='wallet-enter_amount_for_conver_bonus').format(
            min_amount=config.MIN_AMOUNT_CONVERT_BONUS
        ), reply_markup=kb.cancel_convert_bonus(user))
        update_cache_msg(user, 'amount_for_conver_bonus', msg.message_id)


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags.await_amount_for_convert_bonus))
def amount_convert_bonus(cli, m):
    user = get_user(m.from_user.id)
    bonus_balance = user.get_balance('BONUS', cent2unit=True)
    try:
        amount = Decimal(m.text.replace(',', '.'))

        if amount > bonus_balance:
            m.reply(user.get_text(name='wallet-limit_convert_bonus').format(amount=round_currency('BONUS', bonus_balance)))
            return

    except InvalidOperation:

        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    flags = user.flags
    flags.await_amount_for_convert_bonus = False
    flags.save()

    delete_inline_kb(cli, user.telegram_id, user.cache['msg']['amount_for_conver_bonus'])

    m.reply(user.get_text(name='wallet-select_currency_for_convert_bonus'), reply_markup=kb.select_currency_for_convert_bonus(user, amount))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('convert_bonus')))
def currency_convert_bonus(cli, cb):
    user = get_user(cb.from_user.id)
    cb_data = cb.data.split('-')
    currency = cb_data[1]
    amount = Decimal(cb_data[2])
    currency_rate = to_units('USD', get_currency_rate(currency))
    amount_in_currency = amount / currency_rate

    cb.message.edit(cb.message.text + '\n\n' + user.get_text(name='you_selected').format(foo=currency))
    cb.message.reply(user.get_text(name='wallet-confirm_convert_bonus').format(
        amount=round_currency('BONUS', amount),
        amount_in_currency=round_currency(currency, amount_in_currency),
        currency=currency
    ), reply_markup=kb.confirm_convert_bonus(user, amount, currency_rate, currency))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('confirm_convert_bonus')))
def confirm_convert_bonus(cli, cb):
    user = get_user(cb.from_user.id)
    cb_data = cb.data.split('-')
    amount = Decimal(cb_data[1])
    currency = cb_data[2]
    currency_rate = Decimal(cb_data[3])
    amount_in_currency = amount / currency_rate

    convert_bonus(user, amount, currency, amount_in_currency)
    cb.message.edit(cb.message.text)
    cb.message.reply(user.get_text(name='wallet-successful_convert_bonus').format(
        amount=round_currency('BONUS', amount),
        amount_in_currency=round_currency(currency, amount_in_currency),
        currency=currency
    ))


@Client.on_callback_query(Filters.callback_data('cancel_convert_bonus'))
def cancel_convert_bonus(cli, cb):
    user = get_user(cb.from_user.id)
    flags = user.flags
    flags.await_amount_for_convert_bonus = False
    flags.save()

    cb.message.edit(cb.message.text)
    cb.message.reply(user.get_text(name='wallet-cancel_convert_bonus'))



@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('currency_for_deposit')))
def currency_for_deposit(cli, cb):
    user = get_user(cb.from_user.id)

    button = cb.data.split('-')[1]

    if button == 'back':
        return cb.message.edit(wallet_info(user), reply_markup=kb.wallet_menu(user))

    if button == 'USDT':
        address = user.wallets.get(currency='ETH').address
    else:
        address = user.wallets.get(currency=button).address

    cb.message.reply(user.get_text(name='wallet-address_for_deposit').format(currency=button))
    cb.message.reply(address)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:5] == 'purse'))
def purse_menu(cli, cb):
    user = get_user(cb.from_user.id)
    action = cb.data.split('-')[1]

    if action == 'back':
        cb.message.edit(wallet_info(user), reply_markup=kb.wallet_menu(user))
        return

    if action == 'add':
        user.requisites.filter(status='invalid').delete()
        cb.message.edit(user.get_text(name='purse-select_currency'), reply_markup=kb.choice_currency_for_wallet)
        return

    requisite = user.requisites.get(id=int(cb.data.split('-')[2]))

    txt = requisite.get_display_text(user)
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

        txt = requisite.get_display_text(user)

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

        txt = requisite.get_display_text(user)

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


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('withdrawal')))
def select_currency_for_withdrawal(cli, cb):
    user = get_user(cb.from_user.id)

    button = cb.data.split('-')[1]

    if button == 'currency':
        currency = cb.data.split('-')[2]
        withdrawal_request = user.cache['clipboard']['withdrawal_request'] = {}

        withdrawal_request['currency'] = currency
        user.save()

        flags = user.flags
        flags.await_amount_for_withdrawal = True
        flags.save()

        cb.message.edit(cb.message.text + '\n\n' + user.get_text(name='you_selected').format(foo=currency))

        max_withdrawal_amount = get_max_amount_withdrawal(user, currency) / to_units('USD', get_currency_rate(currency))
        cb.message.reply(
            user.get_text(name='wallet-enter_amount_for_withdrawal').format(
                max_amount=round_currency(currency, max_withdrawal_amount),
                currency=currency),
            reply_markup=kb.cancel_withdrawal(user)
        )

    if button == 'back':
        cb.message.edit(wallet_info(user), reply_markup=kb.wallet_menu(user))


@Client.on_callback_query(Filters.callback_data('cancel_withdrawal'))
def cancel_withdrawal(cli, cb):
    user = get_user(cb.from_user.id)
    flags = user.flags
    flags.await_amount_for_withdrawal = False
    flags.save()
    cb.message.edit(wallet_info(user), reply_markup=kb.wallet_menu(user))


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id) and
                                               get_user(m.from_user.id).flags.await_amount_for_withdrawal))
def amount_withdrawal(cli, m):
    user = get_user(m.from_user.id)

    try:
        amount = Decimal(m.text.replace(',', '.'))

    except InvalidOperation:

        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    withdrawal_request = user.cache['clipboard']['withdrawal_request']
    currency = withdrawal_request['currency']

    max_withdrawal_amount = get_max_amount_withdrawal(user, currency) / to_units('USD', get_currency_rate(currency))

    # TODO учесть комсу
    if amount > max_withdrawal_amount:
        m.reply(f'Вы не можете вывести больше чем {round_currency(currency, max_withdrawal_amount)} {currency}')
        return

    withdrawal_request['amount'] = to_cents(currency, amount)
    user.save()

    flags = user.flags
    flags.await_amount_for_withdrawal = False
    flags.save()

    m.reply(user.get_text(name='wallet-select_requisite_for_withdrawal').format(currency=currency), reply_markup=kb.select_requisite_for_withdrawal(user, currency))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('selectreqwithdrawal')))
def requisite_for_withdrawal(cli, cb):
    user = get_user(cb.from_user.id)

    button = cb.data.split('-')[1]

    if button == 'use':
        user.cache['clipboard']['withdrawal_request']['address'] = user.requisites.get(id=int(cb.data.split('-')[2])).address
        user.save()
        currency = user.cache['clipboard']['withdrawal_request']['currency']
        address = user.cache['clipboard']['withdrawal_request']['address']
        amount = round_currency(currency, to_units(currency, user.cache['clipboard']['withdrawal_request']['amount']))

        cb.message.edit(
            user.get_text(name='wallet-confirm_withdrawal').format(
                amount=amount,
                currency=currency,
                address=address),
            reply_markup=kb.confirm_withdrawal(user))

    if button == 'new':
        pass


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('confirm_withdrawal')))
def confirm_withdrawal(cli, cb):
    user = get_user(cb.from_user.id)

    button = cb.data.split('-')[1]
    currency = user.cache['clipboard']['withdrawal_request']['currency']
    address = user.cache['clipboard']['withdrawal_request']['address']
    amount = user.cache['clipboard']['withdrawal_request']['amount']
    if button == 'yes':

        # TODO учесть комсу
        WithdrawalRequest.objects.create(
            user=user,
            currency=currency,
            amount=amount,
            address=address,
            fee=0
        )
        cb.message.edit(cb.message.text)
        cb.message.reply('Ваша заявка создана')

    if button == 'no':
        cb.message.edit(user.get_text(name='wallet-select_requisite_for_withdrawal').format(currency=currency), reply_markup=kb.select_requisite_for_withdrawal(user, currency))


@Client.on_callback_query(Filters.callback_data('confirm_cancel_withdrawal'))
def confirm_cancel_withdrawal(cli, cb):
    user = get_user(cb.from_user.id)

    withdrawal_request = user.withdrawalRequests.get(status__in=['pending verification', 'verifed'])
    withdrawal_request.status = 'canceled by user'
    withdrawal_request.save()

    cb.message.edit('Успешно!')

    msgs = user.msg

    delete_msg(cli, user.telegram_id, msgs.wallet_menu)

    msg = cb.message.reply(wallet_info(user), reply_markup=kb.wallet_menu(user))
    msgs.wallet_menu = msg.message_id
    msgs.save()
