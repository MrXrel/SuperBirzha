import pandas as pd
from math import pi
from datetime import datetime, timedelta, timezone
from parser import parser
from bokeh.plotting import figure, show

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


def build_graph(
    cur_info: parser.CurrencyInfo,
    ticker: str,
    start_time: datetime,
    end_time: datetime,
    interval: str,
):
    data = cur_info.get_history_of_current_currency_by_ticker(
        ticker, start_time, end_time, intervals[interval]
    )
    pprint.pprint(data)
    data = {i: data[i] for i in range(len(data))}
    print(data)
    data = pd.DataFrame.from_dict(data, orient="index")
    print(data)
    try:
        inc = data["close"] > data["open"]
        dec = data["open"] > data["close"]
    except KeyError:
        return "BirzhaIsClosed"

    w = width_of_candle[interval]  # trading time in ms

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(
        x_axis_type="datetime",
        width=1000,
        tools=TOOLS,
        title="Pfizer Candlestick Chart",
    )
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3

    p.segment(data["time"], data["high"], data["time"], data["low"], color="black")
    p.vbar(
        data["time"][inc],
        w,
        data["open"][inc],
        data["close"][inc],
        fill_color="blue",
        line_color="black",
    )
    p.vbar(
        data["time"][dec],
        w,
        data["open"][dec],
        data["close"][dec],
        fill_color="red",
        line_color="black",
    )
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
    build_graph(
        cur,
        "USD000000TOD",
        start_time=get_start_time(hours=59),
        end_time=get_start_time(),
        interval="1hour",
    )


if __name__ == "__main__":
    main()
