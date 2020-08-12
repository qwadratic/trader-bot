from pyrogram import Client, Filters

from bot.helpers.shortcut import get_user, to_units
from bot.models import WithdrawalRequest
from user.logic import kb
from user.logic.core import finish_withdraw
from user.logic.filters import filter_admin


@Client.on_message(Filters.create(lambda _, m: m.text == get_user(m.from_user.id).get_text(name='admin-kb-withdrawal_requests'))
                   & filter_admin)
def open_withdrawal_requests(cli, m):
    user = get_user(m.from_user.id)

    m.reply('Cписок заявок на ручной вывод', reply_markup=kb.withdrawal_requests(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('withdrawal_request_list')))
def view_withdrawal_request(cli, cb):
    user = get_user(cb.from_user.id)

    button = cb.data.split('-')[1]

    if button == 'open':
        req_id = int(cb.data.split('-')[2])

        withdrawal_request = WithdrawalRequest.objects.get(id=req_id)
        currency = withdrawal_request.currency
        amount = withdrawal_request.amount
        address = withdrawal_request.address
        cb.message.reply(
            user.get_text(name='bot-withdrawal_request_info').format(
                id=req_id,
                user=user.username,
                amount=to_units(currency, amount, round=True),
                currency=currency,
                address=address
            ),
            reply_markup=kb.manual_withdrawal(user, req_id)
        )

    if button == 'send_tx':
        req_id = int(cb.data.split('-')[2])
        flags = user.flags
        flags.await_tx_hash_for_withdrawal = True
        flags.save()

        user.cache['admin'] = dict(request_withdrawal_id=req_id)
        user.save()

        cb.message.edit(cb.message.text)
        cb.message.reply(user.get_text(name='admin-await_withdrawal_tx_hash'), reply_markup=kb.cancel_withdrawal_tx_hash(user))

    if button == 'refuse':
        req_id = int(cb.data.split('-')[2])
        withdrawal_request = WithdrawalRequest.objects.get(id=req_id)
        withdrawal_request.status = 'canceled by admin'
        withdrawal_request.save()

        user = withdrawal_request.user
        currency = withdrawal_request.currency
        amount = to_units(currency, withdrawal_request.amount, round=True)

        txt = user.get_text(name='wallet-denied withdrawal').format(
            amount=amount,
            currency=currency,
        )

        cli.send_message(user.telegram_id, txt)

        cb.message.edit(cb.message.text)
        cb.message.reply('Готово!')


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id) and
                                               get_user(m.from_user.id).flags.await_tx_hash_for_withdrawal))
def check_tx_hash_for_withdrawal(cli, m):
    user = get_user(m.from_user.id)

    tx_hash = m.text
    user.cache['admin']['withdrawal_hash'] = tx_hash
    user.save()

    flags = user.flags
    flags.await_tx_hash_for_withdrawal = False
    flags.save()

    m.reply(user.get_text(name='admin-confirm_tx_hash_withdrawal').format(tx_hash=tx_hash), reply_markup=kb.confirm_tx_hash_withdrawal(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('confirm_tx_hash_withdrawal')))
def confirm_tx_hash_withdrawal(cli, cb):
    admin = get_user(cb.from_user.id)
    req_id = admin.cache['admin']['request_withdrawal_id']

    button = cb.data.split('-')[1]
    if button == 'yes':
        tx_hash = admin.cache['admin']['withdrawal_hash']
        finish_withdraw(req_id, tx_hash)

        withdrawal_request = WithdrawalRequest.objects.get(id=req_id)
        user = withdrawal_request.user
        currency = withdrawal_request.currency
        amount = to_units(currency, withdrawal_request.amount, round=True)
        address = withdrawal_request.address
        txt = user.get_text(name='wallet-successful_withdrawal').format(
            amount=amount,
            currency=currency,
            address=address
        )
        cli.send_message(user.telegram_id, txt, reply_markup=kb.show_tx(user, currency, tx_hash))

        cb.message.edit(cb.message.text)
        cb.message.reply('Готово!')



@Client.on_callback_query(Filters.callback_data('cancel_withdrawal_tx'))
def cancel_withdrawal_tx(cli, cb):
    user = get_user(cb.from_user.id)
    flags = user.flags
    flags.await_tx_hash_for_withdrawal = False
    flags.save()

    cb.message.edit(cb.message.text)
    cb.message.reply('Отменено')


