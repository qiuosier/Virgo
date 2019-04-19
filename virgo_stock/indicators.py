class MovingAverage:
    def __init__(self, time_series, method_name):
        """
        TimeSeries stores data in reverse order.
        """
        self.ts = time_series
        self.method = getattr(self.ts, method_name)

    def series_cross(self, n, k):
        """Finds the timestamps where n-day moving average breaking above k-day moving average.
        """
        series_n = self.method(n).iloc[:,0]
        series_k = self.method(k).iloc[:,0]
        crosses = []
        for i in range(0, len(self.ts) - 1):
            if series_n[i + 1] < series_k[i + 1] and series_n[i] > series_k[i]:
                crosses.append(i)
        return self.ts.df['timestamp'][crosses]

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
    def __init__(self, time_series):
        super().__init__(time_series, 'sma')


class EMA(MovingAverage):
    """Exponential Moving Average"""
    def __init__(self, time_series):
        super().__init__(time_series, 'ema')
