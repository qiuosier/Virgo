"""Contains tests for the stock module.
"""
import datetime
import unittest
import pandas as pd

import os
import sys
from tests.base import TestWithAlphaVantage
from virgo_stock.stock import Stock
from virgo_stock.strategy import Strategy


class TestStrategy(TestWithAlphaVantage):

    def test_base_strategy(self):
        """
        """
        stock = Stock("AAPL", self.data_source)
        df = stock.daily_series("2016-01-01", "2017-01-01")
        strategy = Strategy(df, 0)
        strategy.evaluate()
        self.assertEqual(strategy.shares, len(df))
        self.assertEqual(strategy.equity(), df.iloc[0].close * (len(df)))
