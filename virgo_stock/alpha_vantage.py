import requests
import time
import datetime
from collections import deque
from requests.exceptions import RequestException
from Aries.tasks import FunctionTask
from Aries.web import WebAPI


class AlphaVantageAPI(WebAPI):
    """Provides methods to access AlphaVantage API.
    
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
        self.api_key = api_key
        self.histories[api_key] = deque()
        base_url = "https://www.alphavantage.co/query"
        super().__init__(base_url, apikey=api_key, **kwargs)

    def get(self, **kwargs):
        url = self.build_url("", **kwargs)
        history = self.histories.get(self.api_key, deque())

        # Remove history that is more than 1 minutes ago
        while len(history) > 0:
            item = history[0]
            if item.get("time") < datetime.datetime.now() - datetime.timedelta(seconds=60):
                history.popleft()
            else:
                break
        
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
        response = requests.get(url)
        return response

    def __get_json(self, **kwargs):
        response = self.get(**kwargs)
        if response.status_code != 200:
            raise RequestException(
                "Unexpected Status Code: %s" % response.status_code,
                response=response
            )
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

        if len(json_data) == 1 and json_data.get("Note") is not None:
            raise RequestException(
                json_data.get("Note"),
                response=response
            )

        return json_data

    def get_json(self, max_retry=5, **kwargs):
        task = FunctionTask(self.__get_json, **kwargs)
        json_data = task.run_and_retry(
            max_retry=max_retry, 
            exceptions=RequestException, 
            base_interval=30, 
            retry_pattern="linear"
        )
        return json_data