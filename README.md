# DeepSeek 智能联网 Agent (MCP 版)

一个基于 LangGraph 构建的智能研究 Agent，结合 DeepSeek 大语言模型和 Tavily MCP Server，通过 LLM 自主决策工具调用，生成结构化的研究总结。

## 应用定位

**全能开发者个人助理 (Dev-Centric Omni-Agent)**

**一句话定义**：一个既懂公网最新技术动态，又能读懂你本地私有代码，并能通过 MCP 协议操作你开发环境的"数字分身"。

**痛点场景**：
- **以前**：你在网上看到一个新库（如 LangGraph 2.0），得自己读文档，再手动改代码。
- **现在**：Agent 联网搜索新文档，通过 MCP 读取你本地的老代码，直接给你生成适配后的补丁并保存。

## 功能特点

- **Agent 自主决策**：LLM 通过 `bind_tools` 自主判断何时调用搜索工具
- **MCP 协议集成**：使用 Tavily 官方远程 MCP Server，标准化工具调用
- **联网搜索**：获取高质量的网络资源（tavily-search、tavily-extract 等工具）
- **结构化总结**：使用 DeepSeek 模型生成 Markdown 格式的详细研究总结
- **有状态工作流**：基于 LangGraph 构建的灵活 Agent 工作流系统

## 需求规划 (Roadmap)

### 第一阶段：Agent 模式 + MCP（进行中）

#### 核心功能

1. **Agent 自主决策**
   - LLM 通过 `bind_tools` 绑定 MCP 工具
   - 自主判断是否需要调用搜索工具，无需显式 Router 节点
   - 支持多轮工具调用，灵活应对复杂查询

2. **MCP 工具集成**
   - 连接 Tavily 官方远程 MCP Server (`https://mcp.tavily.com/mcp/`)
   - 使用 `langchain-mcp-adapters` 实现 MCP 协议对接
   - 提供 tavily-search、tavily-extract、tavily-map、tavily-crawl 等工具

3. **专业报告生成**
   - 设定 DeepSeek 为"首席技术分析师"角色，提供专业分析
   - 输出标准化报告：包含核心结论 (Executive Summary)、详细分析 (Detailed Analysis) 和来源引用 (References)

4. **思考轨迹追踪**
   - 记录完整的执行步骤，形成可追溯的思考轨迹
   - 彩色日志输出，清晰标识当前运行的节点和状态

#### 技术实现

1. **Agent 模式**：使用 LangGraph 标准 Agent 工作流，包含 Agent 节点、工具条件判断、工具执行节点
2. **MCP 集成**：使用 `langchain-mcp-adapters` 连接 MCP Server，获取工具列表
3. **异步工作流**：基于 LangGraph 构建异步工作流，使用 `await app.ainvoke()` 处理
4. **状态管理**：AgentState 包含 `messages` 字段存储对话历史，实现完整的状态追踪

#### 代码结构

- **Agent 节点**：LLM + bind_tools，负责自主决策
- **Tool 节点**：执行 MCP 工具调用
- **Summarize 节点**：生成专业报告
- **工作流定义**：基于 LangGraph 的 Agent 模式，实现工具调用循环

### 第二阶段：私有上下文感知（接入 MCP Filesystem）
- **核心功能**：通过 MCP Filesystem Server，让 Agent 具备 `read_file` 和 `list_directory` 能力
- **应用**：你可以问"结合我 main.py 里的 AgentState 定义，帮我从网上找一个最适合的持久化存储方案"

### 第三阶段：闭环执行官（工具自动化）
- **核心功能**：增加 MCP Terminal/Git Server
- **应用**：Agent 搜索完方案后，自动创建一个新的 Git 分支，修改代码，并运行测试

## 技术栈架构 (2026 推荐)

- **大脑 (LLM)** : DeepSeek-V3 / R1 (高性价比推理核心)
- **骨架 (Framework)** : LangGraph (处理循环、记忆和复杂的条件状态切换)
- **连接器 (Protocol)** : MCP (Model Context Protocol) (官方 Python SDK，用于标准化工具调用)
- **搜索引擎** : Tavily / Exa AI (专为 AI 优化的搜索，直接返回清洗后的文本)
- **编辑器** : Trae (利用其 Builder Mode 进行代码自动重构)

