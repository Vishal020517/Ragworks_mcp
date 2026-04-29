from typing import TypedDict, Optional


class GraphState(TypedDict):
    query: str
    symbol: str
    username: Optional[str]
    history: Optional[str]

    market: Optional[dict]
    technical: Optional[dict]
    news: Optional[dict]
    fundamental: Optional[dict]
    rag: Optional[str]
    final: Optional[str]
