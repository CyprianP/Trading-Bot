import Config
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import alpaca_trade_api as tradeapi
import yfinance as yf
import pandas as pd
import numpy as np
import yahooquery as yq
from scipy.optimize import minimize

class Alpaca_Trading_Bot: 
    
    def __init__(self): 
        """
            Create variable for TradingClient 
        """
        self.Api_key = Config.Api_key
        self.Api_secret_key = Config.Api_sectret_key
        self.alpaca_client = TradingClient(self.Api_key, self.Api_secret_key, paper = True)

    def get_account_info(self): 
        """
            Get account information of Alpaca client
        """
        self.account = self.alpaca_client.get_account()
        
        return self.account

    def get_open_orders(self): 
        """
            Get last 100 open orders 

            returns: list of all open orders --> to be checked if true
        """

        open_orders = self.alpaca_client.get_orders()
        return open_orders

    def get_positions(self): 
        """_summary_: Get all open positions

            returns: List of all positions with a dictionary of each ticker and position side
        """
        open_positions = self.alpaca_client.get_all_positions()
        return open_positions

    def submit_buy(self, market_order_data): 
        """Submit buy order 
        Args:
            market_order_data (list): order data as list with first value ticker as string and second quantity as int
        """
        self.market_order_data = market_order_data

        self.market_order_data = MarketOrderRequest(
            symbol = market_order_data[0], 
            qty = market_order_data[1], 
            side = OrderSide.BUY, 
            time_in_force = TimeInForce.GTC
        )

        market_order = self.alpaca_client.submit_order(self.market_order_data)

        for property_name, value in market_order: 
            print(f"{property_name}\": {value}")

    def submit_sell(self, market_order_data): 
        """Submit sell order 

        Args:
            market_order_data (list): order data as list with first value ticker as string and second quantity as int
        """
        self.market_order_data = market_order_data

        self.market_order_data = MarketOrderRequest(
            symbol = market_order_data[0], 
            qty = market_order_data[1], 
            side = OrderSide.SELL, 
            time_in_force = TimeInForce.GTC
        )

        market_order = self.alpaca_client.submit_order(self.market_order_data)

        for property_name, value in market_order: 
            print(f"{property_name}\": {value}")

