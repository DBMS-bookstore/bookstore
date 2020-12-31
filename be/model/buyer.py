import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
import time
from bson import json_util

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                cursor = self.conn.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = ? AND book_id = ?;",
                    (store_id, book_id))
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor = self.conn.execute(
                    "UPDATE store set stock_level = stock_level - ? "
                    "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                    (count, store_id, book_id, count))
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id, )

                self.conn.execute(
                        "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                        "VALUES(?, ?, ?, ?);",
                        (uid, book_id, count, price))
            print('插入订单')
            # 插入订单更新：添加两个属性
            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id, state, create_time) "
                "VALUES(?, ?, ?, ?, ?);",
                (uid, store_id, user_id, 0, time.time()))
            self.conn.commit()
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = conn.execute("SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor = conn.execute("SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor = conn.execute("SELECT store_id, user_id FROM user_store WHERE store_id = ?;", (store_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = conn.execute("SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;", (order_id,))
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute("UPDATE user set balance = balance - ?"
                                  "WHERE user_id = ? AND balance >= ?",
                                  (total_price, buyer_id, total_price))
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)
            # 加钱的是卖家
            cursor = conn.execute("UPDATE user set balance = balance + ?"
                                  "WHERE user_id = ?",
                                  (total_price, seller_id))

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            # 修改订单状态
            cursor = conn.execute("UPDATE new_order set  state = ?", (1,))
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            # cursor = conn.execute("DELETE FROM new_order WHERE order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            #
            # cursor = conn.execute("DELETE FROM new_order_detail where order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            conn.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.execute("SELECT password  from user where user_id=?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "UPDATE user SET balance = balance + ? WHERE user_id = ?",
                (add_value, user_id))
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def cancel_order(self, buyer_id: str, order_id: str) -> (int, str):
        try:
            # 不存在该用户
            cursor = self.conn.execute("SELECT password  from user where user_id=?", (buyer_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            # 不存在该订单
            cursor = self.conn.execute("SELECT order_id,state  from new_order where order_id=? and user_id=?",
                                       (order_id, buyer_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id()
            # 用户主动删除该订单
            elif row[1] == 2 or row[1] == 3:
                return error.error_already_delivered()
            self.conn.execute("Delete FROM new_order WHERE order_id = ?;", (order_id,))
            self.conn.execute("Delete FROM new_order_detail WHERE order_id = ?;", (order_id,))
            self.conn.commit()
            return 200, "ok"
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

    def query_order(self, user_id):
        try:
            order_list = []
            cursor = self.conn.execute("SELECT password  from user where user_id=?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                response = error.error_authorization_fail()
                code = response[0]
                message = response[1]
                return code, message, order_list

            cursor = self.conn.execute(
                "SELECT order_id FROM new_order WHERE user_id = ?",
                (user_id,))

            if cursor.rowcount != 0:
                for row in cursor:
                    order_list.append(row[0])
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        # print(order_list)
        return 200, "ok", order_list

