from time import sleep
from decimal import Decimal, InvalidOperation

from pyrogram import Client, Filters

from bot.models import CurrencyList

from order.logic import kb
from order.logic.core import get_order_info, create_order, order_info_for_owner, hold_money_order, \
    check_balance_from_order, update_order, close_order
from order.logic.text_func import choice_payment_currency_text, get_lack_balance_text
from order.models import TempOrder, Order

from bot.helpers.converter import currency_in_usd
from bot.helpers.shortcut import get_user, delete_msg, to_cents, to_units, get_currency_rate, \
    round_currency, update_cache_msg, delete_inline_kb, get_fee_amount
from trade.logic.trade_filters import in_trade

from constance import config


@Client.on_message(Filters.create(lambda _, m: m.text == get_user(m.from_user.id).get_text(name='user-kb-trade')) & in_trade)
def trade_menu(cli, m):
    user = get_user(m.from_user.id)

    delete_msg(cli, user.telegram_id, user.cache['msg']['trade_menu'])
    msg = m.reply(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))
    update_cache_msg(user, 'trade_menu', msg.message_id)

    m.delete()


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('trade_menu')))
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

        cb.message.edit(user.get_text(name='order-market_depth-select_trade_currency'),
                        reply_markup=kb.market_depth_trade_currency(user))

    elif button == 'my_orders':
        cb.message.edit(user.get_text(name='order-my_orders'), reply_markup=kb.owner_order_list(user, 'sale', 0))

    elif button == 'my_trades':
        pass
    elif button == 'notifications':
        pass


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('select_currency_for_market_depth')))
def select_currency_for_market_depth(cli, cb):
    user = get_user(cb.from_user.id)
    cb_data = cb.data.split('-')
    type_currency = cb_data[1]

    if type_currency == 'trade_currency':
        currency = cb_data[2]

        # TODO костыль
        try:
            user.cache['clipboard']['market_depth']['trade_currency'] = currency
        except KeyError:
            user.cache['clipboard']['market_depth'] = {}
            user.cache['clipboard']['market_depth']['trade_currency'] = currency

        user.save()

        cb.message.edit(user.get_text(name='order-market_depth-select_payment_currency'),
                        reply_markup=kb.market_depth_payment_currency(currency, user))

    if type_currency == 'payment_currency':
        currency = cb_data[2]
        user.cache['clipboard']['market_depth']['payment_currency'] = currency
        user.cache['clipboard']['market_depth']['revers'] = False
        user.save()

        trade_currency = user.cache['clipboard']['market_depth']['trade_currency']
        payment_currency = user.cache['clipboard']['market_depth']['payment_currency']

        cb.message.edit(user.get_text(name='order-orders_menu'),
                        reply_markup=kb.market_depth(user, trade_currency, payment_currency, 0))

    if type_currency == 'back_menu':
        cb.message.edit(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))

    if type_currency == 'back_trade_currency':
        cb.message.edit(user.get_text(name='order-market_depth-select_trade_currency'),
                        reply_markup=kb.market_depth_trade_currency(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('market_depth')))
