class User:
    def __init__(self, user_id, email, password, surname, name, balance=10000):
        self.user_id = user_id
        self.email = email
        self._password = password
        self.surname = surname
        self.name = name
        self._balance = balance
        self._is_authorized = False

    def authorized(self):
        self._is_authorized = True
