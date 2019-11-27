import os
import logging
import json
import datetime
from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render
from Aries.storage import StorageFile
from Aries.tasks import FunctionTask
from .virgo_stock.source import AlphaVantage
from .virgo_stock.plotly import Candlestick
from .virgo_stock import sp500
logger = logging.getLogger(__name__)
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
SP500_FILE = os.environ.get("SP500_PATH")
SYMBOLS_FILE = os.environ.get("SYMBOLS_PATH")
last_idx = 0


def authentication_required(function=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            session = request.session
            if request.GET.get("virgo_token"):
                session["virgo_token"] = request.GET.get("virgo_token")
            if session.get("virgo_token") == os.environ.get("VIRGO_TOKEN"):
                return view_func(request, *args, **kwargs)
            return HttpResponseRedirect(reverse("virgo:index"))
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator


def index(request):
    return HttpResponse("This is the homepage for project Virgo.")


def candle_stick(request, symbol, start=None, end=None):
    if start is None:
        start = "2019-01-01"
    logger.debug("Getting data of %s" % symbol)
    data_source = AlphaVantage(API_KEY, "gs://qiu_virgo/stocks/")
    stock = data_source.get_stock(symbol)
    daily_chart = Candlestick(stock.daily_series(start, end)).set_title(symbol)
    return render(request, "virgo/candle.html", {
        "title": str(symbol).upper(),
        "chart": daily_chart.to_html()
    })


def update_sp500(request):
    """Updates the S&P500 symbols and store them into a JSON file.
    The JSON file will contain a dictionary of one key (sp500) and a list of strings as value.
    """
    symbols = sp500.download_symbols()
    with StorageFile.init(SP500_FILE, 'w') as f:
        json.dump({"sp500": symbols}, f)
    return HttpResponse("%s symbols in S&P500" % len(symbols))


def update_symbols(request):
    """Updates the list of symbols for requesting data using update_next()
    """
    update_sp500(request)
    symbols = json.load(StorageFile.init(SP500_FILE)).get("sp500")
    symbols.extend([
        "DJI",
        "INX",
    ])
    with StorageFile.init(SYMBOLS_FILE, 'w') as f:
        json.dump({"symbols": symbols}, f)
    return HttpResponse("%s symbols saved to %s" % (len(symbols), SYMBOLS_FILE))


def update_stock(symbol):
    logger.debug("Updating %s" % symbol)
    data_source = AlphaVantage(API_KEY, "gs://qiu_virgo/stocks/")
    stock = data_source.get_stock(symbol)
    logger.debug("Checking daily data...")
    stock.daily_series()
    logger.debug("Checking intraday data...")
    stock.intraday_series()


def update_next(request):
    """Requests daily and intraday data for a symbol in the symbol list.
    The index of the symbol in symbol list is calculated from the number of minutes since EPOCH.
    A different symbol will be used in this function every 10 minutes.
    This function is designed to be triggered every 10 minutes.
    Assuming updating data of a symbol every 10 minute.
    There will be 144 updates per day, 1008 updates per week.

    """
    global last_idx
    idx = round(datetime.datetime.now().timestamp() / 60 / 10) % len(symbols)
    if last_idx and idx == last_idx:
        return HttpResponse("%s was already updated or being updated.")
    last_idx = idx
    symbols = json.load(StorageFile.init(SYMBOLS_FILE)).get("symbols")
    idx = round(datetime.datetime.now().timestamp() / 60 / 10) % len(symbols)
    logger.debug("Index: %s" % idx)
    symbol = symbols[idx]
    update_stock(symbol)
    # task = FunctionTask(update_stock, symbol)
    # task.run_async()
    return HttpResponse("Updated %s." % symbol)
