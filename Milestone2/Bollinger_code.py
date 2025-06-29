from AlgorithmImports import *

class BollingerBandsMeanReversion(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol

        self.bb = self.BB(self.symbol, 20, 2, MovingAverageType.Simple, Resolution.Daily)

        # Stop-loss parameters
        self.stop_loss_pct = 0.05  # 5%
        self.entry_price = None

    def OnData(self, data: Slice):
        if not self.bb.IsReady or self.symbol not in data or not data[self.symbol]:
            return

        price = data[self.symbol].Price
        lower = self.bb.LowerBand.Current.Value
        upper = self.bb.UpperBand.Current.Value

        if not self.Portfolio[self.symbol].Invested:
            if price < lower:
                self.SetHoldings(self.symbol, 1.0)
                self.entry_price = price  # Save entry price for stop-loss
        else:
            # Stop-loss: exit if price drops more than 5% below entry
            if self.entry_price and price < self.entry_price * (1 - self.stop_loss_pct):
                self.Liquidate(self.symbol)
                self.entry_price = None
                return

            # Take-profit: exit if price goes above upper band
            if price > upper:
                self.Liquidate(self.symbol)
                self.entry_price = None
