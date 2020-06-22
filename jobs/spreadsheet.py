from model import Text
import json
import requests

# api_spreadsheets
def json_get(path='http://gsx2json.com/api?id=1ljtGgQoaLdU0HiYYAou4JlImbvYyBVHCK2I6bEdqhiQ&sheet=1'):
    response = requests.get(path)
    data_spreadsheet = json.loads(response.text)
    data_db = data_spreadsheet['rows']
    d = []
    for i in data_db:
        d.append(dict(
            name=i['name'],
            text=i['text'],
            text_ru=i['textru'],
            text_en=i['texten']
        ))
    return d

def get_data_db():
    query_text = Text.select().dicts()
    data_text = []
    for i in query_text:
        data_text.append(dict(
            name=i['name'],
            text=i['text'],
            text_ru=i['text_ru'],
            text_en=i['text_en']
        ))
    return data_text

def write_data():
    new_data = json_get()
    update_data = []
    for i in new_data:
        update_data.append(dict(
            name=i['name'],
            text=i['text'],
            text_ru=i['text_ru'],
            text_en=i['text_en']
        ))
    return Text.insert(update_data)
