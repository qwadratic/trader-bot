

def create_reflink(user_id, trade_id=None):
    bot_link = f'https://t.me/bankertest_bot?start=u{user_id}'

    if trade_id:
        bot_link = f'https://t.me/bankertest_bot?start=t{trade_id}'

    return bot_link
