import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from dev_centric_omni_agent.graph import create_graph


@pytest.mark.asyncio
async def test_create_graph_initializes_with_tools_and_model(monkeypatch):
    """Test that create_graph retrieves tools and model"""
    mock_tools = [SimpleNamespace(name="tool1"), SimpleNamespace(name="tool2")]
    mock_model = MagicMock()
    
    # Mock get_tools and get_model
    async def mock_get_tools():
        return mock_tools
    
    async def mock_get_model():
        return mock_model
    
    monkeypatch.setattr("dev_centric_omni_agent.graph.get_tools", mock_get_tools)
    monkeypatch.setattr("dev_centric_omni_agent.graph.get_model", mock_get_model)
    
    # Mock StateGraph and its methods
    mock_workflow = MagicMock()
    mock_workflow.compile = MagicMock(return_value=MagicMock())
    
    mock_state_graph_class = MagicMock(return_value=mock_workflow)
    monkeypatch.setattr("dev_centric_omni_agent.graph.StateGraph", mock_state_graph_class)
    
    # Mock ToolNode
    mock_tool_node_class = MagicMock()
    monkeypatch.setattr("dev_centric_omni_agent.graph.ToolNode", mock_tool_node_class)
    
    result = await create_graph()
    
    # Verify StateGraph was instantiated
    mock_state_graph_class.assert_called_once()
    
    # Verify nodes were added
    assert mock_workflow.add_node.call_count == 2
    
    # Verify edges were added
    assert mock_workflow.add_edge.call_count == 2
    
    # Verify conditional edges
    mock_workflow.add_conditional_edges.assert_called_once()
    
    # Verify compile was called
    mock_workflow.compile.assert_called_once()
    
    # Verify result is the compiled app
    assert result is not None


@pytest.mark.asyncio
async def test_create_graph_adds_agent_and_tools_nodes(monkeypatch):
    """Test that create_graph adds agent and tools nodes"""
    mock_tools = [SimpleNamespace(name="test_tool")]
    mock_model = MagicMock()
    
    async def mock_get_tools():
        return mock_tools
    
    async def mock_get_model():
        return mock_model
    
    monkeypatch.setattr("dev_centric_omni_agent.graph.get_tools", mock_get_tools)
    monkeypatch.setattr("dev_centric_omni_agent.graph.get_model", mock_get_model)
    
    mock_workflow = MagicMock()
    mock_workflow.compile = MagicMock(return_value=MagicMock())
    
    mock_state_graph_class = MagicMock(return_value=mock_workflow)
    monkeypatch.setattr("dev_centric_omni_agent.graph.StateGraph", mock_state_graph_class)
    
    mock_tool_node_class = MagicMock()
    monkeypatch.setattr("dev_centric_omni_agent.graph.ToolNode", mock_tool_node_class)
    
    await create_graph()
    
    # Verify ToolNode was created with tools
    mock_tool_node_class.assert_called_once_with(mock_tools)
    
    # Verify add_node calls - should be "agent" and "tools"
    calls = mock_workflow.add_node.call_args_list
    assert len(calls) == 2
    assert calls[0][0][0] == "agent"  # First call should add "agent" node
    assert calls[1][0][0] == "tools"  # Second call should add "tools" node


@pytest.mark.asyncio
async def test_create_graph_builds_workflow_with_start_edge(monkeypatch):
    """Test that create_graph builds workflow with START edge"""
    mock_tools = [SimpleNamespace(name="workflow_tool")]
    mock_model = MagicMock()
    
    async def mock_get_tools():
        return mock_tools
    
    async def mock_get_model():
        return mock_model
    
    monkeypatch.setattr("dev_centric_omni_agent.graph.get_tools", mock_get_tools)
    monkeypatch.setattr("dev_centric_omni_agent.graph.get_model", mock_get_model)
    
    mock_workflow = MagicMock()
    mock_workflow.compile = MagicMock(return_value=MagicMock())
    
    mock_state_graph_class = MagicMock(return_value=mock_workflow)
    monkeypatch.setattr("dev_centric_omni_agent.graph.StateGraph", mock_state_graph_class)
    
    mock_tool_node_class = MagicMock()
    monkeypatch.setattr("dev_centric_omni_agent.graph.ToolNode", mock_tool_node_class)
    
    monkeypatch.setattr("dev_centric_omni_agent.graph.START", "START")
    
    await create_graph()
    
    # Verify add_edge calls
    edge_calls = mock_workflow.add_edge.call_args_list
    assert len(edge_calls) >= 1
    # First edge should be START -> "agent"
    assert edge_calls[0][0][0] == "START"
    assert edge_calls[0][0][1] == "agent"
