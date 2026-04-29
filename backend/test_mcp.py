from mcp_client import call_tool

print("PRICE:", call_tool("get_stock_price_tool", {"symbol": "AAPL"}))
print("RSI:", call_tool("calculate_rsi_tool", {"symbol": "AAPL"}))
print("NEWS:", call_tool("get_news_tool", {"query": "Apple"}))
print("FUND:", call_tool("get_fundamentals_tool", {"symbol": "AAPL"}))