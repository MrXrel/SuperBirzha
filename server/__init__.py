from flask import Flask
from flask_login import LoginManager
from db import database
import os

DATABASE = "/SuperBirzha/superbirzha.db"
SECRET_KEY = "KETUNREAL"  # Запилить конфиг-файл надо будет

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "superbirzha.db")))

login_manager = LoginManager(app)
login_manager.login_view = "get_user_authorization"


dbase = database.Database()


from server import models
from server import views
