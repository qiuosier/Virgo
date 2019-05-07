"""Contains tests for the indicators module.
"""
import datetime
import unittest
import pandas as pd

import os
import sys
from tests.base import TestWithAlphaVantage
from virgo_stock.stock import Stock
from virgo_stock.indicators import TimeSeries, SMA, EMA


class TestTimeSeries(TestWithAlphaVantage):
    def test_time_series_initialization(self):
        stock = Stock("AAPL", self.data_source)
        daily_series = stock.daily_series("2016-01-01", "2017-01-01")
        TimeSeries(daily_series)
        series_name = "Series_1"
        self.assertIn(series_name, daily_series.columns)
        for value in daily_series[series_name]:
            self.assertIsNone(value)

class TestMovingAverage(TestWithAlphaVantage):
    def assert_set_values_equal(self, expect_set, actual_iterable):
        actual_set = set([str(s)[:10] for s in actual_iterable])
        self.assertEqual(actual_set, expect_set)

    def test_sma(self):
        expect_golden_crosses = set([
            "2018-07-11", 
            "2017-03-23",
            "2016-09-08",
            "2014-07-07",
            "2014-02-20",
            "2013-04-15"
        ])
        expect_death_crosses = set([
            "2018-06-11", 
            "2016-11-01",
            "2015-10-15",
            "2014-04-24",
            "2013-11-26",
            "2012-12-03"
        ])
        stock = Stock("VRTX", self.data_source)
        daily_series = stock.daily_series("2011-08-01", "2019-05-01")
        golden_crosses = SMA.golden_cross(daily_series)
        death_crosses = SMA.death_cross(daily_series)
        self.assert_set_values_equal(expect_golden_crosses, golden_crosses)
        self.assert_set_values_equal(expect_death_crosses, death_crosses)

    def test_ema(self):
        expect_golden_crosses = set([
            "2017-03-28", 
            "2015-11-18",
            "2014-06-26",
            "2013-12-27",
            "2013-03-18",
            "2012-03-13",
            "2011-09-08",
            "2011-08-24",
        ])
        expect_death_crosses = set([
            "2016-01-12", 
            "2015-10-12",
            "2014-04-17",
            "2013-12-06",
            "2012-11-20",
            "2011-10-10",
            "2011-08-29",
        ])
        stock = Stock("VRTX", self.data_source)
        daily_series = stock.daily_series("2011-08-01", "2019-05-01")
        golden_crosses = EMA.golden_cross(daily_series)
        death_crosses = EMA.death_cross(daily_series)
        self.assert_set_values_equal(expect_golden_crosses, golden_crosses)
        self.assert_set_values_equal(expect_death_crosses, death_crosses)

    def test_pass(self):
        pass
