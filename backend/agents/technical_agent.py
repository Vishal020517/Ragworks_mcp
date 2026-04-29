from mcp_server.tools.financial_tools import calculate_rsi
from config import get_llm


class TechnicalAgent:
    def __init__(self):
        self.llm = get_llm(model_name="openai/gpt-oss-20b")

    def run(self, symbol: str):
        rsi_data = calculate_rsi(symbol)

        prompt = f"""
You are a technical stock analyst.

RSI Data:
{rsi_data}

Interpret this RSI value:
- Above 70 → overbought
- Below 30 → oversold

Give trading insight.
"""
        response = self.llm.invoke(prompt)
        return {
            "agent": "technical",
            "symbol": symbol,
            "data": rsi_data,
            "analysis": response.content
        }
