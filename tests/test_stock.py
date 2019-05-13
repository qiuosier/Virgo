"""Contains tests for the stock module.
"""
import datetime
import unittest
import pandas as pd

import os
import sys
from tests.base import TestWithAlphaVantage
from virgo_stock.stock import Stock


class TestStock(TestWithAlphaVantage):
    def assert_data_frame(self, actual_df, expect_df):
        # Check if the data frames have the same number of rows
        self.assertEqual(len(actual_df), len(expect_df), "Data frames have different number of rows.")
        # Check the each data point of "open", "close", "high", "low", and "volume" columns
        columns = ["open", "close", "high", "low", "volume"]
        for col in columns:
            for i in range(len(actual_df)):
                self.assertEqual(round(actual_df.iloc[i][col], 2), round(expect_df.iloc[i][col], 2))
        # Check index
        for i in range(len(actual_df)):
            self.assertEqual(actual_df.index[i], expect_df.index[i])

    def test_daily_series(self):
        """Tests getting daily series data.
        """
        daily_data_file = os.path.join(self.fixtures, "AAPL_daily.xlsx")
        expect_df = pd.read_excel(daily_data_file, index_col=0)
        stock = Stock("AAPL", self.data_source)
        actual_df = stock.daily_series("2015-01-01", "2017-01-01")
        self.assert_data_frame(actual_df, expect_df)

    def test_weekly_series(self):
        """Tests getting weekly series data.
        """
        data_file = os.path.join(self.fixtures, "AAPL_weekly.xlsx")
        expect_df = pd.read_excel(data_file, index_col=0)
        stock = Stock("AAPL", self.data_source)
        actual_df = stock.weekly_series("2015-01-01", "2017-01-01")
        self.assert_data_frame(actual_df, expect_df)

    def test_monthly_series(self):
        """Tests getting monthly series data.
        """
        data_file = os.path.join(self.fixtures, "AAPL_monthly.xlsx")
        expect_df = pd.read_excel(data_file, index_col=0)
        stock = Stock("AAPL", self.data_source)
        actual_df = stock.monthly_series("2015-01-01", "2017-01-01")
        self.assert_data_frame(actual_df, expect_df)
