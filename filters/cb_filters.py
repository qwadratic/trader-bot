from pyrogram import Filters


class UserCallbackFilter:

    create = Filters.create

    choice_language = create(lambda _, cb: cb.data[:4] == 'lang')

    choice_currency = create(lambda _, cb: cb.data[:8] == 'currency')


class TradeFilter:

    create = Filters.create

    trade_menu = create(lambda _, cb: cb.data[:5] == 'tmenu')

    buy_menu = create(lambda _, cb: cb.data[:3] == 'buy')

    choice_trade_currency = create(lambda _, cb: cb.data[:5] == 'tcurr')

    choice_payment_instrument = create(lambda _, cb: cb.data[:7] == 'paycurr')

    sale_menu = create(lambda _, cb: cb.data[:4] == 'sale')

    deal_start = create(lambda _, cb: cb.data[:10] == 'deal start')

    announcement_menu = create(lambda _, cb: cb.data[:7] == 'annlist')

    open_announcement = create(lambda _, cb: cb.data[:12] == 'open announc')

    start_deal = create(lambda _, cb: cb.data[:10] == 'start deal')

    confirm_trade = create(lambda _, cb: cb.data[:9] == 'conftrade')

