from sqlalchemy import *
from datetime import time, datetime
import os


class Database:
    def __init__(self):
        self.engine = create_engine(
            "sqlite:///superbirzha.db", isolation_level="AUTOCOMMIT"
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
            Column("time_to_note", Time(), default=time(hour=10, minute=0)),
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
            Column("type_of_operation", String(10), nullable=False),
            Column("time", DateTime(), default=datetime.now()),
        )
        self.currency = Table(
            "Currency",
            self.metadata,
            Column("ID", Integer(), primary_key=True),
            Column("currency_name", String(200), nullable=False),
            Column("price", Float(), nullable=False),
        )
        self.metadata.create_all(self.engine)

    def create_user(self, email: str, password: str, surname: str, name: str) -> int:
        ins = insert(self.users).values(
            email=email, password=password, surname=surname, name=name
        )
        try:
            r = self.conn.execute(ins)
            return r.inserted_primary_key
        except Exception:
            return 0

    def print_all_users(self):  # для отладки
        s = select(self.users)
        rs = self.conn.execute(s)
        for row in rs:
            print(row)

    def get_balance_by_id(self, user_id: int) -> float:
        s = select(self.users.c.balance).where(self.users.c.ID == user_id)
        r = self.conn.execute(s)
        try:
            return r.fetchall()[0][0]
        except Exception:
            return 0

    def get_name_by_id(self, user_id: int) -> dict:
        s = select(self.users).where(self.users.c.ID == user_id)
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {"surname": p[3], "name": p[4]}

    def get_data_by_id(self, user_id: int) -> dict:
        s = select(self.users).where(self.users.c.ID == user_id)
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}

    def get_data_by_email(self, email: str) -> dict:
        s = select(self.users).where(self.users.c.email == email)
        r = self.conn.execute(s)
        p = r.fetchall()[0]
        return {key: value for key, value in zip(self.user_keys, p)}


if __name__ == "__main__":
    dbase = Database()
    dbase.print_all_users()
