"""Contains classes for time series data.
TimeSeries is a sub-class of pandas Series
TimeDataFrame is a sub-class of pandas DataFrame

All sub-classes of pandas DataFrame/Series must define properties in _metadata or _internal_names
See also: https://pandas.pydata.org/pandas-docs/stable/development/extending.html

"""
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
