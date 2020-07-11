from django.contrib import admin

from trade.models import Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'user', 'status',
        'payment_currency', 'amount', 'price_trade', 'type_trade',
        'tx_hash'
    )
