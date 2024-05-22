from flask_wtf import FlaskForm
from wtforms import SubmitField


class BuySellButton(FlaskForm):
    submit_buy = SubmitField("Купить")
    submit_sell = SubmitField("Продать")
