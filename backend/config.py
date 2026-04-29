import os
import itertools
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load .env from the backend/ directory regardless of where the script is run from
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# Collect all GROQ keys defined in .env
_GROQ_KEYS = [
    os.getenv("GROQ_API_KEY_1"),
    os.getenv("GROQ_API_KEY_2"),
    os.getenv("GROQ_API_KEY_3"),
]
_GROQ_KEYS = [k for k in _GROQ_KEYS if k]

if not _GROQ_KEYS:
    raise EnvironmentError(
        "No Groq API keys found. Set GROQ_API_KEY_1, GROQ_API_KEY_2, or GROQ_API_KEY_3 in backend/.env"
    )

# Round-robin iterator across all available keys
_key_cycle = itertools.cycle(_GROQ_KEYS)


def _next_key() -> str:
    return next(_key_cycle)


def get_llm(model_name: str = "openai/gpt-oss-120b", temperature: float = 0) -> ChatGroq:
    """
    Returns a ChatGroq instance using the next available API key (round-robin).
    Use this factory in every module instead of constructing ChatGroq directly.
    """
    return ChatGroq(
        model_name=model_name,
        temperature=temperature,
        api_key=_next_key()
    )


# LangSmith tracing — set from .env if present
_langchain_key = os.getenv("LANGCHAIN_API_KEY")
if _langchain_key:
    os.environ["LANGCHAIN_API_KEY"] = _langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "financial-agent")
