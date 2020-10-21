"""
@Time : 10/20/2020 14:59
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : data.py
@Project : banner_generator
"""
import pickle


def load_data(data_path: str):
    with open(data_path, 'rb') as file:
        data = pickle.load(file)
    return data


def save_data(data, data_path: str):
    with open(data_path, 'wb') as file:
        pickle.dump(data, file)
