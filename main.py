import asyncio

from dotenv import load_dotenv

from src.graph import app

load_dotenv()


async def run_agent():
    print("=== DeepSeek 智能联网 Agent ===")
    print("输入 'exit' 或 '退出' 结束对话\n")

    while True:
        topic = input("请输入研究课题：")
        if topic.lower() in ['exit', '退出']:
            print("对话结束，再见！")
            break

        print(f"\n研究课题：{topic}")

        inputs = {"topic": topic, "steps": []}
        final_state = inputs

        async for event in app.astream(inputs, stream_mode="updates"):
            for node_name, output in event.items():
                final_state.update(output)

                if node_name == "router":
                    decision = output.get("router_decision", {})
                    print(f"\n\033[94m[Router]\033[0m 决策: {decision.get('action')}")
                    if decision.get('action') == 'search' and decision.get('queries'):
                        print(f"\033[94m[Router]\033[0m 搜索关键词: {decision.get('queries')}")
                    print(f"\033[94m[Router]\033[0m 决策理由: {decision.get('reason')}")

                elif node_name == "search_web":
                    results = output.get("search_results", [])
                    print(f"\n\033[92m[Search]\033[0m 找到 {len(results)} 条相关信息")

        print("\n\n=== 思考轨迹 ===")
        for i, step in enumerate(final_state.get("steps", []), 1):
            print(f"{i}. {step}")
        print("\n" + "="*30 + "\n")


if __name__ == "__main__":
    asyncio.run(run_agent())