import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import yfinance as yf


def load_heatmap(tickers, period, file_path):
    file_path = f"../assets/{file_path}"
    try:
        data = yf.download(
            tickers=tickers, period=period, interval="1d", progress=False
        )["Close"]
        if data.empty:
            raise ValueError("Data missing")

        returns = data.pct_change()
        corr_matrix = returns.corr()

        # Get rid of the stock exchange location
        corr_matrix.columns = [col.split(".")[0] for col in corr_matrix.columns]
        corr_matrix.index = [idx.split(".")[0] for idx in corr_matrix.index]
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        # Option if diagonals needs to be part of the CorMatrix:
        # mask = np.triu(np.ones_like(corr_matrix, dtype=bool),k=1)
        plt.figure(figsize=(12, 10))  # According to portfolio size
        sns.heatmap(
            corr_matrix,
            mask=mask,
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            linewidths=0.5,
        )
        plt.title(f"CorMatrix for past {period}")
        # Make sure we have a png file
        if not file_path.endswith(".png"):
            file_path += ".png"
        plt.savefig(file_path)
        plt.close()
        return file_path, corr_matrix

    except Exception as e: # noqa: BLE001
        print(f"⚠️ Can't load CorMatrix: {e!s}")
        return None
