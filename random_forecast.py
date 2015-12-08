import numpy as np
import pandas as pd
import Quandl 

from backtest import Strategy, Portfolio

class RandomForecastingStrategy(Strategy):
  """Obtains from Strategy to produce a set of signals that
  are randomly generated long/shorts.  Not a cogent strategy, but usefeul
  to demenstrate the backtesting infrastructure!"""
  
  def __init__(self, symbol, bars):
    """Requires the symbol ticker and the pandas Dataframe of bars"""
    self.symbol = symbol
    self.bars = bars
    
  def generate_signals(self):
    """Creates a pandas df of random signals."""
    signals = pd.DataFrame(index=self.bars.index)
    signals['signal'] = np.sign(np.random.randn(len(signals))
    
    # The first five elements are set to zero in order to minimise
    # upstream Nan errors in the forecaster.
    signals['signal'][0:5] = 0.0
    return signals
    
class marketOnOpenPortfolio(Portfolio):
  """Inherts Portfolio to create a system that purchases 100
  units of a particular symbol upon a long/short signal, assuming
  the market open price of a bar.
  
  Requires:
  symbol - A stock symbol which form the basic of the portfolio.
  bars - A df of bars for a symbol set.
  signals - A pandas df of signals (0, 1, -1) for each symbol.
  initial_capital - The amount in cash at the start of the portfolio."""
  
  def __init__(self, symbol, bars, signals, initial_capital=1000000.0):
    self.symbol = symbol
    self.bars = bars
    self.signals = signals
    self.initial_capital = float(initial_capital)
    self.positions = self.generate_positions()
    
  def generate_positions(self):
    """Creates a 'positions' df that simply longs or shorts
    100 of the particular symbol based on the forecase signals of
    {1, 0, -1} from the signal df."""
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    positions[self.symbol] = 100*signals['signal']
    return positions 
    
  def backtest_portfolio(self):
    """Constructs a portfolio from the positions df by assuming
    the ability to trade at the precise market open price of each bar (
    not possible in reality!).
    Calculates the total of case and the holdings (market price of
    each position per bar), in order to generate an equity curve ('total')
    and a set of bar-based returns ('returns').
    Returns the portfolio object to be used elsewhere."""
    
    #Construct the portfolio df to use the same index
    # as 'positions' and with a set of 'trading orders'
    # in the 'pos_diff' object, assuming market open prices.
    portfolio =  self.positions*self.bars['Open']
    pos_diff = self.positionns.diff()
    
    #Create the 'holdings' and 'cash' series by running through
    # the trades and adding /  subtracting the relevant quantity from
    # each column
    portfolio['holdings'] = (self.positions*self.bars['Open']).sum(axis=1)
    portfolio['cash'] = self.initial_capital - (pos_diff*self.bars['Open']).sum(axis=1).cumsum()
    
    # Finalize the total and bar-based returns based on the 'cash'
    # and the 'holdings' figures for the portfolio
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']
    portfolio['returns'] = portfolio['total'].pct_change()
    return portfolio
    
    
if __name__ == "__main__":
  # Obtain daily bars of SPY (ETF that generally 
  # follows the S&P500) from Quandl 
  symbol = 'SPY'
  bars = Quandl.get("GOOG/NYSE_%s" % symbol, collapse="daily")
  
  # Create a set of random forecasting signals for SPY
  rfs = RandomForecastingStrategy(symbol, bars)
  signals = rfs.generate_signals()
  
  # Create a portfolio of SPY
  portfolio = MarketOnOpenPortfolio(symbol, bars, signals, initial_capital=100000.0)
  returns = portfolio.backtest_portfolio()
  
  print returns.tail(10)
  
