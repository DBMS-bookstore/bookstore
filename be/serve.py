import logging
import os
from flask import Flask
from flask import Blueprint
from flask import request

from be.view import auth
from be.view import seller
from be.view import buyer
import time
from threading import Timer
from be.model import error
from init_db.ConnectDB import Session, New_order, New_order_detail, Store, User_store, User



bp_shutdown = Blueprint("shutdown", __name__)


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@bp_shutdown.route("/shutdown")
def be_shutdown():
    shutdown_server()
    return "Server shutting down..."


def be_run():
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")
    # init_database()

    logging.basicConfig(filename=log_file, level=logging.ERROR)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    app = Flask(__name__)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)
    polling(10)
    app.run(use_reloader=False)


def polling(seconds):
    cursor1 = Session.query(New_order).filter(time.time()-New_order.create_time >= 300, New_order.state == 0).all()
    cursor2 = Session.query(New_order).filter(time.time()-New_order.delivery_time >= 3600*7,
                                              New_order.delivery_time > 0, New_order.state==2).all()
    if cursor1 is not None:
        for row in cursor1:
            order_id = row.order_id
            store_id = row.store_id
            state = row.state
            create_time = row.create_time
            # delivery_time = row.delivery_time
            # 若超时且状态为未付款
            # 增加库存
            cur = Session.query(New_order_detail.book_id, New_order_detail.count).filter(New_order_detail.order_id == order_id)
            for x in cur:
                book_id = x[0]
                count = x[1]
                stock_level = Session.query(Store.stock_level).filter(Store.store_id == store_id, Store.book_id == book_id).first()[0]
                stock_level += count
            row.state = -1
    if cursor2 is not None:
        for row in cursor2:
            order_id = row.order_id
            store_id = row.store_id
            row.state = 3
            cur = Session.query(New_order_detail.book_id, New_order_detail.count,
                                    New_order_detail.price).filter(New_order_detail.order_id == order_id).all()
            total_price = 0
            for row1 in cur:
                count = row1[1]
                price = row1[2]
                total_price = total_price + price * count
            row2 = Session.query(User_store).filter(User_store.store_id == store_id).first()
            if row2 is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = row2.user_id
            row3 = Session.query(User).filter(User.user_id == seller_id).first()
            if row3 is None:
                return error.error_non_exist_user_id(seller_id)
            balance = row3.balance
            row3.balance = balance + total_price
    Session.commit()
    t = Timer(seconds, polling(), (seconds,))
    t.start()
