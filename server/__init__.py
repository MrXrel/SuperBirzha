from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "KETUNREAL"  # Запилить конфиг-файл надо будет

USERS = []

from server import models
from server import views
from server import forms
