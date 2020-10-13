"""
@Time : 10/8/2020 20:06
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : db.py
@Project : banner_generator
"""

import logging
from io import BytesIO


import pymongo
from PIL import Image
from gridfs import GridFS


class MongoConnection(object):
    """
    mongodb operating
    """

    def __init__(self, db_name: str, collection_name: str):
        """
        init mongo db connection
        :param db_name: databse name
        :param collection_name: collection name
        """
        self.mongo_connection = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_connection[db_name]
        self.mongo_collection = self.mongo_db[f'{collection_name}.files']
        self.fs = GridFS(self.mongo_db, collection="sspai")  # 连接collection

    def drop_db(self, db_name):
        self.mongo_connection.drop_database(db_name)

    def drop_collection(self, collection_name):
        try:
            self.mongo_db.drop_collection(collection_name)
            return {'state': 'success', 'msg': ''}
        except Exception as e:
            logging.exception(e)
            return {'state': 'error', 'msg': e}

    def insert_img(self, data, **kwargs):
        self.fs.put(data, **kwargs)

    def get_one_img(self, query_filter=None) -> Image.Image:
        result = self.fs.find_one(query_filter)
        result = result.read()
        image = Image.open(BytesIO(result))
        return image

    def find_one(self, filter=None, projection=None):
        result = self.mongo_collection.find_one(filter=filter, projection=projection)
        return result

    def find(self, filter=None, projection=None):
        results = self.mongo_collection.find(filter, projection)
        return results

    def is_exist(self, filter: dict) -> bool:
        result = self.find_one(filter)
        if result == None:
            return False
        else:
            return True

    def update(self, filter, document):
        self.mongo_collection.update(filter, document)
