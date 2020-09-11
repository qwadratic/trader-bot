from pyrogram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers.shortcut import to_units
from bot.models import WithdrawalRequest

choice_language = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇬🇧 English', callback_data=f'choicelanguage-en')],
                [InlineKeyboardButton('🇷🇺 Русский', callback_data=f'choicelanguage-ru')]
            ]
        )


def select_currency(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='user-kb-usd'), callback_data=f'choicecurrency-USD')],
                [InlineKeyboardButton(user.get_text(name='user-kb-uah'), callback_data=f'choicecurrency-UAH')],
                [InlineKeyboardButton(user.get_text(name='user-kb-rub'), callback_data=f'choicecurrency-RUB')]
            ]
        )

    return kb


def start_menu(user):
    if user.telegram_id in [69062067, 373283223, 862797627]:
        kb = ReplyKeyboardMarkup(
            [
                [user.get_text(name='user-kb-wallet'), user.get_text(name='user-kb-trade')],
                [user.get_text(name='user-kb-settings')],
                [user.get_text(name='admin-kb-withdrawal_requests')]
            ],
            resize_keyboard=True,
        )
    else:
        kb = ReplyKeyboardMarkup(
            [
                [user.get_text(name='user-kb-wallet'), user.get_text(name='user-kb-trade')],
                [user.get_text(name='user-kb-settings')]
            ],
            resize_keyboard=True,
        )

    return kb


def hide(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='user-hide'), callback_data=f'hide')]
            ]
        )

    return kb


def wallet_menu(user):
    kb = list(
        [
            [InlineKeyboardButton(user.get_text(name='wallet-kb-deposit'), callback_data=f'wallet_menu-deposit'),
             InlineKeyboardButton(user.get_text(name='wallet-kb-withdrawal'), callback_data=f'wallet_menu-withdrawal')],
            [InlineKeyboardButton(user.get_text(name='wallet-kb-purse'), callback_data=f'wallet_menu-purse')],
            [InlineKeyboardButton(user.get_text(name='wallet-kb-affiliate_program'), callback_data=f'wallet_menu-afiliate_program')],
            [InlineKeyboardButton(user.get_text(name='wallet-kb-premium'), callback_data=f'wallet_menu-premium')]
        ]
    )

    withdrawal_requests = user.withdrawalRequests.filter(status__in=['pending verification', 'verifed'])

    if withdrawal_requests.count() > 0:
        kb.insert(0, [InlineKeyboardButton(user.get_text(name='wallet-kb-cancel_withdrawal'), callback_data=f'wallet_menu-cancel_withdrawal')])

    bonus_balance = to_units('BONUS', user.virtual_wallets.get(currency='BONUS').balance, round=True)

    if bonus_balance >= 0.01:
        kb.insert(0, [InlineKeyboardButton(user.get_text(name='wallet-kb-convert_bonus'),
                                           callback_data=f'wallet_menu-convert_bonus')])
    return InlineKeyboardMarkup(kb)


def purse_menu(user):
    requisites = user.requisites.all()

    kb = [[InlineKeyboardButton('🔙 Назад', callback_data='purse-back')],
          [InlineKeyboardButton('Добавить реквизиты', callback_data='purse-add')]]

    for r in requisites:
        name = f'[{r.name}]' if r.name else ''
        kb.append([InlineKeyboardButton(f'{name}[{r.currency}] {r.address}', callback_data=f'purse-req-{r.id}')])

    return InlineKeyboardMarkup(kb)


choice_currency_for_wallet = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('BIP', callback_data='chcurr-BIP'),
         InlineKeyboardButton('BTC', callback_data='chcurr-BTC'),
         InlineKeyboardButton('USDT', callback_data='chcurr-USDT'),
         InlineKeyboardButton('ETH', callback_data='chcurr-ETH')],
        [InlineKeyboardButton('USD', callback_data='chcurr-USD'),
         InlineKeyboardButton('RUB', callback_data='chcurr-RUB'),
         InlineKeyboardButton('UAH', callback_data='chcurr-UAH')],
        [InlineKeyboardButton('🔙', callback_data='chcurr-back')]

    ])


