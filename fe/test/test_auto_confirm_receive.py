import pytest

from fe.access.book import Book
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid
import time

from init_db.ConnectDB import New_order


class TestAutoReceive:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.total_price = 0
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        self.buy_book_info_list = self.gen_book.buy_book_info_list
        for item in self.buy_book_info_list:
            # book: Book = item[0]
            price = item[2]
            num = item[1]
            if price is None:
                continue
            else:
                self.total_price = self.total_price + price * num
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_auto_receive(self):
        # 暂时设置超时60s未付款就取消订单
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        self.gen_book.seller.delivery_book(self.seller_id, self.order_id)
        assert code == 200
        # self.buyer.receive_book(self.buyer_id, self.order_id)
        # assert code == 200
        time.sleep(70)
        # 然后去查询订单,订单状态为已收货
        code, order_state = self.buyer.query_order_state(self.order_id)
        assert order_state == 3
