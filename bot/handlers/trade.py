from decimal import Decimal, InvalidOperation
from time import sleep

from pyrogram import Client, Filters

from bot.models import CurrencyList
from order.logic.core import get_order_info
from order.models import Order
from order.logic import kb as order_kb
from trade.logic.core import auto_trade, check_balance_from_trade
from trade.logic import kb
from trade.models import Trade
from bot.helpers.shortcut import get_user, to_cents, to_units, round_currency, update_cache_msg, delete_inline_kb
from bot.blockchain.core import check_tx_hash


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:11] == 'start_trade'))
def start_trade(cli, cb):
    user = get_user(cb.from_user.id)

    order_id = int(cb.data.split('-')[1])

    order = Order.objects.get(id=order_id)

    payment_currency_rate = to_cents(order.payment_currency, 1) / order.currency_rate
    trade = Trade.objects.create(
            order=order,
            user=user,
            trade_currency=order.trade_currency,
            payment_currency=order.payment_currency,
            trade_currency_rate=order.currency_rate,
            payment_currency_rate=payment_currency_rate
        )

    user.cache['clipboard']['active_trade'] = trade.id
    user.save()

    flags = user.flags
    flags.await_amount_for_trade = True
    flags.save()
    order_amount = to_units(trade.order.trade_currency, trade.order.amount)

    if trade.order.type_operation == 'sale':
        balance = user.get_balance(trade.payment_currency, cent2unit=True)

        max_amount = round_currency(trade.payment_currency, balance / to_units(trade.trade_currency, trade.trade_currency_rate))

        if max_amount > order_amount:
            max_amount = round_currency(trade.trade_currency, order_amount)

    else:
        balance = user.get_balance(trade.trade_currency, cent2unit=True)

        if balance > order_amount:
            max_amount = round_currency(trade.trade_currency, order_amount)
        else:
            max_amount = round_currency(trade.trade_currency, balance)

    msg = cb.message.edit(user.get_text(name='trade-enter_amount_for_trade').format(
        amount=max_amount,
        currency=trade.trade_currency
    ), reply_markup=kb.cancel_trade(user))

    update_cache_msg(user, 'trade_enter_amount', msg.message_id)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('trade_cancel')))
