import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn

from pandas.io.data import DataReader
from sklearn.qda import QDA

from backtest import Strategy, Portfolio
from forecast import create_lagged_series

class SNPForecastingStrategy(Strategy):
  """Requires:
    symbol - A stock symbol to form a strategy.
    bars - A df of bars for the above symbol."""
    
  def __init__(self, symbol, bars):
    self.symbol = symbol
    self.bars = bars
    self.create_periods()
    self.fit_model()
    
  def create_periods(self):
    """Create training/test periods."""
    self.start_train = datetime.datetime(2001,1,10)
    self.start_test = datetime.datetime(2005,1,1)
    self.end_period = datetimme.datetime(2005,12,31)
    
  def fit_model(self):
    """Fits a Quadratic Discriminat Analyser to the US
    sock market index (^GPSC in Yahoo)."""
    # Create a laggged series of the S&P500 US stock market index
    
    snpret =  create_lagged_series(self.symbol, self.start_train,
                self.end_period, lags=5)
    
    # Use the prior two days of returns as 
    # predictor value, with direction as the response
    X = snpret[["Lag1", "Lag2"]]
    y = snpret["Direction"]
    
    # Create training and test sets
    X_train = X[X.index < self.start_test]
    y_train = y[y.index < self.start_test]
    
    # Create the prediciting factors for use
    # in direction forecasting.
    self.predictors = X[X.index >= self.start_test]
    
    # Create the Quadractic Discriminant Analysis model
    # and the forcasting strategy
    self.model = QDA()
    self.model.fit(X_train, y_train)
    
  def generate_signals(self):
    """Returns the df of symbols containing the signals
    to go long, short, or hold (1, -1, 0)."""
    signals = pd.DataFrame(index=self.bars.index)
    signals['signal'] = 0.0
    
    # predict the subsequent period with the QDA model
    signals['signal'] = self.model.predict(self.predictors)
    
    # Remove the first five signals entries to eliminate
    # NaN issues with the signal df
    signals[''signal'][0:5] = 0.0
    signals['positions'] = signals['signal'].diff()
    
    return signals
    
  class MarketingIntradayPortfolio(Portfolio):
    """Buys or sells 500 shares of an asset at the opening price
    of every bar, depending upon the direction of the forcast,
    closing out the trade at the close of the bar.
    
    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A df of bars for a symbol set.
    signal - A df of signals (1, 0, -1) for each symbol
    initial_capital - The amount in cash at the start of the portfolio."""
    
    def __init__(self, symbol, bars, signals, initial_capital=100000.0):
      self.symbol = symbol
      self.bars = bars
      self.signals = signals
      self.initial_capital = float(initial_capital)
      self.positions = self.generate_positions()
      
    def generate_positions(self):
      """Generate the positions df, based on the signals provided by the 'signals; df."""
      positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
      
      # Long or short 500 shares of SPY based on directional signal every day
      positions[self.symbol] = 500*self.signals['signal']
      return positions
      
    def backtest_portfolio(self):
      """Backtest the portfolio and return a df containing
      the equity curve and the percentage returns.""
      
      # Set the portfolio object to have the same time period
      # as the positions df.
      portfolio = pd.DateFrame(index=self.positions.index)
      pos_diff = self.positions.diff()
      
      # Work out the intraday profit of the difference
      # in open and closing prices and then determine
      # the daily profit by longing if an up day is predicted 
      # and shorting if a down day is predicted
      
      portfolio['price_diff'] = self.bars['Close'] - self.bars['Open']
      portfolio['price_diff'][0:5] = 0.0
      portfolio['profit'] = self.positions[self.symbol] * portfolio['price_diff']
      
      # Generate the equity curve and percentage returns
      portfolio['total'] = self.initial_capital + portfolio['profit'].cumsum()
      portfolio['returns'] = portfolio['total'].pct_change()
      return portfolio
      
if __name__ == "__main__":
  start_test = datetime.datetime(2005,1,1)
  end_period = datetime.datetime(2005,12,31)
  
  # Obtain the bars for SPY ETF which tracks the S&P500 index
  
  bars = DataReader("SPY", "yahoo", start_test, end_period)
  
  # Create the S&P500 forecasting strategy
  snpf = SNPForecastingStrategy("^GSPC", bars)
  signals = snpf.generate_signals()
  
  # Create the portfolio based on the forecaster
  portfolio = MarketIntradayPortfolio("SPY", bars, signals, 
                      initial_capital=100000.0)
                      
  returns = portfolio.backtest_portfolio()
  
  # Plot results
  fig = plt.figure()
  fig.patch.set_facecolor('white')
  
  # Plot the price of the SPY ETF
  ax1 = fig.add_subplot(211, ylabel='SPY ETF price in $')
  bars['Close'].plot(ax=ax1, color='r', lw=2.)
  
  # Plot the equity curve
  ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
  returns['total'].plot(ax=ax2, lw=2.)
  
  fig.show()
  
      
  
