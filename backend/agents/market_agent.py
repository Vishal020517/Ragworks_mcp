from mcp_server.tools.stock_tools import get_stock_price
from config import get_llm


class MarketAgent:
    def __init__(self):
        self.llm = get_llm(model_name="openai/gpt-oss-20b")

    def run(self, symbol: str):
        stock_data = get_stock_price(symbol)

        prompt = f"""
You are a financial market analyst.

Stock Data:
{stock_data}

Analyze the stock condition:
- Is the price high or low?
- Any immediate observation?

Give a short professional analysis.
"""
        response = self.llm.invoke(prompt)
        return {
            "agent": "market",
            "symbol": symbol,
            "data": stock_data,
            "analysis": response.content
        }
