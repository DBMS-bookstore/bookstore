# -*- coding: utf-8 -*-
import json
import time
from be.model import error
from be.model import db_conn
from init_db.ConnectDB import Store, User_store, New_order, Book
from init_db.init_search_table import Book_Onsale
import sqlalchemy
import time

class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, stock_level: int, price:int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            obj = Store(store_id=store_id, book_id=book_id, stock_level=stock_level, price=price)
            self.Session.add(obj)
            this_book = self.Session.query(Book).filter(Book.book_id == book_id).first()
            if this_book.book_intro:
                this_book.book_intro = str(this_book.book_intro)
            if this_book.content:
                this_book.content = str(this_book.book_intro)
            book_onsale_obj = Book_Onsale(store_id=store_id, book_id=book_id, title=this_book.title, author=this_book.author,
                                          translator=this_book.translator, price=price,
                                          book_intro=this_book.book_intro, content=this_book.content, tags=this_book.tags)
            self.Session.add(book_onsale_obj)
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print('加书出错:', e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            row = self.Session.query(Store).filter(Store.store_id == store_id, Store.book_id == book_id).first()
            stock_level = row.stock_level
            row.stock_level = stock_level + add_stock_level
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print('加库存出错:',e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            store_obj = User_store(store_id=store_id, user_id=user_id)
            self.Session.add(store_obj)
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def delivery_book(self, user_id: str, order_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id):
                return error.error_invalid_order_id(order_id)
            row = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            if row is None:
                return error.error_invalid_order_id(order_id)
            if row.state == 0:
                return error.error_no_payment_to_deliver()
            elif row.state == 2 or row.state == 3:
                return error.error_already_delivered()
            row.state = 2
            row.delivery_time = time.time()
            self.Session.commit()
            row = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"