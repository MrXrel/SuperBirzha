from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class PayDeposit(FlaskForm):
    count = StringField(
        validators=[DataRequired()],
        render_kw={"placeholder": "Введите желаему сумму"},
    )
    submit = SubmitField("Пополнить")
