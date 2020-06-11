from django.db.models import Model, IntegerField, CharField, DateTimeField, PositiveIntegerField, ForeignKey, CASCADE, \
    BooleanField, DecimalField, OneToOneField


from django.utils import timezone
from django.utils.translation import gettext as _


class User(Model):
    telegram_id = PositiveIntegerField(_('Telegram user ID'), unique=True)
    username = CharField(_('User name'), max_length=255, null=True)
    first_name = CharField(_('First name'), max_length=255,null=True)
    last_name = CharField(_('Last name'), max_length=255, null=True)
    last_activity = DateTimeField(_('Last activity'), null=True)
    created_at = DateTimeField(_('Registration date'), auto_now_add=True)

    class Meta:
        verbose_name = 'Telegram User'


class UserFlag(Model):
    user = ForeignKey(User, related_name='flags', on_delete=CASCADE)
    temp_currency = CharField(null=True, max_length=255)
    requisites_for_trade = BooleanField(default=False)
    requisites_for_start_deal = BooleanField(default=False)
    await_amount_for_trade = BooleanField(default=False)
    await_currency_value = BooleanField(default=False)
    await_amount_for_deal = BooleanField(default=False)
    await_requisites_address = BooleanField(default=False)
    await_requisites_name = BooleanField(default=False)
    edit_requisite = BooleanField(default=False)


class UserSettings(Model):
    user = OneToOneField(User, related_name='settings', on_delete=CASCADE)
    language = CharField(default='ru', max_length=255)
    currency = CharField(default='USD', max_length=255)
    announcement_id = PositiveIntegerField(null=True)
    active_deal = IntegerField(null=True)


class UserRef(Model):
    user = OneToOneField(User, related_name='ref', on_delete=CASCADE)
    ref_user = ForeignKey(User, on_delete=CASCADE)
    ref_created_at = DateTimeField(auto_now_add=True)


class MsgId(Model):
    user_id = OneToOneField(User, related_name='msg', on_delete=CASCADE)
    trade_menu = PositiveIntegerField(null=True)
    wallet_menu = PositiveIntegerField(null=True)


class Wallet(Model):
    user = ForeignKey(User, related_name='wallets', on_delete=CASCADE)
    currency = CharField(max_length=255)
    address = CharField(max_length=255)
    mnemonic = CharField(max_length=255, null=True)
    private_key = CharField(max_length=255)


class VirtualWallet(Model):
    user = ForeignKey(User, related_name='virt_wallets', on_delete=CASCADE)
    currency = CharField(max_length=255)
    balance = DecimalField(max_digits=40, decimal_places=0, default=0)


class UserPurse(Model):
    user = ForeignKey(User, related_name='purse', on_delete=CASCADE)
    name = CharField(max_length=255, null=True)
    currency = CharField(max_length=255)
    address = CharField(max_length=255, null=True)
    status = CharField(max_length=255, default='invalid')



