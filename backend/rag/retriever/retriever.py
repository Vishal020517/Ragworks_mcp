from pathlib import Path
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE_DIR / "index"

class RAGRetriever:
    def __init__(self):
        self.index = self._load_index()

    def _load_index(self):
        """
        Load persisted index from disk
        """
        print("[INFO] Loading index...")

        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        storage_context = StorageContext.from_defaults(
            persist_dir=str(INDEX_DIR)
        )

        index = load_index_from_storage(storage_context)

        print("[INFO] Index loaded successfully")
        return index

    def query(self, query: str) -> str:
        """
        Retrieve relevant chunks WITHOUT using LLM
        """
        retriever = self.index.as_retriever(similarity_top_k=3)

        nodes = retriever.retrieve(query)

        results = []
        for node in nodes:
            results.append(node.node.text)

        return "\n\n---\n\n".join(results)