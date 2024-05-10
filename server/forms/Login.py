from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField(
        validators=[Email("Неккоректная почта")],
        render_kw={"placeholder": "Электронная почта"},
    )
    password = PasswordField(
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "Пароль"},
    )
    submit = SubmitField("Войти")
