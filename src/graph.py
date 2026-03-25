from typing import Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.state import AgentState
from src.nodes import agent_node
from src.models import get_mcp_tools, get_agent_model


async def create_graph():
    tools = await get_mcp_tools()
    model = get_agent_model(tools)
    tool_node = ToolNode(tools)
    
    async def agent_wrapper(state, config):
        return await agent_node(state, config, model)
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_wrapper)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        START,
        lambda state: "agent",
        {"agent": "agent"}
    )
    
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    app = workflow.compile()
    
    return app


app = None