from langchain.tools import tool

@tool("route_query", return_direct=True)
def route_query(query: str) -> str:
    """
    Routes a user query to the correct tool based on intent keywords.
    The returned string is the tool name to execute.
    """

    q = query.lower()

    # 1. If user wants vulnerabilities or "top issues"
    if "vulnerability" in q or "top 5" in q or "issues" in q:
        return "run_top5_workflow"

    # 2. Agent-related queries
    if "agent" in q or "agents" in q:
        return "get_active_wazuh_agents"

    # 3. Alerts — summary, alerts, security events, etc.
    if "alert" in q or "summary" in q:
        return "wazuh_alert_summary"

    # 4. Logs
    if "logs" in q or "manager logs" in q:
        return "get_all_manager_logs"

    # 5. FIM
    if "file integrity" in q or "fim" in q:
        return "custom_fim_queries"

    # 6. Processes
    if "process" in q:
        return "get_wazuh_processes"

    # 7. Ports
    if "port" in q:
        return "get_wazuh_agent_ports"

    # 8. Alerts filtering
    if "filter" in q and "alert" in q:
        return "custom_alert_filters"

    # 9. Default → RAG semantic search
    return "wazuh_rag_search"
