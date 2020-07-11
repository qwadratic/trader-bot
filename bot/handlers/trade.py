from decimal import Decimal, InvalidOperation
from time import sleep

from mintersdk.shortcuts import to_bip, to_pip
from pyrogram import Client, Filters

from order.models import Order
from trade.logic.core import auto_trade, check_tx_hash, semi_auto_trade
from trade.logic import kb
from trade.models import Trade
from bot.helpers.shortcut import get_user


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:11] == 'start_trade'))
def start_trade(cli, cb):
    user = get_user(cb.from_user.id)

    order_id = int(cb.data.split('-')[1])

    order = Order.objects.get(id=order_id)
   
    trade = Trade.objects.create(
        order=order,
        user=user,
        trade_currency=order.trade_currency,
        payment_currency=order.payment_currency,
        trade_currency_rate=order.parent_order.currency_rate,
        payment_currency_rate=order.parent_order.payment_currency_rate[order.payment_currency]
    )

    user.cache['clipboard']['active_trade'] = trade.id
    user.save()

    flags = user.flags
    flags.await_amount_for_trade = True
    flags.save()

    cb.message.edit(user.get_text(name='trade-enter_amount_for_trade'), reply_markup=kb.cancel_trade(user))


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags.await_amount_for_trade))
def amount_for_trade(cli, m):
    user = get_user(m.from_user.id)
    trade = Trade.objects.get(id=user.cache['clipboard']['active_trade'])

    try:
        amount = to_pip(Decimal(m.text.replace(',', '.')))
        if amount == 0:
            raise InvalidOperation

        if amount > trade.order.amount:
            msg = m.reply(f'Вы не можете купить больше чем {to_bip(trade.order.amount)} {trade.trade_currency}')
            sleep(5)
            msg.delete()
            return

    except InvalidOperation:
        msg = m.reply(user.get_text(name='bot-type_error'))
        sleep(5)
        msg.delete()
        return

    price_trade = to_bip(amount) * to_bip(trade.trade_currency_rate) / to_bip(
        trade.payment_currency_rate)

    trade.price_trade = to_pip(price_trade)
    trade.amount = amount
    trade.save()

    flags = user.flags
    flags.await_amount_for_trade = False
    flags.save()

    if trade.order.type_operation == 'sale':
        type_translate = user.get_text(name='order-type_operation_translate_buy_1')
    else:
        type_translate = user.get_text(name='order-type_operation_translate_sale_1')

    txt = user.get_text(name='trade-confirm_amount_for_trade').format(
        type_operation=type_translate,
        amount=to_bip(amount),
        payment_currency=trade.trade_currency,
        price_trade=price_trade,
        trade_currency=trade.payment_currency
    )
    m.reply(txt, reply_markup=kb.confirm_amount_for_trade(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:24] == 'confirm_amount_for_trade'))
def confirm_amount_for_trade(cli, cb):
    user = get_user(cb.from_user.id)
    trade = user.trade.filter(id=user.cache['clipboard']['active_trade'])
    answer = cb.data.split('-')[1]

    if answer == 'yes':
        txt = f'\n\n{user.get_text(name="bot-you_choosed").format(foo="yes")}'
        cb.message.edit(cb.message.text+txt)
        cb.message.reply(user.get_text(name='trade-select_type_trade'), reply_markup=kb.select_type_trade(user))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:17] == 'select_type_order'))
