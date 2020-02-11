"""Contains tests for the stock module.
"""
import datetime
import unittest
import pandas as pd

import os
import sys
from tests.base import TestWithAlphaVantage
from ..virgo_stock import sp500, plotly


class TestDataSource(TestWithAlphaVantage):
    def assert_data_frame_index(self, actual_df, expect_df):
        """Asserts if two pandas dataframes have the same index.
        """
        # Check if the data frames have the same number of rows
        self.assertEqual(len(actual_df), len(expect_df), "Data frames have different number of rows.")
        # Check index
        for i in range(len(actual_df)):
            self.assertEqual(actual_df.index[i], expect_df.index[i])

    def test_intraday_series(self):
        stock = self.get_stock("AAPL")
        intraday = stock.intraday_series()
        date = str(intraday.index[0])[:10]
        for i in range(len(intraday)):
            self.assertTrue(str(intraday.index[i]).startswith(date))

    def test_daily_series(self):
        """Tests getting daily series data.
        """
        daily_data_file = os.path.join(self.fixtures, "AAPL_daily.xlsx")
        expect_df = pd.read_excel(daily_data_file, index_col=0)
        stock = self.get_stock("AAPL")
        actual_df = stock.daily_series("2015-01-01", "2017-01-01")
        self.assert_data_frame_index(actual_df, expect_df)

    def test_weekly_series(self):
        """Tests getting weekly series data.
        """
        data_file = os.path.join(self.fixtures, "AAPL_weekly.xlsx")
        expect_df = pd.read_excel(data_file, index_col=0)
        stock = self.get_stock("AAPL")
        actual_df = stock.weekly_series("2015-01-01", "2017-01-01")
        self.assert_data_frame_index(actual_df, expect_df)

    def test_monthly_series(self):
        """Tests getting monthly series data.
        """
        data_file = os.path.join(self.fixtures, "AAPL_monthly.xlsx")
        expect_df = pd.read_excel(data_file, index_col=0)
        stock = self.get_stock("AAPL")
        actual_df = stock.monthly_series("2015-01-01", "2017-01-01")
        self.assert_data_frame_index(actual_df, expect_df)

    def test_download_sp500(self):
        symbol_list = sp500.download_symbols()
        self.assertGreaterEqual(len(symbol_list), 500)

    def test_plot_candlestick(self):
        """Tests if the candlestick chart can be plotted.
        """
        stock = self.get_stock("AAPL")
        daily_data = stock.daily_series("2015-01-01", "2017-01-01")
        html = plotly.Candlestick(daily_data).to_html()
