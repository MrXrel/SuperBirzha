from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "KETUNREAL"  # Запилить конфиг-файл надо будет
login_manager = LoginManager(app)
login_manager.login_view = "get_user_authorization"
USERS = []

from server import models
from server import views
