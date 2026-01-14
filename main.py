# Import all needed libraries for the project
import yfinance as yf
import pandas as pd
import duckdb as dd

def investment_report(ticker1):
    ticker = yf.Ticker(ticker1)
    history = ticker.history(period="2d")

    if len(history) < 2:
        return "Lack Data for the day"
    
    today_price = history['Close'].iloc[-1]
    yesterday_price = history['Close'].iloc[-2]
    var = (today_price - yesterday_price)/yesterday_price*100 if yesterday_price != 0 else 0
    return {
        "ticker": ticker1,
        "today_price": f"{today_price:.2f}",
        "yesterday_price": f"{yesterday_price:.2f}",
        "var": f"{var:.2f}%"
    }

print(investment_report("AAPL"))