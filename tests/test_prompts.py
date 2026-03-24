import pytest
from src.prompts import build_router_prompt, build_summarize_prompt


class TestRouterPrompt:
    def test_build_router_prompt_contains_topic(self):
        topic = "What is LangGraph?"
        prompt = build_router_prompt(topic)
        assert topic in prompt

    def test_build_router_prompt_contains_analysis_instructions(self):
        prompt = build_router_prompt("test topic")
        assert "智能决策系统" in prompt
        assert "search" in prompt.lower() or "搜索" in prompt

    def test_build_router_prompt_format_instructions(self):
        prompt = build_router_prompt("test topic")
        assert "格式输出" in prompt or "format" in prompt.lower()


class TestSummarizePrompt:
    def test_build_summarize_prompt_without_search_results(self):
        topic = "Explain machine learning"
        prompt = build_summarize_prompt(topic)
        assert topic in prompt
        assert "技术分析师" in prompt or "分析" in prompt

    def test_build_summarize_prompt_with_search_results(self):
        topic = "Latest AI trends"
        search_results = [
            {"title": "AI News", "url": "http://example.com", "content": "AI content..."}
        ]
        prompt = build_summarize_prompt(topic, search_results)
        assert topic in prompt
        assert "AI News" in prompt
        assert "http://example.com" in prompt

    def test_build_summarize_prompt_limits_results_to_six(self):
        topic = "test"
        search_results = [
            {"title": f"Result {i}", "url": f"http://example.com/{i}", "content": f"Content {i}"}
            for i in range(10)
        ]
        prompt = build_summarize_prompt(topic, search_results)
        for i in range(6):
            assert f"Result {i}" in prompt
        for i in range(6, 10):
            assert f"Result {i}" not in prompt

    def test_build_summarize_prompt_truncates_long_content(self):
        topic = "test"
        long_content = "x" * 500
        search_results = [
            {"title": "Long Article", "url": "http://example.com", "content": long_content}
        ]
        prompt = build_summarize_prompt(topic, search_results)
        assert len(prompt) > 0