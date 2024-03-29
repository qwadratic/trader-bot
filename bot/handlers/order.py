from time import sleep
from decimal import Decimal, InvalidOperation

from mintersdk.shortcuts import to_bip, to_pip
from pyrogram import Client, Filters

from user.models import UserPurse
from order.logic import kb
from order.logic.core import get_order_info, create_order, order_info_for_owner
from order.logic.text_func import choice_payment_currency_text
from order.models import TempOrder
from bot.helpers.converter import currency_in_user_currency, currency_in_usd
from bot.helpers.shortcut import get_user, delete_msg, check_address


@Client.on_message(Filters.create(lambda _, m: m.text == get_user(m.from_user.id).get_text(name='user-kb-trade')))
def trade_menu(cli, m):
    user = get_user(m.from_user.id)
    user_msg = user.msg

    delete_msg(cli, user.telegram_id, user_msg.trade_menu)

    msg = m.reply(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))
    user_msg.trade_menu = msg.message_id
    user_msg.save()

    m.delete()


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:10] == 'trade_menu'))
def trade_menu_controller(cli, cb):
    user = get_user(cb.from_user.id)

    button = cb.data.split('-')[1]

    if button == 'new_buy':

        TempOrder.objects.delete_and_create(
            user=user,
            type_operation='buy'
        )
        cb.message.edit(
            user.get_text(name='order-select_trade_currency').format(
                type_operation=user.get_text(name='order-type_operation_translate_buy_1')),
            reply_markup=kb.trade_currency(user))

    elif button == 'new_sale':

        TempOrder.objects.delete_and_create(
            user=user,
            type_operation='sale'
        )

        cb.message.edit(
            user.get_text(name='order-select_trade_currency').format(
                type_operation=user.get_text(name='order-type_operation_translate_sale_1')),
            reply_markup=kb.trade_currency(user))

    elif button == 'orders':
        cb.message.edit(user.get_text(name='order-orders_menu'), reply_markup=kb.order_list(user, 'sale', 0))

    elif button == 'my_orders':
        cb.message.edit(user.get_text(name='order-my_orders'), reply_markup=kb.owner_order_list(user, 0))

    elif button == 'my_trades':
        pass
    elif button == 'notifications':
        pass


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:10] == 'order_list'))
def order_list(cli, cb):
    user = get_user(cb.from_user.id)

    action = cb.data.split('-')[1]

    if action == 'back':
        cb.message.edit(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))

    elif action == 'switch':
        type_orders = cb.data.split('-')[2]
        cb.message.edit(user.get_text(name='order-orders_menu'), reply_markup=kb.order_list(user, type_orders, 0))

    elif action == 'move':
        cours = cb.data.split('-')[2]
        type_operation = cb.data.split('-')[3]
        offset = int(cb.data.split('-')[4])

        if cours == 'right':
            offset += 7

        elif cours == 'left':
            offset -= 7

        cb.message.edit(user.get_text(name='order-orders_menu'), reply_markup=kb.order_list(user, type_operation, offset))

    elif action == 'open':
        order_id = int(cb.data.split('-')[2])
        type_orders = cb.data.split('-')[3]
        offset = int(cb.data.split('-')[4])
        cb.message.edit(get_order_info(user, order_id), reply_markup=kb.order_for_user(user, order_id, type_orders, offset))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:10] == 'order_info'))
def order_info(cli, cb):
    user = get_user(cb.from_user.id)

    action = cb.data.split('-')[1]

    if action == 'back':
        cours = cb.data.split('-')[2]
        if cours == 'order_list':
            type_orders = cb.data.split('-')[3]
            offset = int(cb.data.split('-')[4])
            cb.message.edit(user.get_text(name='order-orders_menu'), reply_markup=kb.order_list(user, type_orders, offset))

        elif cours == 'my_orders':
            cb.message.edit(user.get_text(name='order-my_orders'), reply_markup=kb.owner_order_list(user, 0))

    elif action == 'share':
        cli.answer_callback_query(cb.id, 'coming soon')


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:14] == 'trade_currency'))
def select_trade_currency(_, cb):
    trade_currency = cb.data.split('-')[1]
    user = get_user(cb.from_user.id)
    temp_order = user.temp_order

    if trade_currency == 'back':
        cb.message.edit(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))

    else:
        temp_order.trade_currency = trade_currency
        temp_order.save()

        if temp_order.type_operation == 'sale':
            txt = f'\n\n{user.get_text(name="order-type_operation_translate_sale_3").format(currency=trade_currency)}'
        else:
            txt = f'\n\n{user.get_text(name="order-type_operation_translate_buy_3").format(currency=trade_currency)}'

        cb.message.edit(cb.message.text + txt)
        cb.message.reply(
            user.get_text('order-select_payment_currency').format(currency=temp_order.trade_currency),
            reply_markup=kb.payment_currency(trade_currency, user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:22] == 'order_payment_currency'))
