# file: wazuh_mcp_server.py
from mcp.server.fastmcp import FastMCP

from mcp_client_call import wazuh_get, wazuh_indexer_post, compress_results
from mcp_helper import auto_params


# ==========================
#   MCP SERVER
# ==========================
mcp = FastMCP(
    name="wazuh-mcp-server",
    host="127.0.0.1",
    port=8080,
    sse_path="/sse",
)

# ============================================================
# 1) RULES SUMMARY — /rules
# ============================================================
@mcp.tool(name="get_wazuh_rules_summary")
def get_rules_summary(params):
    data = wazuh_get("/rules?limit=5000")
    count = data["data"]["total_affected_items"]
    return f"Total rules installed: {count}"


# ============================================================
# 2) MANAGER LOGS — /manager/logs
# ============================================================
@mcp.tool(name="get_wazuh_manager_logs")
@auto_params("limit", defaults={"limit": "50"})
def get_manager_logs(params):
    raw = params["limit"]

    # Convert to int safely
    try:
        limit = int(raw)
    except:
        limit = 50  # fallback

    # Enforce acceptable range
    if limit <= 0:
        limit = 50
    if limit > 5000:
        limit = 5000

    data = wazuh_get(f"/manager/logs?limit={limit}&sort=-timestamp")
    return str(compress_results(data,max_items=10, max_fields=6))

# ============================================================
# 3) WEEKLY STATS — /manager/stats/weekly
# ============================================================
@mcp.tool(name="get_wazuh_weekly_stats")
def get_weekly_stats(params):
    data = wazuh_get("/manager/stats/weekly")
    return str(compress_results(data,max_items=10, max_fields=6))


# ============================================================
# 4) CLUSTER NODES — /cluster/nodes
# ============================================================
@mcp.tool(name="get_wazuh_cluster_nodes")
def get_cluster_nodes(params):
    data = wazuh_get("/cluster/nodes")
    return str(compress_results(data,max_items=10, max_fields=6))


# ============================================================
# 5) CLUSTER HEALTH — /cluster/healthcheck
# ============================================================
@mcp.tool(name="get_wazuh_cluster_health")
def get_cluster_health(params):
    data = wazuh_get("/cluster/healthcheck")
    return str(compress_results(data,max_items=10, max_fields=6))


# ============================================================
# 6) VULNERABILITIES — /vulnerability/os/{agent_id}
# ============================================================
@mcp.tool(name="get_wazuh_vulnerabilities")
@auto_params("agent_id", defaults={"agent_id": "001"})
def get_wazuh_vulnerabilities(params):
    agent_id = params["agent_id"]

    body = {
        "size": 50,
        "query": {
            "bool": {
                "must": [
                    {"term": {"agent.id": agent_id}}
                ]
            }
        }
    }

    result = wazuh_indexer_post(
        "/wazuh-states-vulnerabilities-*/_search",body
    )

    hits = result.get("hits", {}).get("hits", [])

    vulns = []
    for hit in hits:
        src = hit.get("_source", {})
        vulns.append(src)


    return str(compress_results(vulns,max_items=10, max_fields=6))



# ============================================================
# 7) PROCESSES — /syscollector/{agent}/processes
# ============================================================
@mcp.tool(name="get_wazuh_processes")
@auto_params("agent_id", defaults={"agent_id": "001"})
def get_processes(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/syscollector/{agent_id}/processes?limit=50")
    return str(compress_results(data,max_items=10, max_fields=6))


# ============================================================
# 8) AGENT PORTS — /syscollector/{agent}/ports
# ============================================================
@mcp.tool(name="get_wazuh_agent_ports")
@auto_params("agent_id", defaults={"agent_id": "001"})
def get_agent_ports(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/syscollector/{agent_id}/ports?limit=50")
    return str(compress_results(data,max_items=10, max_fields=6))


# ============================================================
# 9) SEARCH MANAGER LOGS — /manager/logs?q=
# ============================================================
@mcp.tool(name="search_wazuh_manager_logs")
@auto_params("query", "limit", defaults={"query": "", "limit": "20"})
def search_manager_logs(params):
    query = params["query"]
    raw_limit = params["limit"]

    # convert limit safely
    try:
        limit = int(raw_limit)
    except:
        limit = 20

    # enforce sane boundaries
    if limit <= 0:
        limit = 20
    if limit > 50:
        limit = 50

    # call API with limit
    data = wazuh_get(f"/manager/logs?q={query}&limit={limit}")

    items = data.get("data", {}).get("affected_items", [])

    # compress ONLY the list of log items (very important!)
    compressed = compress_results(items, max_items=limit, max_fields=6)

    return str(compressed)


# ============================================================
# 10) CUSTOM ALERT FILTERS — /alerts
# ============================================================
@mcp.tool(name="custom_alert_filters")
@auto_params("agent_id", defaults={"agent_id": "001"})
def custom_alert_filters(params):
    agent_id = params["agent_id"]

    body = {
        "size": 50,
        "query": {
            "bool": {
                "must": [
                    {"term": {"agent.id": agent_id}}
                ]
            }
        },
        "sort": [
            {"@timestamp": {"order": "desc"}}
        ]
    }

    result = wazuh_indexer_post(
        "/wazuh-alerts-*/_search", body
    )

    hits = result.get("hits", {}).get("hits", [])

    alerts = []
    for hit in hits:
        src = hit.get("_source", {})
        alerts.append(src)

    return str(compress_results(alerts,max_items=10, max_fields=6))


# ============================================================
# 11) FIM CHANGES — /syscheck/{agent_id}
# ============================================================
@mcp.tool(name="custom_fim_queries")
@auto_params("agent_id", defaults={"agent_id": "001"})
def custom_fim_queries(params):
    agent_id = params["agent_id"]

    body = {
        "size": 50,
        "query": {
            "bool": {
                "must": [
                    {"term": {"agent.id": agent_id}}
                ]
            }
        },
        "sort": [
            {"@timestamp": {"order": "desc"}}
        ]
    }

    result = wazuh_indexer_post(
        "/wazuh-syscheck-*/_search",
        body
    )

    hits = result.get("hits", {}).get("hits", [])

    events = []
    for hit in hits:
        src = hit.get("_source", {})
        events.append(src)

    return str(compress_results(events,max_items=10, max_fields=6))


# ============================================================
# 12) OSQUERY RESULTS — /osquery/{agent}/queries
# ============================================================
@mcp.tool(name="get_osquery_results")
@auto_params("agent_id", defaults={"agent_id": "001"})
def get_osquery_results(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/osquery/{agent_id}/queries")
    return str(compress_results(data,max_items=10, max_fields=6))


# ============================================================
# 13) AGENTS HOTFFIX — /experimental/hotfixes/{aid}
# ============================================================
@mcp.tool(name="get_all_agents_hotfixes")
def get_all_agents_hotfixes():
    agents = wazuh_get("/agents?limit=5001")
    items = agents.get("data", {}).get("affected_items", [])
    all_hotfixes = {}
    for agent in items:
        aid = agent.get("id")
        if not aid:
            continue
        try:
            data = wazuh_get(f"/experimental/hotfixes/{aid}")
            hot = data.get("data", {}).get("affected_items", [])
        except:
            hot = []
        all_hotfixes[aid] = hot

    
    return str(compress_results(all_hotfixes,max_items=10, max_fields=6))


# ============================================================
#   RUN SERVER
# ============================================================
if __name__ == "__main__":
    print("🚀 Wazuh MCP Server running at http://127.0.0.1:8080/sse")
    mcp.run(transport="sse")




