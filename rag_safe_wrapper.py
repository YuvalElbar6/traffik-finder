from langchain_core.tools import tool

@tool
def safe_rag_explain(text: str) -> str:
    """
    Safe RAG mode:
    - NEVER generate information not found in your RAG index.
    - State clearly when information is missing.
    - Explanations must be simple (non-expert user).
    """

    from rag_tool import wazuh_rag_search

    results = wazuh_rag_search(text)
    if not results or results.strip() == "":
        return (
            "No reliable information was found in the RAG database for this topic."
            "I cannot generate details that are not present in your index documents"
        )
    
    return (
        "Here is a simple explanation based strictly on your RAG data:\n\n"
        + results
        + "\n\n(Explanation limited to available non-hallucinatory sources.)"
    )