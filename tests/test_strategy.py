"""Contains tests for the stock module.
"""
import datetime
import unittest
import pandas as pd

import os
import sys
from tests.base import TestWithAlphaVantage
from virgo_stock.stock import Stock
from virgo_stock.strategy import Strategy, GoldenCrossStrategy
from virgo_stock.indicators import SMA


class TestStrategy(TestWithAlphaVantage):

    def test_base_strategy(self):
        """
        """
        stock = Stock("AAPL", self.data_source)
        df = stock.daily_series("2016-01-01", "2017-01-01")
        strategy = Strategy(df, 0)
        strategy.evaluate()
        self.assertEqual(strategy.position(), len(df))
        self.assertEqual(strategy.equity(), df.iloc[0].close * (len(df)))

    def test_golden_cross_strategy(self):
        """Tests if the golden cross strategy can be executed.
        """
        stock = Stock("AAPL", self.data_source)
        df = stock.daily_series("2003-01-01", "2013-01-01")
        golden_crosses = SMA.golden_cross(df)
        death_crosses = SMA.death_cross(df)
        strategy = GoldenCrossStrategy(df, initial_cash=5000, golden_crosses=golden_crosses, death_crosses=death_crosses)
        strategy.evaluate()
        self.assertEqual(len(strategy.trading_history), 8)
        self.assertEqual(round(strategy.value()), 8796)
        self.assertEqual(round(strategy.profit()), 3796)