class Trading_Data: 

    def __init__(self, ticker, price_range=Config.analysis_period):
        self.ticker = ticker
        self.price_range = price_range
        self.price_data =self.get_historic_price(ticker = self.ticker, price_range=price_range)
        self.price_data = self.price_data[:int(round(len(self.price_data)/2,0))]
        self.beta = self.get_beta()
        self.current_price = self.get_current_price()
        self.technical_data = self.perform_technical_analysis()

    def get_beta(self):
        """get beta of company

        Args:
            ticker (str): ticker as string
        """
        # https://www.learnpythonwithrune.org/calculate-the-market-sp-500-beta-with-python-for-any-stock/

        benchmark_price = self.get_historic_price(ticker=Config.beta_benchmark, price_range=self.price_range)['Adj Close'].rename(Config.beta_benchmark)
        if self.price_range == Config.backtesting_period: benchmark_price = benchmark_price[:int(round(len(benchmark_price)/2,0))]
        stock_price = self.price_data['Adj Close'].rename(self.ticker)
        both_prices = pd.concat([benchmark_price, stock_price], names=[Config.beta_benchmark, self.ticker], axis=1)
        
        log_returns = np.log(both_prices/both_prices.shift())
        cov = log_returns.cov()
        var = log_returns[Config.beta_benchmark].var()
        beta = cov.loc[self.ticker, Config.beta_benchmark]/var
        return beta

    def get_historic_price(self, ticker, price_range): 
        """Gets the historic price data

        Args:
            ticker (String): Ticker to get the price data from
            price_range (String): 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        returns: 
            DataFrame with historic price information from now on until price_range back in time
        """
        price_data = yf.download(tickers=ticker, period=price_range)
        return price_data

    def get_current_price(self): 
        """Gets the current price 

        Returns:
            Float: Current Price of ticker
        """
        current_price = self.price_data['Adj Close'][-1]
        return current_price

    def perform_technical_analysis(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        technical_data = pd.DataFrame(index=self.price_data.index)
        
        technical_data[f'SMA{Config.shortMA}'] = self.price_data['Close'].rolling(Config.shortMA).mean()
        technical_data[f'SMA{Config.longMA}'] = self.price_data['Close'].rolling(Config.longMA).mean()
        technical_data[f'EMA{Config.shortMA}'] = self.price_data['Close'].ewm(span=Config.shortMA).mean()
        technical_data[f'EMA{Config.longMA}'] = self.price_data['Close'].ewm(span=Config.longMA).mean()
        
        return technical_data

#################################################################################################################
# Gets list of betas from Excel list 
#################################################################################################################

def get_betas(sheet_name): 
    """Get betas from Excel

    Args:
        sheet_name (String): "Positive" or "Negative"
    return: Dataframe of ticker and Beta 
    """

    beta = pd.ExcelFile(Config.beta_data).parse(sheet_name)
    list_to_split = beta.Company.to_list()
    ticker_list = list(map(lambda x: x.split("_")[0], list_to_split))
    new_df = pd.DataFrame(list(zip(ticker_list, beta.Beta)), columns=['Ticker', 'Beta'])
    return new_df

def calc_beta_sums(posititve_betas, negative_betas): 
    """Calculate the sum of positive and negative betas

    Args:
        posititve_betas (List): List of positive betas
        negative_betas (List): List of negative betas
        
    return: List of lists with each results value
    """ 
    summed_betas = []

    for i in posititve_betas:
        current_sum = []
        for j in negative_betas: 
            res = i+j
            current_sum.append(res)
        summed_betas.append(current_sum)
    return summed_betas

def get_index(summed_betas): 
    """Get the index of the beta sum closest to zero for further data preparation

    Args:
        summed_betas (List): List of lists with each results value
    returns: 
        List of index positions for all positive tickers in their order
    """
    indexes = [i.index(min(i, key=abs)) for i in summed_betas]
    return indexes

def get_index_ticker(index_betas, beta_negative): 
    """Gets the ticker according to the return list of get_index()
    Args:
        index_betas (List): List of index positions for all positive tickers in their order
        
    returns: 
        List of Tickers
    """
    ticker_list = [beta_negative.iloc[i, 0] for i in index_betas]
    return ticker_list

def get_corresponding_beta(both, negative): 
    return negative[(negative.Ticker == both.negative_Ticker)].Beta.values[0]

def get_trade_couples(sheet_positive, sheet_negative): 
    """Gets tickers and betas according to 

    Args:
        sheet_positive (String): Excel-Sheet name for positive tickers and betas 
        sheet_negative (String): Excel-Sheet name for negative tickers and betas 
    returns: 
        Dataframe with positive and negative tickers and betas sorted for lowest sum at the top
    """

    beta_positive = get_betas(sheet_positive)
    beta_negative = get_betas(sheet_negative)
    
    positive = beta_positive.Beta.to_list()
    negative = beta_negative.Beta.to_list()  

    summed_betas = calc_beta_sums(positive, negative)
    index_betas = get_index(summed_betas)
    ticker_list = get_index_ticker(index_betas, beta_negative)

    trade_couples = pd.DataFrame()
    trade_couples['positive_Ticker'] = beta_positive.Ticker
    trade_couples['positive_Beta'] = beta_positive.Beta
    trade_couples['negative_Ticker'] = ticker_list
    trade_couples['negative_Beta'] = trade_couples.apply(get_corresponding_beta, negative=beta_negative, axis=1)
    trade_couples['summed_Beta'] = abs(trade_couples.positive_Beta + trade_couples.negative_Beta)

    trade_couples.sort_values(by=['summed_Beta'], ascending=True, inplace=True)
    trade_couples.reset_index(drop=True, inplace=True)
    return trade_couples

#################################################################################################################
# Lagrange optimization - minimize -> https://www.youtube.com/watch?v=cXHvC_FGx24
#################################################################################################################

def objective(x): # Objective: return sum of weighted betas
    return x[0]*x[1]+x[2]*x[3] 
def constraint1(x): # Weights summed up equal zero
    return 1-x[1]-x[3]
def constraint2(x): # Objective equal zero
    return objective(x) #x[0]*x[1]+x[2]*x[3]
def get_beta_weights(positive, negative):
    """Gets the weights for the positive and negative beta. Uses the lagrange minimization function

    Args:
        positive (TradingData-Object): TradingData-Object with positive beta.
        negative (TradingData-Object): TradingData-Object with negative beta.

    Returns:
        scypi.OptimizeResult-Object: Optimization results with weight for positive beta at result.x[1] and weight for negative beta at result.x[3]
    """

    beta_weights = [positive.beta, 0.5, negative.beta, 0.5]
    b = (0,1) # Bounds for weights
    bnds = ((positive.beta,positive.beta), b, (negative.beta, negative.beta),b) # Bounds for each weight
    con1 = {'type': 'eq', 'fun':constraint1}
    con2 = {'type': 'eq', 'fun':constraint2}
    cons = [con1, con2] # List of all constraints

    sol = minimize(objective, beta_weights, method='SLSQP', bounds = bnds, constraints=cons)
    return sol