from peewee import *
from bot_tools.dbconnect import db_conn


db = PostgresqlDatabase(**db_conn)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    tg_id = IntegerField()
    user_name = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    last_activity = DateTimeField(null=True)
    date_reg = DateTimeField()

    @property
    def wallets(self):
        return self.wallets_.select()

    @property
    def virt_wallets(self):
        return self.virt_wallets_.select()

    @property
    def settings(self):
        return self.settings_.get()

    @property
    def ref(self):
        return self.ref_.get()

    @property
    def msg(self):
        return self.msgid_.get()

    @property
    def temp_announcement(self):
        return self.tempannounc_.get()

    @property
    def flags(self):
        return self.flags_.get()

    @property
    def purse(self):
        return self.purse_.get()


class UserFlag(BaseModel):
    user = ForeignKeyField(User, unique=True, backref='flags_', on_delete='CASCADE')
    temp_currency = CharField(null=True)
    requisites_for_trade = BooleanField(default=False)
    requisites_for_start_deal = BooleanField(default=False)
    await_amount_for_trade = BooleanField(default=False)


class UserSettings(BaseModel):
    user_id = ForeignKeyField(User, backref='settings_', on_delete='CASCADE')
    language = CharField(default='ru')
    currency = CharField(default='USD')


class UserRef(BaseModel):
    user_id = ForeignKeyField(User, unique=True, backref='ref_', on_delete='CASCADE')
    ref_user_id = IntegerField()
    ref_created_at = DateTimeField(null=True)


class Wallet(BaseModel):
    user = ForeignKeyField(User, backref='wallets_', on_delete='CASCADE')
    name = CharField()
    address = CharField()
    mnemonic = CharField(null=True)
    private_key = CharField()


class VirtualWallet(BaseModel):
    user = ForeignKeyField(User, backref='virt_wallets_', on_delete='CASCADE')
    currency = CharField()
    balance = DecimalField(40, 0, default=0)


class UserPurse(BaseModel):
    user_id = IntegerField()
    currency = CharField()
    address = CharField()


class MsgId(BaseModel):
    user_id = ForeignKeyField(User, unique=True, backref='msgid_', on_delete='CASCADE')
    trade_menu = IntegerField(null=True)
    await_exchange_rate = IntegerField(null=True)
    await_count = IntegerField(null=True)
    await_requisites = IntegerField(null=True)
    await_payment_pending = IntegerField(null=True)
    await_limit = IntegerField(null=True)
    await_requisites_from_seller = IntegerField(null=True)
    await_requisites_from_buyer = IntegerField(null=True)
    await_respond_from_seller = IntegerField(null=True)
    await_respond_from_buyer = IntegerField(null=True)
    await_payment_details = IntegerField(null=True)


class TempAnnouncement(BaseModel):
    user_id = ForeignKeyField(User, unique=True, backref='tempannounc_', on_delete='CASCADE')
    type_operation = CharField(null=True)
    trade_currency = CharField(null=True)
    amount = FloatField(null=True)
    max_limit = IntegerField(null=True)
    exchange_rate = FloatField(null=True)


class TempPaymentCurrency(BaseModel):
    user_id = IntegerField()
    payment_currency = CharField(unique=True, null=True)


class Announcement(BaseModel):
    user = ForeignKeyField(User, backref='announc_', on_delete='CASCADE')
    type_operation = CharField()
    trade_currency = CharField()
    amount = IntegerField()
    max_limit = IntegerField()
    exchange_rate = FloatField(null=True)
    status = CharField()

    @property
    def payment_currency(self):
        return self.paycurr_.get()

    @property
    def trade(self):
        return self.trade_.get()


class PaymentCurrency(BaseModel):
    announcement = ForeignKeyField(Announcement, backref='paycurr_', on_delete='CASCADE')
    payment_currency = CharField()


class Trade(BaseModel):
    announcement = ForeignKeyField(Announcement, backref='trade_', on_delete='CASCADE')
    user = ForeignKeyField(User, backref='trade_', on_delete='CASCADE')
    status = CharField()
    user_currency = IntegerField(null=True)
    created_at = DateTimeField(null=True)

