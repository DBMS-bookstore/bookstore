from sqlalchemy import create_engine,ForeignKey,Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String , Text, TIMESTAMP, LargeBinary#区分大小写
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:123456@localhost/bookstore',encoding='utf-8',echo=True)
base=declarative_base()
db_session_class = sessionmaker(bind=engine)    # db_session_class 仅仅是一个类
Session = db_session_class()


# 用户
class User(base):
    __tablename__ = 'user'
    user_id = Column('user_id', String(64), primary_key=True)
    password = Column('password', String(64), nullable=False)
    balance = Column('balance', Integer, nullable=False)
    token = Column('token', String(64))
    terminal = Column('terminal', String(64))


# 书
class Book(base):
    __tablename__ = 'book'
    book_id = Column(String(64), primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    original_price = Column(Integer)
    currency_unit = Column(Text)
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    picture = Column(LargeBinary)


# 店铺
class User_store(base):
    __tablename__ = 'user_store'
    user_id = Column('user_id', String(64), ForeignKey("user.user_id", ondelete='CASCADE'), primary_key=True)
    store_id = Column('store_id', String(64), primary_key=True)


# 店铺详情
class Store(base):
    __tablename__ = 'store'
    store_id = Column('store_id', String(64), primary_key=True)
    book_id = Column('book_id', String(64), ForeignKey("book.book_id", ondelete='CASCADE'), primary_key=True)
    book_info = Column('book_info', Text)
    stock_level = Column('stock_level', Integer)


# 新订单
class New_order(base):
    __tablename__ = 'new_order'
    order_id = Column('order_id', String(64), primary_key=True)
    user_id = Column('user_id', String(64), ForeignKey("user.user_id", ondelete='CASCADE'))
    store_id = Column('store_id', String(64), ForeignKey("store.store_id", ondelete='CASCADE'))
    state = Column('state', Integer)
    create_time = Column('creat_time', TIMESTAMP)


# 订单详情
class New_order_detail(base):
    __tablename__ = 'new_order_detail'
    order_id = Column('order_id', String(64), ForeignKey("new_order.order_id", ondelete='CASCADE'), primary_key=True)
    book_id = Column('book_id', String(64), ForeignKey("book.book_id", ondelete='CASCADE'), primary_key=True)
    count = Column('count', Integer, nullable=False)
    price = Column('price', Integer)

base.metadata.create_all(engine) #创建表结构