from src.agent import create_agent


async def create_graph():
    """
    创建 Agent 工作流（使用 create_react_agent）
    
    Returns:
        Runnable: 配置好的 Agent
    """
    return await create_agent()


app = None