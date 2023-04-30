import Alpaca_Bot as ab
from Alpaca_Bot import Alpaca_Trading_Bot as tc
from Alpaca_Bot import Trading_Data as td
import pandas as pd
import time 
import Config
import sys
import numpy as np
from scipy.optimize import minimize
import Plotting as pl
start_time = time.time()
print('\n--- Program start ---\n')

# Bot = tc()
cash = 100000 #float(Bot.get_account_info().buying_power)

trade_couples = ab.get_trade_couples(sheet_positive='Positive', sheet_negative='Negative')

for i in range(len(trade_couples)): 
    positive_ticker, negative_ticker = trade_couples.positive_Ticker[i], trade_couples.negative_Ticker[i]
    try: 
        positive, negative = td(positive_ticker), td(negative_ticker)
    except: 
        continue

    if len(positive.price_data) != len(negative.price_data): continue    
    
    sol = ab.get_beta_weights(positive, negative)
    p_weight, n_weight = sol.x[1], sol.x[3]

    #############################################################
    ## Backtesting 
    #############################################################

    backtest_p, backtest_n = td(ticker=positive_ticker, price_range=Config.backtesting_period), td(ticker=negative_ticker, price_range=Config.backtesting_period)
    
    backtest_p.price_data['Adj_Close_Delta'] = backtest_p.price_data['Adj Close'].pct_change()
    backtest_n.price_data['Adj_Close_Delta'] = backtest_n.price_data['Adj Close'].pct_change()
    # print(backtest_p.beta, backtest_n.beta)
    
    amt_p, amt_n = round(cash*Config.order_size*p_weight,2), round(cash*Config.order_size*n_weight,2)
    

    ##############
    ## Calculating position size
    ##############

    backtest_p.price_data['position_size'] = amt_p
    backtest_n.price_data['position_size'] = amt_n

    for i in range(len(backtest_p.price_data['position_size'])-1):

        backtest_p.price_data['position_size'][i+1] = backtest_p.price_data['position_size'][i]*(1+backtest_p.price_data['Adj_Close_Delta'][i+1])
        backtest_n.price_data['position_size'][i+1] = backtest_n.price_data['position_size'][i]*(1+backtest_n.price_data['Adj_Close_Delta'][i+1])

    position_size = backtest_p.price_data[['position_size']].rename(columns={'position_size':'position_size_p'})
    position_size['position_size_n'] = backtest_n.price_data['position_size']
    position_size['portfolio_size'] = position_size['position_size_p'] + position_size['position_size_n']
      

    # pl.plot_candles_volume(backtest_p)
    pl.plot_all(backtest_p, backtest_n, position_size)

    break   

end_time = time.time()
print(f"\nRuntime: {round(end_time-start_time, 2)} Seconds.")