def trade_cancel(cli, cb):
    user = get_user(cb.from_user.id)
    flags = user.flags
    flags.await_amount_for_trade = False
    flags.await_replenishment_for_trade = False
    flags.save()

    trade_id = user.cache['clipboard']['active_trade']
    trade = user.trade.get(id=trade_id)
    cb.message.edit(cb.message.text + '\n\n' + user.get_text(name='trade-your_canceled_trade'))
    cb.message.reply(get_order_info(user, trade.order.id), reply_markup=order_kb.order_for_user(user, trade.order.id))

    trade.delete()


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags.await_amount_for_trade))
def amount_for_trade(cli, m):
    user = get_user(m.from_user.id)
    trade = Trade.objects.get(id=user.cache['clipboard']['active_trade'])

    try:
        # TODO лимит установить
        amount = Decimal(m.text.replace(',', '.'))
        if amount == 0:
            raise InvalidOperation

        if to_cents(trade.trade_currency, amount) > trade.order.amount:
            if trade.order.type_operation == 'sale':
                type_operation = user.get_text(name='order-type_operation_translate_buy_2')
            else:
                type_operation = user.get_text(name='order-type_operation_translate_sale_2')

            limit = round_currency(trade.trade_currency, to_units(trade.trade_currency, trade.order.amount))
            msg = m.reply(f'Вы не можете {type_operation} больше чем {limit} {trade.trade_currency}')
            sleep(5)
            msg.delete()
            return

        flags = user.flags
        flags.await_amount_for_trade = False
        flags.save()

        price_trade = amount * to_units(trade.trade_currency, trade.trade_currency_rate)
        trade.price_trade = to_cents(trade.payment_currency, price_trade)
        trade.amount = to_cents(trade.trade_currency, amount)
        trade.save()

        if trade.order.type_operation == 'sale':
            currency = trade.payment_currency
            balance = user.get_balance(currency, cent2unit=True)
            cost_trade = price_trade
        else:
            currency = trade.trade_currency
            balance = user.get_balance(currency, cent2unit=True)
            cost_trade = amount

        is_good_balance = check_balance_from_trade(currency, cost_trade, balance)

        if not is_good_balance[0]:
            currency = is_good_balance[1]
            amount_deposit = is_good_balance[2]
            msg = m.reply(user.get_text(name='trade-not_enough_money_to_trade').format(
                amount=amount_deposit,
                currency=currency
            ), reply_markup=kb.not_enough_money_to_trade(user, currency))

            delete_inline_kb(cli, user.telegram_id, user.cache['msg']['trade_enter_amount'])
            update_cache_msg(user, 'last_trade', msg.message_id)

            return

    except InvalidOperation:
        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    if trade.order.type_operation == 'sale':
        type_translate = user.get_text(name='order-type_operation_translate_buy_1')
    else:
        type_translate = user.get_text(name='order-type_operation_translate_sale_1')

    txt = user.get_text(name='trade-confirm_amount_for_trade').format(
        type_operation=type_translate,
        amount=amount,
        payment_currency=trade.payment_currency,
        price_trade=round_currency(trade.payment_currency, price_trade),
        trade_currency=trade.trade_currency

    )
    m.reply(txt, reply_markup=kb.confirm_amount_for_trade(user))

    delete_inline_kb(cli, user.telegram_id, user.cache['msg']['trade_enter_amount'])


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('trade_deposit')))
def trade_deposit(cli, cb):
    user = get_user(cb.from_user.id)
    currency = cb.data.split('-')[1]

    user.cache['clipboard']['trade_deposit_currency'] = []
    user.cache['clipboard']['trade_deposit_currency'].append(currency)
    user.save()

    flags = user.flags
    flags.await_replenishment_for_trade = True
    flags.save()

    address = user.get_address(currency)

    cb.message.reply(user.get_text(name='wallet-address_for_deposit').format(currency=currency))
    cb.message.reply(f'```{address}```')

#
# @Client.on_callback_query(Filters.callback_data('continue_trade_after_deposit'))
# def continue_trade_after_deposit(cli, cb):
#     user = get_user(cb.from_user.id)
#
#     trade = user.trade.get(id=user.cache['clipboard']['active_trade'])
#
#


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith('confirm_amount_for_trade')))
def confirm_amount_for_trade(cli, cb):
    user = get_user(cb.from_user.id)
    trade = user.trade.get(id=user.cache['clipboard']['active_trade'])
    owner = trade.order.parent_order.user
    answer = cb.data.split('-')[1]

    if answer == 'yes':
        txt = f'\n\n{user.get_text(name="bot-you_choosed").format(foo="yes")}'
        cb.message.edit(cb.message.text+txt)

        inst_trade_currency = CurrencyList.objects.get(currency=trade.trade_currency)
        inst_payment_currency = CurrencyList.objects.get(currency=trade.payment_currency)

        if inst_trade_currency.type == 'crypto' and inst_payment_currency.type == 'crypto':

            if trade.order.type_operation == 'sale':
                type_translate_for_user = user.get_text(name='order-type_operation_translate_buy_2')
                type_translate_for_owner = owner.get_text(name='order-type_operation_translate_sale_2')
            else:
                type_translate_for_user = user.get_text(name='order-type_operation_translate_sale_2')
                type_translate_for_owner = owner.get_text(name='order-type_operation_translate_buy_2')

            trade.type_trade = 'auto'
            trade.status = 'in processing'
            trade.save()

            # проведение автотрейда
            auto_trade(trade)

            txt_for_user = user.get_text(name='trade-success_trade').format(
                type_operation=type_translate_for_user,
                amount=round_currency(trade.trade_currency, to_units(trade.trade_currency, trade.amount)),
                trade_currency=trade.trade_currency,
                price_trade=to_units(trade.payment_currency, trade.price_trade),
                payment_currency=trade.payment_currency
            )

            txt_for_owner = owner.get_text(name='trade-success_trade').format(
                type_operation=type_translate_for_owner,
                amount=round_currency(trade.trade_currency, to_units(trade.trade_currency, trade.amount)),
                trade_currency=trade.trade_currency,
                price_trade=round_currency(trade.payment_currency, to_units(trade.payment_currency, trade.price_trade)),
                payment_currency=trade.payment_currency
            )

            cb.message.reply(txt_for_user)
            cli.send_message(owner.telegram_id, txt_for_owner)

    if answer == 'no':
        trade_id = user.cache['clipboard']['active_trade']
        trade = Trade.objects.get(id=trade_id)

        cb.message.edit(cb.message.text + '\n\n' + user.get_text(name='trade-your_canceled_trade'))
        cb.message.reply(get_order_info(user, trade.order.id), reply_markup=order_kb.order_for_user(user, trade.order.id))

