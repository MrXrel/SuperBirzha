from flask_login import UserMixin


class User:
    def __init__(self, user_id, email, password, surname, name, balance=5000):
        self.user_iid = user_id
        self.email = email
        self._password = password
        self.surname = surname
        self.name = name
        self._balance = balance


class UserLogin(UserMixin):
    def fromDB(self, user_id, dbase):
        print(user_id)
        self.__user = dbase.get_user_data_by_id(user_id)
        if self.__user == 0:
            self.__user = dbase.get_user_data_by_id(1)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user["ID"])

    def get_name(self):
        return self.__user["name"]

    def get_surname(self):
        return self.__user["surname"]

    def get_balance(self):
        return self.__user["balance"]


class Currency:
    def __init__(self, id, ru_name, buy_price, sell_price):
        self.id = id
        self.ru_name = ru_name
        self.buy_price = buy_price
        self.sell_price = sell_price
