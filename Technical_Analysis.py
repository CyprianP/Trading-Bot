import pandas as pd
import numpy as np

def volume_green_red(df): 
    """ Takes in DataFrame and returns two pd.DataFrames with green and red volume bars.

    Args:
        df (DataFrame): DataFrame with the price data of TradingData-Object
    
    Returns: 
        Two DataFrames with green and red Volume bars.
    """

    colors = ['green']

    for i in range(len(df['Volume'])-1): 
        colors.append('green') if df['Volume'][i+1]>df['Volume'][i] else colors.append('red')

    df['Volume_Color'] = colors

    green_df = df[df.Volume_Color == 'green']
    red_df = df[df.Volume_Color == 'red']
    
    return green_df, red_df

def candles_green_red(df): 
    """ Takes in DataFrame and returns two pd.DataFrames with green and red Candles.

    Args:
        df (DataFrame): DataFrame with the price data of TradingData-Object
    
    Returns: 
        Two DataFrames with green and red Candles.
    """
    
    green_df = df[df.Close > df.Open].copy()
    green_df['Height'] = green_df['Close']- green_df['Open']
    red_df = df[df.Close < df.Open].copy()
    red_df['Height'] = red_df['Open']- red_df['Close']

    return green_df, red_df
        
