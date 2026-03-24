from src.models import router_parser


def build_router_prompt(topic: str) -> str:
    return f"""你是一个智能决策系统，需要分析用户的研究课题，决定处理策略。

研究课题：{topic}

请分析这个问题：
1. 是否需要联网搜索获取最新信息？
2. 如果需要搜索，请拆解出 2-3 个精准的搜索关键词
3. 给出决策理由

请按照以下格式输出：
{router_parser.get_format_instructions()}

注意：
- action 只能是 "search" 或 "direct_answer"
- 如果 action 是 "search"，queries 必须包含 2-3 个精准的搜索关键词
- 如果 action 是 "direct_answer"，queries 可以是空列表
"""