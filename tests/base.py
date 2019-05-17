import unittest
import os
import json
from virgo_stock.source import AlphaVantage

class TestWithAlphaVantage(unittest.TestCase):
    # Fixtures directory stored the test data.
    fixtures = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")
    # API Key required for getting data from AlphaVantage.
    key_file = os.path.join(fixtures, "private.json")
    api_key = None
    if os.path.exists(key_file):
        with open(key_file) as f:
            api_key = json.load(f).get("AlphaVantage")

    if os.environ.get("AlphaVantage_Key"):
        api_key = os.environ["AlphaVantage_Key"]
        
    if not api_key:
        raise FileNotFoundError(
            "AlphaVantage API Key must be stored in environment variable \"AlphaVantage_Key\""
            "or \"fixtures/private.json.\""
        )

    # Cache folder for AlphaVantage data
    cache_folder = os.path.join(fixtures, "..", "cache")
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    data_source = AlphaVantage(api_key, cache_folder)
