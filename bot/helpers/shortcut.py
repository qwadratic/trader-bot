from decimal import Decimal, ROUND_DOWN

from bot.blockchain import minterAPI, ethAPI
from bot.models import ExchangeRate, CashFlow, CurrencyList
from user.models import TelegramUser
from mintersdk.shortcuts import to_pip, to_bip


def get_user(tg_id):
    return TelegramUser.objects.get_or_none(telegram_id=tg_id)


def delete_msg(cli, user_id, msg):
    try:
        cli.delete_messages(user_id, msg)
    except Exception:
        pass


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

    # TODO костыль
    if currency not in ['ETH', 'USDT', 'BIP']:
        valid = True

    return valid


def to_cents(currency, amount):
    if currency in ['USDT', 'ETH']:
        return ethAPI.Web3.toWei(amount, 'ether')

    if currency == 'BIP':
        return to_pip(amount)

    # TODO  допилить логику других валют
    return to_pip(amount)


def to_units(currency, amount, round=False):
    if currency in ['USDT', 'ETH']:
        amount = ethAPI.Web3.fromWei(amount, 'ether')

    elif currency == 'BIP':
        amount = to_bip(amount)
    else:
        amount = to_bip(amount)

    if round:
        return round_currency(currency, amount)

    # TODO  допилить логику других валют
    return amount


def get_currency_rate(currency):
    if currency == 'USD':
        return to_cents('USD', 1)
    return ExchangeRate.objects.filter(currency=currency).latest('time').value


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


def round_currency(currency_id, number):

    currency = CurrencyList.objects.get(currency=currency_id)
    #result = round(Decimal(number), currency.accuracy)
    #
    # if isinstance(number, float):
    #     number = Decimal(number)
    #
    if number % 1 == 0:
        return int(number)
    if isinstance(number, Decimal):
        return number.quantize(Decimal(f'0.{"1" * currency.accuracy}'), rounding=ROUND_DOWN)
    return number

    # if result % 1 == 0:
    #     return int(result)
    # else:
    #     return result


def get_max_amount_withdrawal(user, currency):
    from bot.helpers.converter import currency_in_usd
    withdrawal_factor = 1  # TODO перенести в настройки
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
