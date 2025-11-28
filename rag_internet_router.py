from langchain.tools import tool

@tool
def route_query(query: str) -> str:
    """
    Decides which tool should be used based on the user's question.
    """
    q = query.lower()

    if "agent" in q:
        return "get_active_wazuh_agents"
    
    if "alert" in q or "summary" in q:
        return "wazuh_alert_summary"   # when you add it
    
    return "wazuh_rag_search"
