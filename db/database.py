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
                           Column('balance', Float(), nullable=False, default=10000)
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
        self.currency_keys = ('ID', 'currency_name', 'price')
        self.tg_bot = Table('Notifier_bot', self.metadata,
                            Column('ID', ForeignKey('Users.ID'), primary_key=True),
                            Column('tg_id', Integer(), default=0),
                            Column('old_briefcase', Float(), nullable=False),
                            Column('new_briefcase', Float(), nullable=False),
                            Column('delta_to_note', Float(), nullable=False),
                            Column('time_to_note', Time(), default=time(hour=10, minute=0)),
                            Column('already_notified', Boolean(), default=False),
                            )
        self.briefcase = Table('Briefcase', self.metadata,
                               Column('ID', Integer(), primary_key=True),
                               Column('user_id', ForeignKey('Users.ID')),
                               Column('currency_id', ForeignKey('Currency.ID')),
                               Column('amount', Float(), default=0),
                               )
        self.list_of_currencies = ['dollar', 'euro', 'yuan', 'gold']
        self.metadata.create_all(self.engine)
        for i in self.list_of_currencies:
            self.add_currency(0, i)

    def create_user(self, email: str, password: str, surname: str, name: str) -> int:
        """
        Создание нового пользователя

        Parameters
        ----------
        email : str
        password : str
        surname : str
        name : str

        Returns
        -------
        int
            id добавленного пользователя
            0 если добавить не получилось (уже есть такой email)
        """

        ins_to_users = insert(self.users).values(
            email=email,
            password=password,
            surname=surname,
            name=name
        )
        try:
            r = self.conn.execute(ins_to_users)
            for i in range(1, 5):
                self.conn.execute(insert(self.briefcase).values(
                    user_id=r.inserted_primary_key[0],
                    currency_id=i
                ))
            return r.inserted_primary_key[0]
        except Exception:
            return 0

    def add_currency(self, price: float, name: str) -> int:
        """
        Добавление новой валюты

        Parameters
        ----------
        price: float
        name: str

        Returns
        -------
        int
            id добавленной валюты
            0 если добавить не получилось (уже есть такая валюта)
        """

        ins = insert(self.currency).values(
            price=price,
            currency_name=name
        )
        try:
            r = self.conn.execute(ins)
            return r.inserted_primary_key
        except Exception:
            return 0

    def get_user_data_by_id(self, user_id: int) -> dict:
        """
        Вывод всей информации о пользователе по его id

        Parameters
        ----------
        user_id: int

        Returns
        -------
        dict
            словарь с полями 'ID', 'email', 'password', 'surname', 'name', 'balance', 'time_to_note'
        """

        s = select(self.users).where(
            self.users.c.ID == user_id
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}

    def get_user_data_by_email(self, email: str) -> dict:
        """
        Вывод всей информации о пользователе по его email

        Parameters
        ----------
        email: str

        Returns
        -------
        dict
            словарь с полями 'ID', 'email', 'password', 'surname', 'name', 'balance', 'time_to_note'
        """

        s = select(self.users).where(
            self.users.c.email == email
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}

    def get_operation_data_by_id(self, operation_id: int) -> dict:
        """
        Вывод всей информации об операции по её id

        Parameters
        ----------
        operation_id: int

        Returns
        -------
        dict
            словарь с полями 'ID', 'user_ID', 'currency_ID', 'price', 'quantity', 'type_of_operation', 'time'
        """

        s = select(self.operations).where(
            self.operations.c.ID == operation_id
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.operations_keys, p)}

    def get_currency_data_by_id(self, currency_id: int) -> dict:
        """
        Вывод всей информации об операции по её id

        Parameters
        ----------
        currency_id: int

        Returns
        -------
        dict
            словарь с полями 'ID', 'currency_name', 'price'
        """

        s = select(self.currency).where(
            self.currency.c.ID == currency_id
        )
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.currency_keys, p)}

    def get_all_currencies(self):
        """
        Цены всех валют

        Returns
        -------
        dict
            ключи 'dollar', 'euro', 'yuan', 'gold'
            поля 'ID', 'price'
        """
        s = select(self.currency)
        rs = self.conn.execute(s)
        currencies = dict()
        for row in rs:
            currencies[row[1]] = {'ID': row[0], 'price': row[2]}
        return currencies

    def add_operation(self, user_id: int, currency_id: int,
                      type_of_operation: str,
                      quantity: float,
                      time_of_operation: datetime) -> int:
        """
        Выполнение операции с изменением баланса

        Parameters
        ----------
        user_id: int
        currency_id: int
        type_of_operation: str
            принимает значения 'BUY' или 'SELL'
        quantity: float
            количество валюты
        time_of_operation: datetime

        Returns
        -------
        int
            id выполненной операции
        """

        price = self.conn.execute(select(self.currency.c.price).where(
            self.currency.c.ID == currency_id
        )).fetchall()[0][0]

        old_balance = self.conn.execute(select(self.users.c.balance).where(
            self.users.c.ID == user_id
        )).fetchall()[0][0]

        old_amount = self.conn.execute(select(
            self.briefcase.c.amount).where(
            self.briefcase.c.user_id == user_id,
            self.briefcase.c.currency_id == currency_id
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

        # изменение количества в Briefcase
        self.conn.execute(update(self.briefcase).where(
            self.briefcase.c.user_id == user_id,
            self.briefcase.c.currency_id == currency_id
        ).values(
            amount=old_amount + quantity * k * -1
        ))
        return r.inserted_primary_key  # id операции

    def change_balance(self, user_id: int, quantity: float,
                       type_of_operation: str, time_of_operation: datetime) -> int:
        """
        Пополнение баланса или вывод средств

        Parameters
        ----------
        user_id: int
        type_of_operation: str
            принимает значения 'DEPOSIT' (пополнение) или 'WITHDRAW' (вывод)
        quantity: float
            количество рублей
        time_of_operation: datetime

        Returns
        -------
        int
            id выполненной операции
        """
        old_balance = self.conn.execute(select(self.users.c.balance).where(
            self.users.c.ID == user_id
        )).fetchall()[0][0]

        ins = insert(self.operations).values(
            user_ID=user_id,
            currency_ID=0,
            price=1,
            quantity=quantity,
            type_of_operation=type_of_operation,
            time=time_of_operation
        )

        r = self.conn.execute(ins)
        # изменение баланса в Users
        k = 0
        if type_of_operation == 'DEPOSIT':
            k = 1
        elif type_of_operation == 'WITHDRAW':
            k = -1
        self.conn.execute(update(self.users).where(
            self.users.c.ID == user_id
        ).values(
            balance=old_balance + quantity * k
        ))
        return r.inserted_primary_key

    def update_currency(self, new_values: dict):
        """
        Обновляет цены всех валют

        Parameters
        ----------
        new_values: dict
            словарь вида {название валюты: новая цена}
        """

        for currency_name, price in new_values.items():
            self.conn.execute(update(self.currency).where(
                self.currency.c.currency_name == currency_name
            ).values(
                price=price
            ))

    def get_history_by_id(self, user_id: int, number_of_rows: int = -1, reverse: bool = False,
                          type_of_operation: str = 'ALL') -> list:
        """
        Получение истории операций по id пользователя

        Parameters
        ----------
        user_id: int
        number_of_rows: int
            -1 - получение всех строк
        reverse: bool
            False - последние N операций
            True - первые N операций
        type_of_operation: str
            'ALL' - все
            'SELL' - продажа
            'BUY' - покупка
            'DEPOSIT' - пополнение баланса
            'WITHDRAW' - вывод средств

        Returns
        -------
        list
            список из словарей с полями 'ID', 'user_ID', 'currency_ID',
            'price' (цена в момент покупки), 'quantity' (количество валюты), 'type_of_operation', 'time'
        """
        if type_of_operation == 'ALL':
            if reverse:

                r = self.conn.execute(select(self.operations).where(
                    self.operations.c.user_ID == user_id
                ))
            else:
                r = self.conn.execute(select(self.operations).where(
                    self.operations.c.user_ID == user_id
                ).order_by(desc(self.operations.c.ID)))
        else:
            if reverse:

                r = self.conn.execute(select(self.operations).where(
                    self.operations.c.user_ID == user_id,
                    self.operations.c.type_of_operation == type_of_operation
                ))
            else:
                r = self.conn.execute(select(self.operations).where(
                    self.operations.c.user_ID == user_id,
                    self.operations.c.type_of_operation == type_of_operation
                ).order_by(desc(self.operations.c.ID)))
        history = []
        if number_of_rows == -1:
            rows = r.fetchall()
        else:
            rows = r.fetchmany(number_of_rows)
        for row in rows:
            history.append({key: value for key, value in zip(self.operations_keys, row)})
        return history

    def get_briefcase_by_id(self, user_id: int) -> dict:
        """
        Получение данных о портфеле пользователя по id

        Parameters
        ----------
        user_id: int

        Returns
        -------
        dict
            словарь вида {название валюты: словарь}

            внутренний словарь имеет поля:
            'quantity' (количество валюты у пользователя),
            'purchase_amount' (общая сумма, за которую была куплена валюта),
            'selling_amount' (сумма, за которую сейчас можно продать всю имеющуюся валюту)
            'profitability' (доходность в десятичном виде)

            например количество долларов у пользователя можно получить как d['dollar']['quantity']
        """

        all_operations = self.conn.execute(select(self.operations).where(
            self.operations.c.user_ID == user_id
        ))
        d = {self.list_of_currencies[key]: {
            'quantity': self.conn.execute(select(
                self.briefcase.c.amount).where(
                self.briefcase.c.user_id == user_id,
                self.briefcase.c.currency_id == key + 1
            )).fetchall()[0][0],
            'purchase_amount': 0,
            'selling_amount': 0,
            'profitability': 0}
            for key in range(4)}

        for row in all_operations.fetchall():
            currency_name = self.conn.execute(select(self.currency.c.currency_name).where(
                self.currency.c.ID == row[2]
            )).fetchall()[0][0]
            if row[5] == 'BUY':
                d[currency_name]['purchase_amount'] += row[4] * row[3]
            elif row[5] == 'SELL':
                d[currency_name]['selling_amount'] += row[4] * row[3]

        for currency in d.keys():
            d[currency]['selling_amount'] += d[currency]['quantity'] * \
                                             self.conn.execute(select(self.currency.c.price).where(
                                                 self.currency.c.currency_name == currency)
                                             ).fetchall()[0][0]
            if d[currency]['quantity'] > 0:
                d[currency]['profitability'] = (d[currency]['selling_amount'] - d[currency]['purchase_amount']) / \
                                               abs(d[currency]['purchase_amount'])

        return d
