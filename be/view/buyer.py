from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    # print("route" + order_id)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code


@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message = b.cancel_order(user_id, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/query_order", methods=["GET", "POST"])
def query_order():
    user_id = request.json.get("user_id")
    b = Buyer()
    code, message, order_list = b.query_order(user_id)
    # print(order_list)
    return jsonify({"message": message, 'order_list': order_list}), code


@bp_buyer.route("/query_order_para", methods=["GET", "POST"])
def query_order_para():
    user_id = request.json.get("user_id")
    para = request.json.get("para")
    b = Buyer()
    code, message, order_list = b.query_order_para(user_id, para)
    # print(order_list)
    return jsonify({"message": message, 'order_list': order_list}), code


@bp_buyer.route("/query_order_state", methods=["GET", "POST"])
def query_order_state():
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message, order_state = b.query_order_state(order_id)
    return jsonify({"message": message, 'order_state': order_state}), code


@bp_buyer.route("/query_detail_order", methods=["GET", "POST"])
def query_detail_order():
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message, order_detail_list = b.query_detail_order(order_id)
    return jsonify({"message": message, 'order_detail_list': order_detail_list}), code


@bp_buyer.route("/receive_book", methods=["POST"])
def receive_book():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")

    b = Buyer()
    code, message = b.receive_book(user_id, order_id)

    return jsonify({"message": message}), code


@bp_buyer.route("/search_book_all", methods=["POST", "GET"])
def search_book_all():
    query: str = request.json.get("query")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_all(query, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code


@bp_buyer.route("/search_book_store", methods=["POST", "GET"])
def search_book_store():
    query: str = request.json.get("query")
    store_id: str = request.json.get("store_id")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_store(query, store_id, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code


@bp_buyer.route("/search_book_all_author", methods=["POST", "GET"])
def search_book_all_author():
    author: str = request.json.get("author")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_all_author(author, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code


@bp_buyer.route("/search_book_store_author", methods=["POST", "GET"])
def search_book_store_author():
    author: str = request.json.get("author")
    store_id: str = request.json.get("store_id")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_store_author(author, store_id, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code


@bp_buyer.route("/search_book_all_tag", methods=["POST", "GET"])
def search_book_all_tag():
    tag: str = request.json.get("tag")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_all_tag(tag, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code


@bp_buyer.route("/search_book_store_tag", methods=["POST", "GET"])
def search_book_store_tag():
    tag: str = request.json.get("tag")
    store_id: str = request.json.get("store_id")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_store_tag(tag, store_id, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code


@bp_buyer.route("/search_book_all_title", methods=["POST", "GET"])
def search_book_all_title():
    title: str = request.json.get("title")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_all_title(title, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code


@bp_buyer.route("/search_book_store_title", methods=["POST", "GET"])
def search_book_store_title():
    title: str = request.json.get("title")
    store_id: str = request.json.get("store_id")
    first: int = request.json.get("first")
    b = Buyer()
    code, message, pages, book_list = b.search_book_store_title(title, store_id, first)
    return jsonify({"message": message, "pages": pages, "book_list": book_list}), code
