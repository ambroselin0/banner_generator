"""
@Time : 10/9/2020 10:01
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : sspai_prider.py
@Project : banner_generator
"""
import logging

from .spider import Spider
from ..utils import MongoConnection


class SspaiSpider(Spider):
    def __init__(self):
        mongo_connection = MongoConnection()

    def get_article_list(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='> %(levelname)s < %(message)s')
