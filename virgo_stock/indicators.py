"""Contains classes for technical analysis indicators.

All technical indicators should be initialized with a pandas DataFrame containing data for a stock.
The data frame should have timestamp as index, as well as 5 columns:
    open, high, low, close and volume.
The data frame stores data in reverse order, i.e. the first row is the latest data.
"""
import pandas as pd
from .series import TimeSeries, TimeDataFrame


class IndicatorSeries(TimeSeries):
    """Represents a TimeSeries indicator being calculated from TimeDataFrame stock data
    
    This is the base class for time series indicators, e.g. moving average.
    This is an abstract class and should not be used directly.

    """

    _metadata = ['df']

    def __init__(self, data_frame, name=None):
        """[summary]
        
        Args:
            data_frame: pandas DataFrame or array-like, iterable or list.
            name (str or None): The name for the new column containing the new indicator. 
                If name is None or empty, a name will be generated using default_name()

        """
        # Stores the source data
        self.df = data_frame
        # Determine the name of the column
        if not name:
            name = self.default_name()
        data = self.calculate()
        TimeSeries.__init__(self, data, name=name)
    
    def default_name(self):
        """Generates a default name for the time series data.
        
        The default name will be "Series_1", if it is not already a column in the data frame.
        If "Series_1" is already in the data frame, 
            this method will try "Series_2", "Series_3", etc.
        
        Returns:
            str: The auto-generated name for the time series.
        """
        i = 0
        while True:
            i += 1
            name = "Series_%s" % i
            if not hasattr(self.df, "columns") or name not in self.df.columns:
                return name

    def calculate(self):
        if isinstance(self.df, pd.DataFrame):
            # Returns the first column of a dataframe
            return self.df.ix[:, 0]
        # Returns self.df, this allows self.df to be any array type.
        return self.df

    def local_minimums(self):
        return self[(self.shift(1) > self) & (self.shift(-1) > self)]

    def local_maximums(self):
        return self[(self.shift(1) < self) & (self.shift(-1) < self)]

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
        return crosses

    def breaking_above(self, series):
        """Finds the timestamps where the moving average breaking above another series.

        Args:
            series (pandas.Series): A pandas series.

        Returns:
            list: A list of indices where this series breaking above another series.
        """
        series_n = self
        series_k = series
        return self.series_cross(series_n, series_k)


class IndicatorDataFrame(TimeDataFrame):

    _metadata = ['df']

    def __init__(self, data_frame):
        """Initializes a multi-column time series. 
        Multiple new columns will be added to the data_frame.
        
        Args:
            data_frame (pandas.DataFrame): A pandas data frame containing stock data, 
        """
        self.df = data_frame
        data = self.calculate()
        TimeDataFrame.__init__(self, data)

    def calculate(self):
        raise NotImplementedError()


class MovingAverage(IndicatorSeries):

    _metadata = IndicatorSeries._metadata + ['n_point', 'series_type']

    def __init__(self, data_frame, n_point, series_type='close', name=None):
        """Initialize a moving average object.
        Args:
            data_frame: A pandas data frame containing stock data, 
                The data_frame should have timestamp as index, as well as 5 columns:
                open, high, low, close and volume.
                The data_frame stores data in reverse order.
            n: Number of data points used to calculate each moving average value, 
                corresponds to what is commonly called an "N-day moving average".
            series_type: The price type used to calculate the moving average.
            name: The name of the calculated column in the returned data frame.
        
        """
        self.n_point = n_point
        self.series_type = series_type
        IndicatorSeries.__init__(self, data_frame, name)

    def calculate(self):
        """Calculate the moving average series.
        This method must be implemented in sub-classes.
        """
        raise NotImplementedError()

    def default_name(self):
        """Default name for the moving average column in the data frame.
        """
        return "Moving_Avg_%s" % self.n_point

    @classmethod
    def n_breaking_k(cls, data_frame, n, k):
        """Finds the timestamps where n-day moving average breaking above k-day moving average.
        """
        series_n = cls(data_frame, n)
        series_k = cls(data_frame, k)
        return MovingAverage.series_cross(series_n, series_k)

    @classmethod
    def golden_cross(cls, data_frame, short_term=50, long_term=200):
        """Finds the timestamps where short-term moving average breaking above 
            long-term moving average.
        """
        return data_frame.index[cls.n_breaking_k(data_frame, short_term, long_term)]

    @classmethod
    def death_cross(cls, data_frame, short_term=50, long_term=200):
        """Finds the timestamps where short-term moving average crossing below 
            long-term moving average.
        """
        return data_frame.index[cls.n_breaking_k(data_frame, long_term, short_term)]


class SMA(MovingAverage):
    """Simple Moving Average
    """

    def default_name(self):
        """Default name for the sample moving average column.
        """
        return 'SMA_%s' % self.n_point

    def calculate(self):
        """Calculates the simple moving average.
        
        Returns:
            pandas.Series: a pandas series containing the simple moving average.
        """
        series = self.df[self.series_type][::-1].rolling(self.n_point).mean()[::-1]
        return series


class EMA(MovingAverage):
    """Exponential Moving Average

    See Also:
        http://pandas.pydata.org/pandas-docs/stable/computation.html#exponentially-weighted-windows
    
    """

    def default_name(self):
        """Default name for the exponential moving average column.
        """
        return 'EMA_%s' % self.n_point
    
    def calculate(self):
        """Calculates the exponential moving average.
        
        Returns:
            pandas.Series: a pandas series containing the exponential moving average.
        """
        series = self.df[self.series_type][::-1].ewm(span=self.n_point).mean()[::-1]
        return series


class BollingerSeries(IndicatorSeries):
    """A series which is K times an N-period standard deviation above or below
        the moving average (upper or lower Bollinger Band)

    See Also:
        https://en.wikipedia.org/wiki/Bollinger_Bands
        https://www.bollingerbands.com/bollinger-bands
    """

    _metadata = IndicatorSeries._metadata + ['n_point', 'k_std', 'series_type']

    def __init__(self, data_frame, n_point=20, k_std=2, series_type='close', name=""):
        self.n_point = n_point
        self.k_std = k_std
        self.series_type = series_type
        IndicatorSeries.__init__(self, data_frame, name)

    def default_name(self):
        return 'BB_%s_%+d' % (self.n_point, self.k_std)

    def calculate(self):
        moving_average = self.df[self.series_type][::-1].rolling(self.n_point).mean()[::-1]
        standard_deviation = self.df[self.series_type][::-1].rolling(self.n_point).std()[::-1]
        return moving_average.add(self.k_std * standard_deviation)


class BollingerBands(IndicatorDataFrame):

    _metadata = IndicatorDataFrame._metadata + ['n_point', 'k_std', 'series_type', 'prefix']

    def __init__(self, data_frame, n_point=20, k_std=2, series_type='close', prefix="BB"):
        self.n_point = n_point
        self.k_std = k_std
        self.series_type = series_type
        self.prefix = prefix
        IndicatorDataFrame.__init__(self, data_frame)

    def calculate(self):
        names = [
            self.prefix + "_upper",
            self.prefix + "_lower",
            self.prefix + "_sma",
        ]
        upper = BollingerSeries(self.df, self.n_point, self.k_std, self.series_type)
        lower = BollingerSeries(self.df, self.n_point, -self.k_std, self.series_type)
        sma = SMA(self.df, self.n_point, self.series_type)
        return {
            self.prefix + "_upper": upper,
            self.prefix + "_lower": lower,
            self.prefix + "_sma": sma
        }
