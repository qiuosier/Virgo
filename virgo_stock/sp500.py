import pandas as pd
from Aries import web
from Aries.storage import StorageFile


def download_symbols():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    symbol_list = []
    tables = web.HTML(url).get_tables()
    if not tables:
        raise ValueError("Table not found.")
    for row in tables[0].get("data", []):
        symbol_list.append(str(row[0]).split(">", 1)[1].split("<", 1)[0])
    return symbol_list
