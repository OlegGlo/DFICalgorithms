from tkinter import Y
import pandas_ta as ta
import dash
import plotly
import numpy as np
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# get ticker data
df = yf.Ticker('GME').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])] #Good examples: TTM,BTC-USD
# calculate EMA values
df.ta.ema(close='close', length=8, append=True)
df.ta.ema(close='close', length=21, append=True)
df.ta.ema(close='close', length=55, append=True)

# Force lowercase (optional)
df.columns = [x.lower() for x in df.columns]
# Construct a 2 x 1 Plotly figure

# print(df)

fig = make_subplots(rows=2, cols=1)
# price Line
fig.append_trace(
    go.Scatter(
        x=df.index,
        y=df['open'],
        line=dict(color='#228B22', width=1),
        name='open',
        # showlegend=False,
        legendgroup='1',
    ), row=1, col=1
)

# Fast Signal (%k)
fig.append_trace(
    go.Scatter(
        x=df.index,
        y=df['ema_8'],
        line=dict(color='#FF0000', width=2), #red
        name='ma_8',
        # showlegend=False,
        legendgroup='2',
    ), row=2, col=1
)
fig.append_trace(
    go.Scatter(
        x=df.index,
        y=df['ema_21'],
        line=dict(color='#00FF00', width=2), #green
        name='ma_21',
        # showlegend=False,
        legendgroup='2',
    ), row=2, col=1
)
fig.append_trace(
    go.Scatter(
        x=df.index,
        y=df['ema_55'],
        line=dict(color='#0000FF', width=2), #orange
        name='ma_55',
        # showlegend=False,
        legendgroup='2',
    ), row=2, col=1
)

# 55 above all - sell, 55 below, buy
positionOpen = False

# Singals generation
def BuySignal(x,df):
    if (df['ema_55'][x] < df['ema_21'][x] and df['ema_55'][x] < df['ema_8'][x]):
        return True
    else:
        return False

def SellSignal(x,df):
    if (df['ema_55'][x] > df['ema_21'][x] and df['ema_55'][x] > df['ema_8'][x]):
        return True
    else:
        return False

# testarrayBuy = []
# for x in range(len(df['macds_12_26_9'])-1):
#     testarrayBuy.append(df['macds_12_26_9'][x])

# testarraySell = []
# for x in range(len(df['macds_12_26_9'])-1):
#     testarraySell.append(df['macds_12_26_9'][x])

#Populate array
markersBuy = []
markersSell = []

#determine entry and exit points
for x in range(len(df['ema_55'])):
    if (BuySignal(x,df) == True and positionOpen == False):
        markersBuy.append(df['ema_55'][x])
        positionOpen = True
    elif (SellSignal(x,df) == True and positionOpen == True):
        markersSell.append(df['ema_55'][x])
        positionOpen = False

#populate arrays
testarrayBuy = []
for x in range(len(df['ema_55'])-1):
    testarrayBuy.append(df['ema_55'][x])

testarraySell = []
for x in range(len(df['ema_55'])-1):
    testarraySell.append(df['ema_55'][x])

#adjust arrays for output
for x in range(len(df['ema_55'])-1):
    if (df['ema_55'][x] not in markersSell):
        testarraySell[x] = None
    else:
        testarraySell[x] = df['open'][x]

for x in range(len(df['ema_55'])-1):
    if (df['ema_55'][x] not in markersBuy):
        testarrayBuy[x] = None
    else:
        testarrayBuy[x] = df['open'][x]

# Plot buy and sell signals
fig.append_trace(
    go.Scatter(
        x=df.index, 
        y=testarrayBuy, 
        mode = 'markers',
        marker =dict(color='Green', symbol='triangle-up', size = 16),
        name='Buy Signal'
        ), row=1, col=1
)

fig.append_trace(
    go.Scatter(
        x=df.index, 
        y=testarraySell, 
        mode = 'markers',
        marker =dict(color='Red', symbol='triangle-down', size = 16),
        name='Sell Signal'
        ), row=1, col=1
)

# Layout edit
layout = go.Layout(
    plot_bgcolor='#efefef',
    # Font Families
    font_family='Monospace',
    font_color='#000000',
    font_size=20,
    xaxis=dict(
        rangeslider=dict(
            visible=False
        )
    )
)

# Update options and show plot
fig.update_layout(layout)
fig.show()