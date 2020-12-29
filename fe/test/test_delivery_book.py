import pytest

from fe.access.new_seller import register_new_seller
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook
import uuid

class TestDeliveryBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_delivery_books_seller_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_delivery_books_buyer_id_{}".format(str(uuid.uuid1()))
        self.order_id = "test_delivery_books_order_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_delivery_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok

        code, _ = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        # book_db = book.BookDB()
        # self.books = book_db.get_book_info(0, 2)

        yield
        # do after test
    def test_ok(self):
        code = self.gen_book.seller.delivery_book(self.seller_id, self.order_id)
        assert code == 200