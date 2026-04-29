from mcp_server.tools.news_tools import get_stock_news
from config import get_llm


class NewsAgent:
    def __init__(self):
        self.llm = get_llm(model_name="openai/gpt-oss-20b")

    def run(self, symbol: str):
        news = get_stock_news(symbol)

        prompt = f"""
You are a financial news analyst.

News Articles:
{news}

Tasks:
- Summarize key themes
- Identify sentiment (positive / negative / neutral)
- Highlight any risks or opportunities

Give concise professional analysis.
"""
        response = self.llm.invoke(prompt)
        return {
            "agent": "news",
            "symbol": symbol,
            "data": news,
            "analysis": response.content
        }
