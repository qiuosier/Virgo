import os
import pandas as pd
import datetime
import logging
logger = logging.getLogger(__name__)


class DataSourceInterface:
    def get_daily_series(self, symbol, start=None, end=None):
        """Gets a pandas data frame of daily stock data.

        Args:
            symbol: The name of the equity/stock.
            start: Starting date for the time series, e.g. 2017-01-21.
            end: Ending date for the time series, e.g. 2017-02-22.

        If start is None, all data up to the end date will be returned.
        If end is None, all data from the start date to current date will be returned.
        All available data will be returned both start and end are None.

        Returns: A pandas data frame of time series data.
        """
        raise NotImplementedError()


class AlphaVantage(DataSourceInterface):

    def __init__(self, api_key, cache_folder=None):
        self.api_key = api_key
        self.cache = cache_folder

    def get_daily_series(self, symbol, start=None, end=None):
        """Gets a pandas data frame of daily stock data.
        The data frame will contain 9 columns:
            timestamp, open, high, low, close, adjusted_close, volume, dividend_amount, and split_coefficient

        Args:
            symbol: The symbol of the equity/stock.
            start: Starting date for the time series, e.g. 2017-01-21.
            end: Ending date for the time series, e.g. 2017-02-22.

        If start is None, all data up to the end date will be returned.
        If end is None, all data from the start date to current date will be returned.
        All available data will be returned both start and end are None.

        Returns: A pandas data frame of time series data.

        """
        if start is None:
            start = "1800-01-01"
        if end is None:
            end = datetime.datetime.now().strftime("%Y-%m-%d")

        if self.cache:
            file_path = self.__cache_file_path(symbol)
            if os.path.exists(file_path):
                print("Reading existing data...")
                df = pd.read_csv(file_path, index_col=0, parse_dates=['timestamp'])
            else:
                df = self._request_data(symbol, 'full')
                print("Caching data...")
                df.to_csv(file_path)

        else:
            df = self._request_data(symbol, 'full')

        df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        return df

    def __cache_file_path(self, symbol):
        table_name = "%s_%s" % (symbol, "DAILY")
        filename = "%s_%s.csv" % (table_name, datetime.datetime.now().strftime("%Y%m%d"))
        file_path = os.path.join(self.cache, filename)
        return file_path

    def _request_data(self, symbol, output_size="compact"):
        """Requests data from AlphaVantage Server

        Args:
            symbol: The symbol of the equity/stock.
            output_size: compact or full

        Returns: A pandas data frame of time series data.

        """
        print("Requesting Data...")
        series_type = "TIME_SERIES_DAILY_ADJUSTED"
        url = "https://www.alphavantage.co/query?apikey=%s&symbol=%s&function=%s&datatype=csv&outputsize=%s" \
              % (
                  self.api_key,
                  symbol,
                  series_type,
                  output_size,
              )
        logger.info("Requesting %s data..." % symbol)
        df = pd.read_csv(url, parse_dates=["timestamp"], infer_datetime_format=True)
        return df