# @Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:17] == 'select_type_order'))
# def select_type_order(cli, cb):
#     user = get_user(cb.from_user.id)
#     trade = user.trade.get(id=user.cache['clipboard']['active_trade'])
#     owner = trade.order.parent_order.user
#     flags = user.flags
#
#     button = cb.data.split('-')[1]
#
#     if trade.order.type_operation == 'sale':
#         type_translate_for_user = user.get_text(name='order-type_operation_translate_buy_2')
#         type_translate_for_owner = owner.get_text(name='order-type_operation_translate_sale_2')
#     else:
#         type_translate_for_user = user.get_text(name='order-type_operation_translate_sale_2')
#         type_translate_for_owner = owner.get_text(name='order-type_operation_translate_buy_2')
#
#     if button == 'internal_wallet':
#         virtual_wallet = user.virtual_wallets.get(currency=trade.payment_currency)
#
#         if trade.price_trade > virtual_wallet.balance:
#             cb.message.edit(user.get_text(name='trade-not_enough_money_to_trade'), reply_markup=kb.not_enough_money_to_trade(user))
#             return
#
#         trade.type_trade = 'auto'
#         trade.status = 'in processing'
#         trade.save()
#
#         # проведение автотрейда
#         auto_trade(trade)
#
#         txt_for_user = user.get_text(name='trade-success_trade').format(
#             type_operation=type_translate_for_user,
#             amount=round_currency(trade.trade_currency, to_units(trade.trade_currency, trade.amount)),
#             trade_currency=trade.trade_currency,
#             price_trade=to_units(trade.payment_currency, trade.price_trade),
#             payment_currency=trade.payment_currency
#         )
#
#         txt_for_owner = owner.get_text(name='trade-success_trade').format(
#             type_operation=type_translate_for_owner,
#             amount=round_currency(trade.trade_currency, to_units(trade.trade_currency, trade.amount)),
#             trade_currency=trade.trade_currency,
#             price_trade=round_currency(trade.payment_currency, to_units(trade.payment_currency, trade.price_trade)),
#             payment_currency=trade.payment_currency
#         )
#
#         cb.message.reply(txt_for_user)
#         cli.send_message(owner.telegram_id, txt_for_owner)
#
#     if button == 'third_party_wallet':
#         owner_requisite = trade.order.requisites
#         trade.type_trade = 'semi-automatic'
#         trade.status = 'in processing'
#         trade.save()
#
#         flags.await_tx_hash = True
#         flags.save()
#
#         # TODO тут логика с депонированием
#         cb.message.reply(user.get_text(name='trade-semi_automatic_start').format(
#             amount=to_units(trade.trade_currency, trade.price_trade),
#             currency=trade.payment_currency,
#             address=owner_requisite
#         ), reply_markup=kb.cancel_trade(user))
#
#     if button == 'deposit':
#         cli.answer_callback_query(cb.id, 'Пока не понятно как сделать красиво)')


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags.await_tx_hash))
def await_tx_hash(cli, m):
    user = get_user(m.from_user.id)
    flags = user.flags
    trade = user.trade.get(id=user.cache['clipboard']['active_trade'])
    tx_hash = m.text

    if check_tx_hash(tx_hash, trade.payment_currency, trade.price_trade, trade.order.requisites):
        flags.await_tx_hash = False
        flags.save()

        trade.tx_hash = tx_hash
        trade.save()

        m.reply(user.get_text(name='trade-await_confirm_from_owner'))

        owner = trade.order.parent_order.user
        cli.send_message(owner.telegram_id, owner.get_text(name='trade-confirm_transaction').format(
            amount=round(to_units(trade.payment_currency, trade.price_trade), 6),
            currency=trade.payment_currency,
            address=trade.order.requisites,
            tx_hash=tx_hash
        ), reply_markup=kb.confirm_payment(owner, trade, tx_hash))

    else:
        # TODO::
        # ошибок может быть две
        #  1. ошибка в вводе юзеа (неверный формат хэша)
        #  2. хэш от транзакции которая не подходит
        #
        #  это разные Ошибочки, вот корректные обработки:
        #  1 - переспросить юзера
        #  2 - проверять транзу по КД (джоба) + дать юзеру кнопку проверки вручную
        #      он также может прислать другую ТХ, тогда проверка текущей ТХ должна закончиться
        m.reply('Ошибочка')


