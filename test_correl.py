import yfinance as yf
import pandas as pd
import numpy as np

tickers = ["TTE.PA", "DCAM.PA"]

topix = yf.Ticker('TTE.PA').history(period='3y')
world = yf.Ticker('DCAM.PA').history(period='3y')
df = yf.download(tickers,period='3y')['Close']
df = df.dropna()

returns = df.pct_change().dropna()

corr = returns.corr()

print(corr)