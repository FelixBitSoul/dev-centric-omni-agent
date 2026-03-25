from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI


async def agent_node(state: Dict[str, Any], config: RunnableConfig, model: ChatOpenAI) -> Dict[str, Any]:
    steps = state.get('steps', [])
    steps.append("Agent 开始思考")
    
    print("\033[94m[Agent Node]\033[0m 正在分析用户问题...")
    
    topic = state['topic']
    messages = state.get('messages', [])
    
    if not messages:
        messages = [HumanMessage(content=topic)]
    
    response = await model.ainvoke(messages)
    
    print(f"\033[94m[Agent Node]\033[0m 决策完成")
    
    steps.append("Agent 决策完成")
    
    return {
        "messages": [response],
        "steps": steps
    }