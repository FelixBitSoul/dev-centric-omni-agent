SYSTEM_PROMPT = "你是一位首席技术分析师，擅长分析技术问题并提供专业、详细的分析报告。"


def build_summarize_prompt(topic: str, search_results: list | None = None) -> str:
    if search_results:
        formatted_results = ""
        for i, result in enumerate(search_results[:6]):
            formatted_results += f"\n[{i+1}] {result['title']}\nURL: {result['url']}\n内容: {result['content'][:300]}...\n"

        return f"""{SYSTEM_PROMPT}

请基于以下搜索结果，对研究课题进行详细分析，输出专业的技术分析报告：

研究课题：{topic}

搜索结果：
{formatted_results}

报告要求：
1. 必须包含以下三个部分：
   - 核心结论 (Executive Summary)：简要概括主要发现和结论
   - 详细分析 (Detailed Analysis)：深入分析问题，提供专业见解
   - 来源引用 (References)：列出使用的信息来源
2. 语言专业、准确，逻辑清晰
3. 确保信息准确，引用搜索结果中的内容
"""
    else:
        return f"""{SYSTEM_PROMPT}

请对以下研究课题进行详细分析，输出专业的技术分析报告：

研究课题：{topic}

报告要求：
1. 必须包含以下三个部分：
   - 核心结论 (Executive Summary)：简要概括主要发现和结论
   - 详细分析 (Detailed Analysis)：深入分析问题，提供专业见解
   - 来源引用 (References)：如果使用了模型内置知识，请注明
2. 语言专业、准确，逻辑清晰
3. 基于你的知识提供高水平的分析
"""