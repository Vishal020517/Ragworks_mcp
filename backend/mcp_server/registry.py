from mcp_server.tools.stock_tools import get_stock_price
from mcp_server.tools.financial_tools import calculate_rsi
from mcp_server.tools.news_tools import get_stock_news
from mcp_server.tools.rag_tool import retrieve_knowledge
from mcp_server.tools.fundamental_tools import get_fundamentals
import time


def register_tools(mcp):


    @mcp.tool()
    def get_stock_price_tool(symbol: str):
        start = time.time()
        print(f"\n[REQUEST] STOCK → {symbol}", flush=True)

        result = get_stock_price(symbol)

        print(f"[RESPONSE] {result}", flush=True)
        print(f"[TIME] {round(time.time() - start, 2)}s", flush=True)

        return result


    @mcp.tool()
    def calculate_rsi_tool(symbol: str):
        start = time.time()
        print(f"\n[REQUEST] RSI → {symbol}", flush=True)

        result = calculate_rsi(symbol)

        print(f"[RESPONSE] {result}", flush=True)
        print(f"[TIME] {round(time.time() - start, 2)}s", flush=True)

        return result


    @mcp.tool()
    def get_news_tool(query: str):
        start = time.time()
        print(f"\n[REQUEST] NEWS → {query}", flush=True)

        result = get_stock_news(query)

        print(f"[RESPONSE] {len(result)} articles", flush=True)
        print(f"[TIME] {round(time.time() - start, 2)}s", flush=True)

        return result


    @mcp.tool()
    def get_fundamentals_tool(symbol: str):
        start = time.time()
        print(f"\n[REQUEST] FUNDAMENTALS → {symbol}", flush=True)

        result = get_fundamentals(symbol)

        print(f"[RESPONSE] {result}", flush=True)
        print(f"[TIME] {round(time.time() - start, 2)}s", flush=True)

        return result