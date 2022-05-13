# region imports
from AlgorithmImports import *
# endregion

class ConstantPriceAlgo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2021, 1, 1)  # Set Start Date
        self.SetEndDate(2022, 1, 1)  # Set End Date - if omitted: will be today
        self.SetCash(100000)

        spy = self.AddEquity("SPY", Resolution.Daily)
        # forex = self.AddForex(ticker) can also do thiss

        #Data normalization
        # can be done if needed:
        # spy.SetDataNormalizationMode(DataNormalizationMode.Raw) - does not accout for stock splits
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
    
        # default: adjusted data

        self.spy = spy.Symbol # to make it universal (good practice)

        # for Alpha and to compare algorithm to it
        self.SetBenchmark("SPY")

        # setting custom brokerage
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.entryPrice = 0
        self.period = timedelta(31)
        self.nextEntryTime = self.Time     

    def OnData(self, data: Slice):

        # to check if data already exists
        if not self.spy in data:
            return
         
        # current SPY price - using bars: 3 methods
        # price = data.Bars[self.spy].Close
        price = data[self.spy].Close
        # price = self.Securities[self.spy].Close

        # check if invested already + logic
        if not self.Portfolio.Invested:
            #invest now

            #principle - hold until rises a certain amount then sell and wait
            if self.nextEntryTime <= self.Time:

                # 2 methods to buy stock
                self.SetHoldings(self.spy, 1) # set 100 of available portfolio to this security
                # self.MarketOrder(self.spy, int (self.Portfolio.Cash / price)) # buy max amount (rounded)

                # Log action for later debug
                self.Log("BUY SPY @" + str(price))

                self.entryPrice = price


        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.9 > price: # exit strategy
            # can do self.MarketOrder(...) with a negative number to indicate sell
            # self.Liquidate(self.spy) # this will liquidate the current holdings with this ticker
            self.Liquidate() # this will liquidate the whole portfolio

            self.Log("SELL SPY @" + str(price))

            #add the 30 days period
            self.nextEntryTime = self.Time + self.period