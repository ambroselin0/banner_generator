"""
@Time : 10/13/2020 10:07
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : text_preprocessing.py
@Project : banner_generator
"""
import re

import jieba
from tensorflow.keras.preprocessing.text import Tokenizer

from utils import DBConnection, get_config, load_data, save_data


# jieba.enable_parallel(16)


class TextTokenizer(object):
    def __init__(self, db_name='sspai', config_path='./config.ini', is_fit=False):
        self.db_name = get_config(config_path, db_name, 'db_name')
        self.collection_name = get_config(config_path, db_name, 'collection_name')
        self.mongo_connection = DBConnection(self.db_name, self.collection_name)
        if is_fit == True:
            self.tokenizer = Tokenizer(num_words=100000, oov_token='OOV', lower=True)
        else:
            self.tokenizer: Tokenizer = load_data('./models/tokenizer.pickle')
        self.cop = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
        self.stop_words = [' ', '丨']  # 停用词

    def get_all_content(self):
        all_text = self.mongo_connection.find({}, {'content': 1, '_id': 0})
        return all_text

    def get_all_banner(self):
        all_banner = self.mongo_connection.find({'banner_text_type': 1}, {'banner_text': 1, '_id': 0})
        return all_banner

    def get_all_title(self):
        all_title = self.mongo_connection.find({}, {'title': 1, '_id': 0})
        return all_title

    def save_tokenizer(self):
        save_data(self.tokenizer, './models/tokenizer.pickle')

    def content_cut(self, content):
        # content = ''.join(content)
        content = [self.cop.sub('', x) for x in content]
        cut_contents = [jieba.cut(x, cut_all=False) for x in content]
        cut_contents = [[y for y in x] for x in cut_contents]
        words = []
        for cut_content in cut_contents:
            words.extend(cut_content)
        words = [x for x in words if x not in self.stop_words]
        # words = [[y for y in x if y not in self.stop_words] for x in cut_contents]
        # print(words)
        return words

    def banner_cut(self, banner):
        banner = self.cop.sub('', banner)
        banner = [x for x in jieba.cut(banner, cut_all=False)]
        banner = [x for x in banner if x not in self.stop_words]
        return banner

    def fit_content_tokenizer(self):
        all_content = self.get_all_content()
        all_cut_content = [self.content_cut(x['content']) for x in all_content]
        self.tokenizer.fit_on_texts(all_cut_content)
        print(len(self.tokenizer.word_counts))
        # for content in tqdm(all_content):
        #     content = content['content']
        #     content = self.content_cut(content)
        #     self.tokenizer.fit_on_texts(content)

    def fit_banner_tokenizer(self):
        all_banner = self.get_all_banner()
        all_cut_banner = [self.banner_cut(x['banner_text']) for x in all_banner]
        self.tokenizer.fit_on_texts(all_cut_banner)
        print(len(self.tokenizer.word_counts))

    def fit_title_tokenizer(self):
        all_title = self.get_all_title()
        all_title = [self.banner_cut(x['title']) for x in all_title]
        self.tokenizer.fit_on_texts(all_title)
        print(len(self.tokenizer.word_counts))


if __name__ == '__main__':
    text_tokenizer = TextTokenizer(is_fit=True)
    text_tokenizer.fit_content_tokenizer()
    text_tokenizer.fit_banner_tokenizer()
    text_tokenizer.fit_title_tokenizer()
    text_tokenizer.save_tokenizer()