def market_depth(cli, cb):
    user = get_user(cb.from_user.id)
    cb_data = cb.data.split('-')
    button = cb_data[1]

    if button == 'back':
        cb.message.edit(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))

    if button == 'open':
        cb_data = cb.data.split('-')
        order_id = int(cb_data[2])

        order = Order.objects.get(id=order_id)

        if user.id == order.parent_order.user_id:

            cb.message.reply(order_info_for_owner(order.parent_order),
                             reply_markup=kb.order_for_owner(order.parent_order))
        else:

            cb.message.reply(get_order_info(user, order_id),
                             reply_markup=kb.order_for_user(user, order_id))

    if button == 'reverse':

        revers = cb_data[2]
        if revers == 'True':
            trade_currency = user.cache['clipboard']['market_depth']['trade_currency']
            payment_currency = user.cache['clipboard']['market_depth']['payment_currency']
            revers = False

        else:
            trade_currency = user.cache['clipboard']['market_depth']['payment_currency']
            payment_currency = user.cache['clipboard']['market_depth']['trade_currency']
            revers = True

        user.cache['clipboard']['market_depth']['revers'] = revers
        user.save()

        cb.message.edit(user.get_text(name='order-orders_menu'),
                        reply_markup=kb.market_depth(user, trade_currency, payment_currency, 0, revers))

    if button == 'look':
        type_orders = cb_data[2]

        cb.message.edit('Глубина стакана', reply_markup=kb.half_market_depth(user, type_orders, 5))

    if button == 'back_to_market_depth':
        revers = user.cache['clipboard']['market_depth']['revers']

        if revers:
            trade_currency = user.cache['clipboard']['market_depth']['payment_currency']
            payment_currency = user.cache['clipboard']['market_depth']['trade_currency']
        else:
            trade_currency = user.cache['clipboard']['market_depth']['trade_currency']
            payment_currency = user.cache['clipboard']['market_depth']['payment_currency']

        cb.message.edit(user.get_text(name='order-orders_menu'),
                        reply_markup=kb.market_depth(user, trade_currency, payment_currency, 0, revers))

    if button == 'move':
        cours = cb.data.split('-')[2]
        type_operation = cb.data.split('-')[3]
        offset = int(cb.data.split('-')[4])

        if cours == 'right':
            offset += 10

        elif cours == 'left':
            offset -= 10

        cb.message.edit(user.get_text(name='order-orders_menu'),
                        reply_markup=kb.half_market_depth(user, type_operation, offset))

    # elif action == 'switch':
    #     type_orders = cb.data.split('-')[2]
    #     cb.message.edit(user.get_text(name='order-orders_menu'), reply_markup=kb.order_list(user, type_orders, 0))
    #
    # elif action == 'move':
    #     cours = cb.data.split('-')[2]
    #     type_operation = cb.data.split('-')[3]
    #     offset = int(cb.data.split('-')[4])
    #
    #     if cours == 'right':
    #         offset += 7
    #
    #     elif cours == 'left':
    #         offset -= 7
    #
    #     cb.message.edit(user.get_text(name='order-orders_menu'),
    #                     reply_markup=kb.order_list(user, type_operation, offset))
    #
    # elif action == 'open':
    #     order_id = int(cb.data.split('-')[2])
    #     type_orders = cb.data.split('-')[3]
    #     offset = int(cb.data.split('-')[4])
    #     order = Order.objects.get(id=order_id)
    #     if user.id == order.parent_order.user_id:
    #         cb.message.edit(get_order_info(user, order_id),
    #                         reply_markup=kb.order_for_owner(order.parent_order, 'orders', type_orders, offset))
    #     else:
    #         cb.message.edit(get_order_info(user, order_id),
    #                          reply_markup=kb.order_for_user(user, order_id, type_orders, offset))


# @Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:10] == 'order_list'))
# def order_list(cli, cb):
#     user = get_user(cb.from_user.id)
#
#     action = cb.data.split('-')[1]
#
#     if action == 'back':
#         cb.message.edit(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))
#
#     elif action == 'switch':
#         type_orders = cb.data.split('-')[2]
#         cb.message.edit(user.get_text(name='order-orders_menu'), reply_markup=kb.order_list(user, type_orders, 0))
#
#     elif action == 'move':
#         cours = cb.data.split('-')[2]
#         type_operation = cb.data.split('-')[3]
#         offset = int(cb.data.split('-')[4])
#
#         if cours == 'right':
#             offset += 7
#
#         elif cours == 'left':
#             offset -= 7
#
#         cb.message.edit(user.get_text(name='order-orders_menu'),
#                         reply_markup=kb.order_list(user, type_operation, offset))
#
#     elif action == 'open':
#         order_id = int(cb.data.split('-')[2])
#         type_orders = cb.data.split('-')[3]
#         offset = int(cb.data.split('-')[4])
#         order = Order.objects.get(id=order_id)
#         if user.id == order.parent_order.user_id:
#             cb.message.edit(get_order_info(user, order_id),
#                             reply_markup=kb.order_for_owner(order.parent_order, 'orders', type_orders, offset))
#         else:
#             cb.message.edit(get_order_info(user, order_id),
#                              reply_markup=kb.order_for_user(user, order_id, type_orders, offset))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('owner_order')))
def owner_order_list(cli, cb):
    user = get_user(cb.from_user.id)

    action = cb.data.split('-')[1]

    if action == 'open':
        order_id = int(cb.data.split('-')[2])
        order = user.parentOrders.get(id=order_id)

        cb.message.reply(order_info_for_owner(order), reply_markup=kb.order_for_owner(order))

    if action == 'move':
        cours = cb.data.split('-')[2]
        offset = int(cb.data.split('-')[3])

        if cours == 'right':
            offset += 7

        elif cours == 'left':
            offset -= 7

        cb.message.edit(user.get_text(name='order-my_orders'), reply_markup=kb.owner_order_list(user, 'sale', offset))

    if action == 'back':
        cb.message.edit(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:10] == 'order_info'))
