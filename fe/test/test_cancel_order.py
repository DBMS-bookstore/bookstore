import uuid
import pytest

from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook


class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_cancel_order_seller_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_order_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        # self.seller = register_new_seller(self.seller_id, self.seller_id)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        yield

    def test_non_exist_user_id(self):
        self.buyer_id = self.buyer_id + "_x"
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200

    # def test_non_exist_store_id(self):
    #     self.store_id = self.store_id + "_x"
    #     code = self.buyer.cancel_order(self.store_id)
    #     assert code != 200

    def test_non_exist_order_id(self):
        self.order_id = self.order_id + "_x"
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        # code = self.buyer.new_order(self.store_id)
        # ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        # assert ok
        # code = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code != 200

    def test_already_delivered(self):
        self.gen_book.seller.delivery_book(self.seller_id, self.order_id)
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200

    def test_ok(self):
        # ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        # assert ok
        # code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200
