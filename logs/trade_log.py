from mintersdk.shortcuts import to_bip
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup

from bot_tools.help import get_balance_from_currency
from datetime import datetime as dt


def trade_start(cli, trade, owner_name, user_name, type_operation, trade_currency_price, trade_currency, price_deal_in_usd, price_deal_in_payment_currency):
    log = f'Начало торговой сделки №{trade.id}\n\n' \
        f'Объвление №{trade.announcement.id}\n' \
        f'Автор объявления: {owner_name}\n' \
        f'Сумма объявления: {to_bip(trade.announcement.amount)} {trade.announcement.trade_currency}\n' \
        f'Цена лота: {to_bip(trade_currency_price)} USD за 1 {trade_currency}\n\n' \
        f'Пользователь сделки: {user_name}\n' \
        f'Тип операции: {type_operation}\n' \
        f'Валюта операции: {trade.announcement.trade_currency}\n' \
        f'Платежный инструмент: {trade.user_currency}\n' \
        f'Сумма сделки: {to_bip(trade.amount)}\n' \
        f'Цена сделки в USD: {price_deal_in_usd}\n' \
        f'Цена сделки в платежном инструменте: {price_deal_in_payment_currency}\n\n' \
        f'Время создания сделки:  ```{dt.utcnow()} UTC-0```'

    broadcast_log(cli, log)


def tx_error(cli, tx_query, trade, balance, from_address, recipient_address, trade_currency, amount, error=None, tx_hash=None):
    txt = 'в первой' if tx_query == 'first' else 'во второй'
    error_log = f'❌ **Ошибка {txt} транзакции**\n\n' \
        f'Сделка №{trade.id}\n' \
        f'Адрес отправителя: ```{from_address}```\n' \
        f'Адрес получателя: ```{recipient_address}```\n\n' \
        f'Сумма транзакции: {amount} {trade_currency}\n' \
        f'Реальный баланс пользователя:  {to_bip(get_balance_from_currency(from_address, trade_currency))} {trade_currency}\n\n' \
        f'Виртуальный баланс пользователя: {to_bip(balance)} {trade.user_currency}' \
        f'Время события:  ```{dt.utcnow()} UTC-0```\n\n' \
        f'{error}'

    url = {'BIP': 'https://minterscan.net/tx/',
           'ETH' or 'USDT': 'https://etherscan.io/tx/'}

    if tx_hash:
        kb = InlineKeyboardButton(f'Транзакция', url=f'{url[trade_currency]}{tx_hash}')
        broadcast_log(cli, error_log, kb)
        return

    broadcast_log(cli, error_log)


def successful_tx(cli, tx_query, trade, from_address, recipient_address, trade_currency, amount, fee, tx_hash):
    txt = 'первая' if tx_query == 'first' else 'вторая'
    fee_currency = 'ETH' if trade_currency == 'USDT' else trade_currency

    log = f'✅ Удачная {txt} транзакция!\n\n' \
        f'Сделка №{trade.id}\n' \
        f'Адрес отправителя: ```{from_address}```\n' \
        f'Адрес получателя: ```{recipient_address}```\n' \
        f'Сумма транзакции: {amount} {trade_currency}\n' \
        f'Комиссия: {fee} {fee_currency}\n\n' \
        f'Время события:  ```{dt.utcnow()} UTC-0```'

    url = {'BIP': 'https://minterscan.net/tx/',
           'ETH' or 'USDT': 'https://etherscan.io/tx/'}

    kb = InlineKeyboardButton(f'Транзакция', url=f'{url[trade_currency]}{tx_hash}')

    broadcast_log(cli, log, kb)


def successful_hold(cli, trade, owner_wallet, trade_currency):
    log = f'Сделка №{trade.id}\n\n' \
        f'Депонирование средств владельца объявления №{trade.announcement.id}\n' \
        f'Виртуальный баланс владельца:\n{to_bip(owner_wallet.balance)} {trade_currency}\n' \
        f'Сумма депонирования: {to_bip(trade.amount)} {trade_currency}\n\n' \
        f'Новый виртуальный баланс: {to_bip(owner_wallet.balance)} {trade_currency}\n\n' \
        f'Время события:  ```{dt.utcnow()} UTC-0```'

    broadcast_log(cli, log)


def successful_trade(cli, trade, amount):
    log = f'✅ Успех! Сделка №{trade.id}\n\n' \
        f'Сумма лота объявления после сделки: {to_bip(trade.announcement.amount)} {trade.announcement.trade_currency}\n' \
        f'Сумма обмена: {to_bip(trade.amount)} {trade.announcement.trade_currency}\n' \
        f'Цена обмена: {amount} {trade.user_currency}\n\n' \
        f'Время заверешния сделки: ```{dt.utcnow()} UTC-0```'

    broadcast_log(cli, log)


def broadcast_log(cli, log, kb=None):
    channel_id = '-1001376981650' #-1001276839371

    if kb:
        try:
            cli.send_message(channel_id, log, reply_markup=InlineKeyboardMarkup([[kb]]))
        except Exception as e:
            print(e)
        return
    try:
        cli.send_message(channel_id, log)
    except Exception as e:
        print(e)
