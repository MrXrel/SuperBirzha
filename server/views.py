from server import app, USERS
from flask import render_template, request, redirect, url_for
from server import models
from .forms.Registration import RegistrationForm

USERS.append(
    models.User(0, "dj@gmail.com", "12323", "Мустафаев", "Алим")
)  # временная мера для тестов, пока нет бд


# Начальная страница
@app.get("/")
def get_about_us():
    user = USERS[0]
    return render_template("About_us.html", user=user)


# Личный кабинет
@app.route("/private-office")
def get_private_office():
    user = USERS[0]
    return render_template("personal_account.html", user=user)


# Страница регистрации
@app.route("/registration", methods=["GET", "POST"])
def user_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = models.User(
            len(USERS),
            form.email,
            form.password,
            form.second_name,
            form.name,
        )
        USERS.append(user)
        return redirect(url_for("user_authorization"), 301)
    user = USERS[0]
    return render_template("sign_up.html", user=user, form=form)


@app.get("/authorization")
def get_user_authorization():
    user = USERS[0]
    return render_template("sign_in.html", user=user)


@app.post("/authorization")
def post_user_authorization():
    user = USERS[0]
    return render_template("sign_in.html", user=user)
