import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_agent():
    print("测试 Agent 模式 + MCP 集成...")
    
    from src.models import get_mcp_tools, get_agent_model
    
    try:
        print("1. 获取 MCP 工具...")
        tools = await get_mcp_tools()
        print(f"✅ 获取到 {len(tools)} 个工具")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        print("\n2. 创建 Agent 模型...")
        model = get_agent_model(tools)
        print("✅ Agent 模型创建成功")
        
        print("\n3. 测试工作流创建...")
        from src.graph import create_graph
        app = await create_graph()
        print("✅ 工作流创建成功")
        
        print("\n🎉 Agent 模式 + MCP 集成测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())