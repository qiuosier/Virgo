import os
import io
import pandas as pd
import datetime
import logging
from .alpha_vantage import AlphaVantageAPI
logger = logging.getLogger(__name__)


class DataSourceInterface:
    """Provides methods for getting daily and intraday series data.
    Subclasses must implement:
        1. get_daily_series()
        2. get_intraday_series().
    Both methods should return a pandas data frame of time series data.
    The returned pandas dataframe should:
        1. Use decending timestamp as index, 
            i.e. use the latest timestamp as the first data point index in the data frame.
        2. Have at least the following 5 columns: open, high, low, close and volume

    See Also: 
    pandas times series, https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
    
    Raises:
        NotImplementedError: get_daily_series() or get_intraday_series() is not implemented.

    """
    def get_daily_series(self, symbol, start=None, end=None):
        """Gets a pandas data frame of daily stock data.

        Args:
            symbol: The name of the equity/stock.
            start: Starting date for the time series, e.g. 2017-01-21.
            end: Ending date for the time series, e.g. 2017-02-22.

        If start is None, all data up to the end date will be returned.
        If end is None, all data from the start date to current date will be returned.
        All available data will be returned both start and end are None.

        Returns: A pandas data frame of daily series data.
        """
        raise NotImplementedError()

    def get_intraday_series(self, symbol, date=None):
        """Gets a pandas data frame of intraday stock data.
        
        Args:
            symbol (str): The name of the equity/stock.
            date (str, optional): Date, e.g. 2017-02-12. Defaults to None.

        Data of the most recent trading day (including today) will be returned if "date" is None.

        Returns: A pandas data frame of intraday series data.
        """
        raise NotImplementedError()


