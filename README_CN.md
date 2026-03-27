# 开发者中心全能Agent

本仓库实现了一个基于 **LangGraph** 的简化 Agent 框架，当前版本已经可运行：
- 主入口：`main.py`
- 工作流：`src/graph.py`
- 模型 + 工具：`src/models/__init__.py`

Agent 能力：
- 使用 `langchain-openai.ChatOpenAI` 的 DeepSeek 模型（`deepseek-chat`）
- 通过 `langchain-mcp-adapters` 连接 MCP 工具：`tavily` + `filesystem`
- 动态系统时间提示（`SystemMessage` 包含当前时间）
- 通过 `bind_tools` 自动判断并调用工具链（搜索、提取、文件操作）
- 支持多轮工具调用循环，基于 `StateGraph` 的节点图

## 当前功能现状（已实现）

1. `main.py` 提供 CLI 交互，输入研究课题后进入长轮次处理。 
2. `src/graph.py` 构建 Agent 工作流：
   - `agent` 节点：调用模型，接受消息并返回 ToolMessage
   - `tools` 节点：`ToolNode` 执行 MCP 工具
   - 通过 `should_continue` 判断工具调用结束
3. `src/models/__init__.py`：
   - `get_tools()` 使用 `MultiServerMCPClient` 加载 `filesystem` + `tavily`
   - `get_model()` 构建 `RunnableLambda(map_deepseek_messages) | raw_llm`
4. `cleanup_tool_outputs` & `map_deepseek_messages` 做消息格式兼容处理（将 ToolMessage 列表转换为字符串）

## 快速启动

1. 安装依赖：

```bash
pip install uv
uv sync
```

2. 新建 `.env`：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

3. 运行：

```bash
python main.py
```

4. 使用：
- 输入文本，回车后 Agent 处理并输出模型/工具流水
- 输入 `exit` 或 `退出` 结束

## 核心文件说明

- `main.py`: 程序运行与事件流展示
- `src/graph.py`: LangGraph 工作图，agent + tools 控制流
- `src/models/__init__.py`: 模型与 MCP 工具初始化

## 代码风格与测试

- Python 版本：>=3.11
- 依赖项见 `pyproject.toml`，已包含 `langchain-core`/`langgraph`/`mcp`
- 可用测试目录（目前无详细测试逻辑）：`tests/`

## 功能愿景（MVP）

本项目定位为开发者个人级“研究+实操” Agent，目标在最小可用产品层面提供：

- 以一条问题输入触发的端到端闭环：问题 -> 模型推理 -> 工具检索 -> 结果汇总
- 支持本地代码与远程搜索两部分数据源（MCP `filesystem` + `tavily`），实现“本地上下文 + 实时互联网补全”
- 重点体验：强调“工具调用透明可观测”，在控制台输出工具启动/结束事件，方便开发者理解智能决策流程
- MVP亮点：低门槛直接跑通（`python main.py`），具备“你问我查我汇总”的实用感

## 未来优化建议

- 增加 `tests/` 单元 + 集成用例：`get_tools`、`create_graph`、`main` 交互
- 迁移 `AgentState` 理念到 `src/state.py`（当前未使用）
- 补全 `src/nodes`
- 增加完整 `README` 运行示例与输出样本

## 许可

MIT
