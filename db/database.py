from sqlalchemy import *
from datetime import time, datetime


class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///superbirzha.db')
        self.conn = self.engine.connect()
        self.metadata = MetaData()
        self.users = Table('Users', self.metadata,
                           Column('ID', Integer(), primary_key=True),
                           Column('login', String(200), nullable=False, unique=True),
                           Column('password', String(200), nullable=False),
                           Column('surname', String(200), nullable=False),
                           Column('name', String(200), nullable=False),
                           Column('authorized', Boolean(), default=False),
                           Column('balance', Float(), nullable=False, default=10000),
                           Column('time_to_note', DateTime(), default=time(hour=10, minute=0))
                           )
        self.operations = Table('Operations', self.metadata,
                                Column('ID', Integer(), primary_key=True),
                                Column('user_ID', Integer(), nullable=False),
                                Column('currency_ID', Integer(), nullable=False),
                                Column('type_of_operation', String(10), nullable=False),
                                Column('time', DateTime(), default=datetime.now())
                                )
        self.currency = Table('Currency', self.metadata,
                              Column('ID', Integer(), primary_key=True),
                              Column('currency_name', String(200), nullable=False),
                              Column('price', Float(), nullable=False)
                              )
        self.metadata.create_all(self.engine)


db = Database()