def select_payment_currency(cli, cb):
    user = get_user(cb.from_user.id)

    payment_currency = cb.data.split('-')[1]

    order = user.temp_order
    trade_currency = order.trade_currency
    payment_currency_list = order.payment_currency

    if payment_currency == 'accept':

        if len(payment_currency_list) == 0:
            cli.answer_callback_query(cb.id, user.get_text(name='order-error_no_selected_payment_instrument'))
            return

        user.cache['clipboard']['requisites'].clear()
        user.save()

        # TODO расширить логику для валют из "таблицы"
        for currency in payment_currency_list:
            order.payment_currency_rate[currency] = to_pip(currency_in_usd(currency, 1))
        order.save()

        if order.type_operation == 'sale':

            for currency in payment_currency_list:
                user.cache['clipboard']['requisites'].append(currency)

            # текущая валюта для выбора реквизитов
            currency = user.cache['clipboard']['currency'] = user.cache['clipboard']['requisites'][0]
            user.save()

            cb.message.edit(cb.message.text)
            cb.message.reply(
                user.get_text(name='order-select_requisite_for_order').format(currency=currency),
                reply_markup=kb.choice_requisite_for_order(order, currency))

        if order.type_operation == 'buy':
            currency = order.trade_currency
            user.cache['clipboard']['requisites'].append(currency)
            user.cache['clipboard']['currency'] = currency
            user.save()

            cb.message.edit(cb.message.text)
            cb.message.reply(
                user.get_text(name='order-select_requisite_for_order').format(currency=currency),
                reply_markup=kb.choice_requisite_for_order(order, currency))

    elif payment_currency == 'back':
        order.payment_currency.clear()
        order.save()
        if order.type_operation == 'sale':
            txt = user.get_text(name='order-select_trade_currency').format(
                type_operation=user.get_text(name='order-type_operation_translate_sale_1'))
        else:
            txt = user.get_text(name='order-select_trade_currency').format(
                type_operation=user.get_text(name='order-type_operation_translate_buy_1'))

        cb.message.edit(txt, reply_markup=kb.trade_currency(user))

    # select currency via inline kb
    else:
        if payment_currency in payment_currency_list:
            payment_currency_list.remove(payment_currency)
        else:
            payment_currency_list.append(payment_currency)

        order.save()

        cb.message.edit(choice_payment_currency_text(order), reply_markup=kb.payment_currency(trade_currency, user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:19] == 'requisite_for_order'))
def select_requisite_for_order(cli, cb):
    user = get_user(cb.from_user.id)
    order = user.temp_order
    cache = user.cache
    flags = user.flags

    current_currency = user.cache['clipboard']['currency']
    choice = cb.data.split('-')[1]

    if choice == 'use_wallet':

        if current_currency == 'USDT':
            internal_address = user.wallets.get(currency='ETH').address
        else:
            internal_address = user.wallets.get(currency=current_currency).address

        order.requisites[current_currency] = internal_address
        order.save()

        txt = f'\n\n{user.get_text(name="bot-you_choosed").format(foo=internal_address)}'

        cache['clipboard']['requisites'].remove(cache['clipboard']['currency'])

        if len(cache['clipboard']['requisites']) <= 0:

            cb.message.edit(cb.message.text + txt)
            cb.message.reply(user.get_text(name='order-enter_currency_rate').format(
                trade_currency=order.trade_currency,
                user_currency=user.settings.currency,
                price=currency_in_user_currency(order.trade_currency, user.settings.currency, 1)))

            flags.await_currency_rate = True
            flags.save()
        else:
            currency = user.cache['clipboard']['requisites'][0]

            cache['clipboard']['currency'] = currency

            cb.message.edit(cb.message.text + txt)
            cb.message.reply(
                user.get_text(name='order-select_requisite_for_order').format(currency=currency),
                reply_markup=kb.choice_requisite_for_order(order, currency))

        user.save()

    if choice == 'use':
        req_id = int(cb.data.split('-')[2])
        internal_address = user.requisites.get(id=req_id)
        order.requisites[current_currency] = internal_address
        order.save()

        txt = f'\n\n{user.get_text(name="bot-you_choosed").format(foo=internal_address)}'
        cb.message.edit(cb.message.text + txt)
        cb.message.reply(user.get_text(name='order-enter_currency_rate').format(
            trade_currency=order.trade_currency,
            user_currency=user.settings.currency,
            price=currency_in_user_currency(order.trade_currency, user.settings.currency, 1)))

        flags.await_currency_rate = True
        flags.save()

    if choice == 'open_purse':
        cb.message.edit(cb.message.text)
        cb.message.reply(user.get_text(name='order-select_requisite_from_purse'),
                         reply_markup=kb.requisites_from_purse(user))

    if choice == 'add_new':
        flags.await_requisite_for_order = True
        flags.save()

        cb.message.edit(cb.message.text)
        cb.message.reply(user.get_text(name='purse-enter_address').format(currency=current_currency))


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags and
                                               get_user(m.from_user.id).flags.await_requisite_for_order))
