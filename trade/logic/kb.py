from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup


def cancel_trade(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-cancel'), callback_data='trade_cancel')]
        ]
    )
    return kb


def confirm_amount_for_trade(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user.get_text(name='kb-yes'), callback_data='confirm_amount_for_trade-yes'),
             InlineKeyboardButton(user.get_text(name='kb-no'), callback_data='confirm_amount_for_trade-no')]
        ]
    )
    return kb


def select_type_trade(user):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                user.get_text(name='trade-kb-use_internal_wallet'),
                callback_data='select_type_order-internal_wallet')],
            [InlineKeyboardButton(
                user.get_text(name='trade-kb-use_third_party_wallet'),
                callback_data='select_type_order-third_party_wallet')]
        ]
    )
    return kb


def not_enough_money_to_trade(user):

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                user.get_text(name='wallet-kb-deposite'),
                callback_data='order-deposit')]
        ]
    )
    return kb


def confirm_payment(user, trade, tx_hash):
    kb_list = [[InlineKeyboardButton(user.get_text(name='trade-kb-confirm_payment'), callback_data=f'confirm_payment-yes-{trade.id}'),
                InlineKeyboardButton(user.get_text(name='trade-kb-decline_payment'), callback_data=f'confirm_payment-no-{trade.id}')]]

    if trade.payment_currency in ['ETH', 'USDT']:
        url_link = f'https://etherscan.io/tx/{tx_hash}'
        button_name = user.get_text(name='trade-kb-view_on').format(name='etherscan.io')
        kb_list.append([InlineKeyboardButton(button_name, url=url_link)])

    elif trade.payment_currency == 'BIP':
        url_link = f'https://minterscan.net/tx/{tx_hash}'
        button_name = user.get_text(name='trade-kb-view_on').format(name='minterscan.net')

        kb_list.append([InlineKeyboardButton(button_name, url=url_link)])

    return InlineKeyboardMarkup(kb_list)


def second_confirm(user, trade, tx_hash):
    kb_list = [[InlineKeyboardButton(user.get_text(name='trade-kb-confirm_payment'), callback_data=f'second_confirm_payment-yes-{trade.id}'),
                InlineKeyboardButton(user.get_text(name='trade-kb-decline_payment'), callback_data=f'second_confirm_payment-no-{trade.id}')]]

    if trade.payment_currency in ['ETH', 'USDT']:
        url_link = f'https://etherscan.io/tx/{tx_hash}'
        button_name = user.get_text(name='trade-kb-view_on').format(name='etherscan.io')
        kb_list.append([InlineKeyboardButton(button_name, url=url_link)])

    elif trade.payment_currency == 'BIP':
        url_link = f'https://minterscan.net/tx/{tx_hash}'
        button_name = user.get_text(name='trade-kb-view_on').format(name='minterscan.net')

        kb_list.append([InlineKeyboardButton(button_name, url=url_link)])

    return InlineKeyboardMarkup(kb_list)