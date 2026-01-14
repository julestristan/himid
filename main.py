# Import all needed libraries for the project
import yfinance as yf
import pandas as pd
import duckdb as dd

def investment_report(ticker1):
    ticker = yf.Ticker(ticker1)
    history = ticker.history(period="2d")

    if len(history) < 2:
        return "Lack Data for the day"
    
    today_price = history['Close'][-1]
    yesterday_price = history['Close'][-2]
    var = today_price - yesterday_price
    return {
        "ticker": ticker1,
        "today_price": round(today_price,),
        "yesterday_price": round(yesterday_price,),
        "var": var
    }

print(investment_report("AAPL"))