def order_info(cli, cb):
    user = get_user(cb.from_user.id)

    action = cb.data.split('-')[1]

    if action == 'switch':
        order_id = int(cb.data.split('-')[2])
        order = user.parentOrders.get(id=order_id)
        if order.status == 'close':
            for currency in order.payment_currency:

                if order.type_operation == 'sale':
                    amount = order.amount
                    balance = user.get_balance(order.trade_currency)
                    if amount > balance:
                        cli.answer_callback_query(cb.id, f'Недостаточно {order.trade_currency} для начала торговли')
                        return

                elif order.type_operation == 'buy':
                    inst_currency = CurrencyList.objects.get(currency=currency)
                    if inst_currency.type == 'fiat':
                        continue

                    price_trade = Decimal(
                        to_units(order.trade_currency, order.amount)
                        * to_units(order.trade_currency, order.currency_rate)
                        / to_units(currency, order.payment_currency_rate[currency]))

                    user_balance = user.get_balance(currency, cent2unit=True)
                    if price_trade > user_balance:
                        cli.answer_callback_query(cb.id, f'Недостаточно {currency} для начала торговли')
                        return

            hold_money_order(order)

            update_order(order, 'set status', 'open')
            cb.message.edit(order_info_for_owner(order),

                            reply_markup=kb.order_for_owner(order))

        elif order.status == 'open':

            close_order(order, 'close')
            cb.message.edit(order_info_for_owner(order), reply_markup=kb.order_for_owner(order))


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

        txt = f'\n\n{user.get_text(name="you_selected").format(foo=trade_currency)}'
        cb.message.edit(cb.message.text + txt)
        cb.message.reply(user.get_text('order-select_payment_currency'), reply_markup=kb.payment_currency(trade_currency, user))


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

        for currency in payment_currency_list:
            order.payment_currency_rate[currency] = to_cents(currency, currency_in_usd(currency, 1))
        order.save()

        if order.type_operation == 'sale':

            for currency in payment_currency_list:
                currency_m = CurrencyList.objects.get(currency=currency)
                if currency_m.type == 'fiat':
                    continue
                    # user.cache['clipboard']['requisites'].append(currency)
                    # user.save()
                else:

                    if currency == 'USDT':
                        internal_address = user.wallets.get(currency='ETH').address
                    else:
                        internal_address = user.wallets.get(currency=currency).address

                    order.requisites[currency] = internal_address
                    order.save()

            cb.message.edit(cb.message.text)
            cb.message.reply(user.get_text(name='order-enter_currency_rate').format(
                trade_currency=order.trade_currency,

                price=round_currency('USD',
                                     to_units(order.trade_currency, get_currency_rate(order.trade_currency)))),
                reply_markup=kb.avarage_rate(user))

        if order.type_operation == 'buy':
            currency = order.trade_currency
            user.cache['clipboard']['requisites'].append(currency)
            user.cache['clipboard']['currency'] = currency
            user.save()
            currency_m = CurrencyList.objects.get(currency=currency)
            if currency_m.type == 'fiat':
                pass
            else:
                if currency == 'USDT':
                    internal_address = user.wallets.get(currency='ETH').address
                else:
                    internal_address = user.wallets.get(currency=currency).address

                order.requisites[currency] = internal_address
                order.save()

            cb.message.edit(cb.message.text)

            cb.message.reply(user.get_text(name='order-enter_currency_rate').format(
                trade_currency=order.trade_currency,
                price=round_currency(order.trade_currency,to_units(order.trade_currency, get_currency_rate(order.trade_currency)))),
                reply_markup=kb.avarage_rate(user))

        flags = user.flags
        flags.await_currency_rate = True
        flags.save()

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


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags and
                                               get_user(m.from_user.id).flags.await_currency_rate))
