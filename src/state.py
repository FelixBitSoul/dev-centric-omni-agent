from typing import Dict, Any, List, TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    topic: str
    messages: List[BaseMessage]
    steps: List[str]