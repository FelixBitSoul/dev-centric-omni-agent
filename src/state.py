from typing import Dict, Any, Optional, List, TypedDict


class AgentState(TypedDict):
    topic: str
    router_decision: Optional[Dict[str, Any]]
    queries: Optional[List[str]]
    search_results: Optional[List[Dict[str, Any]]]
    summary: Optional[str]
    steps: List[str]