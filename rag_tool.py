# rag_tool.py
from langchain.tools import tool
from rag_store import load_rag_vectorstore

db = load_rag_vectorstore()


@tool
def wazuh_rag_search(query: str) -> str:
    """Searches your Wazuh documentation using vector embeddings."""
    results = db.similarity_search(query, k=4)

    if not results:
        return "No relevant information found in the Wazuh RAG store."

    output = []
    for r in results:
        output.append(r.page_content)

    return "\n\n---\n\n".join(output)
