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

    def get_intraday_series(self, symbol, date=None):
        raise NotImplementedError()


class AlphaVantage(DataSourceInterface):

    intraday_time_fmt = "_%Y-%m-%d_%H%M"
    date_fmt = "%Y-%m-%d"

    def __init__(self, api_key, cache_folder=None):
        self.api_key = api_key
        self.cache = cache_folder
        if not os.path.exists(self.cache):
            os.makedirs(self.cache)
        self.intraday_cache_expiration = 30

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
            end = datetime.datetime.now().strftime(self.date_fmt)

        df = self.__get_daily_data(symbol)

        df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        return df

    def __get_daily_data(self, symbol):
        series_type = "TIME_SERIES_DAILY_ADJUSTED"
        if self.cache:
            file_path = self.__cache_file_path(symbol, series_type)
            if os.path.exists(file_path):
                print("Reading existing data...")
                df = pd.read_csv(file_path, index_col=0, parse_dates=['timestamp'])
            else:
                df = self.__request_data(symbol, series_type, 'full')
                print("Saving data...")
                df.to_csv(file_path)
        else:
            df = self.__request_data(symbol, series_type, 'full')
        return df

    def get_intraday_series(self, symbol, date=None):
        """

        Args:
            symbol:
            date:

        Returns:

        """
        requested_date = date
        if date is None:
            date = datetime.datetime.now().strftime(self.date_fmt)

        dt_date = datetime.datetime.strptime(date, self.date_fmt)
        dt_next = dt_date.date() + datetime.timedelta(days=1)
        next_date = dt_next.strftime(self.date_fmt)

        series_type = "TIME_SERIES_INTRADAY"
        if self.cache:
            file_path = self.__cache_file_path(symbol, series_type, date)
            if os.path.exists(file_path):
                print("Reading existing data...")
                df = pd.read_csv(file_path, index_col=0, parse_dates=['timestamp'])
            else:
                df = self.__intraday_get_full_data(symbol)
                df = df[(df['timestamp'] >= date) & (df['timestamp'] < next_date)]
        else:
            df = self.__request_data(symbol, series_type, 'full')
            df = df[(df['timestamp'] >= date) & (df['timestamp'] < next_date)]

        # When date is not specified, try to get data of the previous day if there is no data today
        if df.empty and requested_date is None:
            prev_date = (dt_date - datetime.timedelta(days=1)).strftime(self.date_fmt)
            df = self.get_intraday_series(symbol, prev_date)
        return df

    def __intraday_get_full_data(self, symbol):
        series_type = "TIME_SERIES_INTRADAY"
        cached_file = self.__intraday_cache_valid(symbol)
        if cached_file:
            df = pd.read_csv(cached_file, index_col=0, parse_dates=['timestamp'])
        else:
            df = self.__request_data(symbol, series_type, 'full', interval="1min")
            file_path = self.__intraday_cache_path_prefix(symbol) \
                + datetime.datetime.now().strftime(self.intraday_time_fmt)
            print("Saving data...")
            df.to_csv(file_path)
            groups = df.groupby(df['timestamp'].dt.normalize())
            for name, group in groups:
                date = str(name).split(" ")[0]
                if not group[group.timestamp == date + " 16:00:00"].empty:
                    date_file_path = self.__cache_file_path(symbol, series_type, date)
                    group.reset_index(drop=True).to_csv(date_file_path)
        return df

    def __intraday_cache_valid(self, symbol):
        cached_files = self.__intraday_cache_files(symbol)
        if cached_files:
            cached_files.sort(reverse=True)
            cached_file = None
            cached_time = None
            # Clean up the cache
            for f in cached_files:
                if cached_file is None:
                    cached_time = self.__intraday_parse_time_from_filename(f)
                    if cached_time:
                        cached_file = f
                else:
                    os.remove(f)
            if cached_time:
                if cached_time + datetime.timedelta(minutes=self.intraday_cache_expiration) > datetime.datetime.now():
                    return cached_file
        return None

    def __intraday_cache_files(self, symbol):
        prefix = self.__intraday_cache_file_prefix(symbol)
        cached_files = []
        for f in os.listdir(self.cache):
            filename = os.path.join(self.cache, f)
            if f.startswith(prefix) and os.path.isfile(filename):
                cached_files.append(filename)
        return cached_files

    def __intraday_parse_time_from_filename(self, filename):
        time_str = filename.split(".")[0].split("cached", 1)[1]
        try:
            parsed_time = datetime.datetime.strptime(time_str, self.intraday_time_fmt)
        except ValueError:
            parsed_time = None
        return parsed_time

    def __intraday_cache_file_prefix(self, symbol):
        series_type = "TIME_SERIES_INTRADAY"
        prefix = "%s_%s_cached" % (symbol.upper(), series_type)
        return prefix

    def __intraday_cache_path_prefix(self, symbol):
        path_prefix = os.path.join(self.cache, self.__intraday_cache_file_prefix(symbol))
        return path_prefix

    def __cache_file_path(self, symbol, series_type, date=None):
        """

        Args:
            symbol:
            series_type:
            date:

        Returns:

        """
        if date is None:
            date = datetime.datetime.now().strftime(self.date_fmt)
        filename = "%s_%s_%s.csv" % (symbol.upper(), series_type, date)
        file_path = os.path.join(self.cache, filename)
        return file_path

    def __request_data(self, symbol, series_type, output_size="compact", **kwargs):
        """Requests data from AlphaVantage Server

        Args:
            symbol: The symbol of the equity/stock.
            output_size: compact or full

        Returns: A pandas data frame of time series data.

        """
        print("Requesting Data...")
        url = "https://www.alphavantage.co/query?apikey=%s&symbol=%s&function=%s&datatype=csv&outputsize=%s" \
              % (
                  self.api_key,
                  symbol,
                  series_type,
                  output_size,
              )
        for k, v in kwargs.items():
            url += "&%s=%s" % (k, v)
        logger.info("Requesting %s data..." % symbol)
        df = pd.read_csv(url, parse_dates=["timestamp"], infer_datetime_format=True)
        return df
