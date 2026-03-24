from typing import Dict, Any

from langgraph.graph import StateGraph, END

from src.state import AgentState
from src.nodes import router, search_web, summarize


def should_search(state: AgentState) -> str:
    decision = state.get('router_decision', {})
    if decision.get('action') == 'search':
        return "search_web"
    else:
        return "summarize"


workflow = StateGraph(AgentState)

workflow.add_node("router", router)
workflow.add_node("search_web", search_web)
workflow.add_node("summarize", summarize)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    should_search,
    {
        "search_web": "search_web",
        "summarize": "summarize"
    }
)

workflow.add_edge("search_web", "summarize")
workflow.add_edge("summarize", END)

app = workflow.compile()