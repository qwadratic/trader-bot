from peewee import *
from bot_tools.dbconnect import db_conn


db = PostgresqlDatabase(**db_conn)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = AutoField()
    tg_id = IntegerField()
    user_name = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    last_active = DateField(null=True)
    date_reg = DateField()


class UserSet(BaseModel):
    user_id = IntegerField(primary_key=True)
    lang = IntegerField(null=True)
    valuta = IntegerField(null=True)

