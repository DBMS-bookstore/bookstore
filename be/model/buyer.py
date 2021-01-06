import json
import logging
import sqlalchemy
import time
import uuid
from init_db.ConnectDB import Store, New_order, New_order_detail, User, User_store
from be.model import db_conn
from be.model import error


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
                row = self.Session.query(Store.stock_level, Store.book_info).filter(Store.store_id==store_id,Store.book_id==book_id).first()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )
                stock_level = row[0]
                book_info = row[1]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                else:
                    stock_level -= count
                new_order = New_order_detail(order_id=uid, book_id=book_id, count=count, price=price)
                self.Session.add(new_order)
            # print('插入订单')
            # 插入订单更新：添加两个属性
            new_ord = New_order(order_id=uid, store_id=store_id, user_id=user_id, state=0, create_time=time.time())
            self.Session.add(new_ord)
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            row = self.Session.query(New_order.order_id, New_order.user_id, New_order.store_id).filter(New_order.order_id == order_id).first()
            if row is None:
                return error.error_invalid_order_id(order_id)
            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            if buyer_id != user_id:
                return error.error_authorization_fail()

            row = self.Session.query(User.balance, User.password).filter(User.user_id == buyer_id).first()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            row = self.Session.query(User_store.store_id, User_store.user_id).filter(User_store.store_id == store_id).first()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = self.Session.query(New_order_detail.book_id, New_order_detail.count, New_order_detail.price).filter(New_order_detail.order_id == order_id)
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            balance -= total_price
            # 加钱的是卖家
            row = self.Session.query(User.balance).filter(User.user_id == seller_id).first()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            balance += total_price
            # 修改订单状态
            row = self.Session.query(New_order.state).filter(New_order.order_id == order_id).first()
            if row is None:
                return error.error_invalid_order_id(order_id)

            # cursor = conn.execute("DELETE FROM new_order WHERE order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            #
            # cursor = conn.execute("DELETE FROM new_order_detail where order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            row = self.Session.query(User.password, User.balance).filter(User.user_id == user_id).first()
            if row is None:
                return error.error_non_exist_user_id(user_id)
            if row[0] != password:
                return error.error_authorization_fail()
            row[1] += add_value
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def cancel_order(self, buyer_id: str, order_id: str) -> (int, str):
        try:
            # 不存在该用户
            row = self.Session.query(User.password, User.balance).filter(User.user_id == buyer_id).first()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            # 不存在该订单
            row = self.Session.query(New_order).filter(New_order.order_id == order_id, New_order.user_id == buyer_id).first()
            if row is None:
                return error.error_invalid_order_id()
            # 用户主动删除该订单
            elif row[3] == 2 or row[3] == 3:
                return error.error_already_delivered()
            row.delete()
            self.Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).delete()
            self.Session.commit()
            return 200, "ok"
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

    def query_order(self, user_id):
        try:
            order_list = []
            row = self.Session.query(User.password).filter(User.user_id == user_id).first()
            if row is None:
                response = error.error_authorization_fail()
                code = response[0]
                message = response[1]
                return code, message, order_list

            cursor = self.Session.query(New_order.order_id).filter(New_order.user_id == user_id)
            if cursor.count() != 0:
                for row in cursor:
                    order_list.append(row[0])
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        # print(order_list)
        return 200, "ok", order_list

    def query_detail_order(self, order_id):
        try:
            row = self.Session.query(New_order.order_id).filter(New_order.order_id == order_id).first()
            order_detail_list = []
            if row is None:
                return 518, "invalid order id.", order_detail_list
            else:

                cursor = self.Session.query("SELECT new_order.order_id, user_id, store_id, state, book_id, count, price "
                                           "from new_order, new_order_detail where new_order.order_id=? and "
                                           "new_order.order_id = new_order_detail.order_id", (order_id,))
                for row in cursor:
                    detail = {"order_id": row[0], "user_id": row[1], "store_id": row[2],
                              "state": row[3], "book_id": row[4], "count": row[5], "price": row[6]}
                    order_detail_list.append(detail)
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        # print(order_list)
        return 200, "ok", order_detail_list

    def receive_book(self, user_id: str, order_id: str) -> (int, str):
        try:
            print(0)
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id):
                return error.error_invalid_order_id(order_id)
            row = self.Session.query(New_order.order_id, New_order.state).filter(New_order.order_id == order_id).first()
            if row is None:
                return error.error_invalid_order_id(order_id)
            if row[1] != 2:
                return error.error_cannot_receive_book()
            row[1] = 3
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

