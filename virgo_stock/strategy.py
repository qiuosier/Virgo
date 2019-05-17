class Strategy:
    """Represents a trading strategy.
    This is the base class for defining a trading strategy, 
        providing utility functions for evaluating the strategy.
    The actual trading strategy is defined in the suggest() method.
    The suggest() method provides suggestion for trading at time t.
    Here, t represents a time point, with t=0 defined as the time of the latest data point 
        in the DataFrame used to initialize the strategy.
    Each strategy must be initialized with a pandas DataFrame of stock series data.

    A new trading strategy can be defined as a sub-class.
    A sub-class should override the suggest() method with a new strategy.
    The __init__() constructor of the base class only require the series data of a particular stock.
    Additional keyword arguments passing into __init__() will become attributes of the strategy.

    Attributes:
        df (pandas.DataFrame): Stock series data with time as index.
            Each row should have at least 5 columns: open, high, low, close and volume.
            The first row contains the latest data.
        initial_cash (float): 
        trading_history (list): A list of 3-tuples storing the trading history (price, shares, time)
    """
    
    HISTORY_PRICE = 0
    HISTORY_SHARES = 1
    HISTORY_TIME = 2

    def __init__(self, stock_data_frame, initial_cash=0, **kwargs):
        """Initialize a strategy.
        
        Args:
            stock_data_frame (pandas.DataFrame): The stock series data.
                Each row should have at least 5 columns: open, high, low, close and volume.
                The first row contains the latest data.
            initial_cash (int, optional): Cash available to trade initially. Defaults to 0.
                initial_cash is used for calculating the value or cash available at time t.
                It does not imply constraits on trading.

        Additional keyword arguments passing into __init__() will become attributes of the strategy.
        """
        self.df = stock_data_frame
        self.initial_cash = initial_cash
        self.trading_history = []
        # Set additional keyword arguments as attributes.
        for key, value in kwargs.items():
            setattr(self, key, value)

    def suggest(self, t=1):
        """Suggests the price and shares of stock to buy/sell at time t.
            assuming t=0 for now, t=1 means the next time point, e.g. tomorrow.

            Generally prices at time > t should not be used for prediction.
        
        Args:
            t (int, optional): The time for which the suggestion is made. Defaults to 1.
        
        Returns:
            (float, int): a tuple of (price, shares), 
            suggesting trading the number of shares at a particular price.
            shares == 0 suggests do nothing.
            shares > 0 suggests a buy.
            shares < 0 suggests a sell.
        """
        prices = self.prices(t)
        if prices is not None:
            price = prices.low
            shares = 1
        else:
            price = 0
            shares = 0
        return price, shares

    def position(self, t=0):
        """Position, i.e. the amount of stocks holding,  at the close of time t.
        """
        pos = 0
        for trade in self.trading_history:
            if trade[self.HISTORY_TIME] is None or trade[self.HISTORY_TIME] <= t:
                pos += trade[self.HISTORY_SHARES]
        return pos

    def cash(self, t=0):
        """Cash available at the close of time t.
        """
        c = self.initial_cash
        for trade in self.trading_history:
            if trade[self.HISTORY_TIME] is None or trade[self.HISTORY_TIME] <= t:
                c -= trade[self.HISTORY_SHARES] * trade[self.HISTORY_PRICE]
        return c
    
    def equity(self, t=0):
        """The value of equity at the close of time t.
        """
        prices = self.prices(t)
        if prices is None:
            return 0
        return self.position(t) * prices.close

    def value(self, t=0):
        """The value of the sum of equity and cash at the close of time t.
        """
        return self.equity(t) + self.cash(t)

    def profit(self, t=0):
        return self.value(t) - self.initial_cash

    def prices(self, t):
        """The prices at time t, which is row in the stock data frame.
        """
        if t > 0 or -t >= len(self.df):
            return None
        return self.df.iloc[-t]

    def trade(self, price, shares, t=None):
        """Trades shares with a particular price at time t

        Returns:
            float: The cost for this trade. Trade is not successful if cost is 0.
        """
        # No trade if shares is 0 or the price at time t is not available.
        if shares == 0 or t > 0:
            return 0
        # Check if it is possible to trade at the price
        if t <= 0:
            prices = self.prices(t)
            if price < prices.low or price > prices.high:
                return 0
        self.trading_history.append((price, shares, t))
        cost = price * shares
        return cost

    def evaluate(self, from_t=None, to_t=1):
        """Simulates/Evaluates this trading strategy from time from_t to to_t, excluding to_t.
        
        Args:
            from_t (int, optional): The starting time for simulating this strategy. 
                Defaults to None, which will use all time available before to_t.
            to_t (int, optional): The ending time for simulating this strategy. Defaults to 1.
        
        Returns:
            float: The profit during the period.
        """
        if to_t > 1:
            to_t = 1
        if from_t is None:
            from_t = 1 - len(self.df)
        for t in range(from_t, to_t):
            p, s = self.suggest(t)
            self.trade(p, s, t)
        return self.profit(to_t - 1) - self.profit(from_t - 1)


class GoldenCrossStrategy(Strategy):
    """Represents a trading strategy of buying at golden crosses and selling at death crosses.
    This is an example of inheriting the Strategy class.
    """
    def __init__(self, stock_data_frame, initial_cash=0, golden_crosses=[], death_crosses=[]):
        """Initializes the strategy with golden crosses and death crosses.
        This is unnecessary as the __init__() of Strategy will set additional keyword arguments
            as attributes.
        """
        super().__init__(stock_data_frame, initial_cash)
        self.golden_crosses = golden_crosses
        self.death_crosses = death_crosses

    def suggest(self, t):
        """Determine the price and shares of stock to buy/sell at time t.
        
        This strategy checks if time t-1 is a golden cross or death cross.
        If t-1 is a golden cross, buy 10 shares at time t at the highest price.
        If t-1 is a death cross, sell all the position at time t at the lowest price.
        The prices (buy at highest and sell at lowest) are conservative 
            to guarantee successful trades.
        """
        prices = self.prices(t - 1)
        if prices is None:
            return 0, 0
        date = prices.name
        p = 0
        s = 0
        if date in self.golden_crosses:
            next_prices = self.prices(t)
            if next_prices is not None:
                p = next_prices.high
                s = 10
        if date in self.death_crosses:
            next_prices = self.prices(t)
            if next_prices is not None:
                p = next_prices.low
                s = -self.position(t - 1)
        return p, s