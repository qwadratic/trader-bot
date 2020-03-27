from peewee import *
from bot_tools.dbconnect import db_conn


db = PostgresqlDatabase(**db_conn)


class BaseModel(Model):
    class Meta:
        database = db
        schema = 'banker'


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    user_name = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    date_reg = DateField()


class UserSet(BaseModel):
    user_id = IntegerField(primary_key=True)
    lang = IntegerField(null=True)
    valuta = IntegerField(null=True)