def enter_currency_rate(cli, m):
    user = get_user(m.from_user.id)
    order = user.temp_order
    try:
        value = Decimal(m.text.replace(',', '.'))
        current_price = to_units(order.trade_currency, get_currency_rate(order.trade_currency))

        max_price_range_factor = config.GET_MAX_PRICE_RANGE_FACTOR

        min_limit = current_price / (1 + max_price_range_factor)
        max_limit = current_price * (1 + max_price_range_factor)

        if value == 0:
            msg = m.reply('Недопустимое значение 0')
            sleep(5)
            msg.delete()
            return

        if value < min_limit or value > max_limit:
            m.reply(f'# TODO:: Недопустимое отклонение от курса\n'
                    f'Допустимый лимит {min_limit} - {max_limit}')

            return

    except InvalidOperation:

        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    order.currency_rate = to_cents(order.trade_currency, value)
    order.save()

    flags = user.flags
    flags.await_currency_rate = False
    flags.await_amount_for_order = True
    flags.save()

    if order.type_operation == 'sale':
        type_operation = user.get_text(name='order-type_operation_translate_sale_1')
        balance = user.get_balance(order.trade_currency, cent2unit=True)
        max_amount = round_currency(order.trade_currency, balance)

        msg = m.reply(user.get_text(name='order-enter_amount_for_sale').format(
            currency=order.trade_currency,
            amount=max_amount), reply_markup=kb.max_amount(user))

    else:

        msg = m.reply(user.get_text(name='order-enter_amount_for_buy').format(
            currency=order.trade_currency), reply_markup=kb.cancel_order(user, order.id))

    update_cache_msg(user, 'order_enter_amount', msg.message_id)


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags and
                                               get_user(m.from_user.id).flags.await_amount_for_order))
def amount_for_order(cli, m):
    user = get_user(m.from_user.id)
    temp_order = user.temp_order

    try:
        amount = Decimal(m.text.replace(',', '.'))

    except InvalidOperation:

        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    if temp_order.type_operation == 'sale':
        balance = user.get_balance(temp_order.trade_currency, cent2unit=True)
        fee_amount = get_fee_amount(config.MAKER_FEE, amount)
        if amount + fee_amount > balance:
            m.reply(f'Вы не можете продать больше чем '
                    f'{balance-fee_amount}'
                    f' {temp_order.trade_currency}')
            return

        if amount == 0:
            msg = m.reply('Недопустимое значение 0')
            sleep(5)
            msg.delete()
            return

        flags = user.flags
        flags.await_amount_for_order = False
        flags.save()

        temp_order.amount = to_cents(temp_order.trade_currency, amount)
        temp_order.save()

        order = create_order(temp_order)

        m.reply(order_info_for_owner(order), reply_markup=kb.order_for_owner(order))
    # покупка
    else:
        temp_order.amount = to_cents(temp_order.trade_currency, amount)
        temp_order.save()

        is_good_balance = check_balance_from_order(user, temp_order)
        if is_good_balance:
            flags = user.flags
            flags.await_amount_for_order = False
            flags.save()

            order = create_order(temp_order)

            m.reply(order_info_for_owner(order), reply_markup=kb.order_for_owner(order))
        else:
            deposit_currency = user.cache['clipboard']['deposit_currency']
            lack_balance_txt = get_lack_balance_text(temp_order, deposit_currency)

            txt = user.get_text(name='order-not_enough_money').format(balance=' '.join(deposit_currency),
                                                                      deposit_amount=lack_balance_txt)

            flags = user.flags
            flags.await_amount_for_order = False
            flags.await_replenishment_for_order = True
            flags.save()

            msg = m.reply(txt, reply_markup=kb.deposit_from_order(user))

            update_cache_msg(user, 'last_temp_order', msg.message_id)

            return

    delete_inline_kb(cli, user.telegram_id, user.cache['msg']['order_enter_amount'])


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('cancel_order_create')))
def cancel_order_create(cli, cb):
    user = get_user(cb.from_user.id)
    user.temp_order.delete()

    flags = user.flags
    flags.await_currency_rate = False
    flags.await_requisites_for_order = False
    flags.await_currency_rate = False
    flags.await_requisite_for_order = False
    flags.await_amount_for_order = False
    flags.await_replenishment_for_order = False
    flags.save()

    cb.message.edit(cb.message.text + '\n\n**Создание объявления отменено**')

    delete_msg(cli, user.telegram_id, user.cache['msg']['trade_menu'])

    msg = cb.message.reply(user.get_text(name='user-trade_menu'), reply_markup=kb.trade_menu(user))

    update_cache_msg(user, 'trade_menu', msg.message_id)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('order_helper')))
