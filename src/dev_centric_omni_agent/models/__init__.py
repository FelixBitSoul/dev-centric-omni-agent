import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

_deepseek_model: Optional[ChatOpenAI] = None
_tools: Optional[List[BaseTool]] = None


def map_deepseek_messages(messages):
    """将消息列表中的 ToolMessage 内容由 list 转换为 string"""
    new_messages = []
    for m in messages:
        if isinstance(m, ToolMessage) and isinstance(m.content, list):
            # 提取文本内容并合并
            combined_text = "".join(
                [block["text"] for block in m.content if block.get("type") == "text"]
            )
            new_messages.append(ToolMessage(content=combined_text, tool_call_id=m.tool_call_id))
        else:
            new_messages.append(m)
    return new_messages


async def get_model() -> ChatOpenAI:
    global _deepseek_model
    tools = await get_tools()
    if _deepseek_model is None:
        raw_llm = ChatOpenAI(
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model="deepseek-chat"
        ).bind_tools(tools)
        # 创建一个兼容 DeepSeek 的链
        # 这在逻辑上等同于：先洗数据 -> 再调 LLM
        _deepseek_model = RunnableLambda(map_deepseek_messages) | raw_llm
    return _deepseek_model


async def get_tools() -> List[BaseTool]:
    global _tools
    if _tools is None:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        mcp_url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_api_key}"
        client = MultiServerMCPClient(
            {
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        os.getcwd(),  # server 只暴露此目录
                    ],
                    "transport": "stdio",
                },
                "tavily": {
                    "transport": "http",
                    "url": mcp_url
                }
            }
        )
        _tools = await client.get_tools()

    return _tools


def clear_deepseek_model():
    global _deepseek_model
    _deepseek_model = None


def clear_mcp_tools():
    global _tools
    _tools = None
