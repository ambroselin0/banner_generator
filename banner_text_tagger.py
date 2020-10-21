"""
@Time : 10/11/2020 20:14
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : banner_text_tagger.py
@Project : banner_generator
"""
import logging
import tkinter as tk

from PIL import ImageTk, Image

from utils import MongoConnection, get_config


class DataWrapper(object):
    def __init__(self, db_name='sspai'):
        config_path = './config.ini'
        self.db_name = get_config(config_path, db_name, 'db_name')
        self.collection_name = get_config(config_path, db_name, 'collection_name')
        self.mongo_connection = MongoConnection(self.db_name, self.collection_name)
        self.target_width = 1080

        self.img = None
        self.data_id = None

    def next_img(self):
        article_info = self.mongo_connection.find_one({'banner_text_type': -1}, {'article_id': 1, 'title': 1})
        # article_info = [x for x in article_info]
        # random.shuffle(article_info)
        # article_info = article_info[0]
        data_id = article_info['_id']
        title = article_info['title']
        logging.info(title)
        try:
            img = self.mongo_connection.get_one_img({'_id': data_id})
            img = self.resize_img(img)
            # img.show()
            # img = ImageTk.PhotoImage(img)
            self.img = img
            self.data_id = data_id
        except:
            logging.exception('image is truncted')

    def resize_img(self, img: Image.Image):
        width, height = img.size
        scale = width / self.target_width
        img = img.resize((int(width / scale), int(height / scale)))
        return img

    def update_data(self, data):
        self.mongo_connection.update({'_id': self.data_id}, {'$set': data})


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='> %(levelname)s < %(message)s')

    data_wrapper = DataWrapper('sspai')
    data_wrapper.next_img()

    root = tk.Tk(className='Banner Text Tagger')

    render = ImageTk.PhotoImage(data_wrapper.img)

    imageview = tk.Label(root, image=render)
    imageview.configure(image=render)

    imageview.grid(row=0, column=0, columnspan=4)

    entry_var = tk.StringVar()
    input_text = tk.Entry(root, width=20, textvariable=entry_var)
    input_text.grid(row=1, column=0, columnspan=2, sticky=tk.E)



    def update_tag(*args):
        text = entry_var.get()
        if text == '':
            tag = 0
        else:
            tag = 1
        if tag == 0:
            data_wrapper.update_data({'banner_text_type': 0})
        else:
            data_wrapper.update_data({'banner_text': text, 'banner_text_type': 1})
        entry_var.set('')
        data_wrapper.next_img()
        render = ImageTk.PhotoImage(data_wrapper.img)
        imageview.image = render
        imageview.configure(image=render)

    input_text.bind("<Return>", update_tag)


    button0 = tk.Button(root, text='next', command=update_tag)
    button0.grid(row=2, column=0, columnspan=2, sticky=tk.E)

    root.mainloop()
