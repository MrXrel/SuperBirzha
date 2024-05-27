from typing import List, Optional, Dict
from tinkoff.invest import InstrumentIdType, InstrumentStatus, CandleInterval, Client, HistoricCandle, Quotation
from pandas import DataFrame
import pandas as pd
from datetime import datetime, timedelta
import requests

#             TICKER        FIGI
# ЗОЛОТО     GLDRUB_TOM    BBG000VJ5YR4
# ДОЛЛАР     USD000000TOD  TCS0013HGFT4
# ЮАНЬ       CNYRUB_TMS    TCS3013HRTL0
# ЕВРО       EUR_RUB__TOM  BBG0013HJJ31

all_figi = {
    ('gold', 'XAU'): 'BBG000VJ5YR4',
    ('dollar', 'USD'): 'TCS0013HGFT4',
    ('yuan', 'CNY'): 'TCS3013HRTL0',
    ('euro', 'EUR'): 'BBG0013HJJ31'
}

class CurrencyInfo:
    '''
    Класс для работы с информацией о валютах через API Tinkoff Invest.

    Предоставляет методы для получения информации о валютах, включая их историю цен, а так же получение
    полного перечня информации о каждой валюте. Используется токен для аутентификации на API Tinkoff Invest.
    '''

    def __init__(self, token, api_metal_key, exchange_rate_key) -> None:
        """
        Инициализация класса с токеном для аутентификации на API Tinkoff Invest.

        Parameters
        ----------
        token : str
            Токен для аутентификации на API Tinkoff Invest.
        """
        self.token = token
        self.api_metal_key = api_metal_key
        self.api_exchange_rate_key = exchange_rate_key

    def get_exchange_rate_of_currency(self, base_currency: str, target_currency: str) -> float:
        """
        Получение курса обмена между двумя валютами.

        Parameters
        ----------
        base_currency : str
            Валюта, для которой требуется получить курс обмена.
        target_currency : str
            Валюта, курс обмена которой требуется получить.

        Returns
        ----------
        float
            Курс обмена между двумя валютами.
        """
        url = f"https://v6.exchangerate-api.com/v6/{self.api_exchange_rate_key}/latest/{base_currency}"
        response = requests.get(url)
        data = response.json()
        rate = data['conversion_rates'].get(target_currency)
        return rate

    def get_exchange_rate_of_metal(self) -> float:
        """
        Получение текущего курса металла

        Parameters
        ----------
        self

        Returns
        -------
        float
            Последняя цена металла или 0 в случае ошибки
        """
        try:
            data = self.get_history_of_current_currency_by_figi('BBG000VJ5YR4',
                                                                datetime.utcnow() - timedelta(days=1),
                                                                datetime.utcnow(),
                                                                interval=CandleInterval.CANDLE_INTERVAL_5_MIN)
            if data:
                return data[-1]["open"]
        except:
            return 0

    def is_metal(self, figi: str) -> bool:
        """
        Проверяет, является ли валюта/металл металлом.

        Parameters
        ----------
        figi : str
            FIGI идентификатор валюты/метала.

        Returns
        ----------
        bool
            True, если валюта/металл определена как металл, в противном случае False.
        """
        return figi == 'BBG000VJ5YR4'

    def create_data_frame(self, instrument: List[str]) -> DataFrame:
        """
        Создает DataFrame из списка инструментов для удобства работы с данными.

        Parameters
        ----------
        instrument : list
            Список инструментов (валют).

        Returns
        ----------
        pandas.DataFrame
            DataFrame с информацией о валютах.
        """
        data_frame = DataFrame(instrument, columns=['ticker', 'figi', 'name', 'nominal'])
        pd.set_option('display.max_rows', 20)
        return data_frame

    def get_all_currencies(self) -> Optional[pd.DataFrame]:
        """
        Извлекает список всех доступных валют через API Tinkoff Invest.

        Returns
        ----------
        Optional[pandas.DataFrame]
            DataFrame с информацией обо всех валютах или сообщение об ошибке, если произошла ошибка.
        """
        all_currencies = None
        with Client(self.token) as client:
            try:
                all_currencies = client.instruments.currencies(
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                return self.create_data_frame(all_currencies)
            except Exception as e:
                return f"В функции get_all_currencies \n {e}"

    def get_all_shares(self) -> pd.DataFrame:
        """
        Извлекает список всех доступных акций через API Tinkoff Invest.

        Returns
        ----------
        Optional[pandas.DataFrame]
            DataFrame с информацией обо всех акциях или сообщение об ошибке, если произошла ошибка.
        """
        all_currencies = None
        with Client(self.token) as client:
            try:
                all_currencies = client.instruments.shares(
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                return self.create_data_frame(all_currencies)
            except Exception as e:
                return f"В функции get_all_shares \n {e}"

    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """
        Получение FIGI валюты по её тикеру.

        Parameters
        ----------
        ticker : str
            Тикер валюты.

        Returns
        ----------
        Optional[str]
            FIGI валюты или сообщение об ошибке, если произошла ошибка.
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
                return f"В функции get_figi_by_ticker \n {e}"

    def get_ticker_by_figi(self, figi: str):
        """
        Получение тикера валюты по её FIGI.

        Parameters
        ----------
        figi : str
            FIGI валюты.

        Returns
        ----------
        str
            Тикер валюты.
        """
        for key, value in all_figi.items():
            if value == figi:
                return key[1]
        return None

    def get_info_about_currency_by_ticker(self, ticker: str) -> Optional[dict]:
        """
        Получение информации о валюте по её тикеру.

        Parameters
        ----------
        ticker : str
            Тикер валюты.

        Returns
        ----------
        Optional[dict]
            Информация о валюте или сообщение об ошибке, если произошла ошибка.
        """
        with Client(self.token) as client:
            try:
                figi = self.get_figi_by_ticker(ticker)
                instrument = client.instruments.currency_by(id=figi,
                                                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
                return instrument
            except Exception as e:
                return f"В функции get_info_about_currency_by_ticker \n {e}"

    def get_info_about_currency_by_figi(self, figi: str) -> Optional[dict]:
        """
        Получение информации о валюте по её FIGI.

        Parameters
        ----------
        figi : str
            FIGI валюты.

        Returns
        ----------
        Optional[dict]
            Информация о валюте или сообщение об ошибке, если произошла ошибка.
        """
        with Client(self.token) as client:
            try:
                instrument = client.instruments.currency_by(id=figi,
                                                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
                return instrument
            except Exception as e:
                return f"В функции get_info_about_currency_by_figi \n {e}"

    def get_current_price_by_figi(self, figi: str) -> float:
        """
        Получение текущей цены валюты по FIGI.

        Parameters
        ----------
        figi : str
            FIGI инструмента.

        Returns
        ----------
        float
            Текущая цена валюты в рублях.
        """
        with Client(self.token) as client:
            instrument = client.instruments.currency_by(id=figi,
                                                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
            ticker = self.get_ticker_by_figi(figi)
            if not (self.is_metal(figi)):
                rate = self.get_exchange_rate_of_currency(ticker, 'RUB')
            else:
                rate = self.get_exchange_rate_of_metal()
            price_based_currency = instrument.nominal.units + instrument.nominal.nano / 1e9
            price_in_rubles = price_based_currency * rate
            return price_in_rubles

    def get_current_price_by_ticker(self, ticker: str) -> float:
        """
        Получение текущей цены валюты по тикеру.

        Parameters
        ----------
        ticker : str
            Тикер инструмента.

        Returns
        ----------
        float
            Текущая цена валюты в рублях.
        """
        with Client(self.token) as client:
            figi = self.get_figi_by_ticker(ticker)
            instrument = client.instruments.currency_by(id=figi,
                                                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI).instrument
            ticker = self.get_ticker_by_figi(figi)
            if not (self.is_metal(figi)):
                rate = self.get_exchange_rate_of_currency(ticker, 'RUB')
            else:
                rate = self.get_exchange_rate_of_metal()
            price_based_currency = instrument.nominal.units + instrument.nominal.nano / 1e9
            price_in_rubles = price_based_currency * rate
            return price_in_rubles

    def get_all_prices(self) -> Dict[str, float]:
        """
        Получение всех текущих цен валют по их FIGI.

        Returns
        ----------
        Dict[str, float]
            Словарь, где ключи - названия валют, а значения - их текущие цены в рублях.
        """
        data_of_prices = {}
        with Client(self.token) as client:
            for key, value in all_figi.items():
                data_of_prices[key[0]] = self.get_current_price_by_figi(value)
        return data_of_prices

    def get_history_of_current_currency_by_ticker(self, ticker: str, start_time: datetime, end_time: datetime,
                                                  interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_HOUR) -> \
            List[dict]:
        """
        Получение истории цен текущей валюты по её тикеру.

        Parameters
        ----------
        ticker : str
            Тикер валюты.
        start_time : datetime
            Начальное время для запроса истории цен.
        end_time : datetime
            Конечное время для запроса истории цен.
        interval : CandleInterval, optional
            Интервал времени для запроса истории цен, по умолчанию CANDLE_INTERVAL_HOUR.

        Returns
        ----------
        List[dict]
            История цен валюты или сообщение об ошибке, если произошла ошибка.
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
                return f"В функции get_history_of_current_currency_by_ticker \n {e}"

    def get_history_of_current_currency_by_figi(self, figi: str, start_time: datetime, end_time: datetime,
                                                interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_HOUR) -> List[
        dict]:
        """
        Получение истории цен текущей акции по её FIGI.

        Parameters
        ----------
        figi : str
            FIGI акции.
        start_time : datetime
            Начальное время для запроса истории цен.
        end_time : datetime
            Конечное время для запроса истории цен.
        interval : CandleInterval, optional
            Интервал времени для запроса истории цен, по умолчанию CANDLE_INTERVAL_HOUR.

        Returns
        ----------
        List[dict]
            История цен акции или сообщение об ошибке, если произошла ошибка.
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
                return f"В функции get_history_of_current_currency_by_figi \n {e}"

    def create_data_list(self, candles: List[HistoricCandle]) -> List[dict]:
        """
        Создание списка данных из истории цен.

        Parameters
        ----------
        candles : list
            Список исторических свечей.

        Returns
        ----------
        list
            Список данных о ценах.
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

    def convert_to_rubles(self, current_candle: Quotation) -> float:
        """
        Конвертация цены валюты в рубли.

        Parameters
        ----------
        current_candle : HistoricCandle
            Объект с информацией о цене валюты.

        Returns
        ----------
        float
            Цена валюты в рублях.
        """
        return current_candle.units + current_candle.nano / 1e9  # nano - 9 нулей

