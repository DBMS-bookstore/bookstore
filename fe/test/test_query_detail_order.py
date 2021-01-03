import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestDetailQueryOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_detail_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_detail_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_detail_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        yield

    def test_non_exist_order_id(self):
        self.order_id = self.order_id + "_x"
        # self.order_id = "test_new_order_detail_order_id_{}".format(str(uuid.uuid1()))
        code, _ = self.buyer.query_detail_order(self.order_id)
        assert code != 200

    def test_ok(self):
        code, _ = self.buyer.query_detail_order(self.order_id)
        assert code == 200
