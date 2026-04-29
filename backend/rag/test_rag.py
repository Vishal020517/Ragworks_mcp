from rag.retriever.retriever import RAGRetriever


def main():
    rag = RAGRetriever()

    while True:
        query = input("\nEnter query (or 'exit'): ")

        if query.lower() == "exit":
            break

        result = rag.query(query)

        print("\n--- RESULT ---\n")
        print(result)


if __name__ == "__main__":
    main()