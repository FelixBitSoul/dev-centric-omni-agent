from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage

from src.models import get_tools, get_model


def cleanup_tool_outputs(state):
    """
    框架级拦截器：
    遍历所有消息，如果发现 ToolMessage 的 content 是列表，将其转为字符串。
    """
    messages = state["messages"]
    new_messages = []

    for msg in messages:
        if isinstance(msg, ToolMessage) and isinstance(msg.content, list):
            # 将列表中的文本内容拼接成字符串
            text_content = "\n".join([
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in msg.content
            ])
            # 创建一个 content 为字符串的新消息
            msg = ToolMessage(
                content=text_content,
                tool_call_id=msg.tool_call_id,
                name=msg.name,
                additional_kwargs=msg.additional_kwargs,
                artifact=msg.artifact
            )
        new_messages.append(msg)

    return {"messages": new_messages}


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

    # 2. 获取模型并绑定工具
    model = get_model()

    # 使用 create_agent，并通过 state_modifier 注入清洗逻辑
    # 在 2026 年的标准中，state_modifier 可以是一个处理函数
    app = create_agent(
        model,
        tools=tools,
        debug=True,
        # 这里的函数会在每一轮 Agent 思考前运行，确保消息格式永远正确
        # state_modifier=cleanup_tool_outputs,
    )

    print("\033[94m[Agent Builder]\033[0m Agent 创建成功")

    return app
