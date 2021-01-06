import logging
import os
import sqlite3 as sqlite
from sqlalchemy import create_engine,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, LargeBinary#区分大小写
from sqlalchemy.orm import sessionmaker
import sqlalchemy

class Store:
    # database: str
    def __init__(self):
        # self.database = os.path.join(db_path, "be.db")
        self.init_tables()

    def init_tables(self):
        try:
            Session = self.get_db_conn()
            # Session.execute(
            #     "CREATE TABLE IF NOT EXISTS user ("
            #     "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
            #     "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            # )
            #
            # Session.execute(
            #     "CREATE TABLE IF NOT EXISTS user_store("
            #     "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            # )
            #
            # Session.execute(
            #     "CREATE TABLE IF NOT EXISTS store( "
            #     "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            #     " PRIMARY KEY(store_id, book_id))"
            # )
            #
            # # 添加订单信息：
            # # ①订单状态（0：未付款，1：已付款，2：已发货，3：已收货）
            # # ②订单提交时间：时间戳
            # Session.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT, state INTEGER, create_time TIMESTAMP )"
            # )
            #
            # Session.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id),"
            #     "CONSTRAINT '1' FOREIGN KEY (order_id) REFERENCES new_order(order_id) "
            #     "ON DELETE CASCADE)"
            # )

            Session.commit()
        except sqlalchemy.ArgumentError as e:
            logging.error(e)
            Session.rollback()

    def get_db_conn(self) -> sqlite.Connection:
        engine = create_engine('postgresql+psycopg2://postgres:123456@localhost/bookstore', encoding='utf-8', echo=True)
        db_session_class = sessionmaker(bind=engine)  # db_session_class 仅仅是一个类
        Session = db_session_class()
        return Session
        # return sqlite.connect(self.database)


database_instance: Store = None


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
