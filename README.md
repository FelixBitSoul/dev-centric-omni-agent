# DeepSeek 智能联网 Agent

一个基于 LangGraph 构建的智能研究 Agent，结合 DeepSeek 大语言模型和 Tavily 搜索引擎，能够自动判断研究课题是否需要联网搜索，并生成结构化的研究总结。

## 应用定位

**全能开发者个人助理 (Dev-Centric Omni-Agent)**

**一句话定义**：一个既懂公网最新技术动态，又能读懂你本地私有代码，并能通过 MCP 协议操作你开发环境的"数字分身"。

**痛点场景**：
- **以前**：你在网上看到一个新库（如 LangGraph 2.0），得自己读文档，再手动改代码。
- **现在**：Agent 联网搜索新文档，通过 MCP 读取你本地的老代码，直接给你生成适配后的补丁并保存。

## 功能特点

- **智能搜索判断**：自动分析研究课题，判断是否需要联网获取最新信息
- **联网搜索**：集成 Tavily 搜索引擎，获取高质量的网络资源
- **结构化总结**：使用 DeepSeek 模型生成 Markdown 格式的详细研究总结
- **有状态工作流**：基于 LangGraph 构建的灵活工作流系统

## 需求规划 (Roadmap)

### 第一阶段：智能情报员（已完成基础）
- **核心功能**：输入一个模糊的开发问题，Agent 自动拆解关键词，联网搜索，输出结构化报告
- **优化点**：引入 JSON 决策路由，让模型自己决定是"直接回答"还是"搜索后再回答"

### 第二阶段：私有上下文感知（接入 MCP）
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

#### Router (决策者)：
- 判断任务类型：是"纯知识问答"、"需要联网"还是"需要查看本地代码"？
- 输出格式： `{"action": "search" | "mcp_read" | "final_answer", "params": {...}}`

#### MCP Tool Node (本地执行器)：
```python
# 模拟 MCP 读取本地文件的逻辑
async def call_mcp_filesystem(state):
    # 使用 mcp-python-sdk 连接本地 server
    # 读取当前项目的 README.md 或 main.py
    return {"local_context" : file_content}
```

#### Search Node (外部执行器)：
- 调用 Tavily，并行搜索多个关键词

#### Synthesizer (汇总者)：
- 将 local_context (本地代码) 和 search_results (网上文档) 喂给 DeepSeek

## 项目结构

```
my-ai-agent/
├── main.py           # 主程序入口
├── requirements.txt  # Python 依赖
├── .env             # 环境变量配置（不提交到 Git）
└── README.md        # 项目说明文档
```

## 技术栈

- **LangGraph**: 构建有状态的 Agent 工作流
- **LangChain OpenAI**: 与 DeepSeek API 交互
- **Tavily Search**: 联网搜索工具
- **Python Dotenv**: 环境变量管理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
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
[判断是否需要搜索] → 是 → [联网搜索] → [生成总结] → 结束
    ↓ 否
[生成总结] → 结束
```

## 核心节点

1. **check_need_search**: 调用 DeepSeek 模型分析课题，判断搜索必要性
2. **search_web**: 使用 Tavily 搜索相关网络资源
3. **summarize**: 整合信息，生成 Markdown 格式的研究总结

## 愿景

从"对话框"到"工作流"，这个应用的最终愿景不是让你在终端里打字，而是成为一个**透明的协作层**：
- 它知道你的代码风格（通过 MCP）
- 它知道最新的技术趋势（通过联网）
- 它在 Trae 里安静地为你准备好下一步的代码修改建议

## 许可证

MIT License
