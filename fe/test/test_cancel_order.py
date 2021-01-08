import uuid
import pytest

from fe.access.book import Book
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook


class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_cancel_order_seller_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_order_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id

        self.total_price = 0
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        self.buy_book_info_list = self.gen_book.buy_book_info_list
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_non_exist_user_id(self):
        self.buyer_id = self.buyer_id + "_x"
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200

    def test_non_exist_order_id(self):
        self.order_id = self.order_id + "_x"
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200

    def test_ok(self):
        # print(self.order_id)
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200

    def test_already_delivered(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        self.gen_book.seller.delivery_book(self.seller_id, self.order_id)
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200
        self.buyer.receive_book(self.buyer_id, self.order_id)
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200

    def test_have_not_pay(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200



