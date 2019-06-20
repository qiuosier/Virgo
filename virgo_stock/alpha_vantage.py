import requests
import time
import datetime
import io
import logging
import pandas as pd
from collections import deque
from requests.exceptions import RequestException
from Aries.tasks import FunctionTask
from Aries.web import WebAPI
logger = logging.getLogger(__name__)


class AlphaVantageAPI(WebAPI):
    """Provides methods to access AlphaVantage API.
    The free Alpha Vantage API key has a limit of 5 requests per miniute and 500 requests per day.
    This class keeps the recent request histories of each API key 
        using the "histories" static attribute.
    Base on the "histories", it will wait (sleep) automatically before making new requests
        when there are already 5 requests in the last minute.
    Also, it will retry automatically when an error occurs.
    From the user perspective, it just looks like the request is taking a long time.
    Users do not need to worry about the delay and retry.

    This class only handles the 5 requests per minute limit.
    This class does not limit the number of request per day.
    If the API key has been used to make more than 500 requests per day,
        an RequestException will be raised.

    This class uses python requests package.
    See https://2.python-requests.org/en/master/user/advanced/#request-and-response-objects
    
    Attributes:
        limits and histories are static properties.
        They stores the rate limits and request histories for each API key.
        limits (dict): A dictionary storing the rate limit per minute for each API key.
            key (str): API key.
            value (int): limit per minute. Default to 5.
        histories (dict): A dictionary storing the recent API requests times and URLs.
            key (str): API key.
            value (deque): A deque of dictionaries. Each dictionary has two keys: "time" and "url".
                "time" stores a datetime instance of the time when the request was made.
                "url: stores the url of the request as a string.
        
        api_key: The Alpha Vantage API key.
        
    """
    limits = {}
    histories = {}

    def __init__(self, api_key, **kwargs):
        """Initialize the API with API key.
        
        Args:
            api_key (str): Alpha Vantage API key
            kwargs: Can be use to specify query string to be included in all requests.
                e.g. To request full size output every time: outputsize="full"

        See Also:
            https://www.alphavantage.co/support/
        
        """
        self.api_key = api_key
        self.histories[api_key] = deque()
        base_url = "https://www.alphavantage.co/query"
        super().__init__(base_url, apikey=api_key, **kwargs)

    def set_limit(self, limit):
        """Sets the limit of per miniute requests.
        By default, each API key will have a per minute limit of 5 requests.
        This method allows the user to set a customied limit.
        
        Args:
            limit (int): Limit for number of requests per minute.

        """
        self.limits[self.api_key] = limit

    @staticmethod
    def __try(func, max_retry=5, **kwargs):
        """Makes API request and retry if there is a RequestException.
        
        Args:
            func: A function making API request.
            max_retry (int, optional): The max number of retry. Defaults to 5.
            kwargs: Can be use to specify query string to be included in all requests.
        
        Returns: A Response Object.

        Raise:
            RequestException: Raise if the request failed after max number of retry.

        """
        task = FunctionTask(func, **kwargs)
        response = task.run_and_retry(
            max_retry=max_retry, 
            exceptions=RequestException, 
            base_interval=30, 
            retry_pattern="linear"
        )
        return response

    @staticmethod
    def __check_response(response):
        """Checks if the response is valid.
        
        Args:
            response: Response Object.
        
        Raises:
            RequestException: Raise if
                1. The response status code is not 200.
                2. The response data is a json containing a note from the server.
                    Usually this means the rate limit is reached.

        """
        # Status code should be 200
        if response.status_code != 200:
            raise RequestException(
                "Unexpected Status Code: %s" % response.status_code,
                response=response
            )

        # Check if the request is over rate limit
        try:
            json_data = response.json()
        except ValueError:
            # Return if the data is not JSON.
            # AlphaVantage send errors in JSON
            return

        if len(json_data) == 1:
            val = next(iter(json_data.values()))
            if isinstance(val, str):
                if "Invalid API call" in val:
                    logger.debug(val)
                    raise ValueError(str(json_data))
                else:
                    raise RequestException(
                        str(json_data),
                        response=response,
                    )

    def __clean_history(self):
        """Removes the history of longer than 1 minute ago.
        """
        # Get history of this API key
        history = self.histories.get(self.api_key, deque())

        # Remove history that is more than 1 minutes ago
        while len(history) > 0:
            item = history[0]
            if item.get("time") < datetime.datetime.now() - datetime.timedelta(seconds=60):
                history.popleft()
            else:
                break
        # 
        self.histories[self.api_key] = history

    def __get(self, **kwargs):
        """Requests data
        Use keyword arguments to specify the query strings in the request.
        
        Returns: A Response Object
        """
        # Replace "." with "-", 
        # otherwise there will be an error when getting data from AlphaVantage.
        logger.debug("Getting AlphaVantage Data...%s" % kwargs)
        symbol = kwargs.get("symbol")
        if symbol:
            kwargs["symbol"] = symbol.replace(".", "-")

        # Build request URL
        url = self.build_url("", **kwargs)

        self.__clean_history()
        history = self.histories.get(self.api_key, deque())
        
        # Wait if there are more items than the limit in the history
        limit = self.limits.get(self.api_key, 5)
        if len(history) >= limit:
            item = history[-limit]
            wait_time = item.get("time") + datetime.timedelta(seconds=61) - datetime.datetime.now()
            wait_seconds = wait_time.total_seconds()
            print("Wait %s seconds..." % wait_seconds)
            time.sleep(wait_seconds)
        
        # Add this request to history
        history.append({"time": datetime.datetime.now(), "url": url})
        self.histories[self.api_key] = history
        
        # Request Data
        response = requests.get(url)

        self.__check_response(response)
        return response

    def __get_json(self, **kwargs):
        """Requests JSON data
        Use keyword arguments to specify the query strings in the request.
        
        Returns: A dictionary
        """
        response = self.__get(**kwargs)
        # Additional error checking for JSON
        try:
            json_data = response.json()
        except ValueError:
            raise RequestException(
                "The response does not contain valid JSON.",
                response=response
            )
        if not json_data:
            raise RequestException(
                "The response does not contain valid JSON.",
                response=response
            )
        return json_data

    def get(self, max_retry=5, **kwargs):
        """Requests Alpha Vantage data

        Use keyword arguments to specify the query strings in the request.
        
        e.g. use 
        get(function="TIME_SERIES_INTRADAY", symbol="MSFT", interval="5min")
        to request the data from the following URL:
        https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min
        
        See https://www.alphavantage.co/documentation/ for more details.
        
        
        Args:
            max_retry (int, optional): Max number of retry. Defaults to 5.
        
        Returns: A Response Object

        """
        return self.__try(self.__get, max_retry, **kwargs)

    def get_json(self, max_retry=5, **kwargs):
        """Requests json data

        Use keyword arguments to specify the query strings in the request.
        
        e.g. use 
        get(function="TIME_SERIES_INTRADAY", symbol="MSFT", interval="5min")
        to request the data from the following URL:
        https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min
        
        See https://www.alphavantage.co/documentation/ for more details.
        
        
        Args:
            max_retry (int, optional): Max number of retry. Defaults to 5.
        
        Returns: A dictionary

        """
        return self.__try(self.__get_json, max_retry, **kwargs)

    def get_dataframe(self, max_retry=5, **kwargs):
        """Requests data and read them into a Pandas Data Frame
        
        Args:
            max_retry (int, optional): Max number of retry. Defaults to 5.
        
        Returns: A pandas dataframe.

        """
        kwargs.update({
            "datatype": "csv"
        })
        response = self.get(max_retry, **kwargs)
        buffer = io.BytesIO(response.content)
        try:
            df = pd.read_csv(
                buffer, 
                parse_dates=["timestamp"],
                infer_datetime_format=True
            )
        except Exception:
            df = pd.read_csv(
                buffer, 
                infer_datetime_format=True
            )
        return df
