import numpy as np
import pandas as pd
from collections import OrderedDict


class TimeSeries:
    """Represents stock time series data.

    Attributes:
        df: A pandas data frame including columns of timestamp, open, high, low, close and volume.

    """
    def __init__(self, data_frame):
        """Initializes the TimeSeries with a pandas data frame.

        Args:
            data_frame: A pandas data frame including columns of timestamp, open, high, low, close and volume.

        """
        self.df = data_frame

    def __len__(self):
        return len(self.df)

    def __getitem__(self, item):
        """Extends the slices

        See https://docs.python.org/2.3/whatsnew/section-slices.html
        Args:
            item:

        Returns:

        """
        if isinstance(item, str):
            return self.df[item]
        else:
            return TimeSeries(self.df[item])

    def __timestamp_index(self, series, column_name):
        df = pd.DataFrame(OrderedDict([
            ('timestamp', self.df['timestamp'].copy()),
            (column_name, series),
        ]))
        df.set_index('timestamp', inplace=True)
        return df

    def sma(self, n=10, series_type='close', column_name=None):
        """Simple Moving Average

        Args:
            n: Number of data points used to calculate each moving average value.
            series_type: The price type used to calculate the moving average.
            column_name: The name of the calculated column in the returned data frame.

        Returns: A date frame with one calculate SMA column and timestamp as index.

        """
        if column_name is None:
            column_name = 'SMA_%s' % n

        values = [None] * len(self.df)
        ret = np.cumsum(np.flip(self.df[series_type].values, 0), dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        values[n - 1:] = ret[n - 1:] / n
        values.reverse()
        series = pd.Series(values, index=self.df.index)

        return self.__timestamp_index(series, column_name)

    def ema(self, n=12, series_type='close', column_name=None):
        """Exponential Moving Average

        Args:
            n: The EMA Span,  corresponds to what is commonly called an "N-day moving average".
            series_type: The price type used to calculate the moving average.
            column_name: The name of the calculated column in the returned data frame.

        Returns: A date frame with one calculate EMA column and timestamp as index.

        See Also:
            http://pandas.pydata.org/pandas-docs/stable/computation.html#exponentially-weighted-windows

        """
        if column_name is None:
            column_name = 'EMA_%s' % n

        series = self.df[series_type][::-1].ewm(span=n).mean()[::-1]
        return self.__timestamp_index(series, column_name)
