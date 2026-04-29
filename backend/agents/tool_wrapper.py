from langchain.tools import StructuredTool
from pydantic import BaseModel

from agents.market_agent import MarketAgent
from agents.technical_agent import TechnicalAgent
from agents.news_agent import NewsAgent
from agents.fundamental_agent import FundamentalAgent
from api_client import call_tool
from guardrails.tool_guard import validate_tool_call


market = MarketAgent()
technical = TechnicalAgent()
news = NewsAgent()
fundamental = FundamentalAgent()


class SymbolInput(BaseModel):
    symbol: str


class QueryInput(BaseModel):
    query: str


def market_tool(symbol: str):
    allowed, err = validate_tool_call("MarketAgent", {"symbol": symbol})
    if not allowed:
        return f"Tool call blocked: {err}"
    return str(market.run(symbol))[:1000]


def technical_tool(symbol: str):
    allowed, err = validate_tool_call("TechnicalAgent", {"symbol": symbol})
    if not allowed:
        return f"Tool call blocked: {err}"
    return str(technical.run(symbol))[:1000]


def news_tool(symbol: str):
    allowed, err = validate_tool_call("NewsAgent", {"symbol": symbol})
    if not allowed:
        return f"Tool call blocked: {err}"
    return str(news.run(symbol))[:1200]


def fundamental_tool(symbol: str):
    allowed, err = validate_tool_call("FundamentalAgent", {"symbol": symbol})
    if not allowed:
        return f"Tool call blocked: {err}"
    return str(fundamental.run(symbol))[:1200]


def rag_tool_func(query: str):
    allowed, err = validate_tool_call("RAGTool", {"query": query})
    if not allowed:
        return f"Tool call blocked: {err}"
    return str(call_tool("retrieve_knowledge", {"query": query}))[:1500]


tools = [

    StructuredTool.from_function(
        name="MarketAgent",
        func=market_tool,
        description="Get stock price and market analysis. Input: stock symbol like AAPL",
        args_schema=SymbolInput
    ),

    StructuredTool.from_function(
        name="TechnicalAgent",
        func=technical_tool,
        description="Get RSI and technical indicators. Input: stock symbol",
        args_schema=SymbolInput
    ),

    StructuredTool.from_function(
        name="NewsAgent",
        func=news_tool,
        description="Get latest news and sentiment. Input: stock symbol",
        args_schema=SymbolInput
    ),

    StructuredTool.from_function(
        name="FundamentalAgent",
        func=fundamental_tool,
        description="Get company fundamentals. Input: stock symbol",
        args_schema=SymbolInput
    ),

    StructuredTool.from_function(
        name="RAGTool",
        func=rag_tool_func,
        description="Get deep knowledge about company including business model, risks, and long-term insights. Input: company name or query",
        args_schema=QueryInput
    ),
]
