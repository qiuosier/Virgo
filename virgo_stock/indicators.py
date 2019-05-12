"""Contains classes for technical analysis indicators.

All technical indicators should be initialized with a pandas DataFrame containing data for a stock.
The data frame should have timestamp as index, as well as 5 columns, open, high, low, close and volume.
The data frame stores data in reverse order, i.e. the first row is the latest data.
"""
import pandas as pd


class TimeSeries:
    """Represents a Time Series Indicator, with data stored in a pandas data frame.
    
    This is the base class for time series indicators, e.g. moving average.
    This is an abstract class and should not be used directly.

    """
    def __init__(self, data_frame, name=None):
        self.df = data_frame
        # Determine the name of the column
        self.name = name
        if not self.name:
            self.name = self.default_name()
    
    def default_name(self):
        """Generates a default name for the time series data.
        
        The default name will be "Series_1", if it is not already a column in the data frame.
        If "Series_1" is already in the data frame, this method will try "Series_2", "Series_3", etc.
        
        Returns:
            str: The auto-generated name for the time series.
        """
        i = 0
        while True:
            i += 1
            name = "Series_%s" % i
            if name not in self.df.columns:
                return name
        return None

    @property
    def series(self):
        """The pandas series (with datetime index) of the calculated indicator.
        """
        raise NotImplementedError()

    def calculate(self):
        raise NotImplementedError()


class SingleSeries(TimeSeries):
    """Represents a time series indicator with single series of data.

    This class is not intended to be used directly.
    The calculate() method in this class does not do any calculation.
    Instead, it creates a series with None as the values.
    Initializing this class with a data frame will add an column with None values to the data frame.
    
    """
    def __init__(self, data_frame, series_type='close', name=None):
        """Initializes a time series. A new column will be added to the data_frame.
        
        Args:
            data_frame (pandas.DataFrame): A pandas data frame containing stock data, 
            series_type (str, optional): The name of the data column to be used in calculating the new indicator. 
                Defaults to 'close'.
            name (str or None, optional): The name for the new column containing the new indicator. 
                Defaults to None.
        """
        super().__init__(data_frame, name)
        self.series_type = series_type
        # Calculate the indicator
        self.df[self.name] = self.calculate()

    def calculate(self):
        """Creates an empty time series.
        
        Returns:
            pandas.Series: Empty series.
        """
        return pd.Series([None] * len(self.df), index=self.df.index)
    
    @property
    def series(self):
        """The pandas series (with datetime index) of the calculated indicator.
        
        Returns:
            pandas.Series: One-dimensional ndarray with datetime as axis label
        """
        return self.df.loc[:, self.name]

    @staticmethod
    def series_cross(series_n, series_k):
        """Finds the indices where series_n breaking above series_k.

        Args:
            series_n (pandas.Series): A pandas series
            series_k (pandas.Series): A pandas series
            series_n and series_k should have the same index.

        Returns:
            list: A list of indices where series_n breaking above series_k.

        """
        crosses = []
        for i in range(0, len(series_n.index) - 1):
            if series_n[i + 1] < series_k[i + 1] and series_n[i] > series_k[i]:
                crosses.append(i)
        return series_n.index[crosses]


class MultiSeries(TimeSeries):
    def __init__(self, data_frame, series_type='close', prefix=None):
        """Initializes a multi-column time series. Multiple new columns will be added to the data_frame.
        
        Args:
            data_frame (pandas.DataFrame): A pandas data frame containing stock data, 
            series_type (str, optional): The name of the data column to be used in calculating the new indicator. 
                Defaults to 'close'.
            name (str or None, optional): The name for the new column containing the new indicator. 
                Defaults to None.
        """
        self.df = data_frame
        self.series_type = series_type
        # Determine the name of the column
        self.name = prefix
        if not self.name:
            self.name = self.default_name()
        self.names = []
        self.calculate()

    @property
    def prefix(self):
        return self.name

    @property
    def series(self):
        """The pandas series (with datetime index) of the calculated indicator.
        
        Returns:
            pandas.Series: One-dimensional ndarray with datetime as axis label
        """
        return self.df.loc[:, self.names]


