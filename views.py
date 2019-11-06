import os
import logging
from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render
from .virgo_stock.source import AlphaVantage
from .virgo_stock.plotly import Candlestick
logger = logging.getLogger(__name__)
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")


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
