import asyncio

from dotenv import load_dotenv

from src.graph import create_graph

load_dotenv()


async def run_agent():
    print("=== DeepSeek 智能联网 Agent (MCP 版) ===")
    print("输入 'exit' 或 '退出' 结束对话\n")
    
    app = await create_graph()

    while True:
        topic = input("请输入研究课题：")
        if topic.lower() in ['exit', '退出']:
            print("对话结束，再见！")
            break

        print(f"\n研究课题：{topic}")

        inputs = {"topic": topic, "steps": [], "messages": []}
        final_state = inputs

        async for event in app.astream(inputs, {"configurable": {}}, stream_mode="updates"):
            for node_name, output in event.items():
                final_state.update(output)

                if node_name == "agent":
                    print(f"\n\033[94m[Agent]\033[0m 正在思考...")

                elif node_name == "tools":
                    print(f"\n\033[92m[Tool]\033[0m 正在执行工具调用...")

        print("\n\n=== 最终回答 ===")
        messages = final_state.get("messages", [])
        if messages:
            last_message = messages[-1]
            print(last_message.content)
        
        print("\n=== 思考轨迹 ===")
        for i, step in enumerate(final_state.get("steps", []), 1):
            print(f"{i}. {step}")
        print("\n" + "="*30 + "\n")


if __name__ == "__main__":
    asyncio.run(run_agent())