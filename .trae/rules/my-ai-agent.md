# Agent Project Rules (LangGraph + DeepSeek)

## 1. 架构与目录 (Structure)
- **模块化**：严禁单文件。`src/state.py` (状态), `src/nodes/` (原子节点), `src/graph.py` (编排), `src/models/` (配置)。
- **Prompt管理**：所有 Prompt 模板必须存放于 `src/prompts.py`。

## 2. 技术规范 (Tech Stack)
- **包管理**：强制使用 `uv` (`uv add`, `uv run`)。
- **异步**：节点必须 `async def`；搜索需 `asyncio.gather` 并发。
- **模型**：使用 `ChatOpenAI` 接入 DeepSeek，必须配置 `astream` 流式输出。
- **工具**：仅限使用 `TavilySearch` 异步 API。

## 3. 开发规范 (Dev Standards)
- **类型安全**：强制 Type Hints；结构化输出必用 `Pydantic`。
- **状态追踪**：所有节点必须 append 描述至 `steps` 列表。
- **健壮性**：搜索必须包裹 `try-except`；Router 须有解析失败的 Fallback (默认 search)。
- **日志规范**：强制使用带颜色的终端输出标识节点：Router(Blue), Search(Green), Summarize(Yellow)。错误信息必须用红色(Red)。禁止使用 print，必须用 loguru。
- **安全**：禁止硬编码 Key，统一从 `.env` 读取。

## 4. AI 行为红线 (AI Behavior)
- 修改 `AgentState` 前必须列出受影响的文件。
- 新增功能需同步建议 `pytest` 测试脚本。
- 严禁在非公式场景使用 LaTeX。