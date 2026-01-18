# Import all needed libraries for the project
import yfinance as yf
import pandas as pd
import duckdb as ddb

def investment_report(ticker1):
    ticker = yf.Ticker(ticker1)
    history = ticker.history(period="2d")

    if len(history) < 2:
        return "Lack of data for the day"
    
    today_price = history['Close'].iloc[-1]
    yesterday_price = history['Close'].iloc[-2]
    var = (today_price - yesterday_price)/yesterday_price*100 if yesterday_price != 0 else 0
    return {
        "ticker": ticker1,
        "today_price": f"{today_price:.2f}",
        "yesterday_price": f"{yesterday_price:.2f}",
        "var": f"{var:.2f}%"
    }

con = ddb.connect('himid.db')
con.execute("""
CREATE TABLE IF NOT EXISTS investments(
            ticker TEXT,
            buy_date DATE,
            buy_price DOUBLE)
""")

def report():
    owned_assets = con.execute("SELECT * FROM investments").fetchall()
    reports=[]
    for ticker, b_date, b_price in owned_assets:
        data = yf.Ticker(ticker).history(period="2d")
        current_price = data['Close'].iloc[-1]

        perf_since_buy = (current_price - b_price) / b_price * 100 if b_price != 0 else 0
        reports.append(f"Performance of {ticker} since buy: {perf_since_buy:.2f}%")
    return reports


# print(report())
print(investment_report("AAPL"))
