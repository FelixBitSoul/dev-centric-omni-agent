import asyncio

from dotenv import load_dotenv

from src.agent import create_agent, run_agent as run_agent_task

load_dotenv()


async def main():
    print("=== DeepSeek 智能联网 Agent (ReAct + MCP) ===")
    print("使用 LangGraph create_react_agent 构建\n")
    print("输入 'exit' 或 '退出' 结束对话\n")
    
    # 创建 Agent
    print("\033[94m[初始化]\033[0m 正在初始化 Agent...")
    agent = await create_agent()
    print("\033[94m[初始化]\033[0m Agent 初始化完成\n")

    while True:
        topic = input("请输入研究课题：")
        if topic.lower() in ['exit', '退出']:
            print("对话结束，再见！")
            break

        print(f"\n研究课题：{topic}")

        # 运行 Agent
        result = await run_agent_task(agent, topic)
        
        print("\n\n=== 最终回答 ===")
        messages = result.get("messages", [])
        if messages:
            # 获取最后一个 AI 消息
            for msg in reversed(messages):
                if hasattr(msg, 'content'):
                    print(msg.content)
                    break
        
        print("\n=== 执行步骤 ===")
        for i, step in enumerate(result.get("steps", []), 1):
            print(f"{i}. {step}")
        print("\n" + "="*30 + "\n")


if __name__ == "__main__":
    asyncio.run(main())