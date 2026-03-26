import asyncio

from dotenv import load_dotenv

from src.graph import create_graph

load_dotenv()


async def main():
    print("=== start dev centric omni agent assistant ===")
    print("输入 'exit' 或 '退出' 结束对话\n")

    # 创建 Agent
    print("\033[94m[初始化]\033[0m 正在初始化 Agent...")
    app = await create_graph()
    print("\033[94m[初始化]\033[0m Agent 初始化完成\n")

    while True:
        topic = input("请输入研究课题：")
        if topic.lower() in ['exit', '退出']:
            print("对话结束，再见！")
            break

        print(f"\n研究课题：{topic}")

        if topic.lower() in ['exit', 'quit', '退出']:
            break

        if not topic:
            continue

        # inputs = {"messages": [("user", topic)]}
        inputs = {
            "messages": [
                {"role": "user", "content": topic}
            ]
        }
        config = {"configurable": {"thread_id": "session_1"}}
        async for event in app.astream_events(inputs, config=config, version="v2"):
            kind = event["event"]

            # 观察模型开始输出内容
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    print(content, end="", flush=True)

            # 观察工具调用过程
            elif kind == "on_tool_start":
                print(f"\n\n[工具调用] 正在启动: {event['name']}...")
                print(f"[输入参数] {event['data'].get('input')}")

            elif kind == "on_tool_end":
                print(f"[工具返回] 执行完毕。\n")
                print("--- 继续思考 ---")

        print("\n" + "=" * 20 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
