from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, MACD
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Select a diversified set of ETFs representing different sectors and asset classes
        # Includes S&P 500 (SPY) for baseline comparison
        self.tickers = ["SPY", "VTI", "VXUS", "BND", "VGT", "VNQ", "VHT"]
        # Initialize last sold for tax-loss harvesting
        self.last_sold = {}

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # No additional data requirements specified
        return []

    def run(self, data):
        allocation_dict = {}
        total_assets = len(self.tickers)
        
        # Basic Moving Average Convergence Divergence (MACD) for trend following/momentum
        for ticker in self.tickers:
            macd_signal = MACD(ticker, data["ohlcv"], 26, 12)
            if macd_signal is not None:
                # If the MACD line crosses below the signal line, consider for tax loss harvesting
                if macd_signal["MACD"][-1] < macd_signal["signal"][-1] and (ticker not in self.last_sold or self.is_long_enough_since_last_sold(ticker)):
                    # Sell to harvest tax losses, adjust allocation to 0
                    allocation_dict[ticker] = 0
                    self.last_sold[ticker] = self.current_date  # Update last sold date
                else:
                    # Equal weight the remaining assets not sold for tax loss harvesting
                    allocation_dict[ticker] = 1 / (total_assets - len(self.last_sold.keys()))
            else:
                log(f"MACD signal not available for {ticker}, assigning equal allocation")
                allocation_dict[ticker] = 1 / total_assets
        
        return TargetAllocation(allocation_dict)
    
    def is_long_enough_since_last_sold(self, ticker):
        # Considering a wash-sale rule, ensuring we don't buy back the asset within 30 days after selling
        if ticker in self.last_sold:
            delta = self.current_date - self.last_sold[ticker]
            return delta.days > 30
        return True
    
    @property
    def current_date(self):
        # Implement to return the current date in your environment (placeholder)
        import datetime
        return datetime.date.today()