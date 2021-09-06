from urllib.parse import quote_plus

from pymongo import MongoClient
import const


def connect_to_mongo():
    password_db = quote_plus(const.PASSWORD)
    # client = MongoClient('mongodb://localhost', connect=True)['Git_education']
    client = MongoClient('mongodb://{login}:{password}@{ip}/{db_name}'.format(
        login=const.LOGIN,
        password=password_db,
        ip=const.IP,
        db_name='admin'))[const.DB_NAME]

    return client


class MongoDBStorage:
    def __init__(self):
        self.client = connect_to_mongo()
        self.alexa_collection = self.client[const.DB_NAME]

    def run(self, data: dict):
        # data['_id'] = website_name
        self.alexa_collection.insert_one(data)
