import logging
import os
from flask import Flask
from flask import Blueprint
from flask import request
from be.view import auth
from be.view import seller
from be.view import buyer
# from be.model.store import init_database
import time
from threading import Timer
from be.model import store
from be.model import error
from init_db.ConnectDB import Session, New_order, New_order_detail, Store
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
    delete_order(10)
    app.run(use_reloader=False)


def delete_order(seconds):
    # Session = store.get_db_conn()
    cursor = Session.query(New_order).all()
    print('cur')
    print(cursor)
    if cursor is not None:
        for row in cursor:
            print('row')
            print(row)
            order_id = row.order_id
            store_id = row.store_id
            state = row.state
            create_time = row.create_time
            delivery_time = row.delivery_time
            # 若超时且状态为未付款
            if time.time()-create_time >= 600 and state == 0:
                # 增加库存
                cur = Session.query(New_order_detail.book_id, New_order_detail.count).filter(New_order_detail.order_id == order_id)
                for x in cur:
                    book_id = x[0]
                    count = x[1]
                    stock_level = Session.query(Store.stock_level).filter(Store.store_id == store_id, Store.book_id == book_id).first()[0]
                    stock_level += count
                Session.query(New_order).filter(New_order.order_id == order_id).delete()
                Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).delete()
            if time.time() - delivery_time >= 60 and state == 2:
                r = Session.query(New_order).filter(New_order.order_id == order_id).first()
                r.state = 3
                cursor1 = Session.query(New_order_detail.book_id, New_order_detail.count,
                                        New_order_detail.price).filter(New_order_detail.order_id == order_id).all()
                total_price = 0
                for row1 in cursor1:
                    count = row1[1]
                    price = row1[2]
                    total_price = total_price + price * count
                row3 = Session.query(User_store).filter(User_store.store_id == store_id).first()
                if row3 is None:
                    return error.error_non_exist_store_id(store_id)

                seller_id = row3.user_id
                row5 = Session.query(User).filter(User.user_id == seller_id).first()
                if row5 is None:
                    return error.error_non_exist_user_id(seller_id)
                row5.balance += total_price
        Session.commit()
    t = Timer(seconds, delete_order, (seconds,))
    t.start()