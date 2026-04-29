from config import get_llm


llm = get_llm(model_name="openai/gpt-oss-120b")


def extract_symbol(query: str) -> str:
    """
    Use LLM to extract stock ticker dynamically
    """

    try:
        prompt = f"""
        Extract the stock ticker symbol from the user query.

        Rules:
        - Return ONLY the ticker symbol
        - No explanation
        - If company name is given → convert to ticker
        - If unsure → return AAPL

        Examples:
        Apple → AAPL
        Tesla → TSLA
        Microsoft → MSFT
        Google → GOOGL

        Query: {query}

        Answer:
        """

        response = llm.invoke(prompt).content.strip().upper()

        symbol = response.split()[0]

        print(f"[SYMBOL] Extracted: {symbol}", flush=True)

        return symbol

    except Exception as e:
        print(f"[SYMBOL] LLM extraction failed: {str(e)}", flush=True)
        return "AAPL"