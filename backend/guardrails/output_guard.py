from config import get_llm

llm_guard = get_llm(model_name="openai/gpt-oss-120b")


def validate_output(response: str) -> tuple[bool, str]:
    """
    Validates the agent's final output.
    Blocks empty, harmful, or clearly nonsensical responses.
    Allows both full financial analyses and valid conversational answers
    (e.g. memory queries, clarification responses).
    Returns (is_valid, response_or_error_message).
    """

    if not response or len(response.strip()) < 10:
        return False, "Response was too short or empty."

    prompt = f"""
You are a financial AI output safety checker.

The AI agent handles two types of responses:
1. Full financial analysis — contains a summary, recommendation (BUY/HOLD/SELL), and reasoning.
2. Conversational answer — a short, factual reply to a memory or context question
   (e.g. "The stock we discussed was AAPL", "You asked about Tesla earlier").

Classify the response below as:
- VALID   → if it is either a proper financial analysis OR a relevant, factual conversational answer related to finance or the ongoing conversation
- INVALID → if it is harmful, completely off-topic, hallucinates financial data without basis, or is nonsensical

Respond ONLY with one word: VALID or INVALID

Response to review:
{response}
"""

    try:
        result = llm_guard.invoke(prompt)
        label = result.content.strip().upper()

        if "INVALID" in label:
            return False, "The generated response did not meet quality standards."

        return True, response

    except Exception as e:
        return False, f"Output guard error: {str(e)}"
