from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, LargeBinary#区分大小写
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:zke20001231@localhost:5432/bookstore', encoding='utf-8', echo=True)
base = declarative_base()
db_session_class = sessionmaker(bind=engine)    # db_session_class 仅仅是一个类
Session = db_session_class()
# base.metadata.drop_all(engine)

# 在架书籍，这个表用于全文检索
class Book_Onsale(base):
    __tablename__ = 'book_onsale'
    store_id = Column('store_id', Text, primary_key=True)
    book_id = Column('book_id', Text, primary_key=True)
    title = Column('title', Text, nullable=False, index=True)
    author = Column('author', Text, index=True)
    translator = Column('translator', Text)
    price = Column('price', Integer)
    book_intro = Column('book_intro', Text)
    content = Column('content', Text)
    tags = Column('tags', Text, index=True)
    __table_args__ = {
        'mysql_charset': 'utf8'
    }

base.metadata.create_all(engine)
# # 添加一个新的字段用于建立倒排索引
# Session.execute('ALTER TABLE book_onsale ADD COLUMN posting tsvector;')
# # 将需要查询的column分词后插入新列中,A-F为重要顺序,A最重要
# Session.execute("UPDATE book_onsale SET posting = setweight(to_tsvector('public.jiebacfg', coalesce(title,'')),'A') || "
#                 "setweight(to_tsvector('public.jiebacfg', coalesce(title,'')),'A')|| "
#                 "setweight(to_tsvector('public.jiebacfg', coalesce(author,'')),'B')|| "
#                 "setweight(to_tsvector('public.jiebacfg', coalesce(translator,'')),'D')|| "
#                 "setweight(to_tsvector('public.jiebacfg', coalesce(book_intro,'')),'E')|| "
#                 "setweight(to_tsvector('public.jiebacfg', coalesce(content,'')),'F')|| "
#                 "setweight(to_tsvector('public.jiebacfg', coalesce(tags,'')),'C');")
# # 建立倒排索引（GIN）
# Session.execute('CREATE INDEX gin_index ON book_onsale USING GIN(posting);')
# # 创建一个分词触发器
# Session.execute("CREATE TRIGGER trigger_posting "
#                 "BEFORE INSERT OR UPDATE ON book_onsale "
#                 "FOR EACH ROW EXECUTE PROCEDURE "
#                 "tsvector_update_trigger(posting, 'public.jiebacfg', title,author,translator,book_intro,content,tags);")
# Session.execute('CREATE INDEX gin_index_2 ON book_onsale USING GIN(title);')
Session.commit()
Session.close()