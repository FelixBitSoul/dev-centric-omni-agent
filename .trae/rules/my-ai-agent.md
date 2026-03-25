# Agent Project Rules (LangGraph + DeepSeek + MCP)

## 1. 架构与目录 (Structure)
- **模块化**：严禁单文件。`src/state.py` (状态), `src/agent.py` (Agent 创建), `src/graph.py` (编排), `src/models/` (配置)。
- **Prompt管理**：所有 Prompt 模板必须存放于 `src/prompts/`。
- **Agent模式**：使用 LangGraph 的 `create_react_agent` 创建标准 ReAct Agent。

## 2. 技术规范 (Tech Stack)
- **包管理**：强制使用 `uv` (`uv add`, `uv run`)。
- **异步**：Agent 创建和调用必须使用 `async/await`。
- **模型**：使用 `ChatOpenAI` 接入 DeepSeek，必须配置 `astream` 流式输出。
- **工具**：使用 `langchain-mcp-adapters` 连接 MCP Server，通过 `bind_tools` 绑定工具。
- **MCP集成**：优先使用 Tavily 官方远程 MCP Server (`https://mcp.tavily.com/mcp/`)。
- **Agent创建**：使用 `langgraph.prebuilt.create_react_agent` 创建标准 Agent。

## 3. 开发规范 (Dev Standards)
- **类型安全**：强制 Type Hints；结构化输出必用 `Pydantic`。
- **状态管理**：使用 `create_react_agent` 的标准状态结构。
- **状态追踪**：通过日志记录 Agent 执行步骤。
- **健壮性**：`create_react_agent` 内置错误处理，无需额外包装。
- **日志规范**：强制使用带颜色的终端输出标识节点：Agent(Blue), ToolCall(Green)。错误信息必须用红色(Red)。
- **安全**：禁止硬编码 Key，统一从 `.env` 读取。

## 4. AI 行为红线 (AI Behavior)
- 修改 Agent 架构前必须列出受影响的文件。
- 新增功能需同步建议 `pytest` 测试脚本。
- 严禁在非公式场景使用 LaTeX。