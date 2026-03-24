import os

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from pydantic import BaseModel
from typing import List
from langchain_core.output_parsers import PydanticOutputParser

tavily_search = TavilySearch()

deepseek_model = ChatOpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-chat"
)


class RouterDecision(BaseModel):
    action: str
    queries: List[str]
    reason: str


router_parser = PydanticOutputParser(pydantic_object=RouterDecision)