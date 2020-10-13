"""
@Time : 10/9/2020 10:46
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : config.py
@Project : banner_generator
"""
from configparser import ConfigParser


# sys.path.append(os.path.dirname(__file__) + os.sep + '../')

def get_config(config_path: str, section: str, key: str) -> str:
    config = ConfigParser()
    config.read(config_path)
    return config.get(section, key)
