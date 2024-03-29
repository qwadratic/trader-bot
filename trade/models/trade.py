from django.db.models import Model, ForeignKey, CharField, DecimalField, DateTimeField, CASCADE


class Trade(Model):
    #  TODO временная заглушка на статус
    order = ForeignKey('order.Order', on_delete=CASCADE)
    user = ForeignKey('user.TelegramUser', related_name='trade', on_delete=CASCADE)
    trade_currency = CharField(max_length=255)
    payment_currency = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)
    price_trade = DecimalField(max_digits=40, decimal_places=0, default=0)
    trade_currency_rate = DecimalField(max_digits=40, decimal_places=0, default=0)
    payment_currency_rate = DecimalField(max_digits=40, decimal_places=0, default=0)
    type_trade = CharField(max_length=255, null=True)
    tx_hash = CharField(max_length=255, null=True)
    status = CharField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)


class HoldMoney(Model):
    trade = ForeignKey('trade.Trade', on_delete=CASCADE)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)
