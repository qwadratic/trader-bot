from model import Text
import json
import requests

# api_spreadsheets
def json_get(path='http://gsx2json.com/api?id=1ljtGgQoaLdU0HiYYAou4JlImbvYyBVHCK2I6bEdqhiQ&sheet=1'):
    response = requests.get(path)
    data = json.loads(response.text)
    data_db = data['rows']
    Text.delete().execute()
    Text.insert(data_db).execute()
