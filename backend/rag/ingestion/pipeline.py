from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
INDEX_DIR = BASE_DIR / "index"


def load_documents():
    """
    Load all documents from raw data directory
    """
    print("[INFO] Loading documents...")

    reader = SimpleDirectoryReader(
        input_dir=str(DATA_DIR),
        recursive=True
    )

    documents = reader.load_data()

    if not documents:
        raise ValueError("No documents found. Run scraper first.")

    print(f"[INFO] Loaded {len(documents)} documents")
    return documents


def chunk_documents(documents):
    """
    Split documents into smaller chunks
    """
    print("[INFO] Chunking documents...")

    parser = SimpleNodeParser.from_defaults(
        chunk_size=300,
        chunk_overlap=50
    )

    nodes = parser.get_nodes_from_documents(documents)

    print(f"[INFO] Created {len(nodes)} chunks")
    return nodes


def build_index(nodes):
    """
    Create vector index using local embeddings
    """
    print("[INFO] Building vector index with local embeddings...")

    # 🔥 set local embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    index = VectorStoreIndex(nodes)

    return index


def save_index(index):
    """
    Persist index to disk
    """
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    index.storage_context.persist(
        persist_dir=str(INDEX_DIR)
    )

    print(f"[SUCCESS] Index saved at: {INDEX_DIR}")


def run_pipeline():
    """
    Full ingestion pipeline
    """
    docs = load_documents()
    nodes = chunk_documents(docs)
    index = build_index(nodes)
    save_index(index)


if __name__ == "__main__":
    run_pipeline()