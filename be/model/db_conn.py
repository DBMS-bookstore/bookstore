from be.model import store
from sqlalchemy import create_engine, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, LargeBinary#区分大小写
from sqlalchemy.orm import sessionmaker
from init_db.ConnectDB import User, Store, User_store, New_order
class DBConn:
    def __init__(self):
        # self.conn = store.get_db_conn()
        engine = create_engine('postgresql+psycopg2://postgres:zke20001231@localhost:5432/bookstore', encoding='utf-8', echo=True)
        # base = declarative_base()
        db_session_class = sessionmaker(bind=engine)  # db_session_class 仅仅是一个类
        self.Session = db_session_class()

    def user_id_exist(self, user_id):
        row = self.Session.query(User.user_id).filter(User.user_id == user_id).first()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        row = self.Session.query(Store.book_id).filter(Store.store_id == store_id, Store.book_id == book_id).first()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        row = self.Session.query(User_store.store_id).filter(User_store.store_id==store_id).first()
        if row is None:
            return False
        else:
            return True

    def order_id_exist(self, order_id):
        row = self.Session.query(New_order.order_id).filter(New_order.order_id == order_id).first()
        if row is None:
            return False
        else:
            return True
