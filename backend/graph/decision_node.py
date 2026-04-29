from config import get_llm

llm = get_llm(model_name="openai/gpt-oss-120b")


def decision_node(state):
    print("[GRAPH] DECISION NODE", flush=True)

    prompt = f"""
You are a financial analyst AI.

User Query: {state['query']}
Retrieved Knowledge: {state.get('rag')}
Market Data: {state.get('market')}
Technical: {state.get('technical')}
News: {state.get('news')}
Fundamentals: {state.get('fundamental')}

Rules:
- Use retrieved knowledge ONLY if relevant
- Prefer real data over vague knowledge
- Do NOT hallucinate

Output:
Summary:
...

Recommendation: BUY / HOLD / SELL

Reasoning:
...
"""
    response = llm.invoke(prompt)
    return {"final": response.content}
