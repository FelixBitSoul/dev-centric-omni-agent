# DeepSeek 智能联网 Agent

一个基于 LangGraph 构建的智能研究 Agent，结合 DeepSeek 大语言模型和 Tavily 搜索引擎，能够自动判断研究课题是否需要联网搜索，并生成结构化的研究总结。

## 功能特点

- **智能搜索判断**：自动分析研究课题，判断是否需要联网获取最新信息
- **联网搜索**：集成 Tavily 搜索引擎，获取高质量的网络资源
- **结构化总结**：使用 DeepSeek 模型生成 Markdown 格式的详细研究总结
- **有状态工作流**：基于 LangGraph 构建的灵活工作流系统

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

## 许可证

MIT License
