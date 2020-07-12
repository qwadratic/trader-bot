import django.db.models
from bot.models.text import Text
from bot.jobs.spreadsheet_google import get_data_db, json_get, write_data
from django.db.models import Q

def check_name():
    old_data = get_data_db()
    request_data = json_get()
    data_name_list = []
    request_name_list = []
    changed_name = []
    for i in old_data:
        data_name_list.append(i['name'])
    if len(data_name_list) == 0:
        query = write_data()
        query.save()
    else:
        for i in request_data:
            request_name_list.append(i['name'])
        for n in data_name_list:
            if n not in request_name_list:
                changed_name.append(n)
                print("Name was changed", changed_name)
                break
            else:
                for row in request_data:
                    if row not in old_data:
                        obj_2 = Text(name=row['name'], text=row['text'],
                                        text_ru=row['text_ru'], text_en=row['text_en'])
                        obj_2.save()
                    else:
                        for i in data_name_list:
                            if i in request_name_list:
                                for text in request_data:
                                    obj_3 = Text.objects.update(text=text['text'],
                                                    text_ru=text['text_ru'],
                                                    text_en=text['text_en'])\
                                        .filter(Q(name == text['name']))
                                    obj_3.save()
