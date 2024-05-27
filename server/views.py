from server import (
    app,
    dbase,
    CURRENCIES,
    parser_API,
    config,
)
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
from .forms.PayMenu import PayDeposit, PayWithdraw
from .graph import build_graph_candles, get_start_time, build_graph_line
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from bokeh.embed import components
import json

times_for_graphs = {
    "1h": [1, "3minutes"],
    "3h": [3, "5minutes"],
    "1d": [24, "30minutes"],
    "7d": [24 * 7, "1hour"],
    "1mon": [24 * 30, "1day"],
    "1year": [24 * 30 * 12, "1week"],
}


@login_manager.user_loader
def load_user(user_id):
    return models.UserLogin().fromDB(user_id, dbase)


# Вывод средств
@app.get("/pay-withdraw")
@login_required
def get_withdraw_pay():
    form = PayWithdraw()
    return render_template("pay_withdraw.html", form=form)


@app.post("/pay-withdraw")
def post_withdraw_pay():
    count = request.form["count"]
    balance = dbase.get_user_data_by_id(current_user.get_id())["balance"]
    if balance - float(count) < 0:
        flash("Недостаточно средств")
        return redirect(url_for("get_withdraw_pay"))
    res = dbase.change_balance(
        current_user.get_id(), float(count), "WITHDRAW", get_current_time()
    )
    if res == 0:
        flash("Недостаточно средств")
        return redirect(url_for("get_withdraw_pay"))
    return redirect(url_for("get_private_office"))


# Пополнение счета
@app.get("/pay-deposit")
@login_required
def get_deposit_pay():
    form = PayDeposit()
    return render_template("pay_deposit.html", form=form)


@app.post("/pay-deposit")
def post_deposit_pay():
    count = request.form["count"]
    res = dbase.change_balance(
        current_user.get_id(), float(count), "DEPOSIT", get_current_time()
    )
    if res == 0:
        flash("Недостаточно средств")
        return redirect(url_for("get_deposit_pay"))
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
@app.get("/currency/<currency_id>/<time>/<graph_type>/<colour>")
def get_currency(currency_id, time="1h", graph_type="lines", colour="standart"):
    price = price = parser_API.get_current_price_by_figi(
        parser_API.get_figi_by_ticker(CURRENCIES[currency_id][0])
    )
    data = models.Currency(
        currency_id, CURRENCIES[currency_id][1], price, price - (price * 0.07)
    )
    with open("server/templates/about_currencies.json", "r", encoding="utf8") as js:
        json_dump = json.load(js)
        about = json_dump[currency_id]
    try:
        if graph_type == "candles":
            graph = build_graph_candles(
                parser_API,
                CURRENCIES[currency_id][0],
                start_time=get_start_time(hours=times_for_graphs[time][0]),
                end_time=get_start_time(),
                interval=times_for_graphs[time][1],
                color=colour,
            )
        else:
            graph = build_graph_line(
                parser_API,
                CURRENCIES[currency_id][0],
                start_time=get_start_time(hours=times_for_graphs[time][0]),
                end_time=get_start_time(),
                interval=times_for_graphs[time][1],
                color=colour,
            )
    except (KeyError, ValueError):
        return redirect(url_for("get_private_office"))

    try:
        script, div = components(graph)
    except ValueError:
        script = "Проблема на стороне api"
        div = "Приносим извинения\n"

    return render_template(
        "pettern_currencies.html",
        curr=data,
        about=about,
        the_div=div,
        the_script=script,
        colour=colour,
    )


# Покупка/продажа валюты
@app.post("/currency/<currency_id>/<time>/<graph_type>/<colour>")
@login_required
def post_buy_sell_currency(
    currency_id, time="1h", graph_type="lines", colour="standart"
):
    data = {}
    if "colour" in request.form:
        colour = request.form["colour"]
    if "graph_type" in request.form:
        graph_type = request.form["graph_type"]
    if "time" in request.form:
        time = request.form["time"]
    if "count" in request.form:
        count_currency = request.form["count"]
        try:
            count_currency = float(count_currency)
        except ValueError:
            flash("Введите число")
            return redirect(
                url_for(
                    "get_currency",
                    currency_id=currency_id,
                    time=time,
                    graph_type=graph_type,
                    colour=colour,
                )
            )
    else:
        return redirect(
            url_for(
                "get_currency",
                currency_id=currency_id,
                time=time,
                graph_type=graph_type,
                colour=colour,
            )
        )

    for cuur in CURRENCIES:
        price = parser_API.get_current_price_by_figi(
            parser_API.get_figi_by_ticker(CURRENCIES[cuur][0])
        )
        data[cuur] = price
    dbase.update_currency(data)

    if "submit_buy" in request.form:
        res = dbase.add_operation(
            current_user.get_id(),
            CURRENCIES[currency_id][2],
            "BUY",
            float(count_currency),
            get_current_time(),
        )
        if res == 0:
            flash("Недостаточно средств")
            return redirect(
                url_for(
                    "get_currency",
                    currency_id=currency_id,
                    time=time,
                    graph_type=graph_type,
                    colour=colour,
                )
            )
    else:
        res = dbase.add_operation(
            current_user.get_id(),
            CURRENCIES[currency_id][2],
            "SELL",
            float(count_currency),
            get_current_time(),
        )
        if res == 0:
            flash("Недостаточно валюты")
            return redirect(
                url_for(
                    "get_currency",
                    currency_id=currency_id,
                    time=time,
                    graph_type=graph_type,
                    colour=colour,
                )
            )
    return redirect(
        url_for(
            "get_currency",
            currency_id=currency_id,
            time=time,
            graph_type=graph_type,
            colour=colour,
        )
    )


# Страница со всеми валютами
@app.get("/currencies")
def get_currencies():
    data = {}
    currencies = []
    for cuur in CURRENCIES:
        price = parser_API.get_current_price_by_figi(
            parser_API.get_figi_by_ticker(CURRENCIES[cuur][0])
        )
        data[cuur] = price
    dbase.update_currency(data)
    for currency in data:
        currencies.append(
            models.Currency(
                currency,
                CURRENCIES[currency][1],
                data[currency],
                data[currency] - (data[currency] * 0.07),
            )
        )

    return render_template("currencies.html", curruncies=currencies)


# Начальная страница
@app.get("/")
def get_about_us():
    return render_template("About_us.html")


# Личный кабинет
@app.get("/private-office")
@login_required
def get_private_office():
    data = dbase.get_briefcase_by_id(current_user.get_id())
    tg_id = None
    for oper in data:
        data[oper]["name_currency"] = CURRENCIES[oper][1]
    tg_id = dbase.get_all_user_for_tg_bot()[int(current_user.get_id())]["tg_id"]
    return render_template(
        "personal_account.html", user=current_user, data=data, tg=tg_id
    )


# Личный кабинет
@app.post("/private-office")
@login_required
def post_private_office():
    if "tg_id" in request.form:
        tg_id = request.form["tg_id"]
        count = request.form["count"]
        dbase.update_tg_id(current_user.get_id(), tg_id)
        dbase.update_delta_to_note(current_user.get_id(), count)
        return redirect(url_for("get_private_office"))
    elif "replace" in request.form:
        dbase.update_tg_id(current_user.get_id(), 0)
        dbase.update_delta_to_note(current_user.get_id(), 0)
        return redirect(url_for("get_private_office"))


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
