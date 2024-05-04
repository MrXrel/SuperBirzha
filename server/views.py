from server import app, USERS
from flask import render_template, request, redirect, url_for
from server import models, login_manager
from .forms.Registration import RegistrationForm
from .forms.Login import LoginForm
from flask_login import login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    if len(USERS) != 0:
        return models.UserLogin().fromDB(user_id)


@app.get("/currencies")
def get_currencies():
    return render_template("currencies.html")


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
        user = models.User(
            len(USERS),
            form.email.data,
            hash,
            form.second_name.data,
            form.name.data,
        )
        USERS.append(user)
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
    for i in USERS:
        if i.email == email and check_password_hash(i._password, psw):
            user = i
            userlogin = models.UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for("get_private_office"), 301)
