from flask import Flask
from flask_login import LoginManager
from db import database
from parser import parser
import os

DATABASE = "db/superbirzha.db"
SECRET_KEY = "KETUNREAL"  # Запилить конфиг-файл надо будет
CURRENCIES = {
    "XAU": ["GLDRUB_TOM", "Золото"],
    "USD": ["USD000000TOD", "Доллар США"],
    "CNY": ["CNYRUB_TMS", "Китайский юань"],
    "EUR": ["EUR_RUB__TOM", "Eвро"],
}
token = "t.IEa99GPRoD0m0Z3MH_M2BUMIAVsqYMCpcmJhQFIKDw8rg3tk7CpENgicqyVpOMSTK1ubCt1ZB7SQCXTcEy0Dcw"


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "superbirzha.db")))

login_manager = LoginManager(app)
login_manager.login_message = ""
login_manager.login_view = "get_user_authorization"


dbase = database.Database()
parser_API = parser.CurrencyInfo(token)

from server import models
from server import views
