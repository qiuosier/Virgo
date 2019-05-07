class MovingAverage:
    def __init__(self, data_frame):
        """
        TimeSeries stores data in reverse order.
        """
        self.df = data_frame

    def calculate(self, n, series_type='close', name=None):
        raise NotImplementedError()

    def series_cross(self, n, k):
        """Finds the timestamps where n-day moving average breaking above k-day moving average.
        """
        series_n = self.calculate(n)
        series_k = self.calculate(k)
        crosses = []
        for i in range(0, len(self.df) - 1):
            if series_n[i + 1] < series_k[i + 1] and series_n[i] > series_k[i]:
                crosses.append(i)
        return self.df.index[crosses]

    def golden_cross(self, short_term=50, long_term=200):
        """Finds the timestamps where short-term moving average breaking above long-term moving average.
        """
        return self.series_cross(short_term, long_term)

    def death_cross(self, short_term=50, long_term=200):
        """Finds the timestamps where short-term moving average crossing below long-term moving average.
        """
        return self.series_cross(long_term, short_term)



class SMA(MovingAverage):
    """Simple Moving Average"""

    def calculate(self, n, series_type='close', name=None):
        if name is None:
            name = 'SMA_%s' % n
        series = self.df[series_type][::-1].rolling(n).mean()[::-1]
        self.df[name] = series
        return self.df.loc[:, name]


class EMA(MovingAverage):
    """Exponential Moving Average

    See Also:
        http://pandas.pydata.org/pandas-docs/stable/computation.html#exponentially-weighted-windows
    
    """
    
    def calculate(self, n, series_type='close', name=None):
        if name is None:
            name = 'EMA_%s' % n
        series = self.df[series_type][::-1].ewm(span=n).mean()[::-1]
        self.df[name] = series
        return self.df.loc[:, name]