select_currency_for_withdrawal = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('BIP', callback_data='withdrawal-currency-BIP'),
         InlineKeyboardButton('BTC', callback_data='withdrawal-currency-BTC'),
         InlineKeyboardButton('USDT', callback_data='withdrawal-currency-USDT'),
         InlineKeyboardButton('ETH', callback_data='withdrawal-currency-ETH')],
        [InlineKeyboardButton('USD', callback_data='withdrawal-currency-USD'),
         InlineKeyboardButton('RUB', callback_data='withdrawal-currency-RUB'),
         InlineKeyboardButton('UAH', callback_data='withdrawal-currency-UAH')],
        [InlineKeyboardButton('🔙', callback_data='withdrawal-back')]

    ])


def select_currency_for_convert_bonus(user, amount):
    kb = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('BIP', callback_data=f'convert_bonus-BIP-{amount}'),
         InlineKeyboardButton('BTC', callback_data=f'convert_bonus-BTC-{amount}')],

        [InlineKeyboardButton('USDT', callback_data=f'convert_bonus-USDT-{amount}'),
         InlineKeyboardButton('ETH', callback_data=f'convert_bonus-ETH-{amount}')],

        [InlineKeyboardButton(user.get_text('wallet-kb-cancel_convert_bonus'), callback_data='cancel_convert_bonus')]

    ])
    return kb


def confirm_convert_bonus(user, amount, currency_rate, currency):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-yes'), callback_data=f'confirm_convert_bonus-{amount}-{currency}-{currency_rate}')],
            [InlineKeyboardButton(user.get_text(name='kb-no'), callback_data='cancel_convert_bonus')]
        ]
    )
    return kb


def cancel_convert_bonus(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='wallet-kb-cancel_convert_bonus'), callback_data=f'cancel_convert_bonus')]
        ]
    )
    return kb


def cancel_withdrawal(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'cancel_withdrawal')]
        ]
    )
    return kb


def select_requisite_for_withdrawal(user, currency):

    requisites = user.requisites.filter(currency=currency)

    kb_list = [[InlineKeyboardButton(user.get_text(name='order-kb-add_new_requisite'), callback_data='selectreqwithdrawal-new')]]

    for i in requisites:
        r_name = f'{i.name} {i.currency} {i.address}'
        kb_list.append([InlineKeyboardButton(r_name, callback_data=f'selectreqwithdrawal-use-{i.id}')])

    kb_list.append([InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'cancel_withdrawal')])

    return InlineKeyboardMarkup(kb_list)


def confirm_withdrawal(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-yes'), callback_data=f'confirm_withdrawal-yes')],
            [InlineKeyboardButton(user.get_text(name='kb-no'), callback_data=f'confirm_withdrawal-no')]
        ]
    )
    return kb


def requisite(user, requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🔙 Назад', callback_data=f'wallet_menu-purse')],

                [InlineKeyboardButton(
                    user.get_text(name='purse-kb-edit_address'),
                    callback_data=f'requisite-address-{requisite_id}')],

                [InlineKeyboardButton(
                    user.get_text(name='purse-kb-edit_add_name'),
                    callback_data=f'requisite-name-{requisite_id}')],

                [InlineKeyboardButton(
                    user.get_text(name='purse-kb-delete'),
                    callback_data=f'requisite-delete-{requisite_id}')]
            ]
        )

    return kb


def skip_add_requisites_name(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-skip'), callback_data=f'addreq-skip')],
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'addreq-cancel')]
            ]
        )

    return kb


def cancel_add_requisites(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'addreq-cancel')]
            ]
        )

    return kb


def cancel_edit_requisite(user, requisite_id):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'requisite-cancel-{requisite_id}')]
            ]
        )

    return kb


def edit_requisite_name(user, requisite_id):
    requisite = user.requisites.get(id=requisite_id)

    if requisite.name:
        kb = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(user.get_text(name='purse-kb-delete'), callback_data=f'requisite-delname-{requisite_id}')],
                    [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'requisite-cancel-{requisite_id}')]
                ]
            )

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'requisite-cancel-{requisite_id}')]
            ]
        )

    return kb


def hide_notification(user):
    return InlineKeyboardMarkup([[InlineKeyboardButton(user.get_text(name='kb-hide'), callback_data='hide')]])


