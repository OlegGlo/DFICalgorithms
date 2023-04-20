
from AlgorithmImports import *

class meanReversion(QCAlgorithm):
    
    def Initialize(self):

        self.SetStartDate(2022, 7, 21)
        self.SetEndDate(2023, 4, 14)
        self.SetCash(140000)

        # vars: IBM
        stk1 = 'F'
        stk2 = 'JNJ'

        # Will use wrapper function to avoid specifying variables
        self.ticker_1 = self.AddEquity(stk1, Resolution.Daily).Symbol
        self.ticker_2 = self.AddEquity(stk2, Resolution.Daily).Symbol
        
        # Create two identity indicators (a indicator that repeats the value without any processing)
        self.ticker_1_identity = Identity(stk1)
        self.ticker_2_identity = Identity(stk2)

        # Set these indicators to receive the data from ticker_1 and ticker_2        
        self.RegisterIndicator(self.ticker_1, self.ticker_1_identity, Resolution.Daily)
        self.RegisterIndicator(self.ticker_2, self.ticker_2_identity, Resolution.Daily)

        # Create the portfolio as a new indicator using slope of linear regression in research.ipynb
        # Will need to re-compute slope for each pair
        self.series = IndicatorExtensions.Minus(self.ticker_1_identity, IndicatorExtensions.Times(self.ticker_2_identity, 0.356))

        # We then create a bollinger band with 120 steps for lookback period
        # Will need to play around with band's std deviation
        self.bb = BollingerBands(120, 0.6, MovingAverageType.Exponential)
        
        # Define the objectives when going long or going short
        # Can play around with divergent thresholds
        self.long_targets = [PortfolioTarget(self.ticker_1, 0.8), PortfolioTarget(self.ticker_2, -0.8)]
        self.short_targets = [PortfolioTarget(self.ticker_1, -0.8), PortfolioTarget(self.ticker_2, 0.8)]

        self.is_invested = None

    def OnData(self, data):

        # For daily bars data is delivered at 00:00 of the day containing the closing price of the previous day (23:59:59)
        if (not data.Bars.ContainsKey(self.ticker_1)) or (not data.Bars.ContainsKey(self.ticker_2)):
            return

        # Update the Bollinger Band value
        self.bb.Update(self.Time, self.series.Current.Value)

        # Check if the bollinger band indicator is ready (filled with 120 steps)
        if not self.bb.IsReady:
            return

        serie = self.series.Current.Value

        self.Plot("ticker_2 Prices", "Open", self.Securities[self.ticker_2].Open)
        self.Plot("ticker_2 Prices", "Close", self.Securities[self.ticker_2].Close)
        
        self.Plot("Indicators", "Serie", serie)
        self.Plot("Indicators", "Middle", self.bb.MiddleBand.Current.Value) # moving average
        self.Plot("Indicators", "Upper", self.bb.UpperBand.Current.Value)   # upper band
        self.Plot("Indicators", "Lower", self.bb.LowerBand.Current.Value)   # lower band
        
        # if it is not invested, check if there is an entry point
        if not self.is_invested:
            # if our portfolio is below the lower band, enter long
            if serie < self.bb.LowerBand.Current.Value:
                self.SetHoldings(self.long_targets)
                self.Debug('Entering Long')
                self.is_invested = 'long'
            
            # if our portfolio is above the upper band, go short
            if serie > self.bb.UpperBand.Current.Value:
                self.SetHoldings(self.short_targets)
                self.Debug('Entering Short')
                self.is_invested = 'short'
        
        # if it is invested in something, check the exiting signal (when it crosses the mean)   
        elif self.is_invested == 'long':
            if serie > self.bb.MiddleBand.Current.Value:
                self.Liquidate()
                self.Debug('Exiting Long')
                self.is_invested = None
                
        elif self.is_invested == 'short':
            if serie < self.bb.MiddleBand.Current.Value:
                self.Liquidate()
                self.Debug('Exiting Short')
                self.is_invested = None
