from rag.retriever.retriever import RAGRetriever

rag = RAGRetriever()

def retrieve_knowledge(query:str) -> str:
    """
    MCP Tool: Retrieve financial knowledge from RAG
    """
    result = rag.query(query)
    return result