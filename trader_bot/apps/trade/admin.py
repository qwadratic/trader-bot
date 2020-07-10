from django.contrib import admin

from trader_bot.apps.trade.models import Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    last_display = ('order', 'user', 'status', 'payment_currency', 'amount', 'price_trade', 'type_trade', 'tx_hash',)

