from tinkoff.invest import Candle, InstrumentType, Share, InstrumentIdType, Currency, CandleInterval, Client, HistoricCandle, GetCandlesResponse
import pprint
from datetime import datetime, timedelta

token = "t.IEa99GPRoD0m0Z3MH_M2BUMIAVsqYMCpcmJhQFIKDw8rg3tk7CpENgicqyVpOMSTK1ubCt1ZB7SQCXTcEy0Dcw"


# Валюта
# price * lot / nomi
def get_info_about_currency(ticker):
    # return type - InstrumentResponse
    with Client(token) as client:
        try:
            instrument = client.instruments.currency_by()
            return instrument
        except Exception as e:
            return f"In function get_info_about_currency \n {e}"

def get_history_of_current_share(figi, start_date, end_date, interval=CandleInterval.CANDLE_INTERVAL_HOUR):

    # start_date - type: google.protobuf.Timestamp - начало запрашиваемого периода в часовом поясе UTC.
    # end_date - type: google.protobuf.Timestamp - окончание запрашиваемого периода в часовом поясе UTC.
    # CANDLE_INTERVAL_1_MIN	    от 1 минуты до 1 дня.
    # CANDLE_INTERVAL_5_MIN	    от 5 минут до 1 дня.
    # CANDLE_INTERVAL_15_MIN    от 15 минут до 1 дня.
    # CANDLE_INTERVAL_HOUR	    от 1 часа до 1 недели.
    # CANDLE_INTERVAL_DAY	    от 1 дня до 1 года.
    # CANDLE_INTERVAL_WEEK	    от 1 недели до 2 лет.

    with Client(token) as client:
        try:
            instrument = client.market_data.get_candles(
                figi=figi,
                from_=start_date,
                to=end_date,
                interval=interval
            )
            candles = instrument.candles
            data_list = create_data_list(candles)
            return data_list
        except Exception as e:
            return f"In function get_history_of_current_currency \n {e}"
def get_history_of_current_share_by_ticker(ticker, start_date, end_date, interval=CandleInterval.CANDLE_INTERVAL_HOUR):

    # start_date - type: google.protobuf.Timestamp - начало запрашиваемого периода в часовом поясе UTC.
    # end_date - type: google.protobuf.Timestamp - окончание запрашиваемого периода в часовом поясе UTC.
    # CANDLE_INTERVAL_1_MIN	    от 1 минуты до 1 дня.
    # CANDLE_INTERVAL_5_MIN	    от 5 минут до 1 дня.
    # CANDLE_INTERVAL_15_MIN    от 15 минут до 1 дня.
    # CANDLE_INTERVAL_HOUR	    от 1 часа до 1 недели.
    # CANDLE_INTERVAL_DAY	    от 1 дня до 1 года.
    # CANDLE_INTERVAL_WEEK	    от 1 недели до 2 лет.

    with Client(token) as client:
        try:
            instrument = client.market_data.get_candles(
                ticker=ticker,
                from_=start_date,
                to=end_date,
                interval=interval
            )
            candles = instrument.candles
            data_list = create_data_list(candles)
            return data_list
        except Exception as e:
            return f"In function get_history_of_current_currency \n {e}"


def create_data_list(candles: [HistoricCandle]):
    data_list = [{
        'time': current.time,
        'volume': current.volume,
        'open': convert_to_rubles(current.open),
        'close': convert_to_rubles(current.close),
        'high': convert_to_rubles(current.high),
        'low': convert_to_rubles(current.low),
    } for current in candles]

    return data_list


def convert_to_rubles(current_candle):
    return current_candle.units + current_candle.nano / 1e9  # nano - 9 нулей


