from pyrogram import Filters
from user.models.user import Text

ref_link = Filters.create(lambda _, m: len(m.command) > 1)

filter_kb = Filters.create(lambda _, m: m.text == Text.objects.get(text_ru=m.text))  #TODO не учтена мультиязычность

filter_admin = Filters.user([69062067, 373283223, 862797627, 263425422])
