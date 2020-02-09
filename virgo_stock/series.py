from pandas import Series, DataFrame


class TimeSeries(Series):

    @property
    def _constructor(self):
        return TimeSeries

    @property
    def _constructor_expanddim(self):
        return TimeDataFrame


class TimeDataFrame(DataFrame):

    @property
    def _constructor(self):
        return TimeDataFrame

    @property
    def _constructor_sliced(self):
        return TimeSeries
