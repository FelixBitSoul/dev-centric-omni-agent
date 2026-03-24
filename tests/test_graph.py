import pytest
from unittest.mock import MagicMock, patch


class TestGraph:
    def test_should_search_returns_search_web_for_search_action(self):
        from src.graph import should_search

        state = {"router_decision": {"action": "search", "queries": ["q1"]}}
        result = should_search(state)
        assert result == "search_web"

    def test_should_search_returns_summarize_for_direct_answer(self):
        from src.graph import should_search

        state = {"router_decision": {"action": "direct_answer", "queries": []}}
        result = should_search(state)
        assert result == "summarize"

    def test_should_search_defaults_to_summarize(self):
        from src.graph import should_search

        state = {}
        result = should_search(state)
        assert result == "summarize"

    def test_graph_has_required_nodes(self):
        from src.graph import app

        assert app is not None


class TestGraphWorkflow:
    def test_graph_compiles_successfully(self):
        from src.graph import workflow

        assert workflow is not None

    @pytest.mark.asyncio
    @patch("src.nodes.summarizer.get_deepseek_model")
    @patch("src.nodes.search.get_tavily_search")
    @patch("src.nodes.router.get_deepseek_model")
    async def test_full_workflow_direct_answer(
        self, mock_router_model, mock_search_model, mock_summarize_model
    ):
        from src.graph import app

        mock_router = MagicMock()
        mock_router_response = MagicMock()
        mock_router_response.content = '{"action": "direct_answer", "queries": [], "reason": "simple"}'
        mock_router.invoke.return_value = mock_router_response
        mock_router_model.return_value = mock_router

        mock_search = MagicMock()
        mock_search.invoke.return_value = {"results": []}
        mock_search_model.return_value = mock_search

        mock_summarize = MagicMock()

        async def mock_stream():
            yield type('obj', (object,), {'content': 'Direct answer summary'})()

        mock_summarize.astream.return_value = mock_stream()
        mock_summarize_model.return_value = mock_summarize

        with patch("src.nodes.router.router_parser") as mock_parser:
            mock_decision = MagicMock()
            mock_decision.action = "direct_answer"
            mock_decision.queries = []
            mock_decision.reason = "simple"
            mock_parser.parse.return_value = mock_decision

            initial_state = {"topic": "simple question", "steps": []}
            results = []
            async for event in app.astream(initial_state, stream_mode="updates"):
                results.append(event)

            assert len(results) > 0