class MovingAverage(SingleSeries):
    def __init__(self, data_frame, n, series_type='close', name=None):
        """Initialize a moving average object.
        Args:
            data_frame: A pandas data frame containing stock data, 
                The data_frame should have timestamp as index, as well as 5 columns, open, high, low, close and volume.
                The data_frame stores data in reverse order.
            n: Number of data points used to calculate each moving average value, 
                corresponds to what is commonly called an "N-day moving average".
            series_type: The price type used to calculate the moving average.
            name: The name of the calculated column in the returned data frame.
        
        """
        self.n = n
        super().__init__(data_frame, series_type, name)

    def calculate(self):
        """Calculate the moving average series.
        This method must be implemented in sub-classes.
        """
        raise NotImplementedError()

    def default_name(self):
        """Default name for the moving average column in the data frame.
        """
        return "Moving_Avg_%s" % self.n

    def breaking_above(self, series):
        """Finds the timestamps where the moving average breaking above another series.

        Args:
            series (pandas.Series): A pandas series.

        Returns:
            list: A list of indices where this series breaking above another series.
        """
        series_n = self.series
        series_k = series
        return self.series_cross(series_n, series_k)

    @classmethod
    def n_breaking_k(cls, data_frame, n, k):
        """Finds the timestamps where n-day moving average breaking above k-day moving average.
        """
        series_n = cls(data_frame, n).series
        series_k = cls(data_frame, k).series
        return MovingAverage.series_cross(series_n, series_k)

    @classmethod
    def golden_cross(cls, data_frame, short_term=50, long_term=200):
        """Finds the timestamps where short-term moving average breaking above long-term moving average.
        """
        return cls.n_breaking_k(data_frame, short_term, long_term)

    @classmethod
    def death_cross(cls, data_frame, short_term=50, long_term=200):
        """Finds the timestamps where short-term moving average crossing below long-term moving average.
        """
        return cls.n_breaking_k(data_frame, long_term, short_term)



class SMA(MovingAverage):
    """Simple Moving Average
    """

    def default_name(self):
        """Default name for the sample moving average column.
        """
        return 'SMA_%s' % self.n

    def calculate(self):
        """Calculates the simple moving average.
        
        Returns:
            pandas.Series: a pandas series containing the simple moving average.
        """
        series = self.df[self.series_type][::-1].rolling(self.n).mean()[::-1]
        return series


class EMA(MovingAverage):
    """Exponential Moving Average

    See Also:
        http://pandas.pydata.org/pandas-docs/stable/computation.html#exponentially-weighted-windows
    
    """

    def default_name(self):
        """Default name for the exponential moving average column.
        """
        return 'EMA_%s' % self.n
    
    def calculate(self):
        """Calculates the exponential moving average.
        
        Returns:
            pandas.Series: a pandas series containing the exponential moving average.
        """
        series = self.df[self.series_type][::-1].ewm(span=self.n).mean()[::-1]
        return series


class BollingerSeries(SingleSeries):
    """A series which is K times an N-period standard deviation above or below the moving average (upper or lower Bollinger Band)

    See Also:
        https://en.wikipedia.org/wiki/Bollinger_Bands
        https://www.bollingerbands.com/bollinger-bands
    """
    def __init__(self, data_frame, n_day=20, k_std=2, series_type='close', name=None):
        self.n_day = n_day
        self.k_std = k_std
        super().__init__(data_frame, series_type, name)

    def default_name(self):
        return 'BB_%s_%+d' % (self.n_day, self.k_std)

    def calculate(self):
        moving_average = self.df[self.series_type][::-1].rolling(self.n_day).mean()[::-1]
        standard_deviation = self.df[self.series_type][::-1].rolling(self.n_day).std()[::-1]
        return moving_average.add(self.k_std * standard_deviation)


class BollingerBands(MultiSeries):
    def __init__(self, data_frame, n_day=20, k_std=2, series_type='close', prefix=None):
        self.n_day = n_day
        self.k_std = k_std
        super().__init__(data_frame, series_type, prefix)

    def default_name(self):
        return 'BB_%s_%d' % (self.n_day, self.k_std)

    def calculate(self):
        self.names = [
            self.prefix + "_upper",
            self.prefix + "_lower",
            self.prefix + "_sma",
        ]
        upper = BollingerSeries(self.df, self.n_day, self.k_std, self.series_type, self.names[0])
        lower = BollingerSeries(self.df, self.n_day, -self.k_std, self.series_type, self.names[1])
        sma = SMA(self.df, self.n_day, self.series_type, self.names[2])
        return [upper, sma, lower]
