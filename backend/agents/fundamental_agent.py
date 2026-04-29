import requests
import yfinance as yf


class FundamentalAgent:

    def get_symbol(self, query: str) -> str:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        try:
            res = requests.get(
                url,
                params={"q": query, "quotesCount": 1, "newsCount": 0},
                timeout=5
            ).json()
            symbol = res["quotes"][0]["symbol"]
            stock = yf.Ticker(symbol)
            if stock.info and stock.info.get("marketCap"):
                return symbol
        except Exception:
            pass

        for word in query.lower().split():
            if len(word) <= 5:
                candidate = word.upper()
                try:
                    if yf.Ticker(candidate).info.get("marketCap"):
                        return candidate
                except Exception:
                    continue

        return "AAPL"

    def run(self, query: str):
        symbol = self.get_symbol(query)
        try:
            info = yf.Ticker(symbol).info
            data = {
                "company": info.get("longName"),
                "sector": info.get("sector"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "eps": info.get("trailingEps"),
                "revenue": info.get("totalRevenue"),
                "profit_margin": info.get("profitMargins"),
            }
            analysis = f"""
Company: {data['company']}
Sector: {data['sector']}
Market Cap: {data['market_cap']}
PE Ratio: {data['pe_ratio']}
EPS: {data['eps']}
Revenue: {data['revenue']}
Profit Margin: {data['profit_margin']}

Interpretation:
- Profit margin > 15% → strong profitability
- High PE → growth expectations
- Low PE → undervaluation or slower growth
"""
            return {
                "agent": "fundamental",
                "symbol": symbol,
                "data": data,
                "analysis": analysis.strip()
            }
        except Exception as e:
            return {"agent": "fundamental", "symbol": symbol, "error": str(e)}
