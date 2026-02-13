import yfinance as yf
import pandas as pd
import numpy as np

def load_cor_matrix(tickers):
    """
    DL data and generate half matrix
    """
    try:
        # DL one month of data
        data = yf.download(tickers, period="1mo", interval="1d", progress=False)['Close']
        
        if data.empty:
            return "⚠️ Data missing"

        # Compute variations of data
        returns = data.pct_change()
        corr_matrix = returns.corr()
        
        # 3. Construction de la chaîne de caractères (Demi-matrice)
        tickers_list = corr_matrix.columns
        output = "📊 CorMatrix for past 30 days\n"
        output += "--------------------------------------\n"
        
        # Header (not entire ticker)
        header = " " * 10
        for t in tickers_list:
            clean_name = t.split('.')[0][:5] # 'Pick the header not the stock exchange location'
            header += f"{clean_name:>8}"
        output += header + "\n"

        # Lines
        for i, row_ticker in enumerate(tickers_list):
            row_name = row_ticker.split('.')[0][:8]
            line = f"{row_name:<10}"
            for j, col_ticker in enumerate(tickers_list):
                if j <= i:  # Only half triangle
                    val = corr_matrix.iloc[i, j]
                    line += f"{val:>8.2f}"
                else:
                    line += " " * 8
            output += line + "\n"
            
        return output

    except Exception as e:
        return f"⚠️ Error while computing : {str(e)}"