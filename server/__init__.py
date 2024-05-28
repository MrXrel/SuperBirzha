from flask import Flask
from flask_login import LoginManager
from db import database
from parser import parser
import os
from server.config import (
    DATABASE,
    SECRET_KEY,
    CURRENCIES,
    TOKEN,
    METAL_KEY,
    EXCHANGE_RATE_KEY,
)

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "superbirzha.db")))

login_manager = LoginManager(app)
login_manager.login_message = ""
login_manager.login_view = "get_user_authorization"


dbase = database.Database()
parser_API = parser.CurrencyInfo(TOKEN, METAL_KEY, EXCHANGE_RATE_KEY)

from server import models
from server import views
