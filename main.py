import os
import asyncio
from typing import Dict, Any, Optional, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from typing_extensions import TypedDict
from pydantic import BaseModel

# 定义决策结构的Pydantic模型
class RouterDecision(BaseModel):
    action: str  # search 或 direct_answer
    queries: List[str]  # 搜索关键词列表
    reason: str  # 决策理由

# 创建Pydantic输出解析器
router_parser = PydanticOutputParser(pydantic_object=RouterDecision)

# 加载环境变量
load_dotenv()

# 初始化工具
tavily_search = TavilySearch()

# 初始化 DeepSeek 模型
deepseek_model = ChatOpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-chat"
)

# 定义状态结构
class AgentState(TypedDict):
    """Agent 状态类"""
    # 用户输入的研究课题
    topic: str
    # 路由决策
    router_decision: Optional[Dict[str, Any]]
    # 搜索关键词列表
    queries: Optional[List[str]]
    # 搜索结果
    search_results: Optional[List[Dict[str, Any]]]
    # 最终总结
    summary: Optional[str]
    # 思考轨迹
    steps: List[str]



# 定义节点函数

def router(state: Dict[str, Any]) -> Dict[str, Any]:
    """智能路由决策节点
    
    分析用户问题，决定是直接回答还是需要搜索
    使用LangChain的PydanticOutputParser进行结构化输出
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    steps = state.get('steps', [])
    steps.append("开始分析用户问题，决定处理策略")
    
    # 构建提示词，包含解析器的格式说明
    prompt = f"""你是一个智能决策系统，需要分析用户的研究课题，决定处理策略。
    
    研究课题：{state['topic']}
    
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
    
    print("\033[94m[Router Node]\033[0m 正在分析用户问题，决定处理策略...")
    
    # 调用模型
    response = deepseek_model.invoke(prompt)
    print(f"router模型输出: {response.content}")
    
    # 使用PydanticOutputParser解析输出
    try:
        decision = router_parser.parse(response.content)
        print(f"\033[94m[Router Node]\033[0m 决策结果: {decision.action}")
        if decision.action == 'search' and decision.queries:
            print(f"\033[94m[Router Node]\033[0m 搜索关键词: {decision.queries}")
        print(f"\033[94m[Router Node]\033[0m 决策理由: {decision.reason}")
        
        # 将Pydantic模型转换为字典
        decision_dict = {
            "action": decision.action,
            "queries": decision.queries,
            "reason": decision.reason
        }
    except Exception as e:
        # 如果模型输出不是有效的格式，默认需要搜索
        print(f"\033[91m[Router Node]\033[0m 模型输出解析错误: {e}，默认需要搜索")
        decision_dict = {
            "action": "search",
            "queries": [state['topic']],
            "reason": "模型输出格式错误，默认需要搜索"
        }
    
    steps.append(f"决策: {decision_dict['action']}")
    
    # 返回更新后的状态
    return {
        "router_decision": decision_dict,
        "queries": decision_dict.get('queries', []),
        "steps": steps
    }

