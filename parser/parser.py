from tinkoff.invest import (
    InstrumentIdType,
    InstrumentStatus,
    CandleInterval,
    Client,
    HistoricCandle,
)
from pandas import DataFrame

all_shares = None
all_currencies = None

token = "t.IEa99GPRoD0m0Z3MH_M2BUMIAVsqYMCpcmJhQFIKDw8rg3tk7CpENgicqyVpOMSTK1ubCt1ZB7SQCXTcEy0Dcw"


def get_all_shares():
    # return array with all shares

    global all_shares
    with Client(token) as client:
        try:
            all_shares = client.instruments.shares(
                instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE
            ).instruments
            return all_shares
        except Exception as e:
            return f"In function get_all_shares \n {e}"


def get_all_currencies():
    # return array with all currencies

    global all_currencies
    with Client(token) as client:
        try:
            all_currencies = client.instruments.currencies(
                instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL
            ).instruments
            return all_currencies
        except Exception as e:
            return f"In function get_all_currencies \n {e}"


def create_data_frame(instrument):
    # return very beautiful data_frame for convenience
    data_frame = DataFrame(instrument, columns=["ticker", "figi", "name"])
    return data_frame


def get_figi_by_ticker(ticker, type_):  #'AMDRUB_TOM'
    # type_ - currency of share
    with Client(token) as client:
        try:
            if type_ == "currency":
                data = get_all_currencies()
            elif type_ == "share":
                data = get_all_shares()
            else:
                return f"Error: Incorrect type"
            data_list = create_data_frame(data)
            filtered_data = data_list[data_list["ticker"] == ticker]
            if filtered_data.empty:
                return None
            else:
                figi = filtered_data["figi"].iloc[0]
                return figi
        except Exception as e:
            return f"In function get_figi_by_ticker \n {e}"


def get_info_about_share_by_ticker(ticker, type_):
    # return DataFrame
    with Client(token) as client:
        try:
            figi = get_figi_by_ticker(ticker, type_)
            instrument = client.instruments.share_by(
                id=figi, id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI
            ).instrument
            data_frame = DataFrame([instrument], columns=["ticker", "figi", "name"])
            return data_frame
        except Exception as e:
            return f"In function get_info_about_share \n {e}"


def get_info_about_share_by_figi(figi):
    # return DataFrame
    with Client(token) as client:
        try:
            instrument = client.instruments.share_by(
                id=figi, id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI
            ).instrument
            data_frame = DataFrame([instrument], columns=["ticker", "figi", "name"])
            return data_frame
        except Exception as e:
            return f"In function get_info_about_share_by_figi \n {e}"


def get_history_of_current_share_by_ticker(
    ticker, type_, start_time, end_time, interval=CandleInterval.CANDLE_INTERVAL_HOUR
):
    # type_ - currency or share

    # start_time - type: google.protobuf.Timestamp - начало запрашиваемого периода в часовом поясе UTC.
    # E.G. start_time = datetime.utcnow() - timedelta(hours=10),
    # end_time - type: google.protobuf.Timestamp - окончание запрашиваемого периода в часовом поясе UTC.

    # CANDLE_INTERVAL_1_MIN	    от 1 минуты до 1 дня.
    # CANDLE_INTERVAL_5_MIN	    от 5 минут до 1 дня.
    # CANDLE_INTERVAL_15_MIN    от 15 минут до 1 дня.
    # CANDLE_INTERVAL_HOUR	    от 1 часа до 1 недели.
    # CANDLE_INTERVAL_DAY	    от 1 дня до 1 года.
    # CANDLE_INTERVAL_WEEK	    от 1 недели до 2 лет.

    figi = get_figi_by_ticker(ticker, type_)

    with Client(token) as client:
        try:
            if type_ == "currency":
                data = get_all_currencies()
            elif type_ == "share":
                data = get_all_shares()
            else:
                return f"Error: Incorrect type"
            instrument = client.market_data.get_candles(
                figi=figi, from_=start_time, to=end_time, interval=interval
            )
            candles = instrument.candles
            data_list = create_data_list(candles)
            return data_list
        except Exception as e:
            return f"In function get_history_of_current_currency \n {e}"


def get_history_of_current_share_by_figi(
    figi, type_, start_time, end_time, interval=CandleInterval.CANDLE_INTERVAL_HOUR
):
    # type_ - currency or share

    # start_time - type: google.protobuf.Timestamp - начало запрашиваемого периода в часовом поясе UTC.
    # E.G. start_time = datetime.utcnow() - timedelta(hours=10),
    # end_time - type: google.protobuf.Timestamp - окончание запрашиваемого периода в часовом поясе UTC.

    # CANDLE_INTERVAL_1_MIN	    от 1 минуты до 1 дня.
    # CANDLE_INTERVAL_5_MIN	    от 5 минут до 1 дня.
    # CANDLE_INTERVAL_15_MIN    от 15 минут до 1 дня.
    # CANDLE_INTERVAL_HOUR	    от 1 часа до 1 недели.
    # CANDLE_INTERVAL_DAY	    от 1 дня до 1 года.
    # CANDLE_INTERVAL_WEEK	    от 1 недели до 2 лет.

    with Client(token) as client:
        try:
            if type_ == "currency":
                data = get_all_currencies()
            elif type_ == "share":
                data = get_all_shares()
            else:
                return f"Error: Incorrect type"
            instrument = client.market_data.get_candles(
                figi=figi, from_=start_time, to=end_time, interval=interval
            )
            candles = instrument.candles
            data_list = create_data_list(candles)
            return data_list
        except Exception as e:
            return f"In function get_history_of_current_currency \n {e}"


def create_data_list(candles: [HistoricCandle]):
    data_list = [
        {
            "time": current.time,
            "volume": current.volume,
            "open": convert_to_rubles(current.open),
            "close": convert_to_rubles(current.close),
            "high": convert_to_rubles(current.high),
            "low": convert_to_rubles(current.low),
        }
        for current in candles
    ]

    return data_list


def convert_to_rubles(current_candle):
    return current_candle.units + current_candle.nano / 1e9  # nano - 9 нулей
