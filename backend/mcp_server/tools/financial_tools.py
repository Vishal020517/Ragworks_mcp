import yfinance as yf
import pandas as pd

def calculate_rsi(symbol: str, period: int = 14) -> dict:
    """
    Calculate RSI using historical stock data
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1mo")

        if data.empty:
            return {"error": "No data"}

        delta = data["Close"].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        latest_rsi = rsi.iloc[-1]

        return {
            "symbol": symbol.upper(),
            "rsi": float(latest_rsi)
        }

    except Exception as e:
        return {"error": str(e)}