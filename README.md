# Dev-Centric Omni Agent

This repository implements a lightweight Agent based on **LangGraph**, currently in a runnable MVP state:
- Entry point: `main.py`
- Workflow: `src/graph.py`
- Model + tools: `src/models/__init__.py`

> Chinese version available: [README_CN.md](README_CN.md)

## What this MVP does

- Connects to the DeepSeek model (`deepseek-chat`) via `langchain-openai.ChatOpenAI`
- Loads MCP tools via `langchain-mcp-adapters`:
  - `filesystem` (local project root)
  - `tavily` (remote search and web extraction)
- Adds dynamic system time context in prompts (`SystemMessage` contains current datetime)
- Uses `bind_tools` for tool-autonomy and supports iterative tool calling
- Runs a looped agent workflow using `StateGraph` and `ToolNode`

## Current implemention details

1. CLI interface in `main.py`: read topic, send messages to graph, stream events
2. Agent graph in `src/graph.py`:
   - `agent` node calls model with current message state
   - `tools` node executes returned tool calls
   - `should_continue` routes back until no tools are required
3. Model & tools in `src/models/__init__.py`:
   - `get_tools()` initializes `MultiServerMCPClient` with `filesystem` and `tavily`
   - `get_model()` builds `RunnableLambda(map_deepseek_messages) | raw_llm`
4. Output compatibility helpers:
   - `cleanup_tool_outputs` and `map_deepseek_messages` convert `ToolMessage` list payloads to text

## Quick Start

1. Install dependencies:

```bash
uv sync
```

2. Create `.env`:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

3. Run:

```bash
uv run app
```

4. Use:
- Enter a query; the agent decides whether to call tools and returns a result
- Enter `exit` or `退出` to quit
## Run tests

```bash
cd path/to/your-project
uv run pytest -q
```

## Core files

- `main.py`: CLI workflow and stream event logging
- `src/graph.py`: LangGraph workflow (agent + tool execution graph)
- `src/models/__init__.py`: DeepSeek model and MCP tools setup

## Specs

- Python: >=3.11
- Dependencies in `pyproject.toml`: `langchain-core`, `langgraph`, `mcp`, etc.
- Tests directory exists: `tests/` (add coverage later)

## MVP Vision

The goal is a personal developer research agent with a minimal but valuable feature set:

- one-shot query path: question -> reasoning -> tool retrieval -> summary
- local source + online source fusion via MCP `filesystem` and `tavily`
- tool call visibility in console output
- MVP highlight: runnable immediately with low setup (single command entrypoint)

## Next steps

- Add unit and integration tests for `get_tools`, `create_graph`, and `main` flow
- Add expanded examples and sample output in docs

## License

MIT
