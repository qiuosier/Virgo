# Virgo_Stocks

## Classes, Objects and the Relations between them
The Virgo_Stock packege defines classes in the following files:
* stock.py: defines `Stock` and `DataPoint`;
* source.py: defines `DataSourceInterface` and implements the `AlphaVantage` data source.
* technical.py: defines `TimeSeries`, which provides methods for calculating technical indicators (e.g. moving average).
* indicators.py: 

### Stock
A `Stock` object represents a stock (or security). Stock objects provides methods for retrieving different `TimeSeries` data of a particular stock. Two parameters are required to initialize a `Stock` object:
* The symbol of the stock as a string.
* A `DataSource` for retrieving the data.