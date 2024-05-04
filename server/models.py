from flask_login import UserMixin
from server import USERS


class User:
    def __init__(self, user_id, email, password, surname, name, balance=5000):
        self.user_iid = user_id
        self.email = email
        self._password = password
        self.surname = surname
        self.name = name
        self._balance = balance


class UserLogin(UserMixin):
    def fromDB(self, user_id):
        self.__user = USERS[int(user_id)]
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user.user_iid)

    def get_name(self):
        return self.__user.name

    def get_surname(self):
        return self.__user.surname

    def get_balance(self):
        return self.__user._balance
