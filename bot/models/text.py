from django.db.models import Model, CharField, TextField


class Text(Model):
    name = CharField(max_length=255)
    text = TextField()
