import datetime
from virgo_stock.source import DataSourceInterface


class Stock:
    def __init__(self, symbol, data_source):
        """

        Args:
            symbol (str):
            data_source (DataSourceInterface):
        """
        self.symbol = symbol
        self.data_source = data_source
        self.__daily_series = None

    def daily_series(self, start=None, end=None):
        if not self.__daily_series:
            self.__daily_series = self.data_source.get_daily_series(self.symbol)

        if start is None:
            start = "1800-01-01"
        if end is None:
            end = datetime.datetime.now().strftime("%Y-%m-%d")

        df = self.__daily_series[
            (self.__daily_series['timestamp'] >= start) & (self.__daily_series['timestamp'] <= end)
        ]

        return df

    def weekly_series(self):
        raise NotImplementedError

    def monthly_series(self):
        raise NotImplementedError
