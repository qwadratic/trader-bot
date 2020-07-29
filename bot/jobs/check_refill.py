from requests import ReadTimeout

from bot.blockchain.core import get_eth_refill_txs, get_bip_refill_txs, order_deposit
from bot.blockchain.ethAPI import w3
from bot.blockchain.minterAPI import Minter, get_wallet_balance
from bot.helpers.misc import retry
from bot.helpers.shortcut import to_units, round_currency

from bot.models import CashFlow, Service
from user.models import Wallet

from user.logic import kb


@retry(Exception)
def check_refill_eth(cli):
    current_block = w3.eth.blockNumber
    service = Service.objects.get_or_none(currency='ETH')
    if not service:
        Service.objects.create(currency='ETH', last_block=current_block)
        return

    last_block = service.last_block
    if current_block == service.last_block:
        return

    block_diff = current_block - last_block

    addresses = [w.address.lower() for w in Wallet.objects.filter(currency='ETH')]
    for block in range(last_block + 1, last_block + block_diff + 1):
        refill_txs = get_eth_refill_txs(addresses, block)
        update_eth_balance(cli, refill_txs)
        service.last_block = block
        service.save()


@retry(ReadTimeout)
def check_refill_bip(cli):
    current_block = Minter.get_latest_block_height()
    service = Service.objects.get_or_none(currency='BIP')
    if not service:
        Service.objects.create(last_block=current_block, currency='BIP')
        return

    last_block = service.last_block
    if current_block == service.last_block:
        return

    block_diff = current_block - last_block

    addresses = [w.address for w in Wallet.objects.filter(currency='BIP')]
    for block in range(last_block + 1, last_block + block_diff + 1):
        refill_txs = get_bip_refill_txs(addresses, block)
        update_bip_balance(cli, refill_txs)
        service.last_block = block
        service.save()


def update_eth_balance(cli, refill_txs):
    address_refills = {}
    for (address, coin), refill_pip in refill_txs.items():
        address_refills.setdefault(address, {})
        address_refills[address][coin] = refill_pip

    refills_list = []

    for address in address_refills:
        user = Wallet.objects.get(address=address).user

        txt_refills = f''

        for currency in address_refills[address]:
            virt_wallet = user.virtual_wallets.get(currency=currency)
            refill = address_refills[address][currency]
            virt_wallet.balance += refill
            virt_wallet.save()

            refills_list.append(dict(user=user,
                                     type_operation='deposit',
                                     amount=refill,
                                     currency=currency))

            txt_refills += f'\n**{to_units(currency, refill)} {currency}**'
        try:

            cli.send_message(user.telegram_id, user.get_text(name='bot-balance_replinished') + txt_refills)
        except Exception as e:
            print('check_refill, line 65\n', e)

    CashFlow.objects.bulk_create([CashFlow(**q) for q in refills_list])


def update_bip_balance(cli, refills):
    # address_refills = {}
    # for (address, coin), refill_pip in refills.items():
    #     address_refills.setdefault(address, {})
    #     address_refills[address][coin] = refill_pip

    refills_list = []

    for address in refills:

        user = Wallet.objects.get(address=address).user
        user_balance = get_wallet_balance(address)

        for refill in refills[address]:
            txt_refills = ''
            refill_in_pip = refill['amount']

            virt_wallet = user.virtual_wallets.get(currency='BIP')

            virt_wallet.balance += refill_in_pip
            virt_wallet.save()

            refills_list.append(dict(user=user,
                                     type_operation='deposit',
                                     amount=refill_in_pip,
                                     currency='BIP',
                                     tx_hash=refill['tx_hash']))

            await_deposite_currency = user.cache['clipboard']['deposit_currency']

            if user.flags.await_replenishment_for_order and 'BIP' in await_deposite_currency:
                order_deposit(cli, user, refills[address])
            else:
                txt_refills += f'\n**{round_currency("BIP", to_units("BIP", refill_in_pip))} BIP**'

                try:
                    cli.send_message(user.telegram_id, user.get_text(name='bot-balance_replinished') + txt_refills,
                                     reply_markup=kb.show_tx(user, 'BIP', refill['tx_hash']))
                except Exception as e:
                    print('check_refill, line 155\n', e)

    CashFlow.objects.bulk_create([CashFlow(**q) for q in refills_list])


