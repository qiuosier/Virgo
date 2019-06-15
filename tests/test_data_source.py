"""Contains tests for the source module.
"""
import datetime
import unittest
import pandas as pd

import os
import sys
import time
import shutil
from tests.base import TestWithAlphaVantage
from virgo_stock.source import AlphaVantage
from virgo_stock.source import DataSourceInterface


class TestDataSource(TestWithAlphaVantage):

    cache = os.path.join(os.path.dirname(__file__), "empty_cache")

    @classmethod
    def setUpClass(cls):
        # Wait 60 seconds before running tests.
        time.sleep(60)

    @classmethod
    def tearDownClass(cls):
        time.sleep(60)

    def tearDown(self):
        if os.path.exists(self.cache):
            shutil.rmtree(self.cache)

    def assert_data_frame(self, df):
        self.assertIsNotNone(df)
        self.assertEqual(len(df.columns), 8, df.columns)

    def test_data_source_not_implemented(self):
        s = DataSourceInterface()
        with self.assertRaises(NotImplementedError):
            s.get_daily_series("AAPL")
        with self.assertRaises(NotImplementedError):
            s.get_intraday_series("AAPL")

    def test_daily_series_without_cache(self):
        """Tests getting daily series data.
        """
        data_source = AlphaVantage(self.api_key)
        df = data_source.get_daily_series("AAPL")
        self.assert_data_frame(df)

    def test_intraday_series_with_cache(self):
        """Tests getting daily series data.
        """
        data_source = AlphaVantage(self.api_key, cache_folder=self.cache)
        df1 = data_source.get_daily_series("AAPL")
        self.assert_data_frame(df1)
        # Get data again, cached data should be returned.
        df2 = data_source.get_daily_series("AAPL")
        self.assert_data_frame(df1)
        self.assertEqual(len(df1), len(df2))
