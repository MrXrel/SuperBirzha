from server import app, dbase
from flask import render_template, request, redirect, url_for, Response
from server import models, login_manager
from .forms.Registration import RegistrationForm
from .forms.Login import LoginForm
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return models.UserLogin().fromDB(user_id, dbase)


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
        if check_password_hash(hash, form.password_confirm.data):
            dbase.create_user(form.email.data, hash, form.surname.data, form.name.data)
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
    return Response("пароль кек")


# Выход из профиля
@app.route("/logout")
@login_required
def user_logout():
    logout_user()
    return redirect(url_for("get_user_authorization"))
