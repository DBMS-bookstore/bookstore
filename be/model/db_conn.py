from be.model import store
from sqlalchemy import create_engine, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, LargeBinary#区分大小写
from sqlalchemy.orm import sessionmaker
from init_db.ConnectDB import User
class DBConn:
    def __init__(self):
        # self.conn = store.get_db_conn()
        engine = create_engine('postgresql+psycopg2://postgres:123456@localhost/bookstore', encoding='utf-8', echo=True)
        # base = declarative_base()
        db_session_class = sessionmaker(bind=engine)  # db_session_class 仅仅是一个类
        self.Session = db_session_class()

    def user_id_exist(self, user_id):
        cursor = self.Session.execute("SELECT user_id FROM user WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        cursor = self.Session.execute("SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;", (store_id, book_id))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        cursor = self.Session.execute("SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def order_id_exist(self, order_id):
        cursor = self.Session.execute("SELECT order_id FROM new_order WHERE order_id = ?;", (order_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
