import os
from typing import Any, Dict
import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient, StreamableHttpConnection
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

MCP_SERVER_URL= os.getenv("WMCP_SERVER_URL", "http://127.0.0.1:8080")

WAZUH_API = os.getenv("WAZUH_API", "https://127.0.0.1:55000")
WAZUH_USER = os.getenv("WAZUH_USER", "")
WAZUH_PASS = os.getenv("WAZUH_PASSWORD", "")

WAZUH_INDEXER_API=os.getenv("WAZUH_INDEXER_API", "https://54.172.121.51:9200")
WAZUH_INDEXER_USER = os.getenv("WAZUH_INDEXER_USER", "")
WAZUH_INDEXER_PASS = os.getenv("WAZUH_INDEXER_PASSWORD", "")


if not WAZUH_USER or not WAZUH_PASS:
    raise RuntimeError("Missing Wazuh credentials!")


if not (WAZUH_USER and WAZUH_PASS):
    raise RuntimeError("Missing Wazuh credentials")


if not WAZUH_INDEXER_USER or not WAZUH_INDEXER_PASS:
    raise RuntimeError("Missing Wazuh index credentials!")


if not (WAZUH_INDEXER_USER and WAZUH_INDEXER_PASS):
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


def wazuh_indexer_post(endpoint: str , body: dict = {}):
    resp = requests.post(
        f"{WAZUH_INDEXER_API}{endpoint}",
        auth=HTTPBasicAuth(WAZUH_INDEXER_USER, WAZUH_INDEXER_PASS),
        json=body,
        verify=False
    )
    resp.raise_for_status()
    return resp.json()


def compress_results(data_list, max_items=10, max_fields=6):
    """
    Reduce list of dicts to a tiny summary to fit in GPT TPM limits.
    - max_items: max number of entries to keep
    - max_fields: max fields to include per entry
    """

    if not isinstance(data_list, list):
        return data_list  # if it's not a list, nothing to compress

    trimmed = data_list[:max_items]

    compressed = []
    for item in trimmed:
        if isinstance(item, dict):
            small = {}
            fields = list(item.keys())[:max_fields]
            for f in fields:
                small[f] = item.get(f)
            compressed.append(small)
        else:
            compressed.append(item)

    return compressed


client = MultiServerMCPClient(
            connections={
                "wazuh": StreamableHttpConnection(
                    url="http://127.0.0.1:8080/",
                    transport="streamable_http",
                )
            }
    )