import yfinance as yf


def get_fundamentals(symbol: str) -> dict:
    """
    Fetch company fundamentals using Yahoo Finance
    """

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info:
            return {"error": "No data found"}

        return {
            "symbol": symbol.upper(),
            "company": info.get("longName"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "revenue": info.get("totalRevenue"),
            "profit_margin": info.get("profitMargins"),
        }

    except Exception as e:
        return {"error": str(e)}