from django.contrib import admin

from trader_bot.apps.order.models import ParentOrder, Order


@admin.register(ParentOrder)
class ParentOrderAdmin(admin.ModelAdmin):
    last_display = ('order_id', 'user', 'type_operation', 'trade_currency', 'amount', 'currency_rate', 'payment_currency',
                    'requisites', 'status', 'created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    last_display = ('parent_order', 'type_operation', 'trade_currency', 'amount', 'currency_rate', 'payment_currency',
                    'requisites', 'status', 'mirror',)
