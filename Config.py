import sys

####################################################################
## Configuration of Output
####################################################################

show_plot = True
show_SMA = False
show_EMA = True

####################################################################
## Variable declaration
####################################################################

Apaca_base_url = "https://paper-api.alpaca.markets"
Api_key = "Your Key"
Api_sectret_key = "Your Secret Key"

beta_data = "Data/Beta.xlsx"

analysis_period = "6mo"
beta_benchmark = "^GSPC" # S&P500

shortMA = 3
longMA = 20

analysis_periods = ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']

if analysis_period in analysis_periods[:analysis_periods.index('10y')]:
    backtesting_period = analysis_periods[analysis_periods.index(analysis_period)+1]
else:
    sys.exit('\nERROR:\n--- Backtesting period unavailable. Please select shorter analysis period. ---')

order_size = 0.03