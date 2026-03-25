import os
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

_deepseek_model: Optional[ChatOpenAI] = None
_tools: Optional[List[BaseTool]] = None

# Initialize the Tavily Search tool
tavily_search = TavilySearch(max_results=3, topic="general")

def get_model() -> ChatOpenAI:
    global _deepseek_model
    if _deepseek_model is None:
        _deepseek_model = ChatOpenAI(
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model="deepseek-chat"
        )
    return _deepseek_model


async def get_tools() -> List[BaseTool]:
    global _tools
    if _tools is None:
        # tavily_api_key = os.getenv("TAVILY_API_KEY")
        # mcp_url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_api_key}"
        #
        # client = MultiServerMCPClient({
        #     "tavily": {
        #         "transport": "http",
        #         "url": mcp_url
        #     }
        # })
        #
        # mcp_tools = await client.get_tools()
        _tools = [tavily_search]
    
    return _tools


def get_agent_model(tools: List[BaseTool]) -> ChatOpenAI:
    model = get_model()
    return model.bind_tools(tools)


def clear_deepseek_model():
    global _deepseek_model
    _deepseek_model = None


def clear_mcp_tools():
    global _tools
    _tools = None