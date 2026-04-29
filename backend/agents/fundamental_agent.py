import requests
import yfinance as yf


class FundamentalAgent:

    # ------------------ SYMBOL RESOLVER ------------------

    def get_symbol(self, query: str) -> str:
        """
        Convert user query → valid stock ticker dynamically
        """

        url = "https://query1.finance.yahoo.com/v1/finance/search"

        # 🔹 STEP 1: Try Yahoo Finance search API
        try:
            res = requests.get(
                url,
                params={"q": query, "quotesCount": 1, "newsCount": 0},
                timeout=5
            ).json()

            symbol = res["quotes"][0]["symbol"]

            # 🔹 Validate symbol using yfinance
            stock = yf.Ticker(symbol)
            info = stock.info

            if info and info.get("marketCap"):
                return symbol

        except Exception:
            pass

        # STEP 2: Smarter fallback (scan words)
        words = query.lower().split()

        for word in words:
            if len(word) <= 5:
                candidate = word.upper()
                try:
                    stock = yf.Ticker(candidate)
                    if stock.info.get("marketCap"):
                        return candidate
                except Exception:
                    continue

        # 🔹 STEP 3: Last safe fallback
        return "AAPL"

    # ------------------ MAIN FUNCTION ------------------

    def run(self, query: str):
        symbol = self.get_symbol(query)

        try:
            stock = yf.Ticker(symbol)
            info = stock.info

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
            return {
                "agent": "fundamental",
                "symbol": symbol,
                "error": str(e)
            }