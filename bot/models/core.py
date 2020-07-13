from django.db.models import Manager, Model, CharField, PositiveIntegerField, DecimalField, ForeignKey, DateTimeField, CASCADE, SET_NULL


class GetOrNoneManager(Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class Service(Model):
    objects = GetOrNoneManager()

    currency = CharField(max_length=255, unique=True)
    last_block = PositiveIntegerField()


class CashFlow(Model):
    user = ForeignKey('user.TelegramUser', related_name='cashflow', on_delete=CASCADE)
    to = ForeignKey('user.TelegramUser', related_name='_cashflow', null=True, on_delete=CASCADE)
    trade = ForeignKey('trade.Trade', null=True, on_delete=SET_NULL)
    type_operation = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)
    currency = CharField(max_length=255)
    tx_hash = CharField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)


class ExchangeRate(Model):
    currency = CharField(max_length=255)
    value = DecimalField(max_digits=40, decimal_places=0, default=0)
    source = CharField(max_length=255)
    time = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = 'time',