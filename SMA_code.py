# region imports
from AlgorithmImports import *
# endregion

class SimpleMovingAverage(QCAlgorithm):
#SMA
    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2023, 12, 31)
        self.SetCash(100000)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol

        self.short_window = 50
        self.long_window = 200

        self.sma_short = self.SMA(self.symbol, self.short_window, Resolution.Daily)
        self.sma_long = self.SMA(self.symbol, self.long_window, Resolution.Daily)

        self.entry_price = None
        self.stop_loss_percent = 0.05  # 5% stop-loss
        self.previous_cross = None

        self.Debug("Initialized with Stop-Loss")

    def OnData(self, data: Slice):
        if not self.sma_short.IsReady or not self.sma_long.IsReady:
            return
        if self.symbol not in data or not data[self.symbol]:
            return

        price = data[self.symbol].Price
        current_short = self.sma_short.Current.Value
        current_long = self.sma_long.Current.Value

        # If invested, check for stop-loss or crossover to exit
        if self.Portfolio[self.symbol].Invested:
            if current_short < current_long:
                self.Liquidate(self.symbol)
                self.Debug(f"SELL (SMA CROSS): {self.Time} @ {price}")
                self.entry_price = None
            elif self.entry_price and price < self.entry_price * (1 - self.stop_loss_percent):
                self.Liquidate(self.symbol)
                self.Debug(f"SELL (STOP-LOSS): {self.Time} @ {price}")
                self.entry_price = None
            return

        # If not invested, check for entry condition
        if self.previous_cross == "below" and current_short > current_long:
            self.SetHoldings(self.symbol, 1.0)
            self.entry_price = price
            self.Debug(f"BUY: {self.Time} @ {price} (SMA CROSS)")
        
        # Update crossover tracking
        if current_short > current_long:
            self.previous_cross = "above"
        elif current_short < current_long:
            self.previous_cross = "below"
