import ast
import json
from typing import Any, Optional, Dict
from langchain.tools import tool
from rag_store import load_rag_vectorstore
from mcp_server import mcp

tool_calls = {
    "get_wazuh_vulnerabilities": {"params":{"agent_id": "001"}},
    "custom_alert_filters": {"params":{"agent_id": "001"}},
    "get_wazuh_processes": {"params":{"agent_id": "001"}},
    "get_wazuh_agent_ports": {"params":{"agent_id": "001"}},
    "custom_fim_queries": {"params":{"agent_id": "001"}},
    "get_wazuh_manager_logs": {"params":{"limit": "50"}},
}

collection = load_rag_vectorstore()


def save_mcp_result_to_chroma(tool_name, result, query, tag: str):


    collection.add_texts(
        texts=[json.dumps(result)],
        metadatas=[
            {
                "type": "mcp",
                "tool": tool_name,
                "tag": tag,
                "query": query
            }
        ],
        ids=[f"{tool_name}-{tag}"]
    )


def load_mcp_result_from_chroma(tool_name: str, tag: str) -> Optional[str]:
    docs = collection.get(
            where={
                "$and": [
                    {"tool": tool_name},
                    {"tag": tag}
                ]
            },
            include=["documents"]
        )
    if not docs:
        return None
    document = docs["documents"][0] if docs["documents"] else None
    if not document:
        return None

    return json.loads(document) 


async def get_mcp_result(tool_name: str, args: Dict[str, Any]) -> str:
    content = await mcp.call_tool(tool_name, args)

    if not content:
        raise RuntimeError("There is no result from the mcp")

    
    if isinstance(content, list):
        text = "".join([c.text if c else "" for c in content])
    else:
        text = str(content)

    # Try converting Python-like list → actual list
    try:
        parsed = ast.literal_eval(text)
        return parsed
    except Exception:
        pass

    # Fallback: return raw text if not parseable
    return text


@tool("run_top5_workflow")
async def run_top5_workflow(user_query: str):
    """
    Runs the top 5 Wazuh security issues workflow.
    Collects data from MCP tools, uses cache if available,
    stores results in Chroma, and returns combined results.
    """
    
    results: Dict[str, Any] = {}
    
    for tool_name,  params in tool_calls.items():
        tag = "".join(f"{k}={v}" for k, v in tool_calls[tool_name]["params"].items())
        cache = load_mcp_result_from_chroma(tool_name, tag)
        if cache:
            print(f"Loaded tool: {tool_name} from cache.")
            results[tool_name] = cache
            continue
        
        print(f"Loading: {tool_name} from mcp")
        try:
            result = await get_mcp_result(tool_name, params)            
            results[tool_name] = result
            save_mcp_result_to_chroma(tool_name, result, user_query, tag)

        except Exception as e:
            print(f"There was a problem: {e}")
        
    return json.dumps(results, ensure_ascii=False)