from decimal import Decimal, ROUND_DOWN, ROUND_UP

from pyrogram import Client

from bot.blockchain import minterAPI, ethAPI, rpc_btc
from bot.models import ExchangeRate, CashFlow, CurrencyList
from config.settings import TG_API_ID, TG_API_HASH, TG_API_TOKEN
from user.models import TelegramUser
from mintersdk.shortcuts import to_pip, to_bip

from constance import config


def get_user(tg_id):
    return TelegramUser.objects.get_or_none(telegram_id=tg_id)


def delete_msg(cli, user_id, msg):
    try:
        cli.delete_messages(user_id, msg)
    except Exception as e:
        print(e, '\ndelete_msg')


def delete_inline_kb(cli, telegram_id, msg_id):
    try:
        msg = cli.get_messages(telegram_id, msg_id)
        msg.edit(msg.text)
    except:
        pass


def check_address(address, currency):

    valid = False

    if currency == 'BIP':
        re = minterAPI.Minter.get_balance(address)
        if 'result' in re:
            valid = True

    if currency in ['ETH', 'USDT']:
        try:
            re = ethAPI.get_balance(address, currency)
            valid = True
        except ValueError:
            pass

    if currency in ['BTC']:
        from bot.blockchain.rpc_btc import check_address_btc
        re = check_address_btc(address)
        if 'Invalid address' not in re:
            valid = True

    # TODO костыль
    if currency not in ['ETH', 'USDT', 'BIP', 'BTC']:
        valid = True

    return valid


def to_cents(currency, amount):
    amount = Decimal(amount)
    if currency in ['USDT', 'ETH']:
        amount = ethAPI.Web3.toWei(amount, 'ether')

    elif currency == 'BIP':
        amount = to_pip(amount)

    elif currency == 'BTC':
        sat = Decimal(100000000)
        amount = int(amount * sat)
    else:
        amount = to_pip(amount)

    return amount


def to_units(currency, amount, round=False):
    if currency in ['USDT', 'ETH']:
        amount = ethAPI.Web3.fromWei(amount, 'ether')

    elif currency == 'BIP':
        amount = to_bip(amount)

    elif currency == 'BTC':
        sat = Decimal(100000000)
        amount = amount / sat
    else:
        amount = to_bip(amount)

    if round:
        return round_currency(currency, amount)
    
    return amount


def get_currency_rate(currency):
    if currency == 'USD':
        return to_cents('USD', 1)

    return ExchangeRate.objects.filter(currency=currency, source='coinmarketcup').latest('time').value  # TODO: Пофиксить на разные источники


def create_record_cashflow(user, to, type_operation, amount, currency, trade=None, tx_hash=None):
    CashFlow.objects.create(
        user=user,
        to=to,
        trade=trade,
        type_operation=type_operation,
        amount=amount,
        currency=currency,
        tx_hash=tx_hash
    )


def round_currency(currency_id, number, to_str=False, round_up=False):
    #TODO пересмотреть эту функцию
    currency = CurrencyList.objects.get(currency=currency_id)
    accuracy = currency.accuracy
    if number % 1 == 0:
        return int(number)
    if isinstance(number, Decimal):
        if '0.00' in str(number) and currency_id in ['USD', 'BIP', 'USDT', 'UAH', 'RUB']:
            accuracy = 4

        if to_str:
            return '%.*f' % (accuracy, number)

        rounding = ROUND_DOWN
        if round_up:
            rounding = ROUND_UP
        return number.quantize(Decimal(f'0.{"1" * accuracy}'), rounding=rounding)
    return number

                                       
def get_max_amount_withdrawal(user, currency):
    from bot.helpers.converter import currency_in_usd
    withdrawal_factor = config.WITHDRAWAL_FACTOR
    deposit_sum = Decimal(0)
    withdrawal_sum = Decimal(0)

    for d in user.cashflow.filter(type_operation='deposit', currency=currency):
        amount = to_units(currency, d.amount)
        deposit_sum += currency_in_usd(d.currency, amount)

    for w in user.cashflow.filter(type_operation='withdrawal', currency=currency):
        amount = to_units(currency, w.amount)
        withdrawal_sum += currency_in_usd(w.currency, amount)

    max_amount = deposit_sum * withdrawal_factor - withdrawal_sum

    return max_amount


def update_cache_msg(user, msg_name, msg_id):
    user.cache['msg'][msg_name] = msg_id
    user.save()


def send_message(cli, telegram_id, msg, kb):
    try:
        if kb:
            return cli.send_message(telegram_id, msg, reply_markup=kb)
        else:
            return cli.send_message(telegram_id, msg)
    except:
        return False


def get_fee_amount(factor_fee, amount):

    return amount * Decimal(factor_fee) / Decimal(100)
