from model import UserRef, Text
import json
import requests
import datetime as dt


def job_check_ref():
    (UserRef
     .delete()
     .where(dt.datetime.utcnow() - UserRef.ref_created_at > dt.timedelta(30))
     .execute())


# api_spreadsheets
def json_get(path='http://gsx2json.com/api?id=1ljtGgQoaLdU0HiYYAou4JlImbvYyBVHCK2I6bEdqhiQ&sheet=1'):
    response = requests.get(path)
    data = json.loads(response.text)
    data_db = data['rows']
    Text.delete().execute()
    Text.insert(data_db).execute()