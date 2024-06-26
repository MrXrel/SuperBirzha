from sqlalchemy import *
from datetime import time, datetime
from sqlalchemy.exc import DBAPIError


class Database:
    def __init__(self):
        self.engine = create_engine(
            "sqlite:///db/superbirzha.db", isolation_level="AUTOCOMMIT"
        )
        self.conn = self.engine.connect()
        self.metadata = MetaData()
        self.users = Table(
            "Users",
            self.metadata,
            Column("ID", Integer(), primary_key=True),
            Column("email", String(200), nullable=False, unique=True),
            Column("password", String(200), nullable=False),
            Column("surname", String(200), nullable=False),
            Column("name", String(200), nullable=False),
            Column("balance", Float(), nullable=False, default=10000),
        )
        self.user_keys = (
            "ID",
            "email",
            "password",
            "surname",
            "name",
            "balance",
            "time_to_note",
        )
        self.operations = Table(
            "Operations",
            self.metadata,
            Column("ID", Integer(), primary_key=True),
            Column("user_ID", ForeignKey("Users.ID")),
            Column("currency_ID", ForeignKey("Currency.ID")),
            Column("price", Float(), nullable=False),
            Column("quantity", Float(), nullable=False),
            Column("type_of_operation", String(10), nullable=False),
            Column("time", DateTime(), default=datetime.now()),
        )
        self.operations_keys = (
            "ID",
            "user_ID",
            "currency_ID",
            "price",
            "quantity",
            "type_of_operation",
            "time",
        )
        self.currency = Table(
            "Currency",
            self.metadata,
            Column("ID", Integer(), primary_key=True),
            Column("currency_name", String(200), nullable=False, unique=True),
            Column("price", Float(), nullable=False),
        )
        self.currency_keys = ("ID", "currency_name", "price")
        self.tg_bot = Table(
            "Notifier_bot",
            self.metadata,
            Column("ID", ForeignKey("Users.ID"), primary_key=True),
            Column("name", String(200), nullable=False),
            Column("tg_id", Integer(), default=0),
            Column("old_briefcase", Float(), default=0),
            Column("new_briefcase", Float(), default=0),
            Column("delta_to_note", Float(), default=100),
            Column("time_to_note", Time(), default=time(hour=10, minute=0)),
        )
        self.tg_bot_keys = (
            "ID",
            "name",
            "tg_id",
            "old_briefcase",
            "new_briefcase",
            "delta_to_note",
            "time_to_note",
            "already_notified",
        )
        self.briefcase = Table(
            "Briefcase",
            self.metadata,
            Column("ID", Integer(), primary_key=True),
            Column("user_id", ForeignKey("Users.ID")),
            Column("currency_id", ForeignKey("Currency.ID")),
            Column("quantity", Float(), default=0),
        )
        self.list_of_currencies = ["USD", "EUR", "CNY", "XAU"]
        self.metadata.create_all(self.engine)
        self.lastID = len(self.conn.execute(select(self.users)).fetchall())
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
            email=email, password=password, surname=surname, name=name
        )
        try:
            r = self.conn.execute(ins_to_users)
            for i in range(1, 5):
                self.conn.execute(
                    insert(self.briefcase).values(
                        user_id=r.inserted_primary_key[0], currency_id=i
                    )
                )
            self.conn.execute(
                insert(self.tg_bot).values(ID=r.inserted_primary_key[0], name=name)
            )
            self.lastID = r.inserted_primary_key[0]
        except DBAPIError:
            return 0
        return r.inserted_primary_key[0]

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

        ins = insert(self.currency).values(price=price, currency_name=name)
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
        try:
            s = select(self.users).where(self.users.c.ID == user_id)
            r = self.conn.execute(s)
            p = r.fetchall()[0]
            return {key: value for key, value in zip(self.user_keys, p)}
        except Exception:
            return 0

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
        try:
            s = select(self.users).where(self.users.c.email == email)
            r = self.conn.execute(s)
            p = r.fetchall()[0]
            return {key: value for key, value in zip(self.user_keys, p)}
        except Exception:
            return 0

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

        s = select(self.operations).where(self.operations.c.ID == operation_id)
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

        s = select(self.currency).where(self.currency.c.ID == currency_id)
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
            currencies[row[1]] = {"ID": row[0], "price": row[2]}
        return currencies

    def add_operation(
        self,
        user_id: int,
        currency_id: int,
        type_of_operation: str,
        quantity: float,
        time_of_operation: datetime,
    ) -> int:
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
            0, если недостаточно средств
        """

        price = self.conn.execute(
            select(self.currency.c.price).where(self.currency.c.ID == currency_id)
        ).fetchall()[0][0]

        # изменение баланса в Users
        old_balance = self.conn.execute(
            select(self.users.c.balance).where(self.users.c.ID == user_id)
        ).fetchall()[0][0]

        # изменение количества в Briefcase
        old_quantity = self.conn.execute(
            select(self.briefcase.c.quantity).where(
                self.briefcase.c.user_id == user_id,
                self.briefcase.c.currency_id == currency_id,
            )
        ).fetchall()[0][0]

        k = 0
        if type_of_operation == "SELL":
            print(old_quantity - quantity)
            if old_quantity - quantity < 0:
                return 0  # недостаточно валюты
            k = 1
        elif type_of_operation == "BUY":
            if old_balance < price * quantity:
                return 0  # недостаточно средств
            k = -1

        # вставка записи в Operations
        ins = insert(self.operations).values(
            user_ID=user_id,
            currency_ID=currency_id,
            price=price,
            quantity=quantity,
            type_of_operation=type_of_operation,
            time=time_of_operation,
        )

        r = self.conn.execute(ins)

        self.conn.execute(
            update(self.users)
            .where(self.users.c.ID == user_id)
            .values(balance=old_balance + price * quantity * k)
        )

        self.conn.execute(
            update(self.briefcase)
            .where(
                self.briefcase.c.user_id == user_id,
                self.briefcase.c.currency_id == currency_id,
            )
            .values(quantity=old_quantity + quantity * k * -1)
        )

        # изменение портфеля в Notifier_bot
        old_new_briefcase = self.conn.execute(
            select(self.tg_bot.c.new_briefcase).where(self.tg_bot.c.ID == user_id)
        ).fetchall()[0][0]

        self.conn.execute(
            update(self.tg_bot)
            .where(self.tg_bot.c.ID == user_id)
            .values(new_briefcase=old_new_briefcase + quantity * k * -1 * price)
        )
        return r.inserted_primary_key  # id операции

    def change_balance(
        self,
        user_id: int,
        quantity: float,
        type_of_operation: str,
        time_of_operation: datetime,
    ) -> int:
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
            0, если недостаточно средств
        """
        old_balance = self.conn.execute(
            select(self.users.c.balance).where(self.users.c.ID == user_id)
        ).fetchall()[0][0]

        ins = insert(self.operations).values(
            user_ID=user_id,
            currency_ID=0,
            price=1,
            quantity=quantity,
            type_of_operation=type_of_operation,
            time=time_of_operation,
        )

        r = self.conn.execute(ins)
        # изменение баланса в Users
        k = 0
        if type_of_operation == "DEPOSIT":
            k = 1
        elif type_of_operation == "WITHDRAW":
            if old_balance < quantity:
                return 0  # недостаточно средств
            k = -1
        self.conn.execute(
            update(self.users)
            .where(self.users.c.ID == user_id)
            .values(balance=old_balance + quantity * k)
        )
        return r.inserted_primary_key

    def update_currency(self, new_values: dict):
        """
        Обновляет цены всех валют, и пересчитывает все портфели для tg бота

        Parameters
        ----------
        new_values: dict
            словарь вида {название валюты: новая цена}
        """

        for currency_name, price in new_values.items():
            self.conn.execute(
                update(self.currency)
                .where(self.currency.c.currency_name == currency_name)
                .values(price=price)
            )

        all_briefcases = self.conn.execute(select(self.briefcase))
        new_new_briefcases = {key: 0 for key in range(0, self.lastID)}
        for row in all_briefcases:
            if self.list_of_currencies[row[2] - 1] in new_values.keys():
                new_new_briefcases[row[1] - 1] += (
                    new_values[self.list_of_currencies[row[2] - 1]] * row[3]
                )

        for user_id, new_new_briefcase in new_new_briefcases.items():
            self.conn.execute(
                update(self.tg_bot)
                .where(self.tg_bot.c.ID == user_id + 1)
                .values(new_briefcase=new_new_briefcase)
            )

    def get_history_by_id(
        self,
        user_id: int,
        number_of_rows: int = -1,
        reverse: bool = False,
        type_of_operation: str = "ALL",
    ) -> list:
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
        if type_of_operation == "ALL":
            if reverse:

                r = self.conn.execute(
                    select(self.operations).where(self.operations.c.user_ID == user_id)
                )
            else:
                r = self.conn.execute(
                    select(self.operations)
                    .where(self.operations.c.user_ID == user_id)
                    .order_by(desc(self.operations.c.ID))
                )
        else:
            if reverse:

                r = self.conn.execute(
                    select(self.operations).where(
                        self.operations.c.user_ID == user_id,
                        self.operations.c.type_of_operation == type_of_operation,
                    )
                )
            else:
                r = self.conn.execute(
                    select(self.operations)
                    .where(
                        self.operations.c.user_ID == user_id,
                        self.operations.c.type_of_operation == type_of_operation,
                    )
                    .order_by(desc(self.operations.c.ID))
                )
        history = []
        if number_of_rows == -1:
            rows = r.fetchall()
        else:
            rows = r.fetchmany(number_of_rows)
        for row in rows:
            history.append(
                {key: value for key, value in zip(self.operations_keys, row)}
            )
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
            'selling_amount' (сумма, за которую сейчас можно продать всю имеющуюся валюту, + уже проданная)
            'profitability' (доходность в десятичном виде)

            например количество долларов у пользователя можно получить как d['dollar']['quantity']
        """

        all_operations = self.conn.execute(
            select(self.operations).where(self.operations.c.user_ID == user_id)
        )
        d = {
            self.list_of_currencies[key]: {
                "quantity": self.conn.execute(
                    select(self.briefcase.c.quantity).where(
                        self.briefcase.c.user_id == user_id,
                        self.briefcase.c.currency_id == key + 1,
                    )
                ).fetchall()[0][0],
                "purchase_amount": 0,
                "selling_amount": 0,
                "profitability": 0,
            }
            for key in range(4)
        }

        for row in all_operations.fetchall():
            try:
                currency_name = self.conn.execute(
                    select(self.currency.c.currency_name).where(
                        self.currency.c.ID == row[2]
                    )
                ).fetchall()[0][0]
            except Exception:
                pass
            if row[5] == "BUY":
                d[currency_name]["purchase_amount"] += row[4] * row[3]
            elif row[5] == "SELL":
                d[currency_name]["selling_amount"] += row[4] * row[3]

        for currency in d.keys():
            d[currency]["selling_amount"] += (
                d[currency]["quantity"]
                * self.conn.execute(
                    select(self.currency.c.price).where(
                        self.currency.c.currency_name == currency
                    )
                ).fetchall()[0][0]
            )
            if d[currency]["quantity"] > 0:
                d[currency]["profitability"] = (
                    d[currency]["selling_amount"] - d[currency]["purchase_amount"]
                ) / abs(d[currency]["purchase_amount"])

        return d

    # функции для tg бота

    def get_all_user_for_tg_bot(self):
        """
        Получение данных для всех пользователей

        Returns
        -------
        dict
            ключ user_id
            поля 'ID', 'price'
        """
        s = select(self.tg_bot)
        rs = self.conn.execute(s)
        users = dict()
        for row in rs:
            users[row[0]] = {key: value for key, value in zip(self.tg_bot_keys, row)}
        return users

    def update_tg_id(self, user_id: int, new_tg_id: int):
        """
        Обновление tg id

        Parameters
        ----------
        user_id: int
        new_tg_id: int
        """
        self.conn.execute(
            update(self.tg_bot)
            .where(self.tg_bot.c.ID == user_id)
            .values(tg_id=new_tg_id)
        )

    def update_time_to_note(self, user_id: int, new_time: time):
        """
        Обновление времени оповещения

        Parameters
        ----------
        user_id: int
        new_time: time
        """
        self.conn.execute(
            update(self.tg_bot)
            .where(self.tg_bot.c.ID == user_id)
            .values(time_to_note=new_time)
        )

    def update_delta_to_note(self, user_id: int, new_delta: float):
        """
        Обновление величины изменения для оповещения

        Parameters
        ----------
        user_id: int
        new_delta: float
        """
        self.conn.execute(
            update(self.tg_bot)
            .where(self.tg_bot.c.ID == user_id)
            .values(delta_to_note=new_delta)
        )

    def update_old_briefcase_by_id(self, user_id: int):
        """
        Приравнивает old_briefcase к new_briefcase

        Parameters
        ----------
        user_id: int
        """
        new_old_briefcase = self.conn.execute(
            select(self.tg_bot.c.new_briefcase).where(self.tg_bot.c.ID == user_id)
        ).fetchall()[0][0]
        self.conn.execute(
            update(self.tg_bot)
            .where(self.tg_bot.c.ID == user_id)
            .values(old_briefcase=new_old_briefcase)
        )


if __name__ == "__main__":
    dbase = Database()
    print(dbase.create_user("d@mai.com", "123", "ово", ",бобо"))
