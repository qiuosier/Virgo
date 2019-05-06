import unittest
import os
import json

class TestWithAlphaVantage(unittest.TestCase):
    # Fixtures directory stored the test data.
    fixtures = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")

    # API Key required for getting data from AlphaVantage.
    key_file = os.path.join(fixtures, "private.json")
    api_key = None
    if os.path.exists(key_file):
        with open(key_file) as f:
            api_key = json.load(f).get("AlphaVantage")
        
    if not api_key:
        raise FileNotFoundError("AlphaVantage API Key must be stored in \"fixtures/private.json\"")

    # Cache folder for AlphaVantage data
    cache_folder = os.path.join(fixtures, "..", "..", "..", "data", "stocks")
    if not os.path.exists(cache_folder):
        raise FileNotFoundError("Cache Folder does not exist.")
    