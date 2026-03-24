import os

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser


class RouterDecision(BaseModel):
    action: str
    queries: List[str]
    reason: str


router_parser = PydanticOutputParser(pydantic_object=RouterDecision)


_deepseek_model: Optional[ChatOpenAI] = None
_tavily_search: Optional[TavilySearch] = None


def get_deepseek_model() -> ChatOpenAI:
    global _deepseek_model
    if _deepseek_model is None:
        _deepseek_model = ChatOpenAI(
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model="deepseek-chat"
        )
    return _deepseek_model


def get_tavily_search() -> TavilySearch:
    global _tavily_search
    if _tavily_search is None:
        _tavily_search = TavilySearch()
    return _tavily_search


def clear_deepseek_model():
    global _deepseek_model
    _deepseek_model = None


def clear_tavily_search():
    global _tavily_search
    _tavily_search = None