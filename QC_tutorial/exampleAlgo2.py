# region imports
from AlgorithmImports import *
# endregion

class DynamicStopLossAlgo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetEndDate(2021, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash

        self.qqq = self.AddEquity("QQQ", Resolution.Hour).Symbol #to reference this secutiry down the line

        # To access the tickets
        self.entryTicket = None 
        self.stopMarketTicket = None

        # initialize to earliest possible date
        self.entryTime = datetime.min
        self.StopMarketOrderFillTime = datetime.min

        # keeps track of qqq's highest price
        self.highestPrice = 0

    def OnData(self, data: Slice):

        # wait 30 days after last exit
        if (self.Time - self.StopMarketOrderFillTime).days < 30:
            return

        price = self.Securities[self.qqq].Price #access the price of securtity

        # send entry limit order
        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq): #if no open order -> the second statement will be an empty list and evaluate to false 
            quantity = self.CalculateOrderQuantity(self.qqq, 0.9) # calculate 90% allocation to our portfolio
            self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order") # send in limit order -> optional: return the ticket and store it/ add a custom tag as a 4th argument
            self.entryTime = self.Time # record the time of entry submission

        # move limit price if not filled after 1 day
        if (self.Time - self.entryTime).days > 1 and self.entryTicket != OrderStatus.Filled: # check if order status is not "filled"
            self.entryTime = self.Time # update the time 
            updateFields = UpdateOrderFields() # update 
            updateFields.LimitPrice = price
            self.entryTicket.Update(updateFields)


        # move up trailing stop loss price (will only be done after buy a position and !!! fill it !!!)
        if self.stopMarketTicket is not None and self.Portfolio.Invested: # check if have a stop market order, 
            if price > self.highestPrice: # update the price if a new high is reached
                self.highestPrice = price 
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = price * 0.95 # update stop loss at 5% below highest price
                self.stopMarketTicket.Update(updateFields)

                #can do debugging similar to print statements with:
                self.Debug(updateFields.StopPrice)

    def OnOrderEvent(self, orderEvent):

        if orderEvent.Status != OrderStatus.Filled: # exits if order is not filled
            return

        # send stop loss order if entry limit order is filled
        if self.entryTicket is not None and self.entryTicket.OrderId == orderEvent.OrderId: # compare the order ID's to verify it is the right order and that the limit entry order is now filled
            self.stopMarketTicket = self.StopMarketOrder(self.qqq, -self.entryTicket.Quantity, 0.95 * self.entryTicket.AverageFillPrice) 

        # save fill time of stop loss order
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: # in the case if the stop loss order is filled -> i.e we exited at the stop loss
            self.StopMarketOrderFillTime = self.Time # to ensure we would wait 30 days
            self.highestPrice = 0 # reset the highest price