import logging
import sqlite3 as sqlite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy

class Store:
    def __init__(self):
        self.init_tables()

    def init_tables(self):
        try:
            Session = self.get_db_conn()
            Session.commit()
        except sqlalchemy.ArgumentError as e:
            logging.error(e)
            Session.rollback()

    def get_db_conn(self) -> sqlite.Connection:
        engine = create_engine('postgresql+psycopg2://postgres:123456@localhost:5433/bookstore', encoding='utf-8', echo=True)
        db_session_class = sessionmaker(bind=engine)  # db_session_class 仅仅是一个类
        Session = db_session_class()
        return Session


database_instance: Store = None


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
