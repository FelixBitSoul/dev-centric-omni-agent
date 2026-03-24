import pytest
from src.state import AgentState


class TestAgentState:
    def test_agent_state_topic_field(self):
        state = AgentState(topic="AI trends", steps=[])
        assert state["topic"] == "AI trends"

    def test_agent_state_steps_list(self):
        initial_steps = ["step1", "step2"]
        state = AgentState(topic="test", steps=initial_steps)
        assert state["steps"] == ["step1", "step2"]
        assert isinstance(state["steps"], list)

    def test_agent_state_can_be_modified(self):
        state = AgentState(topic="test", steps=[])
        state["router_decision"] = {"action": "search", "queries": ["query1"]}
        state["steps"].append("new step")
        assert state["router_decision"] == {"action": "search", "queries": ["query1"]}
        assert "new step" in state["steps"]

    def test_agent_state_complete_state(self):
        state = AgentState(
            topic="test topic",
            steps=["step1", "step2"],
            router_decision={"action": "search", "queries": ["q1"], "reason": "test"},
            queries=["q1"],
            search_results=[{"title": "t", "url": "u", "content": "c"}],
            summary="summary text"
        )
        assert state["topic"] == "test topic"
        assert state["router_decision"] == {"action": "search", "queries": ["q1"], "reason": "test"}
        assert state["queries"] == ["q1"]
        assert state["search_results"] == [{"title": "t", "url": "u", "content": "c"}]
        assert state["summary"] == "summary text"