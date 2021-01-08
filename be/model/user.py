import jwt
import time
import logging
from be.model import error
from be.model import db_conn
import sqlalchemy
from init_db import ConnectDB
from init_db.ConnectDB import Session
# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }

U = ConnectDB.User
def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode('utf-8').decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            user_obj = U(user_id=user_id, password=password, balance=0, token=token, terminal=terminal)
            self.Session.add(user_obj)
            # self.Session.execute(
            #     "INSERT INTO user (user_id, password, balance, token, terminal) values (:user_id, :password, 0, :token, :terminal)",{"user_id":user_id,"password": password,"token":token,"terminal":terminal }
            #     )
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError:
            # 已存在user_id
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        row = self.Session.query(U.token).filter(U.user_id == user_id).first()
        if row is None:
            return error.error_authorization_fail()
        db_token = row[0]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        row = self.Session.query(U.password).filter(U.user_id == user_id).first()
        if row is None:
            # print('没有该用户')
            return error.error_authorization_fail()

        if password != row[0]:
            # print('密码错误')
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            print("tokenxxxxx")
            # 验证密码
            code, message = self.check_password(user_id, password)
            if code != 200:
                print('xxxxxxxxxxxxxxxxxxx')
                return code, message, ""
            # 生成token
            token = jwt_encode(user_id, terminal)
            row = self.Session.query(U).filter(U.user_id == user_id).first()
            if row is None:
                return error.error_authorization_fail() + ("", )
            row.token = token
            row.terminal = terminal
            self.Session.commit()
            row = self.Session.query(U).filter(U.user_id == user_id).first()
            print('token:', row.token)
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            row = self.Session.query(U).filter(U.user_id == user_id).first()
            if row is None:
                return error.error_authorization_fail() + ("",)
            row.token == dummy_token
            row.terminal == terminal
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            row = self.Session.query(U).filter(U.user_id == user_id)
            if row is not None:
                row.delete()
                self.Session.commit()
            else:
                return error.error_authorization_fail()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            row = self.Session.query(U).filter(U.user_id == user_id).first()
            if row is None:
                return error.error_authorization_fail()
            row.password = new_password
            row.token = token
            row.terminal = terminal
            self.Session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