# @Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:15] == 'confirm_payment'))
# def confirm_payment(cli, cb):
#     user = get_user(cb.from_user.id)
#     trade_id = int(cb.data.split('-')[2])
#     trade = Trade.objects.get(id=trade_id)
#
#     answer = cb.data.split('-')[1]
#     if answer == 'yes':
#         cb.message.reply(user.get_text(name='trade-second_confirm_transaction'), reply_markup=kb.second_confirm(user, trade, trade.tx_hash))
#
#     elif answer == 'no':
#         cli.answer_callback_query(cb.id, 'Пожалуйста, не торопитесь. По нашим данным транзакция успешна.', show_alert=True)
#
#
# @Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:22] == 'second_confirm_payment'))
# def second_payment(cli, cb):
#     owner = get_user(cb.from_user.id)
#     trade_id = int(cb.data.split('-')[2])
#     trade = Trade.objects.get(id=trade_id)
#
#     user = trade.user
#
#     answer = cb.data.split('-')[1]
#
#     if trade.order.type_operation == 'sale':
#         type_translate_for_user = user.get_text(name='order-type_operation_translate_buy_2')
#         type_translate_for_owner = owner.get_text(name='order-type_operation_translate_sale_2')
#     else:
#         type_translate_for_user = user.get_text(name='order-type_operation_translate_sale_2')
#         type_translate_for_owner = owner.get_text(name='order-type_operation_translate_buy_2')
#
#     if answer == 'yes':
#         semi_auto_trade(trade)
#
#         txt_for_user = user.get_text(name='trade-success_trade').format(
#             type_operation=type_translate_for_user,
#             amount=round(to_units(trade.trade_currency, trade.amount), 6),
#             trade_currency=trade.trade_currency,
#             price_trade=round(to_units(trade.payment_currency, trade.price_trade), 6),
#             payment_currency=trade.payment_currency
#         )
#
#         txt_for_owner = owner.get_text(name='trade-success_trade').format(
#             type_operation=type_translate_for_owner,
#             amount=round(to_units(trade.trade_currency, trade.amount), 6),
#             trade_currency=trade.trade_currency,
#             price_trade=round(to_units(trade.payment_currency, trade.price_trade), 6),
#             payment_currency=trade.payment_currency
#         )
#
#         cb.message.reply(txt_for_owner)
#         cli.send_message(user.telegram_id, txt_for_user)
#
#     elif answer == 'no':
#         cli.answer_callback_query(cb.id, 'Пожалуйста, не торопитесь. По нашим данным транзакция успешна.',
#                                   show_alert=True)
