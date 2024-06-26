from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    name = StringField(
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "Имя"},
    )
    surname = StringField(
        validators=[DataRequired(), Length(min=3, max=30)],
        render_kw={"placeholder": "Фамилия"},
    )
    email = StringField(
        validators=[Email("Неккоректная почта")],
        render_kw={"placeholder": "Электронная почта"},
    )
    password = PasswordField(
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "Пароль"},
    )
    password_confirm = PasswordField(
        validators=[
            DataRequired(),
            Length(min=3, max=20),
            EqualTo("password", message="Пароли не совпадают"),
        ],
        render_kw={"placeholder": "Подтвердите пароль"},
    )
    submit = SubmitField("Зарегистрироваться")