def settings_menu(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='user-kb-language'), callback_data=f'setuser-language'),
                 InlineKeyboardButton(user.get_text(name='user-kb-currency'), callback_data=f'setuser-currency')],
                [InlineKeyboardButton(user.get_text(name='user-kb-service_info'), callback_data=f'setuser-about')],
                [InlineKeyboardButton(user.get_text(name='kb-close'), callback_data=f'hide')]
            ]
        )
    return kb


def set_language(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🇬🇧 English', callback_data=f'userset-language-en')],
                [InlineKeyboardButton('🇷🇺 Русский', callback_data=f'userset-language-ru')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'userset-back-1')]
            ]
        )

    return kb


def set_currency(user):
    kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(user.get_text(name='user-kb-usd'), callback_data=f'userset-currency-USD')],
                [InlineKeyboardButton(user.get_text(name='user-kb-uah'), callback_data=f'userset-currency-UAH')],
                [InlineKeyboardButton(user.get_text(name='user-kb-rub'), callback_data=f'userset-currency-RUB')],
                [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'userset-back-1')]
            ]
        )

    return kb


def show_tx(user, currency, tx_hash):
    info_dict = dict(
        ETH=dict(
            url=f'https://etherscan.io/tx/{tx_hash}',
            url_name='etherscan.io'),

        USDT=dict(
            url=f'https://etherscan.io/tx/{tx_hash}',
            url_name='etherscan.io'),

        BIP=dict(
            url=f'https://minterscan.net/tx/{tx_hash}',
            url_name='minterscan.net'),

        BTC=dict(
            url=f'https://www.blockchain.com/ru/btc/tx/{tx_hash}',
            url_name='blockchain.com'
        )
    )

    button_name = user.get_text(name='trade-kb-view_on').format(name=info_dict[currency]['url_name'])

    return InlineKeyboardMarkup([[InlineKeyboardButton(button_name, url=info_dict[currency]['url'])]])



def withdrawal_requests(user):
    requests = WithdrawalRequest.objects.filter(status='verifed', type_withdrawal='manual')

    kb_list = [[InlineKeyboardButton(user.get_text(name='kb-close'), callback_data='close')]]

    for r in requests:
        amount = to_units(r.currency, r.amount, round=True)
        currency = r.currency
        bt_name = f'{amount} {currency}'
        kb_list.append([InlineKeyboardButton(bt_name, callback_data=f'withdrawal_request_list-open-{r.id}')])

    return InlineKeyboardMarkup(kb_list)


def confirm_cancel_withdrawal(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-yes'), callback_data=f'confirm_cancel_withdrawal')],
            [InlineKeyboardButton(user.get_text(name='kb-no'), callback_data=f'close')],
        ]
    )

    return kb


def manual_withdrawal(user, req_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='admin-kb-withdrawal_send_tx'), callback_data=f'withdrawal_request_list-send_tx-{req_id}')],
            [InlineKeyboardButton(user.get_text(name='admin-kb-withdrawal_cancel'), callback_data=f'withdrawal_request_list-refuse-{req_id}')],
            [InlineKeyboardButton(user.get_text(name='kb-close'), callback_data=f'close')]
        ]
    )

    return kb


def cancel_withdrawal_tx_hash(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'cancel_withdrawal_tx')]
        ]
    )
    return kb


def confirm_tx_hash_withdrawal(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='admin-kb-send_tx-hash'), callback_data=f'confirm_tx_hash_withdrawal-yes')],
            [InlineKeyboardButton(user.get_text(name='admin-kb-edit_tx_hash'), callback_data=f'confirm_tx_hash_withdrawal-edit')],
            [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data=f'confirm_tx_hash_withdrawal-cancel')]

        ]
    )
    return kb


def select_currency_for_deposit(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('ETH', callback_data=f'currency_for_deposit-ETH'),
             InlineKeyboardButton('USDT', callback_data=f'currency_for_deposit-USDT'),
             InlineKeyboardButton('BTC', callback_data=f'currency_for_deposit-BTC'),
             InlineKeyboardButton('BIP', callback_data=f'currency_for_deposit-BIP')],
            [InlineKeyboardButton(user.get_text(name='kb-back'), callback_data=f'currency_for_deposit-back')]
        ]
    )
    return kb
