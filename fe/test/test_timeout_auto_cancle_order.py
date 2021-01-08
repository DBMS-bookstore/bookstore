import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid
import time


class TestAutoCancle:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, _ = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_non_exist_user_id(self):
        self.buyer_id = self.buyer_id + "_x"
        code, _ = self.buyer.query_order(self.buyer_id)
        # print(code)
        assert code != 200


    def test_auto_cancle(self):
        # 暂时设置超时60s未付款就取消订单
        time.sleep(100)
        # 然后去查询订单
        code, order_list = self.buyer.query_order(self.buyer_id)
        assert len(order_list) == 0
