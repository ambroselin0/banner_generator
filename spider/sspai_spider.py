"""
@Time : 10/9/2020 10:01
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : sspai_spider.py
@Project : banner_generator
"""
import logging
import os
import sys

sys.path.append(os.path.dirname(__file__) + os.sep + '../')

from spider import Spider
from utils import get_config, get_db_connection
import time
import numpy as np
import requests
from bs4 import BeautifulSoup as bs
import bs4
import multiprocessing


class SspaiSpider(Spider):
    def __init__(self):
        self.db_connection = get_db_connection()
        self.header = {
            'Authorization': 'cdn.sspai.com',
            'Host': 'cdn.sspai.com'
        }
        self.sspai_banner_url = 'https://cdn.sspai.com/'
        self.sspai_article_url = 'https://sspai.com/post/'

    def initial(self):
        try:
            # mongoDB part
            self.mongo_connection.drop_db(self.db_name)
            return {'state': 'success', 'msg': ''}
        except Exception as e:
            logging.exception(e)
            return {'state': 'error', 'msg': e}

    @staticmethod
    def get_article_content(article_id: int, title: str) -> dict:
        header = {
            'Authorization': 'cdn.sspai.com',
            'Host': 'cdn.sspai.com'
        }
        sspai_article_url = 'https://sspai.com/post/'
        article_url = sspai_article_url + str(article_id)
        try:
            page = requests.get(article_url, headers=header)
            soup = bs(page.text, 'html.parser')
            context = []
            context_html = soup.find(class_=['content', 'wangEditor-txt'])
            [img.extract() for img in context_html.find_all(class_='ss-img-wrapper')]
            [img.extract() for img in context_html.find_all(class_='row')]
            [span.parent.extract() for span in context_html.find_all(class_='ss-app-card')]
            [span.parent.extract() for span in context_html.find_all(class_='ss-loading')]

            for part in [child for child in context_html.children]:
                if type(part) != bs4.element.NavigableString and type(part) != bs4.element.Comment:
                    text = (part.text).replace('\xa0', '')
                    text = text.replace('\n', '')
                    text = text.replace('\t', '')
                    if text == '':
                        continue
                    context.append(text)
            return {'article_id': article_id, 'context': context, 'title': title, 'status': True}
        except Exception as e:
            logging.exception(e)
            logging.exception(article_url)
            return {'status': False}

    @staticmethod
    def get_banner_img(article_id: int, banner_name: str):
        sspai_banner_url = 'https://cdn.sspai.com/'
        header = {
            'Authorization': 'cdn.sspai.com',
            'Host': 'cdn.sspai.com'
        }
        banner_url = sspai_banner_url + banner_name
        try:
            img = requests.get(banner_url, headers=header).content
            return {'article_id': article_id, 'img': img, 'status': True}
        except Exception as e:
            logging.exception(e)
            logging.exception(banner_url)
            return {'status': False}

    def start(self):
        """get urls of article which has banner
        """
        limit = 50
        total = np.inf
        offset = 0
        while offset + limit < total:
            content_pool = multiprocessing.Pool(10)
            banner_pool = multiprocessing.Pool(10)
            content_results = []
            banner_results = []
            try:
                logging.info(f'{offset}-{offset + limit}/{total}')
                url = f"https://sspai.com/api/v1/articles?offset={offset}&limit={limit}&sort=matrix_at"
                article_list = requests.get(url, headers=self.header)
                article_list = article_list.json()
                total = article_list['total']
                article_list = article_list['list']
                for article in article_list:
                    # banner url
                    banner_name = article['banner']
                    if banner_name == '':
                        continue

                    # article url
                    article_id = article['id']
                    if self.mongo_connection.is_exist({'article_id': article_id}):
                        logging.info(f'{article_id} exists')
                        continue

                    # title
                    title = article['title']

                    # 爬取
                    content_result = content_pool.apply_async(func=SspaiSpider.get_article_content,
                                                              args=(article_id, title))
                    banner_result = banner_pool.apply_async(func=SspaiSpider.get_banner_img,
                                                            args=(article_id, banner_name))
                    content_results.append(content_result)
                    banner_results.append(banner_result)

                content_pool.close()
                banner_pool.close()
                content_pool.join()
                banner_pool.join()

                content_results = [x.get() for x in content_results]
                banner_results = [x.get() for x in banner_results]

                content_data = {}
                banner_data = {}
                for content_result in content_results:
                    if content_result['status']:
                        key = content_result['article_id']
                        context = content_result['context']
                        title = content_result['title']
                        content_data[key] = {'context': context, 'title': title}

                for banner_result in banner_results:
                    if banner_result['status']:
                        key = banner_result['article_id']
                        img = banner_result['img']
                        banner_data[key] = img

                for key in content_data:
                    if key not in banner_data:
                        continue
                    article_id = key
                    content = content_data[key]['context']
                    title = content_data[key]['title']
                    img = banner_data[key]
                    # banner_text_type
                    # -1: not finished
                    # 0: no text
                    # 1: have text
                    self.mongo_connection.insert_img(data=img, **{'article_id': article_id, 'content': content,
                                                                  'banner_text_type': -1, 'title': title})

                offset += limit
                time.sleep(5)
            except Exception:
                logging.exception(Exception)
        logging.info('URL done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='> %(levelname)s < %(message)s')
    sspai_spider = SspaiSpider()
    sspai_spider.initial()
    sspai_spider.start()
