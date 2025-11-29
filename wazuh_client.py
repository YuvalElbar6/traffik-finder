from __future__ import annotations

import asyncio
import os
import ssl

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from agent_prompt import get_agent_prompt
from chroma_run import run_top5_workflow
from mcp_client_call import client
from rag_internet_router import route_query
from rag_tool import wazuh_rag_search

load_dotenv()

API_KEY = os.getenv('api_key', '')

if not API_KEY:
    raise RuntimeError('No api key for the llm!')

# Disable SSL checks for internal Wazuh API traffic
ssl._create_default_https_context = ssl._create_unverified_context  # type: ignore # noqa: E501


# ============================================================
#  Extract agent output reliably
# ============================================================
def extract_answer(result):

    # Standard LangChain AgentExecutor output
    if isinstance(result, dict):
        if 'output' in result:
            return result['output']
        if 'final_output' in result:
            return result['final_output']
        if 'messages' in result and result['messages']:
            return result['messages'][-1].content

    # Direct AIMessage object
    if hasattr(result, 'content'):
        return result.content

    return str(result)


# ============================================================
#  Chat loop
# ============================================================
async def chat_loop(agent):
    print('🔥 Wazuh Copilot (MCP + RAG) is live!  Ctrl+C to exit.\n')

    try:
        while True:
            user_input = input('You: ').strip()
            if not user_input:
                continue

            result = await agent.ainvoke({'input': user_input})
            answer = extract_answer(result)

            print('\nAssistant:', answer, '\n')

    except KeyboardInterrupt:
        print('\n👋 Exiting Wazuh Copilot...')


# ============================================================
#  Main
# ============================================================
async def main():

    # MCP connection

    # Load MCP tools
    mcp_tools = await client.get_tools()

    print('Loaded MCP Tools:')
    for t in mcp_tools:
        print(' -', t.name)

    all_tools = mcp_tools + [route_query, wazuh_rag_search, run_top5_workflow]
    model = ChatOpenAI(
        model='gpt-4o',
        api_key=os.getenv('api_key'),
    )

    prompt = get_agent_prompt()
    print(prompt)
    agent = create_agent(
        model=model,
        tools=all_tools,
        system_prompt=prompt,
    )

    await chat_loop(agent)


asyncio.run(main())
