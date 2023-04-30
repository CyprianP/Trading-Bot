import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mplfinance as mpl
from matplotlib.gridspec import GridSpec
import Technical_Analysis as ta
import sys
import Config

def plot_position_size_adjclose(p_data, n_data, portfolio_data):
    """_summary_

    Args:
        df (_type_): _description_
    """ 
    sns.lineplot(data=p_data, x = 'Date', y = 'position_size', label='position_size_p')
    sns.lineplot(data=n_data, x = 'Date', y = 'position_size', label='position_size_n')
    sns.lineplot(data=portfolio_data, x = 'Date', y = 'portfolio_size', label='portfolio_size')
    
    plt.show()

def plot_mplcandlestick(df):
    """_summary_

    Args:
        df (_type_): _description_
    """

    df = df.price_data

    mpl.plot(df, type="candle", volume=True, style='charles')

def plot_pltcandlestick_volume(df): 
    """_summary_

    Args:
        df (_type_): _description_
    """

    ticker = df.ticker
    df = df.price_data
    green_df, red_df = ta.candles_green_red(df)
        
    grid = GridSpec(3,3)
    fig = plt.figure(f'{ticker} Chart')
    ax1 = fig.add_subplot(grid[:2, :])

    plt.vlines(x=green_df.index, ymin = green_df['Low'], ymax = green_df['High'], color = 'green')
    plt.vlines(x=red_df.index, ymin = red_df['Low'], ymax = red_df['High'], color = 'orangered')
    plt.bar(x=green_df.index, height = green_df['Height'], bottom = green_df['Open'], color = 'green')
    plt.bar(x=red_df.index, height = red_df['Height'], bottom = red_df['Close'], color = 'orangered')
    
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.title(f'{ticker} Chart')
    plt.grid(visible=True, which='both', linewidth=0.25)
    plt.tight_layout()
    ax1.set_facecolor('gainsboro')

    green_df_v, red_df_v = ta.volume_green_red(df)
    ax2 = fig.add_subplot(grid[2:, :])
    
    plt.bar(x=green_df_v.index, height=green_df_v['Volume'], color='green')
    plt.bar(x=red_df_v.index, height=red_df_v['Volume'], color='orangered')
    
    plt.ylabel('Volume')
    plt.grid(visible=True, which='both', linewidth=0.25)
    plt.tight_layout()
    ax2.set_facecolor('gainsboro')

    plt.show()

def plot_candles_volume(df): 
    """_summary_

    Args:
        df (_type_): _description_
    """

    ticker = df.ticker
    
    grid = GridSpec(3,3)
    fig = plt.figure(f'{ticker} Chart')

    ax1 = plot_candles(df, grid=grid[:2, :], fig=fig)
    ax2 = plot_volume(df, grid=grid[2:, :], fig=fig)

    plt.show()

def plot_all(df_p, df_n, position_size):
    """Plots two figures, one with the candle stick charts of the stocks, one with the combined portfolio value

    Args:
        df_p (Trading_Data - Object): Trading_Data-Object  with all information for positive beta stock
        df_n (Trading_Data - Object): Trading_Data-Object  with all information for negative beta stock
        position_size (pd.DataFrame): Portfolio data with position size of positive stock, negative stock and both combined
    """

    ticker_p = df_p.ticker
    ticker_n = df_n.ticker
    
    grid = GridSpec(6,6)
    fig = plt.figure(f'{ticker_p}/{ticker_n}_Chart')
    fig.tight_layout()

    ax1 = plot_candles(df_p, grid=grid[:4, :3], fig=fig)
    ax2 = plot_volume(df_p, grid=grid[4:, :3], fig=fig)
    ax3 = plot_candles(df_n, grid=grid[:4, 3:], fig=fig)
    ax4 = plot_volume(df_n, grid=grid[4:, 3:], fig=fig)

    fig_portfolio_value = plt.figure(f'{ticker_p}/{ticker_n}_Portfolio_value')
    ax_portfolio_value = fig_portfolio_value.add_subplot(111)
    plt.plot(position_size.index, position_size.position_size_p, label=f'{ticker_p}')
    plt.plot(position_size.index, position_size.position_size_n, label=f'{ticker_n}')
    plt.plot(position_size.index, position_size.portfolio_size, label=f'portfolio_size')
    
    plt.grid(visible=True, which='both', linewidth=0.25)
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    ax_portfolio_value.set_facecolor('gainsboro')

    if Config.show_plot: plt.show()

def plot_candles(df, grid, fig): 
    """Plots the candle stick chart of the selected stock

    Args:
        df (Trading_Data - Object): Trading_Data-Object  with all information of stock
        grid (GridSpec-Object): GridSpec-Object with the slice where the candle stick chart should be plotted
        fig (plt.figure-Object): plt.figure-Object where all axs should be plotted in
        
    """

    ticker = df.ticker
    df_price = df.price_data
    df_technical = df.technical_data
    green_df, red_df = ta.candles_green_red(df_price)

    ax1 = fig.add_subplot(grid)

    ### Candles ###
    plt.vlines(x=green_df.index, ymin = green_df['Low'], ymax = green_df['High'], color = 'green')
    plt.vlines(x=red_df.index, ymin = red_df['Low'], ymax = red_df['High'], color = 'orangered')
    plt.bar(x=green_df.index, height = green_df['Height'], bottom = green_df['Open'], color = 'green')
    plt.bar(x=red_df.index, height = red_df['Height'], bottom = red_df['Close'], color = 'orangered')
    
    ### Technical Analsysis ###
    if Config.show_SMA:
        plt.plot(df_technical[f'SMA{Config.shortMA}'], label=F'SMA{Config.shortMA}', linewidth=0.75)
        plt.plot(df_technical[f'SMA{Config.longMA}'], label=F'SMA{Config.longMA}', linewidth=0.75)
    if Config.show_EMA:
        plt.plot(df_technical[f'EMA{Config.shortMA}'], label=F'EMA{Config.shortMA}', linewidth=0.75)
        plt.plot(df_technical[f'EMA{Config.longMA}'], label=F'EMA{Config.longMA}', linewidth=0.75)
    
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.title(f'{ticker} Chart')
    plt.grid(visible=True, which='both', linewidth=0.25)
    plt.tight_layout()
    plt.legend()
    ax1.set_facecolor('gainsboro')

    return ax1

def plot_volume(df, grid, fig): 
    """Plots the volume chart of the selected stock

    Args:
        df (Trading_Data - Object): Trading_Data-Object  with all information of stock
        grid (GridSpec-Object): GridSpec-Object with the slice where the candle stick chart should be plotted
        fig (plt.figure-Object): plt.figure-Object where all axs should be plotted in
    """
    
    ticker = df.ticker
    df = df.price_data
    ax1 = fig.add_subplot(grid)

    green_df_v, red_df_v = ta.volume_green_red(df)

    plt.bar(x=green_df_v.index, height=green_df_v['Volume'], color='green')
    plt.bar(x=red_df_v.index, height=red_df_v['Volume'], color='orangered')
    
    plt.ylabel('Volume')
    plt.grid(visible=True, which='both', linewidth=0.25)
    plt.tight_layout()
    ax1.set_facecolor('gainsboro')

    return ax1