import pandas as pd
from math import pi
from datetime import datetime, timedelta, timezone
from parser import parser
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, FactorRange, HoverTool
import pprint
from tinkoff.invest import CandleInterval

intervals = {
    "1minute": CandleInterval.CANDLE_INTERVAL_1_MIN,
    "3minutes": CandleInterval.CANDLE_INTERVAL_3_MIN,
    "5minutes": CandleInterval.CANDLE_INTERVAL_5_MIN,
    "10minutes": CandleInterval.CANDLE_INTERVAL_10_MIN,
    "30minutes": CandleInterval.CANDLE_INTERVAL_30_MIN,
    "1hour": CandleInterval.CANDLE_INTERVAL_HOUR,
    "1day": CandleInterval.CANDLE_INTERVAL_DAY,
    "1week": CandleInterval.CANDLE_INTERVAL_WEEK,
    "1month": CandleInterval.CANDLE_INTERVAL_MONTH,
}

width_of_candle = {
    "1minute": 60 * 1000,
    "3minutes": 3 * 60 * 1000,
    "5minutes": 5 * 60 * 1000,
    "10minutes": 10 * 60 * 1000,
    "30minutes": 30 * 60 * 1000,
    "1hour": 60 * 60 * 1000,
    "1day": 24 * 60 * 60 * 1000,
    "1week": 7 * 24 * 60 * 60 * 1000,
    "1month": 30 * 24 * 60 * 60 * 1000,
}


def build_graph_candles(
    cur_info: parser.CurrencyInfo,
    ticker: str,
    start_time: datetime,
    end_time: datetime,
    interval: str,
):
    data = cur_info.get_history_of_current_currency_by_ticker(
        ticker, start_time, end_time, intervals[interval]
    )
    for el in data:
        el["change"] = (el["close"] - el["open"]) / 100
    data = {i: data[i] for i in range(len(data))}
    data = pd.DataFrame.from_dict(data, orient="index")
    # data['change'] =
    source = ColumnDataSource(
        data=dict(
            time=data["time"].tolist(),
            open=data["open"].tolist(),
            volume=data["volume"].tolist(),
            close=data["close"].tolist(),
            high=data["high"].tolist(),
            low=data["low"].tolist(),
            change=data["change"].tolist(),
        )
    )
    try:
        data_inc = data[data["close"] > data["open"]]
        data_dec = data[data["open"] > data["close"]]

        source_inc = ColumnDataSource(
            data=dict(
                time=data_inc["time"].tolist(),
                open=data_inc["open"].tolist(),
                volume=data_inc["volume"].tolist(),
                close=data_inc["close"].tolist(),
                high=data_inc["high"].tolist(),
                low=data_inc["low"].tolist(),
                change=data_inc["change"].tolist(),
            )
        )
        source_dec = ColumnDataSource(
            data=dict(
                time=data_dec["time"].tolist(),
                open=data_dec["open"].tolist(),
                volume=data_dec["volume"].tolist(),
                close=data_dec["close"].tolist(),
                high=data_dec["high"].tolist(),
                low=data_dec["low"].tolist(),
                change=data_dec["change"].tolist(),
            )
        )

    except KeyError:
        return "BirzhaIsClosed"
    w = width_of_candle[interval]  # trading time in ms

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    TOOLTIPS = [
        ("Date", "@time{%d.%m.%Y %H:%M}"),
        ("Open", "@open{0.2f}"),
        ("High", "@high{0.2f}"),
        ("Low", "@low{0.2f}"),
        ("Close", "@close{0.2f}"),
        ("Change", "@change{0.4f}"),
        ("Volume", "@volume{0.2f}"),
    ]

    hover_tool = HoverTool(tooltips=TOOLTIPS, formatters={"@time": "datetime"})
    p = figure(
        x_axis_type="datetime",
        width=1000,
        tools=TOOLS,
        title="Курс Валюты",
    )
    p.add_tools(hover_tool)
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3

    p.segment(x0="time", y0="high", x1="time", y1="low", source=source, color="black")
    p.vbar(
        width=w,
        fill_color="blue",
        line_color="black",
        x="time",
        top="open",
        bottom="close",
        source=source_inc,
    )
    p.vbar(
        width=w,
        fill_color="red",
        line_color="black",
        x="time",
        top="open",
        bottom="close",
        source=source_dec,
    )
    return p


def build_graph_line(
    cur_info: parser.CurrencyInfo,
    ticker: str,
    start_time: datetime,
    end_time: datetime,
    interval: str,
):
    data = cur_info.get_history_of_current_currency_by_ticker(
        ticker, start_time, end_time, intervals[interval]
    )
    for el in data:
        el["change"] = (el["close"] - el["open"]) / 100
    data = {i: data[i] for i in range(len(data))}
    data = pd.DataFrame.from_dict(data, orient="index")
    # data['change'] =
    source = ColumnDataSource(
        data=dict(
            time=data["time"].tolist(),
            open=data["open"].tolist(),
            volume=data["volume"].tolist(),
            close=data["close"].tolist(),
            high=data["high"].tolist(),
            low=data["low"].tolist(),
            change=data["change"].tolist(),
        )
    )
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    TOOLTIPS = [
        ("Date", "@time{%d.%m.%Y %H:%M}"),
        ("Open", "@open{0.2f}"),
        ("Close", "@close{0.2f}"),
        ("Volume", "@volume{0.2f}"),
        ("Change", "@change{0.4f}"),
    ]
    hover_tool = HoverTool(tooltips=TOOLTIPS, formatters={"@time": "datetime"})
    p = figure(
        x_axis_type="datetime",
        width=1000,
        tools=TOOLS,
    )
    p.add_tools(hover_tool)
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3

    p.line(x="time", y="close", source=source, line_width=2)
    return p


def get_start_time(hours=0, days=0, weeks=0, months=0, years=0) -> datetime:
    weeks += months * 4
    weeks += years * 12 * 4
    delta = timedelta(hours=hours, days=days, weeks=weeks)
    return datetime.now(timezone.utc) - delta


def main():
    token = "t.IEa99GPRoD0m0Z3MH_M2BUMIAVsqYMCpcmJhQFIKDw8rg3tk7CpENgicqyVpOMSTK1ubCt1ZB7SQCXTcEy0Dcw"
    metal_key = "5f266da4bdd540557f1d6c8707360cc8"
    exchange_rate_key = "752cb5b3134f445168799121"
    cur = parser.CurrencyInfo(token, metal_key, exchange_rate_key)
    build_graph_candles(
        cur,
        "USD000000TOD",
        start_time=get_start_time(hours=59),
        end_time=get_start_time(),
        interval="1hour",
    )


if __name__ == "__main__":
    main()
