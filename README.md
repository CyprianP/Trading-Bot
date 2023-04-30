# Trading-Bot

The Alpaca trading bot is an ongoing project that aims to automate the process of trading on the Alpaca platform. The bot uses beta weights to determine the optimal allocation of capital between two assets and executes trades accordingly. Beta weights are calculated using historical price data for the two assets and a benchmark index, such as the S&P500. The bot then uses this beta weight to determine the appropriate position size for each asset in order to achieve a desired level of market exposure.

The current state of the project includes downloading stock data and calculating beta weights using Lagrange optimization for a beta-neutral equity trading strategy. Lagrange optimization is used to find the optimal values of beta weights that minimize portfolio variance while maintaining a beta-neutral position.

The next step in the development of the bot is to implement exit and entry rules for the trading period to increase positions and portfolio performance. This will involve developing algorithms that can identify profitable entry and exit points based on technical indicators, such as moving averages, relative strength index (RSI), or other momentum indicators.

To manage the project dependencies and ensure reproducibility, I am using pipenv, a popular package manager for Python projects. 