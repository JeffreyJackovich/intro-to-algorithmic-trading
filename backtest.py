from abc import ABCMETA, abstractmethod

class Strategy(object):
    """An abstract base class providing an interface for all trading strategies"""
    
    __metaclass__ = ABCNeta
    
    @abstractmethod
    def generate_signals(self):
    """An implementation is required to return the df of symbols containing the signals to go long, short, or hold (1, -1, or 0)."""
    raise NotImplementedError("Should implement generate_signals()!")
    

class Portfolio(object):
  """An abstract base class representing a portfolio of positions determined on the basis of a set of signals provided by a Strategy"""
  
  __metaclass__ = ABCMeta
  
  @abstractmethod
  def generate_positions(self):
    """Provides the logic to determine how the portfolio positions are allocated on the basis of forecasting signals and available cash."""
    raise NotImplementedError("Should implement generate_positionns()!")
    
  @abstractmethod
  def backtest_portfolio(self):
    """Provides the logic to generate the trading orders and subsequent equity curve(i.e. growth of total equity), as a sum of holding and cash, and the bar-period returns associated witth this curve based on the 'positions' df.
    Produces a portfolio object that can be examined by other classes/functions."""
    raise NotImplementedError("Shoul implement backtest_portfolio()!")
    
    
