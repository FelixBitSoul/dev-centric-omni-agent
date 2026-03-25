from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from src.models import get_mcp_tools, get_deepseek_model


async def create_agent() -> Any:
    """
    使用 LangGraph 的 create_react_agent 创建标准 ReAct Agent
    
    Returns:
        Runnable: 配置好的 Agent
    """
    print("\033[94m[Agent Builder]\033[0m 正在创建 ReAct Agent...")
    
    # 1. 获取 MCP 工具
    tools = await get_mcp_tools()
    print(f"\033[94m[Agent Builder]\033[0m 获取到 {len(tools)} 个工具")
    
    # 2. 获取模型并绑定工具
    model = get_deepseek_model()
    model_with_tools = model.bind_tools(tools)
    
    # 3. 使用 create_react_agent 创建标准 Agent
    agent = create_react_agent(model_with_tools, tools)
    
    print("\033[94m[Agent Builder]\033[0m ReAct Agent 创建成功")
    
    return agent


async def run_agent(agent: Any, topic: str) -> Dict[str, Any]:
    """
    运行 Agent 处理研究课题
    
    Args:
        agent: create_react_agent 创建的 Agent
        topic: 研究课题
    
    Returns:
        Dict: 包含最终消息和步骤的结果
    """
    print(f"\033[94m[Agent Runner]\033[0m 处理课题: {topic}")
    
    # 创建初始消息
    messages = [HumanMessage(content=topic)]
    
    # 运行 Agent
    result = await agent.ainvoke({"messages": messages})
    
    print("\033[94m[Agent Runner]\033[0m Agent 执行完成")
    
    return {
        "messages": result.get("messages", []),
        "steps": ["Agent 执行完成"]
    }