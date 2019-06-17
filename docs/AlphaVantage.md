# Alpha Vantage Data
Alpha Vantage provides web API for stock data and more.

This package implemented an `AlphaVantage` data source. The implementation here includes:
1. The `AlphaVantageAPI` class as a simple python API for accessing the AlphaVantage data.
2. An option to cache the data to reduce the outgoing API requests.

See also: https://www.alphavantage.co/

## The AlphaVantageAPI
The `AlphaVantageAPI` class defined in `alpha_vantage.py` provides a simple python API for accessing Alpha Vantage data. To use the API, simply initialize an instance with your API key and use the `get()` method. For example, to get the daily adjusted time series data of Apple Inc.:

```
from virgo_stock.alpha_vantage import AlphaVantageAPI

web_api = AlphaVantageAPI(YOUR_API_KEY)
response = web_api.get(symbol="AAPL", function="TIME_SERIES_DAILY_ADJUSTED")
```
The `get()` method accepts keyword arguments for specifying the query strings in the request.
For example, use:
```
web_api.get(function="TIME_SERIES_INTRADAY", symbol="MSFT", interval="5min")
```
to request the data from the following endpoint:

https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min
        
See https://www.alphavantage.co/documentation/ for more details of the endpoints.        

This class provides 3 major methods for getting different types of data:
* `get()`, returns a Response object (see [Requests](https://2.python-requests.org/en/master/user/advanced/#request-and-response-objects) package)
* `get_json()`, returns a dictionary.
* `get_dataframe()`, returns a [pandas](https://pandas.pydata.org/) data frame.

## Rate Limit and Automatic Retry
The free Alpha Vantage API key has a limit of 5 requests per miniute and 500 requests per day.
The `AlphaVantageAPI` class keeps the recent request histories of each API key using the "histories" static attribute.
Base on the "histories", it will wait (sleep) automatically before making new requests when there are already 5 requests in the last minute. Also, it will retry automatically when an error occurs.
From the user perspective, it just looks like the request is taking a long time.
Users do not need to worry about the delay and retry.