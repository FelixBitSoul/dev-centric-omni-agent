import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import ToolMessage

from dev_centric_omni_agent.models import map_deepseek_messages, clear_deepseek_model, clear_mcp_tools, get_tools, get_model


def test_map_deepseek_messages_transforms_toolmessage_list_content():
    original = ToolMessage(
        content=[
            {"type": "text", "text": "hello"},
            {"type": "text", "text": " "},
            {"type": "text", "text": "world"},
            {"type": "image", "text": "unused"},
        ],
        tool_call_id="tool1",
    )

    output = map_deepseek_messages([original])

    assert len(output) == 1
    assert isinstance(output[0], ToolMessage)
    assert output[0].content == "hello world"
    assert output[0].tool_call_id == "tool1"


def test_map_deepseek_messages_preserves_other_messages():
    normal = SimpleNamespace(content="orig", tool_call_id=None)

    output = map_deepseek_messages([normal])

    assert len(output) == 1
    assert output[0] is normal


def test_clear_deepseek_model_and_tools_can_be_called_without_errors():
    clear_deepseek_model()
    clear_mcp_tools()


@pytest.mark.asyncio
async def test_get_tools_initializes_mcp_client_and_returns_tools(monkeypatch):
    """Test that get_tools initializes MultiServerMCPClient and returns tools"""
    mock_tools = [SimpleNamespace(name="tool1"), SimpleNamespace(name="tool2")]
    
    mock_client = AsyncMock()
    mock_client.get_tools = AsyncMock(return_value=mock_tools)
    
    # Use a regular Mock that returns the mock_client when called
    mock_mcp_client_class = lambda *args, **kwargs: mock_client
    
    monkeypatch.setenv("TAVILY_API_KEY", "test_key")
    monkeypatch.setattr(
        "dev_centric_omni_agent.models.MultiServerMCPClient",
        mock_mcp_client_class
    )
    
    # Clear any cached tools
    clear_mcp_tools()
    
    result = await get_tools()
    
    assert result == mock_tools
    mock_client.get_tools.assert_called_once()


@pytest.mark.asyncio
async def test_get_tools_caches_result_on_second_call(monkeypatch):
    """Test that get_tools returns cached tools on subsequent calls"""
    mock_tools = [SimpleNamespace(name="tool_cached")]
    
    mock_client = AsyncMock()
    mock_client.get_tools = AsyncMock(return_value=mock_tools)
    
    call_count = 0
    def mock_mcp_client_class(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return mock_client
    
    monkeypatch.setenv("TAVILY_API_KEY", "test_key")
    monkeypatch.setattr(
        "dev_centric_omni_agent.models.MultiServerMCPClient",
        mock_mcp_client_class
    )
    
    # Clear any cached tools
    clear_mcp_tools()
    
    result1 = await get_tools()
    result2 = await get_tools()
    
    assert result1 == mock_tools
    assert result2 == mock_tools
    assert call_count == 1  # MultiServerMCPClient should only be instantiated once
    mock_client.get_tools.assert_called_once()


@pytest.mark.asyncio
async def test_get_model_initializes_and_returns_model(monkeypatch):
    """Test that get_model initializes ChatOpenAI with tools and returns runnable chain"""
    mock_tools = [SimpleNamespace(name="test_tool")]
    
    # Mock get_tools to return our mock tools
    async def mock_get_tools_func():
        return mock_tools
    
    monkeypatch.setattr("dev_centric_omni_agent.models.get_tools", mock_get_tools_func)
    
    # Mock ChatOpenAI
    mock_llm = MagicMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    
    mock_chat_openai_class = MagicMock(return_value=mock_llm)
    monkeypatch.setattr("dev_centric_omni_agent.models.ChatOpenAI", mock_chat_openai_class)
    
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_deepseek_key")
    
    # Clear any cached model
    clear_deepseek_model()
    
    result = await get_model()
    
    # Verify ChatOpenAI was instantiated with correct params
    mock_chat_openai_class.assert_called_once_with(
        base_url="https://api.deepseek.com",
        api_key="test_deepseek_key",
        model="deepseek-chat"
    )
    
    # Verify bind_tools was called with our mock tools
    mock_llm.bind_tools.assert_called_once_with(mock_tools)
    
    # Result should be a runnable chain (RunnableLambda | raw_llm)
    assert result is not None


@pytest.mark.asyncio
async def test_get_model_caches_result_on_second_call(monkeypatch):
    """Test that get_model returns cached model on subsequent calls"""
    mock_tools = [SimpleNamespace(name="cached_tool")]
    
    # Mock get_tools
    async def mock_get_tools_func():
        return mock_tools
    
    monkeypatch.setattr("dev_centric_omni_agent.models.get_tools", mock_get_tools_func)
    
    # Mock ChatOpenAI
    mock_llm = MagicMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    
    call_count = 0
    def mock_chat_openai_class(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return mock_llm
    
    monkeypatch.setattr("dev_centric_omni_agent.models.ChatOpenAI", mock_chat_openai_class)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_deepseek_key")
    
    # Clear any cached model
    clear_deepseek_model()
    
    result1 = await get_model()
    result2 = await get_model()
    
    # Verify ChatOpenAI was only instantiated once
    assert call_count == 1
    # Verify bind_tools was only called once
    mock_llm.bind_tools.assert_called_once()
    # Results should be the same
    assert result1 is result2
