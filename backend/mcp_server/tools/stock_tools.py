import yfinance as yf


def get_stock_price(symbol: str) -> dict:
    """
    Fetch real-time stock price using Yahoo Finance
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        if data.empty:
            return {"error": "No data found"}

        latest_price = data["Close"].iloc[-1]

        return {
            "symbol": symbol.upper(),
            "price": float(latest_price)
        }

    except Exception as e:
        return {"error": str(e)}