from typing import Any

from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from dev_centric_omni_agent.models import get_tools
from dev_centric_omni_agent.nodes import call_model
from dev_centric_omni_agent.nodes import should_continue


async def create_graph() -> Any:
    """
    使用 langchain 的 create_agent 创建 agent
    
    Returns:
        Runnable: 配置好的 Agent
    """
    print("\033[94m[Agent Builder]\033[0m 正在创建 Agent...")

    # 1. 获取 MCP 工具
    tools = await get_tools()
    print(f"\033[94m[Agent Builder]\033[0m 获取到 {len(tools)} 个工具")

    # 2. 构建 LangGraph 流程

    # 组装图
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    app = workflow.compile()

    print("\033[94m[Agent Builder]\033[0m Agent 创建成功")

    return app
