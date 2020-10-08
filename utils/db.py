"""
@Time : 10/8/2020 20:06
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : db.py
@Project : banner_generator
"""

from io import BytesIO

import numpy as np
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
        self.mongo_collection = self.mongo_db[collection_name]
        self.fs = GridFS(self.mongo_db, collection="images")  # 连接collection

    def insert_img(self, data, **kwargs):
        self.fs.put(data, **kwargs)

    def get_one_img(self, query_filter: dict) -> np.ndarray:
        result = self.fs.find_one(query_filter)
        result = result.read()
        image = Image.open(BytesIO(result))
        image = np.asarray(image)
        return image
