import pytest
from types import SimpleNamespace

from langgraph.constants import END
from langchain_core.messages import ToolMessage

from dev_centric_omni_agent.nodes.agent import call_model, should_continue
from dev_centric_omni_agent.nodes.tool import cleanup_tool_outputs


def test_should_continue_no_tool_calls():
    state = {"messages": [SimpleNamespace(tool_calls=[])]}
    assert should_continue(state) == END


def test_should_continue_with_tool_calls():
    state = {"messages": [SimpleNamespace(tool_calls=["dummy"])]}
    assert should_continue(state) == "tools"


def test_cleanup_tool_outputs_normal_message():
    state = {"messages": [ToolMessage(content="hello", tool_call_id="id1")]}
    result = cleanup_tool_outputs(state)
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0].content == "hello"


def test_cleanup_tool_outputs_list_content():
    content = [{"text": "line1"}, {"text": "line2"}, "line3"]
    msg = ToolMessage(content=content, tool_call_id="id2")

    result = cleanup_tool_outputs({"messages": [msg]})

    assert len(result["messages"]) == 1
    assert result["messages"][0].content == "line1\nline2\nline3"


@pytest.mark.asyncio
async def test_call_model_with_mocked_model(monkeypatch):
    class DummyModel:
        async def ainvoke(self, messages):
            return SimpleNamespace(content="OK")

    async def dummy_get_model():
        return DummyModel()

    monkeypatch.setattr("dev_centric_omni_agent.nodes.agent.get_model", dummy_get_model)

    state = {"messages": [SimpleNamespace(content="hi")]}
    result = await call_model(state)

    assert "messages" in result
    assert result["messages"][0].content == "OK"
