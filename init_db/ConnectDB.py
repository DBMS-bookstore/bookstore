from sqlalchemy import create_engine,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, LargeBinary#区分大小写
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:xsh13766277896@localhost/bookstore',encoding='utf-8',echo=True)
base = declarative_base()
db_session_class = sessionmaker(bind=engine)    # db_session_class 仅仅是一个类
Session = db_session_class()
# base.metadata.drop_all(engine)
# 用户
class User(base):
    __tablename__ = 'user'
    user_id = Column('user_id', Text, primary_key=True)
    password = Column('password', Text, nullable=False)
    balance = Column('balance', Integer, nullable=False)
    token = Column('token', Text)
    terminal = Column('terminal', Text)


# 书
class Book(base):
    __tablename__ = 'book'
    book_id = Column('id', Text, primary_key=True)
    title = Column('title', Text, nullable=False)
    author = Column('author', Text)
    publisher = Column('publisher', Text)
    original_title = Column('original_title', Text)
    translator = Column('translator', Text)
    pub_year = Column('pub_year', Text)
    pages = Column('pages', Integer)
    price = Column('price', Integer)
    currency_unit = Column('currency_unit', Text)
    binding = Column('binding', Text)
    isbn = Column('isbn', Text)
    author_intro = Column('author_intro', Text)
    book_intro = Column('book_intro', Text)
    content = Column('content', Text)
    tags = Column('tags', Text)
    picture = Column('picture', LargeBinary)


# 店铺
class User_store(base):
    __tablename__ = 'user_store'
    user_id = Column('user_id', Text, ForeignKey("user.user_id", ondelete='CASCADE'), primary_key=True)
    store_id = Column('store_id', Text, primary_key=True)


# 店铺详情
class Store(base):
    __tablename__ = 'store'
    store_id = Column('store_id', Text, primary_key=True)
    book_id = Column('book_id', Text, primary_key=True)
    book_info = Column('book_info', Text)
    stock_level = Column('stock_level', Integer)


# 新订单
class New_order(base):
    __tablename__ = 'new_order'
    order_id = Column('order_id', Text, primary_key=True)
    user_id = Column('user_id', Text, ForeignKey("user.user_id", ondelete='CASCADE'))
    store_id = Column('store_id', Text)
    state = Column('state', Integer)
    create_time = Column('create_time', Integer)


# 订单详情
class New_order_detail(base):
    __tablename__ = 'new_order_detail'
    order_id = Column('order_id', Text, primary_key=True)
    book_id = Column('book_id', Text, primary_key=True)
    count = Column('count', Integer, nullable=False)
    price = Column('price', Integer)

base.metadata.create_all(engine) #创建表结构
# user_obj = User(user_id="u_id", password="password", balance=0, token="token", terminal="terminal")
# Session.add(user_obj)
# Session.commit()
Session.close()