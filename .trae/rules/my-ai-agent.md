# Trae Project Rules: DeepSeek & LangGraph AI Agent

## 1. 核心架构与目录规范 (Architecture & Directory)
* **模块化平铺原则**：禁止将所有逻辑堆叠在 `main.py`。必须按照功能拆分文件，以降低 AI 维护成本。
* **目录结构标准**：
    * `src/state.py`: 统一管理 `AgentState` (TypedDict)。
    * `src/nodes/`: 存放独立的节点函数（如 `router.py`, `search.py`, `summarizer.py`）。
    * `src/graph.py`: 负责 `StateGraph` 的定义、边界连接与编译。
    * `src/models/`: 统一配置和初始化 `ChatOpenAI` (DeepSeek)。
    * `src/prompts/`: 抽离所有的 Prompt 模板，避免硬编码在业务逻辑中。

## 2. 技术栈与性能约束 (Tech Stack & Performance)
* **包管理**：强制使用 `uv` 进行依赖管理。新增库必须通过 `uv add` 执行。
* **异步编程**：所有节点必须使用 `async def`，并确保搜索节点使用 `asyncio.gather` 进行并发请求。
* **模型调用**：使用 `langchain_openai` 接入 DeepSeek，并配置 `astream` 以支持流式响应。
* **联网工具**：统一使用 `TavilySearch` 及其异步 API。

## 3. 代码质量与 AI 协作规范 (Coding & AI Collaboration)
* **强类型约束**：
    * 所有函数必须包含类型标注 (Type Hints)。
    * 结构化输出必须通过 `PydanticOutputParser` 与 `pydantic.BaseModel` 实现。
* **状态追踪**：每个节点在执行任务时，必须向 `steps` 列表添加描述性字符串，以记录思考轨迹。
* **错误处理机制**：
    * 网络请求必须包裹在 `try-except` 块中。
    * Router 节点必须具备 Fallback 逻辑，解析失败时默认进行搜索。
* **日志输出**：使用带颜色的终端打印 (ANSI colors) 区分不同节点，方便调试。

## 4. 自动化维护红线 (Maintenance Redlines)
* **配置安全**：严禁硬编码 API Key，必须从 `.env` 文件读取。
* **变更审计**：AI 在修改 `AgentState` 字段前，必须先列出受影响的节点文件。
* **测试驱动**：新增功能建议同步在 `tests/` 目录下生成对应的 pytest 脚本。

## 5. 违禁项 (Prohibitions)
* 禁止在非技术/非公式语境下使用 LaTeX 格式。
* 禁止删除现有的 `steps` 追踪逻辑。
* 禁止在未更新 `src/state.py` 的情况下直接修改节点间的传参结构。