

def choice_payment_currency_text(order):
    payment_currency_list = order.payment_currency

    txt = f'{order.user.get_text(name="order-choice_payment_currency")}\n\n'
    if len(payment_currency_list) > 0:
        txt += f'{order.user.get_text(name="order-your_choice")}\n'
        for currency in payment_currency_list:
            txt += f'**{currency}**\n'

    return txt
