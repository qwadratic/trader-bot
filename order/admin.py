from django.contrib import admin

from order.models import ParentOrder, Order


@admin.register(ParentOrder)
class ParentOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'user', 'type_operation',
        'trade_currency', 'amount', 'currency_rate', 'payment_currency',
        'requisites', 'status', 'created_at'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'parent_order', 'type_operation',
        'trade_currency', 'amount', 'currency_rate', 'payment_currency',
        'requisites', 'status', 'mirror'
    )
