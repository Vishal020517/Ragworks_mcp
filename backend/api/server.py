from fastapi import FastAPI
from pydantic import BaseModel

from mcp_server.tools.stock_tools import get_stock_price
from mcp_server.tools.financial_tools import calculate_rsi
from mcp_server.tools.news_tools import get_stock_news
from mcp_server.tools.fundamental_tools import get_fundamentals
from mcp_server.tools.rag_tool import retrieve_knowledge

app = FastAPI()


class ToolRequest(BaseModel):
    tool: str
    input: dict


@app.post("/tool")
def call_tool(req: ToolRequest):
    tool = req.tool
    data = req.input

    print(f"\n[API REQUEST] {tool} -> {data}", flush=True)

    if tool == "get_stock_price":
        result = get_stock_price(data["symbol"])
    elif tool == "calculate_rsi":
        result = calculate_rsi(data["symbol"])
    elif tool == "get_news":
        result = get_stock_news(data["query"])
    elif tool == "get_fundamentals":
        result = get_fundamentals(data["symbol"])
    elif tool == "retrieve_knowledge":
        result = retrieve_knowledge(data["query"])
    else:
        result = {"error": "Invalid tool"}

    print(f"[API RESPONSE] {result}", flush=True)

    return result