def order_helper(cli, cb):
    user = get_user(cb.from_user.id)
    order = user.temp_order
    button = cb.data.split('-')[1]

    if button == 'average_rate':
        current_rate = get_currency_rate(order.trade_currency)
        order.currency_rate = current_rate
        order.save()

        cb.message.edit(
            cb.message.text + '\n\n' + user.get_text(name='order-your_choice') +
            f'{round_currency(order.trade_currency, to_units(order.trade_currency, current_rate))}'
        )

        flags = user.flags
        flags.await_currency_rate = False
        flags.await_amount_for_order = True
        flags.save()

        if order.type_operation == 'sale':
            type_operation = user.get_text(name='order-type_operation_translate_sale_1')
            balance = user.get_balance(order.trade_currency, cent2unit=True)
            max_amount = round_currency(order.trade_currency, balance)

            msg = cb.message.reply(user.get_text(name='order-enter_amount_for_sale').format(
                currency=order.trade_currency,
                amount=max_amount), reply_markup=kb.max_amount(user))

        # покупка
        else:

            msg = cb.message.reply(user.get_text(name='order-enter_amount_for_buy').format(
                currency=order.trade_currency), reply_markup=kb.cancel_order(user, order.id))

        update_cache_msg(user, 'order_enter_amount', msg.message_id)

    if button == 'max_amount':
        if order.type_operation == 'sale':
            max_amount = user.get_balance(order.trade_currency)

        # покупка
        else:
            currency_balance = {}

            for currency in order.payment_currency:
                inst_currency = CurrencyList.objects.get(currency=currency)
                if inst_currency.type == 'fiat':
                    continue

                balance = user.get_balance(currency, cent2unit=True)
                currency_balance[currency] = balance * to_units(currency, order.payment_currency_rate[currency])

            min_currency = min(currency_balance, key=lambda currency: currency_balance[currency])

            max_amount = to_cents(order.trade_currency,
                                  currency_balance[min_currency] / to_units(order.trade_currency, order.currency_rate))

        order.amount = max_amount
        order.save()

        flags = user.flags
        flags.await_amount_for_order = False
        flags.save()

        new_order = create_order(order)

        cb.message.reply(order_info_for_owner(new_order), reply_markup=kb.order_for_owner(new_order))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('order_deposit')))
def order_deposit_navigation(cli, cb):
    user = get_user(cb.from_user.id)
    temp_order = user.temp_order
    button = cb.data.split('-')[1]

    if button == 'show_address':
        currency = cb.data.split('-')[2]
        deposit_address = user.cache['clipboard']['deposit_currency'][currency]['address']
        cb.message.reply(f'```{deposit_address}```')

    if button == 'back':
        flags = user.flags
        flags.await_replenishment_for_order = False
        flags.save()

        temp_order = user.temp_order
        temp_order.payment_currency = []
        temp_order.save()
        cb.message.edit(cb.message.text)

        cb.message.reply(user.get_text('order-select_payment_currency'),
                         reply_markup=kb.payment_currency(temp_order.trade_currency, user))

    if button == 'continue':

        user_currency_list = list(cb.data.split('-')[2].split(', '))

        for currency in temp_order.payment_currency:
            if currency not in user_currency_list:
                temp_order.payment_currency.remove(currency)

        temp_order.save()
        order = create_order(temp_order)
        cb.message.edit(cb.message.text)

        cb.message.reply(order_info_for_owner(order), reply_markup=kb.order_for_owner(order))


@Client.on_callback_query(Filters.callback_data('complete_order_create'))
def create_order_after_deposit(cli, cb):
    user = get_user(cb.from_user.id)
    order = create_order(user.temp_order)
    cb.message.edit(cb.message.text)

    cb.message.reply(order_info_for_owner(order), reply_markup=kb.order_for_owner(order))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('share_order')))
def share_order(cli, cb):
    user = get_user(cb.from_user.id)

    order_id = int(cb.data.split('-')[1])

    parent_order = user.parentOrders.get(id=order_id)
    for order in parent_order.orders.all():
        cb.message.reply(get_order_info(user, order.id), reply_markup=kb.share_url(user, order.id))