class AlphaVantage(DataSourceInterface):
    """Implements the DataSourceInterface by getting data from AlphaVantage

    See Also: https://www.alphavantage.co/

    Data Cache:
    A cache data folder can be specified when initializing this data source.
    CSV file containing the series will be saved into the cache data folder.
    Mainly there are two types of cache data: TIME_SERIES_DAILY_ADJUSTED and INTRADAY.

    When cache folder is specified:
        When daily data is requested for the first time in a day. 
        The full TIME_SERIES_DAILY_ADJUSTED data will be requested from the server.
        The cached data will be re-used in the same day.
        The full daily data from the server always contain all the historical data.
        Old daily data cache files can be deleted when a new file is generated.
        
        When intraday data is first requested, the INTRADAY data will be requested from the server.
        The cached data for today will be re-used in 30 minutes.
        Cached data for past days will always be re-used.
        The cached data will be saved in a file with filename containing "cached".
        This file will be referred as "temporary" file in this class.
        This file usually contains intraday data for the last a few days.
        The intraday data from AlphaVantage contains data for the last a few days only.
        The caching process also extracts intraday data for each day from the "cached" file.
        The intraday data for each day will be saved as an independent CSV file.
        These independent data files can be useful in the future,
             when the response from server on longer contain the data for "old days".
    
    """

    intraday_time_fmt = "_%Y-%m-%d_%H%M"
    date_fmt = "%Y-%m-%d"

    def __init__(self, api_key, cache_folder=None):
        """Initialize the AlphaVantage Data Source
        
        Args:
            api_key (str): AlphaVantage API key.
            cache_folder (str, optional): Path to local cache data folder. Defaults to None.
                CSV file containing the series will be saved into the cache_folder
        """
        self.api_key = api_key
        self.cache = cache_folder
        if self.cache and not os.path.exists(self.cache):
            os.makedirs(self.cache)

        self.web_api = AlphaVantageAPI(api_key, datatype="csv")

        # Expiration time for daily cache data (days)
        self.daily_cache_expiration = 1
        # Expiration time for intraday cache data (minutes)
        self.intraday_cache_expiration = 30
        

    def __request_data(self, symbol, series_type, output_size="compact", **kwargs):
        """Requests data from AlphaVantage Server.
        This function read data directly from HTTP response.

        Args:
            symbol: The symbol of the equity/stock.
            output_size: "compact" or "full".
            kwargs: Additional query strings as key value pairs.
            
        See Also: https://www.alphavantage.co/documentation/

        Returns: A pandas data frame of time series data.

        """
        kwargs.update({
            "symbol": symbol,
            "function": series_type,
            "outputsize": output_size,
        })
        
        logger.info("Requesting %s data..." % symbol)
        df = self.web_api.get_dataframe(**kwargs)
        return df

    def __cache_file_path(self, symbol, series_type, date=None):
        """Generates the cache file path.

        This class determine whether the data is cached by checking whether the cache file exists.
        For daily data, the file contains all historical data.
        For intraday data, the file contains the data for a single day.
        This class uses an additional temporary cache file for intraday data that are available.

        Args:
            symbol (str): The symbol of the equity/stock.
            series_type (str): Type of the data series. 
                This is the same as the AlphaVantage "function" parameter.
            date: The date of the data, e.g. 2017-01-21.

        Returns (str): Cache data file path.

        """
        if date is None:
            date = datetime.datetime.now().strftime(self.date_fmt)
        filename = "%s_%s_%s.csv" % (symbol.upper(), series_type, date)
        file_path = os.path.join(self.cache, filename)
        return file_path

    def get_daily_series(self, symbol, start=None, end=None):
        """
        Gets a pandas data frame of daily series data.
        The data frame will contain timestamp index and 8 columns:
            open, high, low, close, adjusted_close, volume, dividend_amount, and split_coefficient

        Args:
            symbol (str): The symbol of the equity/stock.
            start (str): Starting date for the time series, e.g. 2017-01-21.
            end (str): Ending date for the time series, e.g. 2017-02-22.

        If start is None, all data up to the end date will be returned.
        If end is None, all data from the start date to current date will be returned.
        All available data will be returned both start and end are None.

        Returns: A pandas data frame of time series data.

        """
        # Sets the default values for start and end.
        if start is None:
            start = "1800-01-01"
        if end is None:
            end = datetime.datetime.now().strftime(self.date_fmt)

        df = self.__get_daily_data(symbol)

        df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        df.set_index('timestamp', inplace=True)
        return df

    def __get_daily_data(self, symbol):
        """Gets all daily data as a panda data frame.
        
        Args:
            symbol (str): The symbol of the equity/stock.
        
        Returns: A pandas data frame of all daily series data.
        """
        series_type = "TIME_SERIES_DAILY_ADJUSTED"
        if self.cache:
            file_path = self.__get_daily_cached_file(symbol)
            if file_path:
                logger.debug("Reading existing data... %s" % file_path)
                df = pd.read_csv(file_path, index_col=0, parse_dates=['timestamp'])
            else:
                df = self.__request_data(symbol, series_type, 'full')
                logger.debug("Saving data... %s" % file_path)
                df.to_csv(file_path)
        else:
            # Request data from server if no cache
            df = self.__request_data(symbol, series_type, 'full')
        return df

    def __get_daily_cached_file(self, symbol):
        """Gets the latest un-expired cache file for daily data.
        
        Args:
            symbol (str): The symbol of the equity/stock.
        
        Returns:
            str: File path if an un-expired cache file exists. Otherwise None.
        """
        series_type = "TIME_SERIES_DAILY_ADJUSTED"
        for i in range(self.daily_cache_expiration):
            d = datetime.datetime.now() - datetime.timedelta(days=i)
            file_path = self.__cache_file_path(symbol, series_type, d.strftime(self.date_fmt))
            if os.path.exists(file_path):
                return file_path
        return None

    def get_intraday_series(self, symbol, date=None):
        """Gets a pandas data frame of intraday series data.

        Args:
            symbol (str): The name of the equity/stock.
            date (str, optional): Date, e.g. 2017-02-12. Defaults to None.

        Returns: A pandas data frame of intraday series data.
            This function will return None,
            if date is None and there is no data available in the last 100 days.

        """
        series_type = "TIME_SERIES_INTRADAY"
        # requested_date stores the original requested date
        requested_date = date
        day_delta = 0
        df = None
        # When date is not specified, try to get data of the previous day if there is no data today
        while df is None or (requested_date is None and df.empty and day_delta < 100):
            if requested_date is None:
                date = (datetime.datetime.now() - datetime.timedelta(days=day_delta)).strftime(self.date_fmt)
            logger.debug("Getting data for %s" % date)
            # Get the next date as string for filtering purpose
            dt_date = datetime.datetime.strptime(date, self.date_fmt)
            dt_next = dt_date.date() + datetime.timedelta(days=1)
            next_date = dt_next.strftime(self.date_fmt)

            if self.cache:
                # Check if data has been cached.
                file_path = self.__cache_file_path(symbol, series_type, date)
                if os.path.exists(file_path):
                    logger.debug("Reading existing data... %s" % file_path)
                    df = pd.read_csv(file_path, index_col=0, parse_dates=['timestamp'])
                else:
                    df = self.__intraday_get_full_data(symbol)
                    df = df[(df['timestamp'] >= date) & (df['timestamp'] < next_date)]
            else:
                # Request new data
                df = self.__request_data(symbol, series_type, 'full')
                df = df[(df['timestamp'] >= date) & (df['timestamp'] < next_date)]

            day_delta += 1
        
        if df is not None:
            df.set_index('timestamp', inplace=True)

        return df

    def __intraday_get_full_data(self, symbol):
        """Gets the most recent intraday data (which may include data of multiple days.)
        
        Args:
            symbol (str): The symbol of the equity/stock.
        
        Returns: A pandas data frame of intraday series data.
        
        """
        series_type = "TIME_SERIES_INTRADAY"
        cached_file = self.__intraday_valid_cache(symbol)
        if cached_file:
            df = pd.read_csv(cached_file, index_col=0, parse_dates=['timestamp'])
        else:
            df = self.__request_data(symbol, series_type, 'full', interval="1min")
            file_path = os.path.join(self.cache, self.__intraday_cache_file_prefix(symbol)) \
                + datetime.datetime.now().strftime(self.intraday_time_fmt)
            logger.debug("Saving intraday data...")
            df.to_csv(file_path)
            groups = df.groupby(df['timestamp'].dt.normalize())
            for name, group in groups:
                date = str(name).split(" ")[0]
                if not group[group.timestamp == date + " 16:00:00"].empty:
                    date_file_path = self.__cache_file_path(symbol, series_type, date)
                    group.reset_index(drop=True).to_csv(date_file_path)
        return df

    def __intraday_valid_cache(self, symbol):
        """Checks if the temporary cache data file for intraday data is expired.
        
        Args:
            symbol (str): The symbol of the equity/stock.
        
        Returns:
            str or None: file path of a valid cache file, or None.
        """
        cached_files = self.__intraday_cache_files(symbol)
        if cached_files:
            cached_files.sort(reverse=True)
            cached_file = None
            cached_time = None
            # Remove the temporary cache files except the latest one.
            for f in cached_files:
                if cached_file is None:
                    cached_time = self.__intraday_parse_time_from_filename(f)
                    if cached_time:
                        cached_file = f
                else:
                    os.remove(f)
            # Return the latest cache file if it is not expired.
            if cached_time:
                if cached_time + datetime.timedelta(minutes=self.intraday_cache_expiration) > datetime.datetime.now():
                    return cached_file
        return None

    def __intraday_cache_files(self, symbol):
        """Gets all temporary cache data file for intraday data.
        
        Args:
            symbol (str): The symbol of the equity/stock.
        
        Returns:
            list: A list of file paths.
        """
        prefix = self.__intraday_cache_file_prefix(symbol)
        cached_files = []
        for f in os.listdir(self.cache):
            file_path = os.path.join(self.cache, f)
            if f.startswith(prefix) and os.path.isfile(file_path):
                cached_files.append(file_path)
        return cached_files

    def __intraday_parse_time_from_filename(self, filename):
        """Parses the time information from intraday cache filename.
        
        Args:
            filename (str): filename of a temporary intraday cache file.
        
        Returns:
            datetime or None: datetime of cache file.
        """
        time_str = filename.split(".")[0].split("cached", 1)[1]
        try:
            parsed_time = datetime.datetime.strptime(time_str, self.intraday_time_fmt)
        except ValueError:
            parsed_time = None
        return parsed_time

    def __intraday_cache_file_prefix(self, symbol):
        """Generate file name prefix for intraday temporary cache file.
        This file may contain intraday data of multiple days.
        
        Args:
            symbol (str): The symbol of the equity/stock.
        
        Returns (str): prefix for the temporary file name.
        """
        series_type = "TIME_SERIES_INTRADAY"
        prefix = "%s_%s_cached" % (symbol.upper(), series_type)
        return prefix
