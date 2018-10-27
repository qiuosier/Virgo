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

    def sma(self, n=10, series_type='close', column_name=None):
        """Simple Moving Average

        Args:
            n: Number of data points used to calculate each moving average value.
            series_type: The price type used to calculate the moving average.
            column_name:

        Returns:

        """
        values = [None] * len(self.df)
        ret = np.cumsum(np.flip(self.df[series_type].values, 0), dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        values[n - 1:] = ret[n - 1:] / n
        values.reverse()
        if column_name is None:
            column_name = 'sma_%s' % n
        df = pd.DataFrame(OrderedDict([
            ('timestamp', self.df['timestamp'].copy()),
            (column_name, pd.Series(values, index=self.df.index)),
        ]))
        df.set_index('timestamp', inplace=True)
        return df