## 实现方案与核心逻辑

### 核心节点逻辑设计

#### Agent (决策者)：
- LLM 通过 `bind_tools` 绑定 MCP 工具
- 自主判断任务类型：是"直接回答"还是"需要调用工具"
- 支持多轮工具调用，灵活应对复杂查询

#### Tool Node (工具执行器)：
- 执行 MCP 工具调用（tavily-search、tavily-extract 等）
- 异步执行工具，确保性能
- 完善的异常捕获机制

#### Summarize Node (汇总者)：
- 设定 DeepSeek 为"首席技术分析师"角色
- 输出包含核心结论、详细分析和来源引用的专业报告

### 技术优势

- **Agent 模式**：LLM 自主决策，更灵活智能
- **MCP 标准化**：统一的工具协议，易于扩展更多 MCP Server
- **异步执行**：使用 LangGraph 的异步 API，提高性能
- **错误处理**：完善的异常处理机制，确保系统稳定性

## 项目结构

```
my-ai-agent/
├── main.py                 # 主程序入口
├── pyproject.toml          # 项目配置和依赖管理
├── uv.lock                 # 依赖锁定文件
├── .python-version         # Python 版本管理
├── .env                    # 环境变量配置（不提交到 Git）
├── .gitignore              # Git 忽略文件
├── README.md               # 项目说明文档
├── .trae/
│   └── rules/
│       └── my-ai-agent.md  # 项目开发规则
├── src/
│   ├── __init__.py
│   ├── state.py            # Agent 状态定义
│   ├── graph.py            # LangGraph 工作流编排
│   ├── models/
│   │   └── __init__.py     # 模型和工具配置
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── router.py       # 路由节点（即将移除）
│   │   ├── search.py       # 搜索节点（即将移除）
│   │   └── summarizer.py   # 总结节点
│   └── prompts/
│       ├── __init__.py
│       ├── router_prompt.py
│       └── summarize_prompt.py
└── tests/
    ├── __init__.py
    ├── test_graph.py
    ├── test_nodes.py
    ├── test_prompts.py
    └── test_state.py
```

## 技术栈

- **LangGraph**: 构建有状态的 Agent 工作流
- **LangChain OpenAI**: 与 DeepSeek API 交互
- **LangChain Core**: 提供核心功能
- **langchain-mcp-adapters**: LangChain 官方 MCP 适配器
- **mcp**: Python 官方 MCP 客户端库
- **Tavily MCP Server**: 联网搜索工具（官方远程服务）
- **Python Dotenv**: 环境变量管理
- **Pydantic**: 用于定义数据模型

## 快速开始

### 1. 安装依赖

本项目使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理，确保你已经安装了 uv：

```bash
# 安装 uv（如果还没有安装）
pip install uv

# 安装项目依赖
uv sync
```

### 2. 配置环境变量

创建 `.env` 文件（参考 `.env` 示例）：

```env
# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Tavily API Key
TAVILY_API_KEY=your_tavily_api_key_here
```

获取 API Key：
- DeepSeek: https://platform.deepseek.com/
- Tavily: https://tavily.com/

### 3. 运行程序

```bash
python main.py
```

## 使用说明

1. 启动程序后，输入您想研究的课题
2. Agent 会自动判断是否需要联网搜索
3. 等待分析完成，查看生成的 Markdown 格式总结
4. 输入 `exit` 或 `退出` 结束对话

## 工作流原理

```
用户输入
    ↓
[Agent 自主决策]
    ↓
[tools_condition 判断]
    ↙          ↘
[调用工具]  [直接回答]
    ↓            ↓
[Tool 执行]  [Summarize 总结]
    ↓            ↓
回到 Agent    结束
```

## 核心节点

1. **agent**: LLM + bind_tools，自主决策是否调用工具
2. **tool_node**: 执行 MCP 工具调用（tavily-search 等）
3. **summarize**: 以"首席技术分析师"角色生成包含核心结论、详细分析和来源引用的专业报告

## 愿景

从"对话框"到"工作流"，这个应用的最终愿景不是让你在终端里打字，而是成为一个**透明的协作层**：
- 它知道你的代码风格（通过 MCP）
- 它知道最新的技术趋势（通过联网）
- 它在 Trae 里安静地为你准备好下一步的代码修改建议

## 许可证

MIT License
