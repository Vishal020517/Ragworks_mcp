from config import get_llm

llm_guard = get_llm(model_name="openai/gpt-oss-120b")


def validate_query_llm(query: str) -> tuple[bool, str]:
    prompt = f"""
You are a strict content safety classifier.

Classify the user query into ONE of these:
- SAFE    → if it is about finance, stocks, companies, or investing
- UNSAFE  → if it involves alcohol, drugs, sexual content, abuse, violence, self-harm, or anything unrelated to finance

Respond ONLY with one word: SAFE or UNSAFE

Query: {query}
"""
    try:
        result = llm_guard.invoke(prompt).content.strip().upper()
        if "UNSAFE" in result:
            return False, "Only financial queries are allowed."
        return True, query
    except Exception as e:
        return False, f"Guard error: {str(e)}"
