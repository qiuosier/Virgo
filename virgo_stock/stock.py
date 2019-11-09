import datetime
import pandas as pd
from collections import OrderedDict


class DataPoint:
    """Represents a stock data point, which contains the open, high, low, close, and volume over a certain period.

    """
    def __init__(self, timestamp, val_open, val_high, val_low, val_close, volume):
        """Initializes a data point.

        Args:
            timestamp: The timestamp for the data point.
            val_open (float): The open value.
            val_high (float: The high value.
            val_low (float): The low value.
            val_close (float): The close value
            volume (int): The volume value.
        """
        self.timestamp = timestamp
        self.open = val_open
        self.high = val_high
        self.low = val_low
        self.close = val_close
        self.volume = volume

    def __str__(self):
        return "%s , Open: %s, High: %s, Low: %s, Close: %s, Vol: %s" % (
            self.timestamp, self.open, self.high, self.low, self.close, self.volume
        )

    @classmethod
    def from_list(cls, data_point_list):
        """Initializes a data point by aggregating a list of data point to a single data point.
        The timestamp of the aggregated data point will be the timestamp of the first data point.
        The open, high, low, close and volume will be aggregated from all the data points in the list, i.e.
            open: the open of the first data point;
            high: the highest high in the data points;
            low: the lowest low in the data points;
            close: the close of the last data point;
            volume: the sum of the volumes of all data points.

        Args:
            data_point_list (list): A list of DataPoint objects.

        Returns: A DataPoint object.

        """
        if len(data_point_list) == 0:
            raise ValueError("The data point list is empty.")
        timestamp = data_point_list[0].timestamp
        val_open = data_point_list[0].open
        val_close = data_point_list[-1].close
        val_high = data_point_list[0].high
        val_low = data_point_list[0].low
        volume = 0
        for p in data_point_list:
            volume += p.volume
            if p.high > val_high:
                val_high = p.high
            if p.low < val_low:
                val_low = p.low
        return cls(timestamp, val_open, val_high, val_low, val_close, volume)


class Stock:
    def __init__(self, symbol, data_source):
        """Initializes a Stock object.

        Args:
            symbol (str): symbol: The symbol of the equity/stock.
            data_source (DataSourceInterface): A data source object for obtaining the data.
        """
        self.symbol = symbol
        self.data_source = data_source
        self.__daily_series = None

    @staticmethod
    def __format_date_range(start, end):
        """Sets the start and/or end date if not specified.
        
        Args:
            start (str): Starting date.
            end (str): Ending date.
        
        Returns:
            (str, str): (start, end)
        """
        if start is None:
            start = "1800-01-01"
        if end is None:
            end = datetime.datetime.now().strftime("%Y-%m-%d")
        return start, end

    def daily_series(self, start=None, end=None):
        """Gets a pandas data frame of daily stock data series.

        Args:
            start: Starting date for the time series, e.g. 2017-01-21.
            end: Ending date for the time series, e.g. 2017-02-22.

        Returns:
            A pandas data frame with daily timestamp as index, as well as 5 columns: open, high, low, close and volume.

        """

        return self.data_source.get_daily_series(self.symbol, start, end)

    def intraday_series(self, date=None):
        return self.data_source.get_intraday_series(self.symbol, date)

    def __aggregate_series(self, trans_func, start=None, end=None):
        """Gets a pandas data frame of aggregated stock data series.

        Args:
            trans_func: A function transforms the timestamp to a string value.
                Rows (data points) with the same transformed value will be aggregated to one row (single data point).
            start: Starting date for the time series, e.g. 2017-01-21.
            end: Ending date for the time series, e.g. 2017-02-22.

        Returns:
            A pandas data frame with daily timestamp as index, as well as 5 columns: open, high, low, close and volume.
            The timestamp of returned data point (data frame row) is the first timestamp of the aggregation period.

        """
        attributes = ["open", "high", "low", "close", "volume"]
        start, end = Stock.__format_date_range(start, end)
        df = self.daily_series(start, end)
        # Initialization
        aggregated_points = []
        daily_points = []

        # Loop through the data IN REVERSE ORDER
        # The index may not start from 0 due to the filtering.
        prev_date_transformed = 0
        for timestamp, row in df.iterrows():
            # Try to parse the time stamp if it is not already datetime.
            if 'Timestamp' not in str(type(timestamp)):
                timestamp = datetime.datetime.strptime(str(timestamp), "%Y-%m-%d")
            date_transformed = trans_func(timestamp)

            # A new period starts if the date_transformed is different from the previous date_transformed
            if date_transformed != prev_date_transformed:
                # # Save last period's data as a aggregated point and reset the daily list
                if daily_points:
                    # IMPORTANT: Reverse the daily point list
                    daily_points.reverse()
                    aggregated_dp = DataPoint.from_list(daily_points)
                    aggregated_points.append(aggregated_dp)
                    daily_points = []

            prev_date_transformed = date_transformed
            # Initialize a new daily data point
            dp = DataPoint(timestamp, row["open"], row["high"], row["low"], row["close"], row["volume"])
            daily_points.append(dp)

        # Termination: Save the last aggregated point
        if daily_points:
            # IMPORTANT: Reverse the daily point list
            daily_points.reverse()
            aggregated_dp = DataPoint.from_list(daily_points)
            aggregated_points.append(aggregated_dp)

        # Generate a new data frame from OrderedDict to preserve the order of the columns
        aggregated_df = pd.DataFrame(
            OrderedDict(
                [
                    ("timestamp", pd.Series([p.timestamp for p in aggregated_points]))
                ] + [
                    (attr, pd.Series(getattr(p, attr) for p in aggregated_points))for attr in attributes
                ]
            )
        )
        aggregated_df.set_index("timestamp", inplace=True)
        aggregated_df.symbol = self.symbol
        return aggregated_df

    def weekly_series(self, start=None, end=None):
        """Gets a pandas data frame of weekly stock data series.

        Args:
            start: Starting date for the time series, e.g. 2017-01-21.
            end: Ending date for the time series, e.g. 2017-02-22.

        Returns: A pandas data frame with weekly timestamp as index, 
            as well as 5 columns: open, high, low, close and volume.
            The timestamp of each data point (data frame row) is the first business day of the week.

        """
        def transform_func(timestamp):
            """Transforms a timestamp to a string of year and week of the year, e.g. "2010_25".

            Args:
                timestamp (datetime.datetime): Timestamp to be transformed.

            Returns: A string with year and week of the year separated by "_" of the timestamp

            """
            return "%s_%s" % (timestamp.date().isocalendar()[0], timestamp.date().isocalendar()[1])

        return self.__aggregate_series(transform_func, start, end)

    def monthly_series(self, start=None, end=None):
        """Gets a pandas data frame of monthly stock data series.

        Args:
            start: Starting date for the time series, e.g. 2017-01-21.
            end: Ending date for the time series, e.g. 2017-02-22.

        Returns: A pandas data frame with monthly timestamp as index, 
            as well as 5 columns: open, high, low, close and volume.
            The timestamp of each data point (data frame row) is the first business day of the month.

        """
        def transform_func(timestamp):
            """Transforms a timestamp to a string of year and month, e.g. "2010_11".

            Args:
                timestamp (datetime.datetime): Timestamp to be transformed.

            Returns: A string with year and month separated by "_" of the timestamp

            """
            return "%s_%s" % (timestamp.year, timestamp.month)
        return self.__aggregate_series(transform_func, start, end)