async def search_web(state: Dict[str, Any]) -> Dict[str, Any]:
    """搜索网页节点
    
    并发处理所有搜索关键词，获取搜索结果
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    steps = state.get('steps', [])
    steps.append("开始执行网络搜索")
    
    queries = state.get('queries', [])
    if not queries:
        queries = [state['topic']]
    
    print(f"\033[92m[Search Node]\033[0m 正在搜索 {len(queries)} 个关键词...")
    
    # 并发执行搜索
    async def search_query(query):
        try:
            print(f"\033[92m[Search Node]\033[0m 搜索: {query}")
            results = tavily_search.invoke(query, max_results=3)
            return results
        except Exception as e:
            print(f"\033[91m[Search Node]\033[0m 搜索 {query} 时出错: {e}")
            return []
    
    # 执行并发搜索
    search_tasks = [search_query(query) for query in queries]
    search_results_list = await asyncio.gather(*search_tasks)
    
    # 聚合搜索结果
    aggregated_results = []
    for i, results in enumerate(search_results_list):
        query = queries[i]
        if isinstance(results, dict) and 'results' in results:
            for result in results['results']:
                aggregated_results.append({
                    "query": query,
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('content', '')
                })
        elif isinstance(results, list):
            for result in results:
                aggregated_results.append({
                    "query": query,
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('content', '')
                })
    
    print(f"\033[92m[Search Node]\033[0m 搜索完成，共获取 {len(aggregated_results)} 条结果")
    
    steps.append(f"完成搜索，获取 {len(aggregated_results)} 条结果")
    
    # 返回更新后的状态
    return {
        "search_results": aggregated_results,
        "steps": steps
    }

async def summarize(state: Dict[str, Any]) -> Dict[str, Any]:
    """总结信息节点
    
    根据搜索结果（如果有）和模型知识，生成最终总结
    支持流式输出
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    steps = state.get('steps', [])
    steps.append("开始生成总结报告")
    
    print("\033[93m[Summarize Node]\033[0m 正在生成总结报告...\n")
    
    # 构建系统提示词
    system_prompt = "你是一位首席技术分析师，擅长分析技术问题并提供专业、详细的分析报告。"
    
    # 构建提示词
    if state.get('search_results'):
        # 格式化搜索结果
        formatted_results = ""
        for i, result in enumerate(state['search_results'][:6]):  # 最多使用前6条结果
            formatted_results += f"\n[{i+1}] {result['title']}\nURL: {result['url']}\n内容: {result['content'][:300]}...\n"
        
        prompt = f"""{system_prompt}
        
        请基于以下搜索结果，对研究课题进行详细分析，输出专业的技术分析报告：
        
        研究课题：{state['topic']}
        
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
        prompt = f"""{system_prompt}
        
        请对以下研究课题进行详细分析，输出专业的技术分析报告：
        
        研究课题：{state['topic']}
        
        报告要求：
        1. 必须包含以下三个部分：
           - 核心结论 (Executive Summary)：简要概括主要发现和结论
           - 详细分析 (Detailed Analysis)：深入分析问题，提供专业见解
           - 来源引用 (References)：如果使用了模型内置知识，请注明
        2. 语言专业、准确，逻辑清晰
        3. 基于你的知识提供高水平的分析
        """
    
    # 使用 astream 获取模型的流式输出
    full_response = ""
    async for chunk in deepseek_model.astream(prompt):
        content = chunk.content
        full_response += content
        # 实时打印到终端 (flush=True 确保立即显示)
        print(content, end="", flush=True)
    
    print("\n\n\033[93m[Summarize Node]\033[0m 总结报告生成完成！")
    
    steps.append("总结报告生成完成")
    
    # 返回更新后的状态
    return {
        "summary": full_response,
        "steps": steps
    }

# 定义条件边函数
def should_search(state: Dict[str, Any]) -> str:
    """判断是否需要搜索的条件边
    
    Args:
        state: 当前状态
    
    Returns:
        下一个节点的名称
    """
    decision = state.get('router_decision', {})
    if decision.get('action') == 'search':
        return "search_web"
    else:
        return "summarize"

# 构建工作流
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("router", router)  # 智能路由决策
workflow.add_node("search_web", search_web)  # 搜索网页
workflow.add_node("summarize", summarize)  # 总结信息

# 设置入口点
workflow.set_entry_point("router")

# 添加边
# 从 router 节点到其他节点的条件边
workflow.add_conditional_edges(
    "router",
    should_search,
    {
        "search_web": "search_web",
        "summarize": "summarize"
    }
)

# 从 search_web 节点到 summarize 节点的边
workflow.add_edge("search_web", "summarize")

# 从 summarize 节点到结束的边
workflow.add_edge("summarize", END)

# 编译工作流
app = workflow.compile()

# 主函数
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
        final_state = inputs # 用于存储最终结果
        
        # 使用 astream 运行工作流
        async for event in app.astream(inputs, stream_mode="updates"):
            # 更新最终状态，这样最后就不需要再 invoke 一次了
            for node_name, output in event.items():
                final_state.update(output)
                
                # 路由节点信息打印
                if node_name == "router":
                    decision = output.get("router_decision", {})
                    print(f"\n\033[94m[Router]\033[0m 决策: {decision.get('action')}")
                    if decision.get('action') == 'search' and decision.get('queries'):
                        print(f"\033[94m[Router]\033[0m 搜索关键词: {decision.get('queries')}")
                    print(f"\033[94m[Router]\033[0m 决策理由: {decision.get('reason')}")
                
                # 搜索节点信息打印
                elif node_name == "search_web":
                    results = output.get("search_results", [])
                    print(f"\n\033[92m[Search]\033[0m 找到 {len(results)} 条相关信息")

        # 输出结果已经由 summarize 节点在流式过程中打印了
        
        # 直接从 final_state 输出思考轨迹，无需二次 invoke
        print("\n\n=== 思考轨迹 ===")
        for i, step in enumerate(final_state.get("steps", []), 1):
            print(f"{i}. {step}")
        print("\n" + "="*30 + "\n")

if __name__ == "__main__":
    # 使用 asyncio 运行
    asyncio.run(run_agent())
