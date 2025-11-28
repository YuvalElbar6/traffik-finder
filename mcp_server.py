# file: wazuh_mcp_server.py
import os
import requests
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
from mcp_helper import auto_params

WAZUH_API = os.getenv("WAZUH_API", "https://54.172.121.51:55000")
WAZUH_USER = os.getenv("wazuh_user", "")
WAZUH_PASS = os.getenv("wazuh_password", "")

if not WAZUH_USER or not WAZUH_PASS:
    raise RuntimeError("Missing Wazuh credentials!")


if not (WAZUH_USER and WAZUH_PASS):
    raise RuntimeError("Missing Wazuh credentials")



def get_token():
    """Authenticate with Wazuh API and return JWT."""
    resp = requests.post(
        f"{WAZUH_API}/security/user/authenticate?raw=true",
        auth=(WAZUH_USER, WAZUH_PASS),
        verify=False
    )
    resp.raise_for_status()
    return resp.text.strip()


def wazuh_get(endpoint: str):
    """GET helper for Wazuh API."""
    token = get_token()
    resp = requests.get(
        f"{WAZUH_API}{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        verify=False
    )
    resp.raise_for_status()
    return resp.json()


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
    return str(data)

# ============================================================
# 3) WEEKLY STATS — /manager/stats/weekly
# ============================================================
@mcp.tool(name="get_wazuh_weekly_stats")
def get_weekly_stats(params):
    data = wazuh_get("/manager/stats/weekly")
    return str(data)


# ============================================================
# 4) CLUSTER NODES — /cluster/nodes
# ============================================================
@mcp.tool(name="get_wazuh_cluster_nodes")
def get_cluster_nodes(params):
    data = wazuh_get("/cluster/nodes")
    return str(data)


# ============================================================
# 5) CLUSTER HEALTH — /cluster/healthcheck
# ============================================================
@mcp.tool(name="get_wazuh_cluster_health")
def get_cluster_health(params):
    data = wazuh_get("/cluster/healthcheck")
    return str(data)


# ============================================================
# 6) VULNERABILITIES — /vulnerability/os/{agent_id}
# ============================================================
@mcp.tool(name="get_wazuh_vulnerabilities")
@auto_params("agent_id", defaults={"agent_id": "000"})
def get_vulnerabilities(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/vulnerability/os/{agent_id}")
    return str(data)


# ============================================================
# 7) PROCESSES — /syscollector/{agent}/processes
# ============================================================
@mcp.tool(name="get_wazuh_processes")
@auto_params("agent_id", defaults={"agent_id": "000"})
def get_processes(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/syscollector/{agent_id}/processes")
    return str(data)


# ============================================================
# 8) AGENT PORTS — /syscollector/{agent}/ports
# ============================================================
@mcp.tool(name="get_wazuh_agent_ports")
@auto_params("agent_id", defaults={"agent_id": "000"})
def get_agent_ports(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/syscollector/{agent_id}/ports")
    return str(data)


# ============================================================
# 9) SEARCH MANAGER LOGS — /manager/logs?q=
# ============================================================
@mcp.tool(name="search_wazuh_manager_logs")
@auto_params("query", defaults={"query": ""})
def search_manager_logs(params):
    query = params["query"]
    data = wazuh_get(f"/manager/logs?q={query}")
    return str(data)


# ============================================================
# 10) CUSTOM ALERT FILTERS — /alerts
# ============================================================
@mcp.tool(name="custom_alert_filters")
@auto_params("severity", "rule", "agent",
             defaults={"severity": "", "rule": "", "agent": ""})
def custom_alert_filters(params):
    severity = params["severity"]
    rule = params["rule"]
    agent = params["agent"]

    url = "/alerts?"

    if severity:
        url += f"severity={severity}&"
    if rule:
        url += f"rule.id={rule}&"
    if agent:
        url += f"agent.id={agent}&"

    data = wazuh_get(url.rstrip("&?"))
    return str(data)


# ============================================================
# 11) FIM CHANGES — /fim/{agent}/changes
# ============================================================
@mcp.tool(name="custom_fim_queries")
@auto_params("agent_id", defaults={"agent_id": "000"})
def custom_fim(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/fim/{agent_id}/changes")
    return str(data)


# ============================================================
# 12) OSQUERY RESULTS — /osquery/{agent}/queries
# ============================================================
@mcp.tool(name="get_osquery_results")
@auto_params("agent_id", defaults={"agent_id": "000"})
def get_osquery_results(params):
    agent_id = params["agent_id"]
    data = wazuh_get(f"/osquery/{agent_id}/queries")
    return str(data)


# ============================================================
#   RUN SERVER
# ============================================================
if __name__ == "__main__":
    print("🚀 Wazuh MCP Server running at http://127.0.0.1:8080/sse")
    mcp.run(transport="sse")