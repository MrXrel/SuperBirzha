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
            return r.inserted_primary_key
        except Exception:
            return 0

    def add_currency(self, price: float, name: str) -> int:
        ins = insert(self.currency).values(
            price=price,
            currency_name=name
        )
        try:
            r = self.conn.execute(ins)
            return r.inserted_primary_key
        except Exception:
            return 0

    def print_all_users(self):  # для отладки
        s = select(self.users)
        rs = self.conn.execute(s)
        print("Users")
        for row in rs:
            print(row)

    def print_all_cur(self):  # для отладки
        s = select(self.currency)
        rs = self.conn.execute(s)
        print("Currency")
        for row in rs:
            print(row)

    def get_data_by_id(self, user_id: int) -> dict:
        s = select(self.users).where(
            self.users.c.ID == user_id
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}

    def get_data_by_email(self, email: str) -> dict:
        s = select(self.users).where(
            self.users.c.email == email
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}

    def add_operation(self, user_id: int, currency_id: int,
                      type_of_operation: str, quantity: float,
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
        return r.inserted_primary_key

    def update_currency(self, new_values: dict):
        for currency_name, price in new_values.items():
            self.conn.execute(update(self.currency).where(
                self.currency.c.currency_name == currency_name
            ).values(
                price=price
            ))
