error_code = {
    401: "authorization fail.",
    511: "non exist user id {}",
    512: "exist user id {}",
    513: "non exist store id {}",
    514: "exist store id {}",
    515: "non exist book id {}",
    516: "exist book id {}",
    517: "stock level low, book id {}",
    518: "invalid order id {}",
    519: "not sufficient funds, order id {}",
    520: "already delivered or take delivery",
    521: "no payment to deliver",
    522: "can not receive book",
    523: "non exit relative book",
    524: "non invalid order state",
    525: "",
    526: "",
    527: "",
    528: "",
}


def error_non_exist_user_id(user_id):
    return 511, error_code[511].format(user_id)


def error_exist_user_id(user_id):
    return 512, error_code[512].format(user_id)


def error_non_exist_store_id(store_id):
    return 513, error_code[513].format(store_id)


def error_exist_store_id(store_id):
    return 514, error_code[514].format(store_id)


def error_non_exist_book_id(book_id):
    return 515, error_code[515].format(book_id)


def error_exist_book_id(book_id):
    return 516, error_code[516].format(book_id)


def error_stock_level_low(book_id):
    return 517, error_code[517].format(book_id)


def error_invalid_order_id(order_id):
    return 518, error_code[518].format(order_id)


def error_not_sufficient_funds(order_id):
    return 519, error_code[519].format(order_id)


def error_authorization_fail():
    return 401, error_code[401]


def error_and_message(code, message):
    return code, message


def error_already_delivered():
    return 520, error_code[520]


def error_no_payment_to_deliver():
    return 521, error_code[521]


def error_cannot_receive_book():
    return 522, error_code[522]


def error_no_book():
    return 523, error_code[523], 0, []


def error_invalid_order_state():
    return 523, error_code[524]
