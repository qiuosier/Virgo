# Virgo_Stocks
Virgo Stock is a package for financial technical analysis. This package is develop with the mind of automatic analysis.

[![Build Status](https://travis-ci.org/qiuosier/Virgo.svg?branch=master)](https://travis-ci.org/qiuosier/Virgo)
[![Coverage Status](https://coveralls.io/repos/github/qiuosier/Virgo/badge.svg?branch=master)](https://coveralls.io/github/qiuosier/Virgo?branch=master)

There are four major components in this package: Data Source, Stock, Indicator, and Strategy.

## Data Source
This package relies on external source to provide market data. The `DataSourceInterface` acts as a layer between the data source and the `Stock` class. The `DataSourceInterface` is intended to provide a unified interface for accessing market data from different data source. 

### Alpha Vantage
Alpha Vantage provides web API for stock data and more.

This package implemented an `AlphaVantage` data source. The implementation here includes:
1. The `AlphaVantageAPI` class as a simple python API for accessing the AlphaVantage data. See [more details](docs/AlphaVantage.md).
2. An option to cache the data to reduce the outgoing API requests.

See also: https://www.alphavantage.co/

## Stock
The Stock component is designed to manipulate and transform stock data.

In this package, a `Stock` object represents a stock (or security). Stock objects provides methods for retrieving and manipulating series data of a particular stock. Two parameters are required to initialize a `Stock` object:
* The symbol of the stock as a string.
* A `DataSource` implemented the `DataSourceInterface` for retrieving the data.

Once initialized, the stock series data are retrieved as a pandas DataFrame. The data frame will have at least 5 columns: open, high, low, close and volume. The first row of the data frame stores the latest data.

## Indicator
Technical Indicator is the basic component of technical analysis.

In this package, each indicator is defined as a class. With each class, this package goes beyond the calculation to provide provide aggregated information (e.g. Moving Average also provides Golden Crosses and Death Crosses). An indicator can be initialized with a stock series data.

## Strategy
The `Strategy` class is designed to simulate and evaluate trading strategies. Simulation is the starting point for automatic analysis. Trading strategies can be complicated. Each strategy should be implemented as a sub-class by the user.

## Modules, Classes, Objects and the Relations between them
The Virgo_Stock package defines classes in the following files:
* stock.py: defines `Stock` and `DataPoint`;
* source.py: defines `DataSourceInterface` and implements the `AlphaVantage` data source.
* indicators.py: defines `Indicator` as the base class and sub-classes for calculating technical indicators (e.g. moving average).
* strategy.py: defines `Strategy` as the base class for simulating and evaluating strategies.

2018-2019 Qiu Qin. All Right Reserved.

This is a mirrored repository, which does not contain the latest Development. This package is part of Qiu's Project Virgo.
