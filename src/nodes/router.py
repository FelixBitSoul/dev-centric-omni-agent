from typing import Dict, Any

from src.models import deepseek_model, router_parser
from src.prompts import build_router_prompt


def router(state: Dict[str, Any]) -> Dict[str, Any]:
    steps = state.get('steps', [])
    steps.append("开始分析用户问题，决定处理策略")

    prompt = build_router_prompt(state['topic'])

    print("\033[94m[Router Node]\033[0m 正在分析用户问题，决定处理策略...")

    response = deepseek_model.invoke(prompt)
    print(f"router模型输出: {response.content}")

    try:
        decision = router_parser.parse(response.content)
        print(f"\033[94m[Router Node]\033[0m 决策结果: {decision.action}")
        if decision.action == 'search' and decision.queries:
            print(f"\033[94m[Router Node]\033[0m 搜索关键词: {decision.queries}")
        print(f"\033[94m[Router Node]\033[0m 决策理由: {decision.reason}")

        decision_dict = {
            "action": decision.action,
            "queries": decision.queries,
            "reason": decision.reason
        }
    except Exception as e:
        print(f"\033[91m[Router Node]\033[0m 模型输出解析错误: {e}，默认需要搜索")
        decision_dict = {
            "action": "search",
            "queries": [state['topic']],
            "reason": "模型输出格式错误，默认需要搜索"
        }

    steps.append(f"决策: {decision_dict['action']}")

    return {
        "router_decision": decision_dict,
        "queries": decision_dict.get('queries', []),
        "steps": steps
    }