def requisite_for_order(cli, m):
    user = get_user(m.from_user.id)
    order = user.temp_order
    flags = user.flags

    current_currency = user.cache['clipboard']['currency']
    requisite = UserPurse.objects.create(user=user, currency=current_currency)

    address = m.text if check_address(m.text, current_currency) else None
    if not address:
        msg = m.reply(user.get_text(name='bot-invalid_address'))
        sleep(3)
        msg.delete()
        return

    if address:
        requisite.address = address
        requisite.status = 'valid'
        requisite.save()

        flags.await_requisite_for_order = False
        flags.save()

    order.requisites[current_currency] = requisite.address
    order.save()

    user.cache['clipboard']['requisites'].remove(current_currency)

    if len(user.cache['clipboard']['requisites']) <= 0:

        m.reply(user.get_text(name='order-enter_currency_rate').format(
            trade_currency=order.trade_currency,
            user_currency=user.settings.currency,
            price=currency_in_user_currency(order.trade_currency, user.settings.currency, 1)))

        flags.await_currency_rate = True
        flags.save()
    else:
        currency = user.cache['clipboard']['requisites'][0]

        user.cache['clipboard']['currency'] = currency

        m.reply(
            user.get_text(name='order-select_requisite_for_order').format(currency=currency),
            reply_markup=kb.choice_requisite_for_order(order, currency))

    user.save()


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:20] == 'requisite_from_purse'))
def requisite_for_order_from_purse(cli, cb):
    user = get_user(cb.from_user.id)
    order = user.temp_order
    flags = user.flags
    current_currency = user.cache['clipboard']['currency']

    button = cb.data.split('-')[1]

    if button == 'back':
        cb.message.edit(
            user.get_text(name='order-choice_requisite_for_order').format(currency=current_currency),
            reply_markup=kb.choice_requisite_for_order(order, current_currency))

        return

    if button == 'use':
        req_id = int(cb.data.split('-')[2])
        internal_address = user.requisites.get(id=req_id).address

        order.requisites[current_currency] = internal_address
        order.save()

        txt = f'\n\n{user.get_text(name="bot-you_choosed").format(foo=internal_address)}'
        cb.message.edit(cb.message.text + txt)
        cb.message.reply(user.get_text(name='order-enter_currency_rate').format(
            trade_currency=order.trade_currency,
            user_currency=user.settings.currency,
            price=currency_in_user_currency(order.trade_currency, user.settings.currency, 1)))

        flags.await_currency_rate = True
        flags.save()


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags and
                                               get_user(m.from_user.id).flags.await_currency_rate))
def enter_currency_rate(cli, m):
    user = get_user(m.from_user.id)

    try:
        value = Decimal(m.text.replace(',', '.'))
    except InvalidOperation:

        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    currency_rate = to_pip(currency_in_usd(user.settings.currency, value))

    order = user.temp_order
    order.currency_rate = currency_rate
    order.save()

    flags = user.flags
    flags.await_currency_rate = False
    flags.await_amount_for_order = True
    flags.save()

    if order.type_operation == 'sale':
        type_operation = user.get_text(name='order-type_operation_translate_sale_1')
        max_amount = round(to_bip(user.virtual_wallets.get(currency=order.trade_currency).balance), 6)
    else:
        type_operation = user.get_text(name='order-type_operation_translate_buy_1')
        max_amount = '))'

    m.reply(user.get_text(name='order-enter_amount').format(
        type_operation=type_operation,
        currency=order.trade_currency,
        amount=max_amount))


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags and
                                               get_user(m.from_user.id).flags.await_amount_for_order))
def amount_for_order(cli, m):
    user = get_user(m.from_user.id)
    temp_order = user.temp_order

    try:
        amount = to_pip(Decimal(m.text.replace(',', '.')))
        if temp_order.type_operation == 'sale':
            if amount > user.virtual_wallets.get(currency=temp_order.trade_currency).balance:
                msg = m.reply(f'Вы не можете продать больше чем {to_bip(user.virtual_wallets.get(currency=temp_order.trade_currency).balance)} {temp_order.trade_currency}')
                sleep(5)
                msg.delete()
                return
    except InvalidOperation:

        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    temp_order.amount = amount

    flags = user.flags
    flags.await_amount_for_order = False
    flags.save()

    order = create_order(temp_order)

    m.reply(order_info_for_owner(order), reply_markup=kb.order_for_owner(order, 1))
