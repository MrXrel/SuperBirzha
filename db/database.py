from sqlalchemy import *
from datetime import time, datetime


class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///superbirzha.db', isolation_level='AUTOCOMMIT')
        self.conn = self.engine.connect()
        self.metadata = MetaData()
        self.users = Table('Users', self.metadata,
                           Column('ID', Integer(), primary_key=True),
                           Column('email', String(200), nullable=False, unique=True),
                           Column('password', String(200), nullable=False),
                           Column('surname', String(200), nullable=False),
                           Column('name', String(200), nullable=False),
                           Column('balance', Float(), nullable=False, default=10000),
                           Column('time_to_note', Time(), default=time(hour=10, minute=0))
                           )
        self.user_keys = ('ID', 'email', 'password', 'surname', 'name', 'balance', 'time_to_note')
        self.operations = Table('Operations', self.metadata,
                                Column('ID', Integer(), primary_key=True),
                                Column('user_ID', ForeignKey('Users.ID')),
                                Column('currency_ID', ForeignKey('Currency.ID')),
                                Column('price', Float(), nullable=False),
                                Column('quantity', Float(), nullable=False),
                                Column('type_of_operation', String(10), nullable=False),
                                Column('time', DateTime(), default=datetime.now())
                                )
        self.operations_keys = ('ID', 'user_ID', 'currency_ID', 'price', 'quantity', 'type_of_operation', 'time')
        self.currency = Table('Currency', self.metadata,
                              Column('ID', Integer(), primary_key=True),
                              Column('currency_name', String(200), nullable=False, unique=True),
                              Column('price', Float(), nullable=False)
                              )
        self.metadata.create_all(self.engine)

    def create_user(self, email: str, password: str, surname: str, name: str) -> int:
        ins = insert(self.users).values(
            email=email,
            password=password,
            surname=surname,
            name=name
        )
        try:
            r = self.conn.execute(ins)
            return r.inserted_primary_key  # id добавленного пользователя
        except Exception:
            return 0  # 0 если добавить не получилось (уже есть такой email)

    def add_currency(self, price: float, name: str) -> int:
        ins = insert(self.currency).values(
            price=price,
            currency_name=name
        )
        try:
            r = self.conn.execute(ins)
            return r.inserted_primary_key  # id добавленной валюты
        except Exception:
            return 0  # 0 если добавить не получилось (уже есть такая валюта)

    def get_user_data_by_id(self, user_id: int) -> dict:
        s = select(self.users).where(
            self.users.c.ID == user_id
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}
        # словарь с полями 'ID', 'email', 'password', 'surname', 'name', 'balance', 'time_to_note'

    def get_user_data_by_email(self, email: str) -> dict:
        s = select(self.users).where(
            self.users.c.email == email
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}
        # словарь с полями 'ID', 'email', 'password', 'surname', 'name', 'balance', 'time_to_note'

    def get_operation_data_by_id(self, user_id: int) -> dict:
        s = select(self.operations).where(
            self.operations.c.ID == user_id
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.operations_keys, p)}

    def add_operation(self, user_id: int, currency_id: int,
                      type_of_operation: str,  # в type_of_operation передавать 'BUY' или 'SELL'
                      quantity: float,  # количество валюты
                      time_of_operation: datetime) -> int:
        price = self.conn.execute(select(self.currency.c.price).where(
            self.currency.c.ID == currency_id
        )).fetchall()[0][0]

        old_balance = self.conn.execute(select(self.users.c.balance).where(
            self.users.c.ID == user_id
        )).fetchall()[0][0]

        # вставка записи в Operations
        ins = insert(self.operations).values(
            user_ID=user_id,
            currency_ID=currency_id,
            price=price,
            quantity=quantity,
            type_of_operation=type_of_operation,
            time=time_of_operation
        )
        r = self.conn.execute(ins)
        # изменение баланса в Users
        k = 0
        if type_of_operation == 'SELL':
            k = 1
        elif type_of_operation == 'BUY':
            k = -1
        self.conn.execute(update(self.users).where(
            self.users.c.ID == user_id
        ).values(
            balance=old_balance + price * quantity * k
        ))
        return r.inserted_primary_key  # id операции

    def update_currency(self, new_values: dict):  # принимает словарь вида {название валюты: новая цена}
        for currency_name, price in new_values.items():
            self.conn.execute(update(self.currency).where(
                self.currency.c.currency_name == currency_name
            ).values(
                price=price
            ))

    def get_history_by_id(self, user_id: int, number_of_rows: int = -1, reverse: bool = False) -> list:
        if reverse:
            r = self.conn.execute(select(self.operations).where(
                self.operations.c.user_ID == user_id
            ))
        else:
            r = self.conn.execute(select(self.operations).where(
                self.operations.c.user_ID == user_id
            ).order_by(desc(self.operations.c.ID)))
        history = []
        if number_of_rows == -1:
            rows = r.fetchall()
        else:
            rows = r.fetchmany(number_of_rows)
        for row in rows:
            history.append({key: value for key, value in zip(self.operations_keys, row)})
        return history
        # список из словарей с полями 'ID', 'user_ID', 'currency_ID',
        # 'price' (цена в момент покупки), 'quantity' (количество валюты), 'type_of_operation', 'time'

    def get_briefcase_by_id(self, user_id) -> dict:
        all_operations = self.conn.execute(select(self.operations).where(
            self.operations.c.user_ID == user_id
        ))
        d = {key[0]: {'quantity': 0, 'purchase_amount': 0, 'selling_amount': 0, 'profitability': 0} for key in
             self.conn.execute(select(self.currency.c.currency_name)).fetchall()}

        for row in all_operations.fetchall():
            currency_name = self.conn.execute(select(self.currency.c.currency_name).where(
                self.currency.c.ID == row[2]
            )).fetchall()[0][0]
            d[currency_name]['quantity'] += row[4]
            d[currency_name]['purchase_amount'] += row[4] * row[3]

        for currency in d.keys():
            d[currency]['selling_amount'] = d[currency]['quantity'] * \
                                            self.conn.execute(select(self.currency.c.price).where(
                                                self.currency.c.currency_name == currency)
                                            ).fetchall()[0][0]
            if d[currency]['quantity'] > 0:
                d[currency]['profitability'] = (d[currency]['selling_amount'] - d[currency]['purchase_amount']) / \
                                               d[currency]['purchase_amount']

        return d
        # словарь вида {название валюты: словарь}
        # внутренний словарь имеет поля:
        # 'quantity' (количество валюты у пользователя),
        # 'purchase_amount' (общая сумма, за которую была куплена валюта),
        # 'selling_amount' (сумма, за которую сейчас можно продать всю имеющуюся валюту)
        # 'profitability' (доходность в десятичном виде)
        #
        # например количество купленных долларов можно получить как d['dollar']['quantity']
