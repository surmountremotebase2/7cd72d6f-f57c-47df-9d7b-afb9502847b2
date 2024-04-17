from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA, EMA
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership

class TradingStrategy(Strategy):
    def __init__(self):
        # Including BOXX as the primary ETF for tax efficiency and diversity.
        # Additional ETFs are chosen for dividends and long-term growth potential.
        self.tickers = ["BOXX", "VIG", "SDY", "SCHD"]
    
    @property
    def interval(self):
        # Utilizing daily interval for long-term strategy adjustments.
        return "1day"
    
    @property
    def assets(self):
        # Returning the chosen tickers for the investment strategy.
        return self.tickers
    
    @property
    def data(self):
        # Data required for decision making includes institutional ownership.
        return [InstitutionalOwnership(i) for i in self.tickers]
    
    def run(self, data):
        # The strategy here allocates investment based on RSI and EMA indicators 
        # to ensure we're not investing in overbought assets and to maintain a trend-following approach.
        
        allocation_dict = {}
        for ticker in self.tickers:
            # Initial allocation before checking conditions
            allocation_dict[ticker] = 0.25  # Even split without adjustment
            
            ohlcv = data["ohlcv"]
            if len(ohlcv) > 14:  # Ensuring enough data for RSI calculation
                rsi = RSI(ticker, ohlcv, 14)
                if rsi and rsi[-1] < 30:
                    # Condition to check if the asset is oversold, implying a potential buy signal.
                    log(f"Buying {ticker} based on RSI")
                    allocation_dict[ticker] += 0.05  # Increasing allocation slightly for this signal

            if len(ohlcv) > 50:  # Ensuring enough data for EMA calculation
                ema_short = EMA(ticker, ohlcv, 12)
                ema_long = EMA(ticker, ohlcv, 26)
                if ema_short and ema_long and ema_short[-1] > ema_long[-1]:
                    # Condition to buy if short-term EMA crosses above long-term EMA
                    log(f"Buying {ticker} based on EMA crossover")
                    allocation_dict[ticker] += 0.05  # Adjusting allocation based on positive trend
        
        # Ensuring the sum of allocation does not exceed 1
        allocation_sum = sum(allocation_dict.values())
        if allocation_sum > 1:
            allocation_dict = {ticker: val/allocation_sum for ticker, val in allocation_dict.items()}
        
        return TargetAllocation(allocation_dict)