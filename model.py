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
    last_active = DateTimeField(null=True)
    date_reg = DateTimeField()

    @property
    def settings(self):
        return self.settings_.get()

    @property
    def ref(self):
        return self.ref_.get()


class UserSettings(BaseModel):
    user_id = ForeignKeyField(User, backref='settings_', on_delete='CASCADE')
    lang = IntegerField(null=True)
    currency = IntegerField(null=True)


class UserRef(BaseModel):
    user_id = ForeignKeyField(User, unique=True, backref='ref_', on_delete='CASCADE')
    ref_user_id = IntegerField()
    ref_created_at = DateTimeField(null=True)