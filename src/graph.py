from datetime import datetime
from typing import Any

from langchain_core.messages import ToolMessage, SystemMessage
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

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
    model = await get_model()

    # 4. 构建 LangGraph 流程

    async def call_model(state: MessagesState):
        # 1. 【核心最佳实践】动态生成包含当前时间的 SystemMessage
        # 无论你哪天运行这个代码，它都会获取真实的系统当前时间
        current_time_str = datetime.now().strftime("%Y年%m月%d日 %A")

        system_prompt = SystemMessage(
            content=(
                "你是一个高级 AI 助手。"
                f"【重要上下文】当前系统真实时间是：{current_time_str}。"
                "请务必以此时间作为你进行逻辑推理、联网搜索和回答问题的基准事实。"
                "如果搜索工具返回了符合当前年份的数据，请直接采纳，绝对不要试图将其修正为你在训练数据中记忆的过去年份（如2023或2024）。"
            )
        )
        # 在调用模型前，先清洗一遍状态中的消息
        response = await model.ainvoke([system_prompt] + state["messages"])
        return {"messages": [response]}

    def should_continue(state: MessagesState):
        last_message = state["messages"][-1]
        return "tools" if last_message.tool_calls else END

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
