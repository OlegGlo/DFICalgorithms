from tkinter import Y
import pandas_ta as ta
import dash
import plotly
import numpy as np
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Notes: Very macro approach

# Code and graph as a proof of concept, which can be developed into a working algorithm relatively quickly

# Works well with big indexes like VFV

# False signals at this stage are still not fixed, limitations of the strategy itself

# Tried to prevent look-ahead bias

# I would like your input on some other indicators to look at/strategies.

# get ticker data
df = yf.Ticker('BTC-USD').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])] #Good examples: BTC-USD,AAPL,VFV.TO Bad examples: TSLA
# calculate MACD values
df.ta.macd(close='close', fast=12, slow=26, append=True)
# Force lowercase (optional)
df.columns = [x.lower() for x in df.columns]
# Construct a 2 x 1 Plotly figure
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

# # Candlestick chart for pricing
# fig.append_trace(
#     go.Candlestick(
#         x=df.index,
#         open=df['open'],
#         high=df['high'],
#         low=df['low'],
#         close=df['close'],
#         increasing_line_color='#ff9900',
#         decreasing_line_color='black',
#         showlegend=False
#     ), row=1, col=1
# )

# Fast Signal (%k)
fig.append_trace(
    go.Scatter(
        x=df.index,
        y=df['macd_12_26_9'],
        line=dict(color='#228B22', width=2), #orange
        name='macd',
        # showlegend=False,
        legendgroup='2',
    ), row=2, col=1
)

# Slow signal (%d)
fig.append_trace(
    go.Scatter(
        x=df.index,
        y=df['macds_12_26_9'],
        line=dict(color='#000000', width=2), #black
        # showlegend=False,
        legendgroup='2',
        name='signal'
    ), row=2, col=1
)


print(len(df['macds_12_26_9']))
# print(df['macds_12_26_9'][len(df['macds_12_26_9'])-1])

def inflextionUp(x, df):
    if (df['macds_12_26_9'][x] > df['macds_12_26_9'][x-1] and (df['macds_12_26_9'][x-3] > df['macds_12_26_9'][x-2] > df['macds_12_26_9'][x-1])):
        return True
    else:
        return False

def inflextionDown(x, df):
    if (df['macds_12_26_9'][x] < df['macds_12_26_9'][x-1] and (df['macds_12_26_9'][x-3] < df['macds_12_26_9'][x-2] < df['macds_12_26_9'][x-1])):
        return True
    else:
        return False

def NotEnd(x,df):
    if ((x + 1) > 63):
        return True
    else:
        return False

testarrayBuy = []
for x in range(len(df['macds_12_26_9'])-1):
    testarrayBuy.append(df['macds_12_26_9'][x])

testarraySell = []
for x in range(len(df['macds_12_26_9'])-1):
    testarraySell.append(df['macds_12_26_9'][x])

markersBuy = []
markersSell = []

for x in range(len(df['macds_12_26_9'])):
    if (inflextionUp(x,df) == True):
        # print(df['macds_12_26_9'][x])
        # infUp = x
        # print(x)
        markersBuy.append(df['macds_12_26_9'][x])

for x in range(len(df['macds_12_26_9'])):
    if (inflextionDown(x,df) == True):
        # print(df['macds_12_26_9'][x])
        # infDown = x
        # print(x)
        markersSell.append(df['macds_12_26_9'][x])

# print(type(df))

for x in range(len(df['macds_12_26_9'])-1):
    if (df['macds_12_26_9'][x] not in markersSell):
        testarraySell[x] = None
    else:
        testarraySell[x] = df['open'][x]

for x in range(len(df['macds_12_26_9'])-1):
    if (df['macds_12_26_9'][x] not in markersBuy):
        testarrayBuy[x] = None
    else:
        testarrayBuy[x] = df['open'][x]

# print(testarrayBuy)
# print(testarraySell)

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

# fig.append_trace( #Paint buy period
#     go.Scatter(
#         x=df.index[45:57],
#         y=df['open'],
#         line=dict(color='#000000', width=1),
#         name='open',
#         # showlegend=False,
#         legendgroup='1',
#     ), row=1, col=1
# )

# if concave up (change colour)

# # Colorize the histogram values
# colors = np.where(df['macdh_12_26_9'] < 0, '#000', '#ff9900')
# # Plot the histogram
# fig.append_trace(
#     go.Bar(
#         x=df.index,
#         y=df['macdh_12_26_9'],
#         name='histogram',
#         marker_color=colors,
#     ), row=2, col=1
# )

# Make it pretty
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