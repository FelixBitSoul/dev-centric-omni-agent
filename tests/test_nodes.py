import pytest
from unittest.mock import MagicMock, patch


class TestRouterNode:
    @patch("src.nodes.router.get_deepseek_model")
    def test_router_returns_search_action(self, mock_get_model):
        from src.nodes.router import router

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"action": "search", "queries": ["query1"], "reason": "test"}'
        mock_model.invoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        with patch("src.nodes.router.router_parser") as mock_parser:
            mock_decision = MagicMock()
            mock_decision.action = "search"
            mock_decision.queries = ["query1"]
            mock_decision.reason = "test"
            mock_parser.parse.return_value = mock_decision

            state = {"topic": "test topic", "steps": []}
            result = router(state)

            assert "router_decision" in result
            assert "steps" in result
            assert result["router_decision"]["action"] == "search"

    @patch("src.nodes.router.get_deepseek_model")
    def test_router_handles_parse_error(self, mock_get_model):
        from src.nodes.router import router

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "invalid response"
        mock_model.invoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        with patch("src.nodes.router.router_parser") as mock_parser:
            mock_parser.parse.side_effect = Exception("Parse error")

            state = {"topic": "test topic", "steps": []}
            result = router(state)

            assert result["router_decision"]["action"] == "search"
            assert state["topic"] in result["router_decision"]["queries"]


class TestSearchNode:
    @pytest.mark.asyncio
    @patch("src.nodes.search.get_tavily_search")
    async def test_search_web_returns_results(self, mock_get_search):
        from src.nodes.search import search_web

        mock_search = MagicMock()
        mock_search.invoke.return_value = {
            "results": [
                {"title": "Result 1", "url": "http://example.com/1", "content": "Content 1"},
                {"title": "Result 2", "url": "http://example.com/2", "content": "Content 2"}
            ]
        }
        mock_get_search.return_value = mock_search

        state = {"topic": "test", "queries": ["query1"], "steps": []}
        result = await search_web(state)

        assert "search_results" in result
        assert len(result["search_results"]) == 2
        assert result["search_results"][0]["title"] == "Result 1"

    @pytest.mark.asyncio
    @patch("src.nodes.search.get_tavily_search")
    async def test_search_web_handles_error(self, mock_get_search):
        from src.nodes.search import search_web

        mock_search = MagicMock()
        mock_search.invoke.side_effect = Exception("Search error")
        mock_get_search.return_value = mock_search

        state = {"topic": "test", "queries": ["query1"], "steps": []}
        result = await search_web(state)

        assert result["search_results"] == []


class TestSummarizerNode:
    @pytest.mark.asyncio
    @patch("src.nodes.summarizer.get_deepseek_model")
    async def test_summarize_returns_summary(self, mock_get_model):
        from src.nodes.summarizer import summarize

        mock_model = MagicMock()

        async def mock_stream():
            chunks = ["This ", "is ", "a ", "summary"]
            for chunk in chunks:
                yield type('obj', (object,), {'content': chunk})()

        mock_model.astream.return_value = mock_stream()
        mock_get_model.return_value = mock_model

        state = {"topic": "test topic", "search_results": [], "steps": []}
        result = await summarize(state)

        assert "summary" in result
        assert result["summary"] == "This is a summary"
        assert "steps" in result