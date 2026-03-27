def build_agent_prompt(topic: str) -> str:
    return f"""你是一位专业的技术分析师。请分析以下研究课题：

{topic}

如果需要获取最新信息，请使用 tavily-search 工具进行搜索。
请给出完整的专业分析报告，包含核心结论、详细分析和来源引用。"""