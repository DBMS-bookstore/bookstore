import sqlite3 as sqlite
import time

from be.model import error
from be.model import db_conn
from init_db.ConnectDB import Store, User_store, New_order
import sqlalchemy

class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            obj = Store(store_id=store_id, book_id=book_id, book_info=book_json_str,stock_level=stock_level)
            self.Session.add(obj)
            # self.Session.execute("INSERT into store(store_id, book_id, book_info, stock_level)"
            #                   "VALUES (?, ?, ?, ?)", (store_id, book_id, book_json_str, stock_level))
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
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
            row = self.Session.query(Store.stock_level).filter(Store.store_id == store_id, Store.book_id == book_id).first()
            stoke_level = row[0]
            stoke_level += add_stock_level
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
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
            print(0)
            if not self.user_id_exist(user_id):
                print(1)
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id):
                print(2)
                return error.error_invalid_order_id(order_id)
            print(3)
            row = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            print(4)
            if row is None:
                return error.error_invalid_order_id(order_id)
            print(5)
            print('目前状态为：', row.state)
            if row.state == 0:
                print(6)
                return error.error_no_payment_to_deliver()
            elif row.state == 2 or row.state == 3:
                print(7)
                return error.error_already_delivered()
            print(8)
            row.state = 2
            print(9)
            row.delivery_time = time.time()
            self.Session.commit()
            row = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            print('已发货：', row.state)
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
