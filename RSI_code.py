from AlgorithmImports import *

class RSIMeanReversion(QCAlgorithm):
    

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol

        # RSI indicator
        self.rsi = self.RSI(self.symbol, 14, MovingAverageType.WILDERS, Resolution.Daily)

        # RSI thresholds
        self.rsi_oversold = 30  # Buy below this
        self.rsi_overbought = 70  # Sell above this

        # Stop-loss config
        self.stop_loss_pct = 0.05  # 5%
        self.entry_price = None

    def OnData(self, data: Slice):
        if not self.rsi.IsReady or self.symbol not in data or not data[self.symbol]:
            return

        price = data[self.symbol].Price
        current_rsi = self.rsi.Current.Value

        if not self.Portfolio[self.symbol].Invested:
            if current_rsi < self.rsi_oversold:
                self.SetHoldings(self.symbol, 1.0)
                self.entry_price = price  # Record entry price
        else:
            # Stop-loss condition
            if self.entry_price and price < self.entry_price * (1 - self.stop_loss_pct):
                self.Liquidate(self.symbol)
                self.entry_price = None
                return

            # Overbought exit condition
            if current_rsi > self.rsi_overbought:
                self.Liquidate(self.symbol)
                self.entry_price = None
