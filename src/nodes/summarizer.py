import asyncio
from typing import Dict, Any

from src.models import deepseek_model
from src.prompts import build_summarize_prompt


async def summarize(state: Dict[str, Any]) -> Dict[str, Any]:
    steps = state.get('steps', [])
    steps.append("开始生成总结报告")

    print("\033[93m[Summarize Node]\033[0m 正在生成总结报告...\n")

    prompt = build_summarize_prompt(state['topic'], state.get('search_results'))

    full_response = ""
    async for chunk in deepseek_model.astream(prompt):
        content = chunk.content
        full_response += content
        print(content, end="", flush=True)

    print("\n\n\033[93m[Summarize Node]\033[0m 总结报告生成完成！")

    steps.append("总结报告生成完成")

    return {
        "summary": full_response,
        "steps": steps
    }