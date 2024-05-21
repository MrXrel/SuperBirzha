from typing import List, Optional
from tinkoff.invest import InstrumentIdType, InstrumentStatus, CandleInterval, Client, HistoricCandle
from pandas import DataFrame
import pandas as pd
from config import token
from datetime import datetime, timedelta


#             TICKER        FIGI
# ЗОЛОТО     GLDRUB_TOM    BBG000VJ5YR4
# ДОЛЛАР     USD000000TOD  TCS0013HGFT4
# ЮАНЬ       CNYRUB_TMS    TCS3013HRTL0
# ЕВРО       EUR_RUB__TOM  BBG0013HJJ31

all_figi = {'gold': 'BBG000VJ5YR4', 'dollar': 'TCS0013HGFT4', 'yuan': 'TCS3013HRTL0', 'euro': 'BBG0013HJJ31'}

class CurrencyInfo:
    '''
    Класс для работы с информацией о валютах через API Tinkoff Invest.

    Предоставляет методы для получения информации о валютах, включая их историю цен, а так же получение
    полного перечня информации о каждой валюте. Используется токен для аутентификации на API Tinkoff Invest.
    '''

    def __init__(self, token: str) -> None:
        """
        Инициализация класса с токеном для аутентификации на API Tinkoff Invest.

        :param token: Токен для аутентификации на API Tinkoff Invest.
        """
        self.token = token

    def get_all_currencies(self) -> Optional[List[str]]:
        """
        Получение списка всех доступных валют через API Tinkoff Invest.

        :return: Список всех валют или сообщение об ошибке, если произошла ошибка.
        """
        all_currencies = None
        with Client(self.token) as client:
            try:
                all_currencies = client.instruments.currencies(
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                return all_currencies
            except Exception as e:
                return f"In function get_all_currencies \n {e}"

    def create_data_frame(self, instrument: List[dict]) -> DataFrame:
        """
        Создание DataFrame из списка инструментов для удобства работы с данными.

        :param instrument: Список инструментов (валют).
        :type instrument: list
        :return: DataFrame с информацией о валютах.
        :rtype: pandas.DataFrame
        """

        data_frame = DataFrame(instrument, columns=['ticker', 'figi', 'name'])
        pd.set_option('display.max_rows', None)
        return data_frame

    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """
        Получение FIGI валюты по ее тикеру.

        :param ticker: Тикер валюты.
        :type ticker: str
        :return: FIGI валюты или сообщение об ошибке, если произошла ошибка.
        """

        with Client(self.token) as client:
            try:
                data = self.get_all_currencies()
                data_list = self.create_data_frame(data)
                filtered_data = data_list[data_list['ticker'] == ticker]
                if filtered_data.empty:
                    return None
                else:
                    figi = filtered_data['figi'].iloc[0]
                    return figi
            except Exception as e:
                return f"In function get_figi_by_ticker \n {e}"

    def get_info_about_currency_by_ticker(self, ticker: str) -> Optional[dict]:
        """
        Получение информации о валюте по ее тикеру.

        :param ticker: Тикер валюты.
        :type ticker: str
        :return: Информация о валюте или сообщение об ошибке, если произошла ошибка.
        """

        with Client(self.token) as client:
            try:
                figi = self.get_figi_by_ticker(ticker)
                instrument = client.instruments.currency_by(id=figi,
                                                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
                return instrument
            except Exception as e:
                return f"In function get_info_about_currency_by_ticker \n {e}"

    def get_info_about_currency_by_figi(self, figi: str) -> Optional[dict]:
        """
        Получение информации о валюте по ее FIGI.

        :param figi: FIGI валюты.
        :type figi: str
        :return: Информация о валюте или сообщение об ошибке, если произошла ошибка.
        """

        with Client(self.token) as client:
            try:
                instrument = client.instruments.currency_by(id=figi,
                                                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
                return instrument
            except Exception as e:
                return f"In function get_info_about_currency_by_figi \n {e}"

    def get_current_price_by_figi(self, figi: str) -> float:
        """
        Получение текущей цены валюты по FIGI.

        :param figi: FIGI инструмента.
        :type figi: str
        :return: Текущая цена валюты в рублях.
        """
        with Client(token) as client:
            try:
                instrument = client.instruments.currency_by(id=figi,
                                                    id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
                return instrument.nominal.units + instrument.nominal.nano / 1e9

            except Exception as e:
                return f"In function get_current_price_by_figi"

    def get_all_prices(self) -> Optional[dict]:
        data = {}
        with Client(token) as client:
            try:
                for elem in all_figi.items():
                    data[elem[0]] = self.get_current_price_by_figi(elem[1])
                return data
            except Exception as e:
                return f"In get_all_prices"


    def get_current_price_by_ticker(self, ticker: str):
        """
        Получение текущей цены валюты по тикеру.

        :param ticker: Тикер инструмента.
        :type ticker: str
        :return: Текущая цена валюты в рублях.
        """
        with Client(token) as client:
            try:
                figi = self.get_figi_by_ticker(ticker)
                instrument = client.instruments.currency_by(id=figi,
                                                    id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
                return instrument.nominal.units + instrument.nominal.nano / 1e9

            except Exception as e:
                return f"In function get_current_price_by_figi"


    def get_history_of_current_currency_by_ticker(self, ticker: str, start_time: datetime, end_time: datetime,
                                                  interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_HOUR) -> List[dict]:
        """
        Получение истории цен текущей валюты по ее тикеру.

        :param ticker: Тикер валюты.
        :type ticker: str
        :param start_time: Начальное время для запроса истории цен.
        :type start_time: datetime
        :param end_time: Конечное время для запроса истории цен.
        :type end_time: datetime
        :param interval: Интервал времени для запроса истории цен.
        :type interval: CandleInterval
        :return: История цен валюты или сообщение об ошибке, если произошла ошибка.
        """

        figi = self.get_figi_by_ticker(ticker)
        with Client(self.token) as client:
            try:
                instrument = client.market_data.get_candles(
                    figi=figi,
                    from_=start_time,
                    to=end_time,
                    interval=interval
                )
                candles = instrument.candles
                data_list = self.create_data_list(candles)
                return data_list
            except Exception as e:
                return f"In function get_history_of_current_currency_by_ticker \n {e}"

    def get_history_of_current_currency_by_figi(self, figi: str, start_time: datetime, end_time: datetime,
                                             interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_HOUR) -> List[dict]:
        """
        Получение истории цен текущей акции по ее FIGI.

        :param figi: FIGI акции.
        :type figi: str
        :param start_time: Начальное время для запроса истории цен.
        :type start_time: datetime
        :param end_time: Конечное время для запроса истории цен.
        :type end_time: datetime
        :param interval: Интервал времени для запроса истории цен.
        :type interval: CandleInterval
        :return: История цен акции или сообщение об ошибке, если произошла ошибка.
        """

        with Client(self.token) as client:
            try:
                instrument = client.market_data.get_candles(
                    figi=figi,
                    from_=start_time,
                    to=end_time,
                    interval=interval
                )
                candles = instrument.candles
                data_list = self.create_data_list(candles)
                return data_list
            except Exception as e:
                return f"In function get_history_of_current_share_by_figi \n {e}"

    def create_data_list(self, candles: List[HistoricCandle]) -> List[dict]:
        """
        Создание списка данных из истории цен.

        :param candles: Список исторических свечей.
        :type candles: list
        :return: Список данных о ценах.
        :rtype: list
        """
        data_list = [{
            'time': current.time,
            'volume': current.volume,
            'open': self.convert_to_rubles(current.open),
            'close': self.convert_to_rubles(current.close),
            'high': self.convert_to_rubles(current.high),
            'low': self.convert_to_rubles(current.low),
        } for current in candles]

        return data_list

    def convert_to_rubles(self, current_candle: HistoricCandle) -> float:
        """
        Конвертация цены валюты в рубли.

        :param current_candle: Объект с информацией о цене валюты.
        :type current_candle: HistoricCandle
        :return: Цена валюты в рублях.
        :rtype: float
        """

        return current_candle.units + current_candle.nano / 1e9  # nano - 9 zeroes


if __name__ == '__main__':
    currency_info = CurrencyInfo(token)
    print(currency_info.get_all_prices())