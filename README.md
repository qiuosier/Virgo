# Virgo_Stocks
Virgo Stock is a package for financial technical analysis. This package is develop with the mind of short term stock market data analysis.

[![Build Status](https://travis-ci.org/qiuosier/Virgo.svg?branch=master)](https://travis-ci.org/qiuosier/Virgo)
[![Coverage Status](https://coveralls.io/repos/github/qiuosier/Virgo/badge.svg?branch=master)](https://coveralls.io/github/qiuosier/Virgo?branch=master)

Calculating the __Technical Indicators__ is basic component of technical analysis. In addition, this package goes beyond the calculation to provide:
* __Data Source Interface__ to minimize the number of outgoing API requests by organizing and caching data.
* __Stock Abstraction__ to manipulate and transform series data.
* __Strategy Abstraction__ to simulate and evaluate trading strategies.

This package is part of Qiu's Project Virgo


## Classes, Objects and the Relations between them
The Virgo_Stock package defines classes in the following files:
* stock.py: defines `Stock` and `DataPoint`;
* source.py: defines `DataSourceInterface` and implements the `AlphaVantage` data source.
* indicators.py: defines `Indicator` as the base class and sub-classes for calculating technical indicators (e.g. moving average).
* strategy.py: defines `Strategy` as the base class for simulating and evaluating strategies.

### Stock
A `Stock` object represents a stock (or security). Stock objects provides methods for retrieving and manipulating series data of a particular stock. Two parameters are required to initialize a `Stock` object:
* The symbol of the stock as a string.
* A `DataSource` implemented the `DataSourceInterface` for retrieving the data.

Once initialized, the stock series data are retrieved as a pandas DataFrame. The data frame will have at least 5 columns: open, high, low, close and volume. The first row of the data frame stores the latest data.

### Data Source
This package relies on external source to provide market data. The `DataSourceInterface` acts as a layer between the data source and the `Stock` class. The `DataSourceInterface` is intended to provide a unified interface for accessing market data from different data source. The `AlphaVantage` data source is implemented in this package. The implementation here also caches the data to reduce the outgoing API requests. Data source may implement cache to reduce external data requests.

See also: https://www.alphavantage.co/

### Indicator
Each indicator is defined as a class. In this way, each indicator can have different methods to provide aggregated information (e.g. Moving Average also provides Golden Crosses and Death Crosses).  An indicator can be initialized with a stock series data.

### Strategy
The `Strategy` class is designed to simulate and evaluate trading strategies. Trading strategies can be complicated. Each strategy should be implemented as a sub-class by the user.


2018-2019 Qiu Qin. All Right Reserved.

This is a mirrored repository, which does not contain the latest Development.
