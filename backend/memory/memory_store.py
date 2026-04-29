import json
import os
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent / "sessions"


def _session_file(username: str) -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    return MEMORY_DIR / f"{username}.json"


def load_history(username: str) -> list[dict]:
    """
    Load conversation history for a given username.
    Returns a list of {"role": "user"/"assistant", "content": "..."} dicts.
    """
    path = _session_file(username)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_turn(username: str, query: str, response: str) -> None:
    """
    Append a user/assistant turn to the session file.
    """
    history = load_history(username)

    history.append({
        "role": "user",
        "content": query,
        "timestamp": datetime.now().isoformat()
    })
    history.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })

    path = _session_file(username)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def format_history_for_prompt(history: list[dict], max_turns: int = 6) -> str:
    """
    Format the last N turns of history into a readable string for the prompt.
    max_turns controls how many user/assistant pairs to include (each pair = 2 entries).
    """
    if not history:
        return "No previous conversation."

    recent = history[-(max_turns * 2):]

    lines = []
    for entry in recent:
        role = "User" if entry["role"] == "user" else "Assistant"
        lines.append(f"{role}: {entry['content']}")

    return "\n".join(lines)


def clear_history(username: str) -> None:
    """
    Delete the session file for a given username.
    """
    path = _session_file(username)
    if path.exists():
        path.unlink()
