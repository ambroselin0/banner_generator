"""
@Time : 10/8/2020 20:06
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : db.py
@Project : banner_generator
"""

import pymysql


class DBConnection(object):
    def __init__(self):
        self.db_connection = self.get_db_connection()

    @staticmethod
    def get_db_connection():
        db_connection = pymysql.connect(host='localhost', port=3306, user='root', passwd='66888622',
                                        db='banner_generator', charset='utf8')
        return db_connection

    def truncate_table(self, table_name: str):
        cursor = self.db_connection.cursor()
        sql = f"""
            truncate table {table_name}
            """
        print(sql)
        cursor.execute(sql)


if __name__ == '__main__':
    db_connection = DBConnection()
    db_connection.truncate_table('banner_generator.sspai_urls')
