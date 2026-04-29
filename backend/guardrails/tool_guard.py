import re

ALLOWED_TOOLS = {"MarketAgent", "TechnicalAgent", "NewsAgent", "FundamentalAgent", "RAGTool"}

SYMBOL_PATTERN = re.compile(r"^[A-Z]{1,5}$")

MAX_INPUT_LENGTH = 300

BLOCKED_KEYWORDS = [
    "drop table", "delete from", "insert into",
    "exec(", "eval(", "__import__",
    "<script", "javascript:",
]


def validate_tool_call(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    if tool_name not in ALLOWED_TOOLS:
        return False, f"Tool '{tool_name}' is not in the allowed tools list."

    for key, value in tool_input.items():
        if not isinstance(value, str):
            continue
        if len(value) > MAX_INPUT_LENGTH:
            return False, f"Input '{key}' exceeds maximum allowed length of {MAX_INPUT_LENGTH} characters."
        lowered = value.lower()
        for pattern in BLOCKED_KEYWORDS:
            if pattern in lowered:
                return False, f"Input '{key}' contains a blocked pattern: '{pattern}'."

    if "symbol" in tool_input:
        symbol = tool_input["symbol"].strip().upper()
        if not SYMBOL_PATTERN.match(symbol):
            return False, f"Invalid stock symbol format: '{tool_input['symbol']}'. Expected 1-5 uppercase letters."

    return True, ""
