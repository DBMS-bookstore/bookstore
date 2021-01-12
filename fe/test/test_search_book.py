import pytest
from fe.access.new_seller import register_new_seller
from fe.access.new_buyer import register_new_buyer
from fe.access import book
import uuid


class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.query = '感人'
        self.title = '美丽心灵'
        self.tag = '漫画'
        self.author = '张乐平'
        self.seller_id = "test_add_book_stock_level1_user_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_book_stock_level1_store_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB()
        self.books = book_db.get_book_id(0, 2)
        for bk in self.books:
            code = self.seller.add_book(self.store_id, 0, bk, 20)
            assert code == 200
        yield

    # 店铺内查询
    def test_error_store_id(self):
        code, pages, book_list = self.buyer.search_book_store(self.query, self.store_id+"_x")
        assert code != 200

    def test_ok_store(self):
        code, pages, book_list = self.buyer.search_book_store(self.query, self.store_id)
        assert code == 200

    def test_ok_all(self):
        code, pages, book_list = self.buyer.search_book_all(self.query)
        assert code == 200

    def test_error_store_id_title(self):
        code, pages, book_list = self.buyer.search_book_store_title(self.title, self.store_id+"_x")
        assert code != 200

    def test_ok_store_title(self):
        code, pages, book_list = self.buyer.search_book_store_title(self.title, self.store_id)
        assert code == 200

    def test_ok_all_title(self):
        code, pages, book_list = self.buyer.search_book_all_title(self.title)
        assert code == 200

    def test_error_store_id_tag(self):
        code, pages, book_list = self.buyer.search_book_store_tag(self.tag, self.store_id + "_x")
        assert code != 200

    def test_ok_store_tag(self):
        code, pages, book_list = self.buyer.search_book_store_tag(self.tag, self.store_id)
        assert code == 200

    def test_ok_all_tag(self):
        code, pages, book_list = self.buyer.search_book_all_tag(self.tag)
        assert code == 200

    def test_error_store_id_author(self):
        code, pages, book_list = self.buyer.search_book_store_author(self.author, self.store_id+"_x")
        assert code != 200

    def test_ok_store_author(self):
        code, pages, book_list = self.buyer.search_book_store_author(self.author, self.store_id)
        assert code == 200

    def test_ok_all_author(self):
        code, pages, book_list = self.buyer.search_book_all_author(self.author)
        assert code == 200