from server import app, dbase, CURRENCIES, parser_API, metal_key, exchange_rate_key
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
from .forms.PayMenu import PayDeposit
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import json


@login_manager.user_loader
def load_user(user_id):
    return models.UserLogin().fromDB(user_id, dbase)


# Пополнение счета
@app.get("/pay")
@login_required
def get_pay():
    form = PayDeposit()
    return render_template("pay.html", form=form)


@app.post("/pay")
def post_pay():
    count = request.form["count"]
    res = dbase.change_balance(
        current_user.get_id(), float(count), "DEPOSIT", get_current_time()
    )
    if res == 0:
        flash("Недостаточно средств")
        return redirect(url_for("get_pay"))
    return redirect(url_for("get_private_office"))


# Страничца с историей операций
@app.get("/history")
@login_required
def get_history():
    data = dbase.get_history_by_id(current_user.get_id())
    for oper in data:
        if int(oper["currency_ID"]) == 0:
            continue
        oper["currency_ID"] = dbase.get_currency_data_by_id(int(oper["currency_ID"]))[
            "currency_name"
        ]
    return render_template("history.html", data=data)


# Страница отдельной валюты
@app.get("/currency/<currency_id>")
def get_currency(currency_id):
    price = price = parser_API.get_current_price_by_figi(
        parser_API.get_figi_by_ticker(CURRENCIES[currency_id][0])
    )
    data = models.Currency(
        currency_id, CURRENCIES[currency_id][1], price, price - (price * 0.07)
    )
    with open("server/templates/about_currencies.json", "r") as js:
        json_dump = json.load(js)
        about = json_dump[currency_id]
    return render_template("pettern_currencies.html", curr=data, about=about)


# Покупка/продажа валюты
@app.post("/currency/<currency_id>")
@login_required
def post_buy_sell_currency(currency_id):
    data = {}
    for cuur in CURRENCIES:
        price = parser_API.get_current_price_by_figi(
            parser_API.get_figi_by_ticker(CURRENCIES[cuur][0])
        )
        data[cuur] = price
    dbase.update_currency(data)
    if "submit_buy" in request.form:
        dbase.add_operation(
            current_user.get_id(),
            CURRENCIES[currency_id][2],
            "BUY",
            1,
            get_current_time(),
        )
    else:
        dbase.add_operation(
            current_user.get_id(),
            CURRENCIES[currency_id][2],
            "SELL",
            1,
            get_current_time(),
        )
    return redirect(url_for("get_currency", currency_id=currency_id))


# Страница со всеми валютами
@app.get("/currencies")
def get_currencies():
    data = {}
    for cuur in CURRENCIES:
        price = parser_API.get_current_price_by_figi(
            parser_API.get_figi_by_ticker(CURRENCIES[cuur][0])
        )
        data[cuur] = price
    dbase.update_currency(data)
    data = []
    for currency in CURRENCIES:
        price = parser_API.get_current_price_by_figi(
            parser_API.get_figi_by_ticker(CURRENCIES[currency][0])
        )
        data.append(
            models.Currency(
                currency, CURRENCIES[currency][1], price, price - (price * 0.07)
            )
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
    print(current_user.get_id())
    data = dbase.get_briefcase_by_id(current_user.get_id())
    for oper in data:
        data[oper]["name_currency"] = CURRENCIES[oper][1]
    return render_template("personal_account.html", user=current_user, data=data)


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
            print(data)
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
    if user == 0:
        flash("Такого пользователя не существует")
        return redirect(url_for("get_user_authorization"))
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


# Получение московского времени
def get_current_time() -> datetime:
    delta = timedelta(hours=3, minutes=0)
    return datetime.now(timezone.utc) + delta
