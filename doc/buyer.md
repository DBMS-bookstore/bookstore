## 买家下单

#### URL：
POST http://[address]/buyer/new_order

#### Request

##### Header:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

##### Body:
```json
{
  "user_id": "buyer_id",
  "store_id": "store_id",
  "books": [
    {
      "id": "1000067",
      "count": 1
    },
    {
      "id": "1000134",
      "count": 4
    }
  ]
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
store_id | string | 商铺ID | N
books | class | 书籍购买列表 | N

books数组：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
id | string | 书籍的ID | N
count | string | 购买数量 | N


#### Response

Status Code:

码 | 描述
--- | ---
200 | 下单成功
511 | 买家用户ID不存在
5XX | 商铺ID不存在
5XX | 购买的图书不存在
5XX | 商品库存不足

##### Body:
```json
{
  "order_id": "uuid"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
order_id | string | 订单号，只有返回200时才有效 | N


## 买家付款

#### URL：
POST http://[address]/buyer/payment

#### Request

##### Body:
```json
{
  "user_id": "buyer_id",
  "order_id": "order_id",
  "password": "password"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
order_id | string | 订单ID | N
password | string | 买家用户密码 | N 


#### Response

Status Code:

码 | 描述
--- | ---
200 | 付款成功
5XX | 账户余额不足
5XX | 无效参数
401 | 授权失败 


## 买家充值

#### URL：
POST http://[address]/buyer/add_funds

#### Request



##### Body:
```json
{
  "user_id": "user_id",
  "password": "password",
  "add_value": 10
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
password | string | 用户密码 | N
add_value | int | 充值金额，以分为单位 | N


Status Code:

码 | 描述
--- | ---
200 | 充值成功
401 | 授权失败
5XX | 无效参数

## 买家主动取消订单

#### URL：

POST http://[address]/buyer/cancel_order

#### Request

##### **Body：**

```
{
  "user_id": "user_id",
  “order_id": "order_id",
}
```

##### 属性说明：

| Key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 买家用户id | N          |
| order_id | string | 订单id     | N          |

Status Code:

| 码             | 描述             |
| -------------- | ---------------- |
| 200            | 取消订单成功     |
| 520            | 订单已发货或收货 |
| 5XX（除去520） | 无效参数         |

## 买家查看订单（粗粒度，只返回买家订单号列表）

#### URL：

POST http://[address]/buyer/query_order

#### Request

**Body：**

```
{
    "order_id": order_id
}
```

##### 属性说明：

| Key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| order_id | string | 订单id | N          |

Status Code:

| 码   | 描述         |
| ---- | ------------ |
| 200  | 查看订单成功 |
| 401  | 授权失败     |
| 5XX  | 无效参数     |

## 买家查看指定状态的订单（返回订单号列表，可以查询已取消的历史订单）

#### URL：

POST http://[address]/buyer/query_order_state

#### Request

**Body：**

```
{
    "order_id": order_id
    "para": para
}
```

##### 属性说明：

| Key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| order_id | string | 订单id | N          |
|   para   | integer| 查询参数 | N          |

Status Code:

| 码   | 描述         |
| ---- | ------------ |
| 200  | 查看订单成功 |
| 401  | 授权失败     |
| 5XX  | 无效参数     |

## 买家查看订单状态（根据订单号返回当前订单状态）

#### URL：

POST http://[address]/buyer/query_order_state

#### Request

**Body：**

```
{
    "order_id": order_id
}
```

##### 属性说明：

| Key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| order_id | string | 订单id | N          |

Status Code:

| 码   | 描述             |
| ---- | ---------------- |
| 200  | 查看订单状态成功 |
| 5XX  | 无效参数         |

## 买家查看订单状态（粗粒度，包括所有订单信息）

#### URL：

POST http://[address]/buyer/query_order_detail

#### Request

**Body：**

```
{
    "order_id": order_id
}
```

##### 属性说明：

| Key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| order_id | string | 订单id | N          |

Status Code:

| 码   | 描述             |
| ---- | ---------------- |
| 200  | 查看订单状态成功 |
| 5XX  | 无效参数         |

##### 查询包括的信息：

```
detail = {"order_id": row.order_id, "book_id": row.book_id, "count": row.count,
          "price": row.price, "state": cursor1.state, "store_id": cursor1.store_id,
          "create_time": cursor1.create_time}
```

## 买家确认收货

#### URL：

POST http://[address]/buyer/receive_book

#### Request

**Body：**

```
{
	"user_id": user_id
    "order_id": order_id
}
```

##### 属性说明：

| Key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 买家用户id | N          |
| order_id | string | 订单id     | N          |

Status Code:

| 码   | 描述                   |
| ---- | ---------------------- |
| 200  | 买家确认收货成功       |
| 522  | 还没发货，无法确认收货 |
| 5XX  | 无效参数               |