import os
import itertools
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

_GROQ_KEYS = [k for k in [
    os.getenv("GROQ_API_KEY_1"),
    os.getenv("GROQ_API_KEY_2"),
    os.getenv("GROQ_API_KEY_3"),
] if k]

if not _GROQ_KEYS:
    raise EnvironmentError(
        "No Groq API keys found. Set GROQ_API_KEY_1, GROQ_API_KEY_2, or GROQ_API_KEY_3 in backend/.env"
    )

_key_cycle = itertools.cycle(_GROQ_KEYS)


def get_llm(model_name: str="openai/gpt-oss-120b", temperature: float=0) -> ChatGroq:
    return ChatGroq(model_name=model_name, temperature=temperature, api_key=next(_key_cycle))


_langchain_key = os.getenv("LANGCHAIN_API_KEY")
if _langchain_key:
    os.environ["LANGCHAIN_API_KEY"] = _langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "financial-agent")
