from server import app, dbase, CURRENCIES, parser_API
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Response,
    flash,
    get_flashed_messages,
)
from server import models, login_manager
from .forms.Registration import RegistrationForm
from .forms.Login import LoginForm
from .forms.Button import BuySellButton
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json


@login_manager.user_loader
def load_user(user_id):
    return models.UserLogin().fromDB(user_id, dbase)


@app.get("/currency/<currency_id>")
def get_currency(currency_id):
    form = BuySellButton()
    low_price = parser_API.get_history_of_current_currency_by_ticker(
        CURRENCIES[currency_id][0],
        datetime.utcnow() - timedelta(hours=8),
        datetime.utcnow(),
    )[0]["low"]
    high_price = parser_API.get_history_of_current_currency_by_ticker(
        CURRENCIES[currency_id][0],
        datetime.utcnow() - timedelta(hours=8),
        datetime.utcnow(),
    )[0]["high"]
    data = models.Currency(
        currency_id, CURRENCIES[currency_id][1], high_price, low_price
    )
    with open("server/templates/about_currencies.json", "r") as js:
        json_dump = json.load(js)
        about = json_dump[currency_id]
    return render_template("pettern_currencies.html", curr=data, about=about, form=form)


# Покупка/продажа валюты
@app.post("/currency/<currency_id>")
@login_required
def post_buy_currency(currency_id):
    data = {}

    for cuur in CURRENCIES:
        price = parser_API.get_history_of_current_currency_by_ticker(
            CURRENCIES[cuur][0],
            datetime.utcnow() - timedelta(hours=6),
            datetime.utcnow(),
        )[0]["high"]
        data[cuur] = price
    dbase.update_currency(data)
    if "submit_buy" in request.form:
        dbase.add_operation(current_user.get_id(), 1, "BUY", 1, datetime.utcnow())
    else:
        dbase.add_operation(current_user.get_id(), 1, "SELL", 1, datetime.utcnow())
    return redirect(url_for("get_currency", currency_id=currency_id))


# Страница со всеми валютами
@app.get("/currencies")
def get_currencies():
    data = []
    for currency in CURRENCIES:
        low_price = parser_API.get_history_of_current_currency_by_ticker(
            CURRENCIES[currency][0],
            datetime.utcnow() - timedelta(hours=6),
            datetime.utcnow(),
        )[0]["low"]
        high_price = parser_API.get_history_of_current_currency_by_ticker(
            CURRENCIES[currency][0],
            datetime.utcnow() - timedelta(hours=6),
            datetime.utcnow(),
        )[0]["high"]
        data.append(
            models.Currency(currency, CURRENCIES[currency][1], high_price, low_price)
        )

    return render_template("currencies.html", curruncies=data)


# Начальная страница
@app.get("/")
def get_about_us():
    return render_template("About_us.html")


# Личный кабинет
@app.route("/private-office")
@login_required
def get_private_office():
    return render_template("personal_account.html", user=current_user)


# Страница регистрации
@app.route("/registration", methods=["GET", "POST"])
def user_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        if check_password_hash(hash, form.password_confirm.data):
            data = dbase.create_user(
                form.email.data, hash, form.surname.data, form.name.data
            )
            if data == 0:
                flash("Пользователь с такой почтой уже существует.")
                return redirect(url_for("user_registration"))
            return redirect(url_for("get_user_authorization"), 301)
    return render_template("sign_up.html", form=form)


# Get запрос на авторизацию
@app.get("/authorization")
def get_user_authorization():
    form = LoginForm()
    return render_template("sign_in.html", form=form)


# Post запрос на авторизацию
@app.post("/authorization")
def post_user_authorization():
    email = request.form["email"]
    psw = request.form["password"]
    user = dbase.get_user_data_by_email(email)
    if check_password_hash(user["password"], psw):
        userlogin = models.UserLogin().create(user)
        login_user(userlogin)
        return redirect(url_for("get_private_office"))
    else:
        flash("Неверный пароль или логин")
        return redirect(url_for("get_user_authorization"))


# Выход из профиля
@app.route("/logout")
@login_required
def user_logout():
    logout_user()
    return redirect(url_for("get_user_authorization"))
