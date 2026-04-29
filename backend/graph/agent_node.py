from agents.tool_agent import run_agent
from guardrails.input_guard import validate_query_llm
from guardrails.output_guard import validate_output
from memory.memory_store import load_history, save_turn, format_history_for_prompt


def agent_node(state):
    print("\n[GRAPH] AGENT NODE", flush=True)

    query = state["query"]
    username = state.get("username") or "default"

    is_safe, result = validate_query_llm(query)
    if not is_safe:
        print(f"[INPUT GUARD] Blocked: {result}", flush=True)
        return {"final": f"Query blocked by input guardrail: {result}"}

    print("[INPUT GUARD] Query passed.", flush=True)

    raw_history = load_history(username)
    history_text = format_history_for_prompt(raw_history)

    response = run_agent(query, history=history_text)

    is_valid, validated = validate_output(response)
    if not is_valid:
        print(f"[OUTPUT GUARD] Blocked: {validated}", flush=True)
        return {"final": f"Response blocked by output guardrail: {validated}"}

    print("[OUTPUT GUARD] Response passed.", flush=True)

    save_turn(username, query, validated)
    print(f"[MEMORY] Turn saved for user: {username}", flush=True)

    return {"final": validated}
