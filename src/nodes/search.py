import asyncio
from typing import Dict, Any

from src.models import tavily_search


async def search_web(state: Dict[str, Any]) -> Dict[str, Any]:
    steps = state.get('steps', [])
    steps.append("开始执行网络搜索")

    queries = state.get('queries', [])
    if not queries:
        queries = [state['topic']]

    print(f"\033[92m[Search Node]\033[0m 正在搜索 {len(queries)} 个关键词...")

    async def search_query(query):
        try:
            print(f"\033[92m[Search Node]\033[0m 搜索: {query}")
            results = tavily_search.invoke(query, max_results=3)
            return results
        except Exception as e:
            print(f"\033[91m[Search Node]\033[0m 搜索 {query} 时出错: {e}")
            return []

    search_tasks = [search_query(query) for query in queries]
    search_results_list = await asyncio.gather(*search_tasks)

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

    return {
        "search_results": aggregated_results,
        "steps": steps
    }