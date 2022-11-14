import csv

class dataParser:

    def __init__(self) -> None:
        self.data = list()
        self.index = 0
        self.file = './tickers/constituents_csv.csv'

    def ParseData(self):
        with open(self.file,'r') as inf:
            for line in inf:
                self.data.append(line.split(',')[0])
    
    def GetTicker(self):
        # print(len(self.data))
        # print(self.data[])

        if (self.index <= len(self.data) - 1):
            ticker = self.data[self.index]
            self.index += 1
            return ticker

test = dataParser()
test.ParseData()
# test.GetTicker()
# print(test.GetTicker())
for x in range(1000):
    ticker = test.GetTicker()
    if ticker is not None:
        print(ticker)
    


        
