import os
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from typing_extensions import TypedDict

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
# 有状态 (State) 是指在工作流执行过程中，能够存储和传递信息的数据结构
# 在 LangGraph 中，State 是一个字典或类，用于在不同节点之间传递数据
# 每次节点执行后，都会返回一个新的 State 对象，包含更新后的信息
class AgentState(TypedDict):
    """Agent 状态类"""
    # 用户输入的研究课题
    topic: str
    # 是否需要搜索
    need_search: bool
    # 搜索结果
    search_results: Optional[str]
    # 最终总结
    summary: Optional[str]

# 定义节点函数

def check_need_search(state: Dict[str, Any]) -> Dict[str, Any]:
    """判断是否需要搜索
    
    这个节点会分析用户的研究课题，判断是否需要联网搜索获取最新信息
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    # 构建提示词，让模型判断是否需要搜索
    prompt = f"""请判断以下研究课题是否需要联网搜索获取最新信息：
    
    研究课题：{state['topic']}
    
    请回答 '是' 或 '否'，并简要说明原因。"""
    
    # 调用模型
    print("正在调用 DeepSeek 模型分析研究课题...")
    response = deepseek_model.invoke(prompt)
    
    # 解析回答
    answer = response.content.strip().lower()
    need_search = "是" in answer
    
    if need_search:
        print("分析结果：需要联网搜索获取最新信息")
    else:
        print("分析结果：不需要联网搜索，使用模型已有知识")
    
    # 返回更新后的状态
    return {"need_search": need_search}

def search_web(state: Dict[str, Any]) -> Dict[str, Any]:
    """搜索网页
    
    这个节点会使用 TavilySearch 工具搜索相关信息
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    # 执行搜索
    print(f"正在使用 Tavily 搜索 '{state['topic']}' 的相关信息...")
    results = tavily_search.invoke(state['topic'])
    
    # 处理搜索结果
    if isinstance(results, dict):
        # 检查 results 的结构
        if 'results' in results:
            # 如果 results 是一个包含 'results' 键的字典
            search_results = "\n".join([f"- {result['title']}: {result['url']}\n  {result['content'][:200]}..." for result in results['results'][:3]])
            print(f"搜索完成，找到 {len(results['results'])} 条结果，使用前 3 条进行分析")
        else:
            # 如果 results 是一个其他结构的字典
            search_results = str(results)
            print("搜索完成，获取到搜索结果")
    else:
        # 如果 results 是一个列表
        search_results = "\n".join([f"- {result['title']}: {result['url']}\n  {result['content'][:200]}..." for result in results[:3]])
        print(f"搜索完成，找到 {len(results)} 条结果，使用前 3 条进行分析")
    
    # 返回更新后的状态
    return {"search_results": search_results}

def summarize(state: Dict[str, Any]) -> Dict[str, Any]:
    """总结信息
    
    这个节点会根据搜索结果（如果有）和模型知识，生成最终总结
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    # 构建提示词
    if state.get('search_results'):
        prompt = f"""请基于以下搜索结果，对研究课题进行详细总结，以 Markdown 格式输出：
        
        研究课题：{state['topic']}
        
        搜索结果：
        {state['search_results']}
        
        总结要求：
        1. 以 Markdown 格式输出
        2. 结构清晰，包含标题、简介、主要内容、结论等部分
        3. 语言流畅，逻辑连贯
        4. 确保信息准确，引用搜索结果中的内容
        """
    else:
        prompt = f"""请对以下研究课题进行详细总结，以 Markdown 格式输出：
        
        研究课题：{state['topic']}
        
        总结要求：
        1. 以 Markdown 格式输出
        2. 结构清晰，包含标题、简介、主要内容、结论等部分
        3. 语言流畅，逻辑连贯
        """
    
    # 调用模型生成总结
    print("正在调用 DeepSeek 模型生成总结...")
    response = deepseek_model.invoke(prompt)
    print("总结生成完成！")
    
    # 返回更新后的状态
    return {"summary": response.content}

# 定义条件边函数
def should_search(state: Dict[str, Any]) -> str:
    """判断是否需要搜索的条件边
    
    循环逻辑是指在工作流中，根据条件判断决定是否重复执行某些节点
    在本项目中，循环逻辑体现在：
    1. 首先判断是否需要搜索
    2. 如果需要搜索，执行搜索节点，然后进入总结节点
    3. 如果不需要搜索，直接进入总结节点
    4. 总结节点执行完毕后，工作流结束
    
    Args:
        state: 当前状态
    
    Returns:
        下一个节点的名称
    """
    if state.get('need_search', False):
        return "search_web"
    else:
        return "summarize"

# 构建工作流
# StateGraph 是 LangGraph 中用于构建有状态工作流的核心类
# 它允许我们定义节点和边，形成一个有向图结构
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("check_need_search", check_need_search)  # 判断是否需要搜索
workflow.add_node("search_web", search_web)  # 搜索网页
workflow.add_node("summarize", summarize)  # 总结信息

# 设置入口点
workflow.set_entry_point("check_need_search")

# 添加边
# 从 check_need_search 节点到其他节点的条件边
workflow.add_conditional_edges(
    "check_need_search",
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
if __name__ == "__main__":
    # 初始化对话历史
    
    print("=== DeepSeek 智能联网 Agent ===")
    print("输入 'exit' 或 '退出' 结束对话\n")
    
    while True:
        # 获取用户输入
        topic = input("请输入研究课题：")
        
        # 检查是否退出
        if topic.lower() in ['exit', '退出']:
            print("对话结束，再见！")
            break
        
        print(f"\n研究课题：{topic}")
        print("正在分析是否需要搜索...")
        
        # 执行工作流
        result = app.invoke({"topic": topic, "need_search": False, "search_results": None, "summary": None})
        
        # 输出结果
        print("\n=== 研究总结 ===\n")
        print(result["summary"])

        print("\n")
