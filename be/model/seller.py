import sqlite3 as sqlite
from be.model import error
from be.model import db_conn


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

            self.conn.execute("INSERT into store(store_id, book_id, book_info, stock_level)"
                              "VALUES (?, ?, ?, ?)", (store_id, book_id, book_json_str, stock_level))
            self.conn.commit()
        except sqlite.Error as e:
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

            self.conn.execute("UPDATE store SET stock_level = stock_level + ? "
                              "WHERE store_id = ? AND book_id = ?", (add_stock_level, store_id, book_id))
            self.conn.commit()
        except sqlite.Error as e:
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
            self.conn.execute("INSERT into user_store(store_id, user_id)"
                              "VALUES (?, ?)", (store_id, user_id))
            self.conn.commit()
        except sqlite.Error as e:
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
            cursor = self.conn.execute("SELECT order_id,state  from new_order where order_id=?",
                                       (order_id,))
            print(4)
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            print(5)
            if row[1] == 0:
                print(6)
                return error.error_no_payment_to_deliver()
            elif row[1] == 2 or row[1] == 3:
                print(7)
                return error.error_already_delivered()
            print(8)
            self.conn.execute("UPDATE new_order set  state = ?"
                              "WHERE order_id = ?", (2, order_id))
            print(9)
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
