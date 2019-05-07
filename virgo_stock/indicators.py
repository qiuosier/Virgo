class TimeSeries:
    @staticmethod
    def series_cross(series_n, series_k):
        crosses = []
        for i in range(0, len(series_n.index) - 1):
            if series_n[i + 1] < series_k[i + 1] and series_n[i] > series_k[i]:
                crosses.append(i)
        return series_n.index[crosses]


class MovingAverage:
    def __init__(self, data_frame, n, series_type='close', name=None):
        """Initialize a moving average object.
        Args:
            data_frame: A pandas data frame containing stock data, 
                The data_frame should have timestamp as index, as well as 5 columns, open, high, low, close and volume.
            n: Number of data points used to calculate each moving average value, 
                corresponds to what is commonly called an "N-day moving average".
            series_type: The price type used to calculate the moving average.
            name: The name of the calculated column in the returned data frame.
        TimeSeries stores data in reverse order.
        
        """
        self.df = data_frame
        self.n = n
        self.series_type = series_type
        self.name = name
        if not self.name:
            self.name = self.default_name()
        self.calculate()

    @property
    def series(self):
        return self.df.loc[:, self.name]

    def calculate(self):
        raise NotImplementedError()

    def default_name(self):
        return "Moving_Avg_%s" % self.n

    def breaking_above(self, series):
        """Finds the timestamps where the moving average breaking above another series.
        """
        series_n = self.series
        series_k = series
        return TimeSeries.series_cross(series_n, series_k)

    @classmethod
    def n_breaking_k(cls, data_frame, n, k):
        """Finds the timestamps where n-day moving average breaking above k-day moving average.
        """
        series_n = cls(data_frame, n).series
        series_k = cls(data_frame, k).series
        return TimeSeries.series_cross(series_n, series_k)

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
        return 'SMA_%s' % self.n

    def calculate(self):
        series = self.df[self.series_type][::-1].rolling(self.n).mean()[::-1]
        self.df[self.name] = series
        return self.df.loc[:, self.name]


class EMA(MovingAverage):
    """Exponential Moving Average

    See Also:
        http://pandas.pydata.org/pandas-docs/stable/computation.html#exponentially-weighted-windows
    
    """

    def default_name(self):
        return 'EMA_%s' % self.n
    
    def calculate(self):
        series = self.df[self.series_type][::-1].ewm(span=self.n).mean()[::-1]
        self.df[self.name] = series
        return self.df.loc[:, self.name]