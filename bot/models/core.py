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


class Settings(Model):
    update_rate_interval = PositiveIntegerField(default=20)
    #price_range_factor = DecimalField(max_digits=4, decimal_places=2, default=1)


class CurrencyList(Model):
    currency = CharField(max_length=255)
    type = CharField(max_length=25)
    accuracy = PositiveIntegerField()


class WithdrawalRequest(Model):
    objects = GetOrNoneManager()

    user = ForeignKey('user.TelegramUser', related_name='withdrawalRequests', on_delete=CASCADE)
    currency = CharField(max_length=25)
    amount = DecimalField(max_digits=40, decimal_places=0)
    address = CharField(max_length=250)
    fee = DecimalField(max_digits=40, decimal_places=0)
    network_fee = DecimalField(max_digits=40, decimal_places=0, null=True)
    tx_hash = CharField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=255, default='pending verification')
    type_withdrawal = CharField(max_length=250, null=True)

