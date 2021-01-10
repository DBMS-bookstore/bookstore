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
            order_id = uid
            for book_id, count in id_and_count:
                row = self.Session.query(Store).filter(Store.store_id==store_id,Store.book_id==book_id).first()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )
                book_info_json = json.loads(row.book_info)
                price = book_info_json.get("price")
                if row.stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                else:
                    row.stock_level -= count
                new_order = New_order_detail(order_id=uid, book_id=book_id, count=count, price=price)
                self.Session.add(new_order)
            # print('插入订单')
            # 插入订单更新：添加两个属性
            new_ord = New_order(order_id=uid, store_id=store_id, user_id=user_id, state=0, create_time=time.time(), delivery_time=0 )
            self.Session.add(new_ord)
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            # print('payment')
            row1 = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            if row1 is None:
                return error.error_invalid_order_id(order_id)
            buyer_id = row1.user_id
            if buyer_id != user_id:
                return error.error_authorization_fail()

            row2 = self.Session.query(User).filter(User.user_id == buyer_id).first()
            if row2 is None:
                return error.error_non_exist_user_id(buyer_id)
            if password != row2.password:
                return error.error_authorization_fail()

            row3 = self.Session.query(User_store).filter(User_store.store_id == row1.store_id).first()
            if row3 is None:
                return error.error_non_exist_store_id(row1.store_id)

            seller_id = row3.user_id
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = self.Session.query(New_order_detail.book_id, New_order_detail.count, New_order_detail.price).filter(New_order_detail.order_id == order_id).all()
            # print('cccc')
            # print(cursor)
            total_price = 0
            for row4 in cursor:
                count = row4[1]
                price = row4[2]
                total_price = total_price + price * count
            # print('balance = ', row2.balance, 'price = ', total_price)
            if row2.balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            row2.balance -= total_price
            # 加钱的是卖家
            # row5 = self.Session.query(User).filter(User.user_id == seller_id).first()
            # if row5 is None:
            #     return error.error_non_exist_user_id(seller_id)
            # row5.balance += total_price
            # 修改订单状态
            row6 = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            if row6 is None:
                return error.error_invalid_order_id(order_id)
            row6.state = 1
            self.Session.commit()
            # row6 = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            # print('改状态：', row6.state)
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            # print('出错啦:', e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            row = self.Session.query(User).filter(User.user_id == user_id).first()
            if row is None:
                return error.error_non_exist_user_id(user_id)
            if row.password != password:
                return error.error_authorization_fail()
            row.balance += add_value
            self.Session.commit()
            row = self.Session.query(User).filter(User.user_id == user_id).first()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def cancel_order(self, buyer_id: str, order_id: str) -> (int, str):
        try:
            # 不存在该用户
            row = self.Session.query(User.password, User.balance).filter(User.user_id == buyer_id).first()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            # 不存在该订单
            row = self.Session.query(New_order).filter(New_order.order_id == order_id,
                                                       New_order.user_id == buyer_id).first()
            # store_id = cursor.store_id
            print('可以')
            if row is None:
                # print(order_id)
                return error.error_invalid_order_id(order_id)
            # 用户主动删除该订单
            if row.state == 2 or row.state == 3:
                return error.error_already_delivered()
            # 未付款，直接取消订单，加回库存
            if row.state == 0 or row.state == 1:
                cursor = self.Session.query(New_order).filter(New_order.order_id == order_id,
                                                              New_order.user_id == buyer_id).first()
                # cursor1 = self.Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).first()
                # count = cursor.count
                store_id = cursor.store_id
                cursor1 = self.Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).all()
                for each_row in cursor1:
                    book_id = each_row.book_id
                    count = each_row.count
                    stock_level = self.Session.query(Store.stock_level).filter(Store.store_id == store_id,
                                                                               Store.book_id == book_id).first()[0]
                    stock_level += count
                if row.state == 0:
                    self.Session.query(New_order).filter(New_order.order_id == order_id,
                                                         New_order.user_id == buyer_id).delete()
                    self.Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).delete()
                    self.Session.commit()
                    return 200, "ok"
                if row.state == 1:
                    # 已付款,退款,加回库存
                    cursor2 = self.Session.query(New_order_detail.book_id, New_order_detail.count, New_order_detail.price)\
                        .filter(New_order_detail.order_id == order_id).all()
                    total_price = 0
                    for row4 in cursor2:
                        count = row4[1]
                        price = row4[2]
                        total_price = total_price + price * count
                    row5 = self.Session.query(User).filter(User.user_id == buyer_id).first()
                    row5.balance += total_price

                self.Session.query(New_order).filter(New_order.order_id == order_id,
                                                     New_order.user_id == buyer_id).delete()
                self.Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).delete()
                self.Session.commit()
                return 200, "ok"

        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(e)
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

            cursor = self.Session.query(New_order.order_id, New_order.state).filter(New_order.user_id == user_id)
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

    def query_order_state(self, order_id):
        try:
            cursor = self.Session.query(New_order.state).filter(New_order.order_id == order_id).first()
            order_state = cursor.state
            return 200, "ok", order_state
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

    def query_detail_order(self, order_id):
        try:
            row = self.Session.query(New_order.order_id).filter(New_order.order_id == order_id).first()
            order_detail_list = []
            if row is None:
                return 518, "invalid order id.", order_detail_list
            else:
                cursor = self.Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).all()
                cursor1 = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
                for row in cursor:
                    detail = {"order_id": row.order_id, "book_id": row.book_id, "count": row.count,
                              "price": row.price, "state": cursor1.state, "store_id": cursor1.store_id,
                              "create_time": cursor1.create_time}
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
            row = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            # if row is None:
            #     return error.error_invalid_order_id(order_id)
            if row.state != 2:
                return error.error_cannot_receive_book()
            row.state = 3
            cursor = self.Session.query(New_order_detail.book_id, New_order_detail.count,
                                        New_order_detail.price).filter(New_order_detail.order_id == order_id).all()
            total_price = 0
            for row4 in cursor:
                count = row4[1]
                price = row4[2]
                total_price = total_price + price * count
            row1 = self.Session.query(New_order).filter(New_order.order_id == order_id).first()
            row3 = self.Session.query(User_store).filter(User_store.store_id == row1.store_id).first()
            if row3 is None:
                return error.error_non_exist_store_id(row1.store_id)

            seller_id = row3.user_id
            row5 = self.Session.query(User).filter(User.user_id == seller_id).first()
            if row5 is None:
                return error.error_non_exist_user_id(seller_id)
            row5.balance += total_price
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
<<<<<<< HEAD
        return 200, "ok"
=======
        return 200, "ok"

    # def search_book(self):


>>>>>>> 6725169bef05400ad9bf36c4512601a6d0c88ea8
