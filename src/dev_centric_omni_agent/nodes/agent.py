from datetime import datetime

from langchain_core.messages import SystemMessage
from langgraph.constants import END
from langgraph.graph import MessagesState

from dev_centric_omni_agent.models import get_model


async def call_model(state: MessagesState):
    current_time_str = datetime.now().strftime("%Y年%m月%d日 %A")

    system_prompt = SystemMessage(
        content=(
            "你是一个高级 AI 助手。"
            f"【重要上下文】当前系统真实时间是：{current_time_str}。"
            "请务必以此时间作为你进行逻辑推理、联网搜索和回答问题的基准事实。"
            "如果搜索工具返回了符合当前年份的数据，请直接采纳，绝对不要试图将其修正为你在训练数据中记忆的过去年份（如2023或2024）。"
        )
    )

    model = await get_model()
    response = await model.ainvoke([system_prompt] + state["messages"])
    return {"messages": [response]}


def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END
