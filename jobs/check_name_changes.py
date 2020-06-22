from model import Text
from jobs.spreadsheet import get_data_db, json_get, write_data
from peewee import IntegrityError


def check_name():
    old_data = get_data_db()
    request_data = json_get()
    data_name_list = []
    request_name_list = []
    changed_name = []
    for i in old_data:
        data_name_list.append(i['name'])
    if len(data_name_list)==0:
        query = write_data()
        query.execute()
        """
        for text in request_data:
            update_data.append(dict(
                name=text['name'],
                text=text['text'],
                text_ru=text['text_ru'],
                text_en=text['text_en']
            ))
        Text.insert(update_data).execute()
        """
    else:
        for i in request_data:
            request_name_list.append(i['name'])
        for n in data_name_list:
            if n not in request_name_list:
                changed_name.append(n)
                print("Name was changed", changed_name)
                break
            else:
                for rows in request_data:
                    if rows not in old_data:
                        try:
                            Text.insert(rows).execute()
                        except IntegrityError:
                            pass
                            continue
                    else:
                        for i in data_name_list:
                            if i in request_name_list:
                                for text in request_data:
                                    Text.update({Text.text: text['text'],
                                                    Text.text_ru: text['text_ru'],
                                                    Text.text_en: text['text_en']})\
                                        .where(Text.name == text['name']).execute()

