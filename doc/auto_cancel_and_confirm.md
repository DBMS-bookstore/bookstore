## 系统自动取消订单

在be.model.serve函数的delete_order中不断轮询，遍历所有订单，判断下单时间是否超时，若超时且状态为未付款，则增加库存，并且从new_order和new_order_detail中删除和该订单有关信息。



## 系统自动确认收货

在be.model.serve函数的delete_order中不断轮询，遍历所有订单，判断发货时间是否超过一定时限，如果超过且状态为发货，则将状态改为3（收货），将订单总金额加到卖家的balance中。



```
def delete_order(seconds):
    # Session = store.get_db_conn()
    cursor = Session.query(New_order).all()
    print('cur')
    print(cursor)
    if cursor is not None:
        for row in cursor:
            print('row')
            print(row)
            order_id = row.order_id
            store_id = row.store_id
            state = row.state
            create_time = row.create_time
            delivery_time = row.delivery_time
            # 若超时且状态为未付款
            if time.time()-create_time >= 600 and state == 0:
                # 增加库存
                cur = Session.query(New_order_detail.book_id, New_order_detail.count).filter(New_order_detail.order_id == order_id)
                for x in cur:
                    book_id = x[0]
                    count = x[1]
                    stock_level = Session.query(Store.stock_level).filter(Store.store_id == store_id, Store.book_id == book_id).first()[0]
                    stock_level += count
                Session.query(New_order).filter(New_order.order_id == order_id).delete()
                Session.query(New_order_detail).filter(New_order_detail.order_id == order_id).delete()
            if time.time() - delivery_time >= 60 and state == 2:
                r = Session.query(New_order).filter(New_order.order_id == order_id).first()
                r.state = 3
                cursor1 = Session.query(New_order_detail.book_id, New_order_detail.count,
                                        New_order_detail.price).filter(New_order_detail.order_id == order_id).all()
                total_price = 0
                for row1 in cursor1:
                    count = row1[1]
                    price = row1[2]
                    total_price = total_price + price * count
                row3 = Session.query(User_store).filter(User_store.store_id == store_id).first()
                if row3 is None:
                    return error.error_non_exist_store_id(store_id)

                seller_id = row3.user_id
                row5 = Session.query(User).filter(User.user_id == seller_id).first()
                if row5 is None:
                    return error.error_non_exist_user_id(seller_id)
                row5.balance += total_price
        Session.commit()
    t = Timer(seconds, delete_order, (seconds,))
    t.start()
```