def select_type_order(cli, cb):
    user = get_user(cb.from_user.id)
    trade = user.trade.get(id=user.cache['clipboard']['active_trade'])
    owner = trade.order.parent_order.user
    flags = user.flags

    button = cb.data.split('-')[1]

    if trade.order.type_operation == 'sale':
        type_translate_for_user = user.get_text(name='order-type_operation_translate_buy_2')
        type_translate_for_owner = owner.get_text(name='order-type_operation_translate_sale_2')
    else:
        type_translate_for_user = user.get_text(name='order-type_operation_translate_sale_2')
        type_translate_for_owner = owner.get_text(name='order-type_operation_translate_buy_2')

    if button == 'internal_wallet':
        virtual_wallet = user.virtual_wallets.get(currency=trade.payment_currency)

        if trade.price_trade > virtual_wallet.balance:
            cb.message.edit(user.get_text(name='trade-not_enough_money_to_trade'), reply_markup=kb.not_enough_money_to_trade(user))
            return

        trade.type_trade = 'auto'
        trade.save()

        # проведение автотрейда
        auto_trade(trade)

        txt_for_user = user.get_text(name='trade-success_trade').format(
            type_operation=type_translate_for_user,
            amount=round(to_bip(trade.amount), 6),
            trade_currency=trade.trade_currency,
            price_trade=to_bip(trade.price_trade),
            payment_currency=trade.payment_currency
        )

        txt_for_owner = owner.get_text(name='trade-success_trade').format(
            type_operation=type_translate_for_owner,
            amount=round(to_bip(trade.amount), 6),
            trade_currency=trade.trade_currency,
            price_trade=to_bip(trade.price_trade),
            payment_currency=trade.payment_currency
        )

        cb.message.reply(txt_for_user)
        cli.send_message(owner.telegram_id, txt_for_owner)

    if button == 'third_party_wallet':
        owner_requisite = trade.order.requisites
        trade.type_trade = 'semi-automatic'
        trade.save()

        flags.await_tx_hash = True
        flags.save()

        # TODO тут логика с депонированием
        cb.message.reply(user.get_text(name='trade-semi_automatic_start').format(
            amount=to_bip(trade.price_trade),
            currency=trade.payment_currency,
            address=owner_requisite
        ), reply_markup=kb.cancel_trade(user))

    if button == 'deposit':
        cli.answer_callback_query(cb.id, 'Пока не понятно как сделать красиво)')


@Client.on_message(Filters.create(lambda _, m: get_user(m.from_user.id).flags.await_tx_hash))
def await_tx_hash(cli, m):
    user = get_user(m.from_user.id)
    flags = user.flags
    trade = user.trade.get(id=user.cache['clipboard']['active_trade'])
    tx_hash = m.text

    if check_tx_hash(trade, tx_hash):
        flags.await_tx_hash = False
        flags.save()

        trade.tx_hash = tx_hash
        trade.save()

        m.reply(user.get_text(name='trade-await_confirm_from_owner'))

        owner = trade.order.parent_order.user
        cli.send_message(owner.telegram_id, owner.get_text(name='trade-confirm_transaction').format(
            amount=round(to_bip(trade.price_trade), 6),
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


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:15] == 'confirm_payment'))
def confirm_payment(cli, cb):
    user = get_user(cb.from_user.id)
    trade_id = int(cb.data.split('-')[2])
    trade = Trade.objects.get(id=trade_id)

    answer = cb.data.split('-')[1]
    if answer == 'yes':
        cb.message.reply(user.get_text(name='trade-second_confirm_transaction'), reply_markup=kb.second_confirm(user, trade, trade.tx_hash))

    elif answer == 'no':
        cli.answer_callback_query(cb.id, 'Пожалуйста, не торопитесь. По нашим данным транзакция успешна.', show_alert=True)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data[:22] == 'second_confirm_payment'))
def second_payment(cli, cb):
    owner = get_user(cb.from_user.id)
    trade_id = int(cb.data.split('-')[2])
    trade = Trade.objects.get(id=trade_id)

    user = trade.user

    answer = cb.data.split('-')[1]

    if trade.order.type_operation == 'sale':
        type_translate_for_user = user.get_text(name='order-type_operation_translate_buy_2')
        type_translate_for_owner = owner.get_text(name='order-type_operation_translate_sale_2')
    else:
        type_translate_for_user = user.get_text(name='order-type_operation_translate_sale_2')
        type_translate_for_owner = owner.get_text(name='order-type_operation_translate_buy_2')

    if answer == 'yes':
        semi_auto_trade(trade)

        txt_for_user = user.get_text(name='trade-success_trade').format(
            type_operation=type_translate_for_user,
            amount=round(to_bip(trade.amount), 6),
            trade_currency=trade.trade_currency,
            price_trade=round(to_bip(trade.price_trade), 6),
            payment_currency=trade.payment_currency
        )

        txt_for_owner = owner.get_text(name='trade-success_trade').format(
            type_operation=type_translate_for_owner,
            amount=round(to_bip(trade.amount), 6),
            trade_currency=trade.trade_currency,
            price_trade=round(to_bip(trade.price_trade), 6),
            payment_currency=trade.payment_currency
        )

        cb.message.reply(txt_for_owner)
        cli.send_message(user.telegram_id, txt_for_user)

    elif answer == 'no':
        cli.answer_callback_query(cb.id, 'Пожалуйста, не торопитесь. По нашим данным транзакция успешна.',
                                  show_alert=True)
