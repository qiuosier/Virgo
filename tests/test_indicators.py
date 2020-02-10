"""Contains tests for the indicators module.
"""
import os
import sys
import datetime
import unittest
import pandas as pd
import numpy as np
from tests.base import TestWithAlphaVantage
from virgo_stock.stock import Stock
from virgo_stock.indicators import IndicatorSeries, SMA, EMA


class TestIndicatorSeries(TestWithAlphaVantage):
    def test_indicator_series(self):
        test_array = [1, 2, 3, 2, 5, 6, 3, 2, 4]
        series = IndicatorSeries(test_array)
        self.assertEqual(
            len(series), 
            len(test_array), 
            "Indicator series should have the same length as the test array"
        )
        self.assertIn(2, series.local_minimums().tolist())
        self.assertIn(3, series.local_maximums().tolist())


class TestMovingAverage(TestWithAlphaVantage):
    def assert_set_values_equal(self, expect_dates, actual_timestamps):
        actual_dates = set([str(t)[:10] for t in actual_timestamps])
        self.assertEqual(actual_dates, expect_dates)

    def test_sma(self):
        expect_golden_crosses = {
            "2018-07-11", 
            "2017-03-23",
            "2016-09-08",
            "2014-07-07",
            "2014-02-20",
            "2013-04-15"
        }
        expect_death_crosses = {
            "2018-06-11", 
            "2016-11-01",
            "2015-10-15",
            "2014-04-24",
            "2013-11-26",
            "2012-12-03"
        }
        stock = Stock("VRTX", self.data_source)
        daily_series = stock.daily_series("2011-08-01", "2019-05-01")
        golden_crosses = SMA.golden_cross(daily_series)
        death_crosses = SMA.death_cross(daily_series)
        self.assert_set_values_equal(expect_golden_crosses, golden_crosses)
        self.assert_set_values_equal(expect_death_crosses, death_crosses)

    def test_ema(self):
        expect_golden_crosses = {
            "2017-03-28", 
            "2015-11-18",
            "2014-06-26",
            "2013-12-27",
            "2013-03-18",
            "2012-03-13",
            "2011-09-08",
            "2011-08-24",
        }
        expect_death_crosses = {
            "2016-01-12", 
            "2015-10-12",
            "2014-04-17",
            "2013-12-06",
            "2012-11-20",
            "2011-10-10",
            "2011-08-29",
        }
        stock = Stock("VRTX", self.data_source)
        daily_series = stock.daily_series("2011-08-01", "2019-05-01")
        golden_crosses = EMA.golden_cross(daily_series)
        death_crosses = EMA.death_cross(daily_series)
        self.assert_set_values_equal(expect_golden_crosses, golden_crosses)
        self.assert_set_values_equal(expect_death_crosses, death_crosses)


class TestBollinger(TestWithAlphaVantage):
    def test_bollinger_band(self):
        stock = Stock("VRTX", self.data_source)
        daily_series = stock.daily_series("2011-08-01", "2019-05-01")
        b_band = daily_series.indicator("BollingerBands")
        print(b_band.head())
        self.assertEqual(len(b_band.columns), 3, "Bollinger Band should have 3 columns")
        self.assertEqual(
            len(b_band), 
            len(daily_series), 
            "Bollinger Band should have the same length as the daily data."
        )
        for i in range(len(b_band)):
            row = b_band.iloc[i]
            if row.isnull().sum() == 0:
                self.assertGreater(row['BB_upper'], row['BB_sma'])
                self.assertGreater(row['BB_sma'], row['BB_lower'])
