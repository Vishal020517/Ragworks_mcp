from api_client import call_tool


def market_node(state):
    print("\n[GRAPH] MARKET NODE", flush=True)
    return {"market": call_tool("get_stock_price", {"symbol": state["symbol"]})}


def technical_node(state):
    print("[GRAPH] TECHNICAL NODE", flush=True)
    return {"technical": call_tool("calculate_rsi", {"symbol": state["symbol"]})}


def news_node(state):
    print("[GRAPH] NEWS NODE", flush=True)
    return {"news": call_tool("get_news", {"query": state["symbol"]})}


def fundamental_node(state):
    print("[GRAPH] FUNDAMENTAL NODE", flush=True)
    return {"fundamental": call_tool("get_fundamentals", {"symbol": state["symbol"]})}


def rag_node(state):
    print("[GRAPH] RAG NODE", flush=True)
    result = call_tool("retrieve_knowledge", {"query": state["query"]})
    return {"rag": result}
