# AgentScope Studio 指南

## 什么是 AgentScope Studio？

AgentScope Studio 是一个**本地部署的可视化工具**，用于支持代理应用的开发、调试和监控。

### 主要功能

1. **实时可视化**
   - 通过 Web 界面展示代理的推理和执行过程
   - 支持交互式调试和消息追踪
   - 实时查看 Agent 的思考和决策过程

2. **项目管理**
   - 提供对代理应用开发的项目管理功能
   - 支持多次运行的组织和比较
   - 便于追踪不同版本的运行结果

3. **内置代理 "Friday"**
   - 内置名为 "Friday" 的代理
   - 支持二次开发
   - 集成 AgentScope 的高级功能
   - 可以回答关于 AgentScope 的问题

4. **追踪和监控**
   - 追踪 Agent 的执行流程
   - 监控性能指标
   - 分析 Agent 的行为模式

## 安装 AgentScope Studio

### 前置要求

- Node.js >= 20.0.0
- npm >= 10.0.0

### 安装步骤

```bash
# 全局安装 AgentScope Studio
npm install -g @agentscope/studio
```

### 启动 Studio

```bash
# 启动 Studio（默认在 http://localhost:3000）
as_studio
```

启动后，在浏览器中访问 `http://localhost:3000` 即可使用。

## 在 LingNexus 中集成 Studio

### 方式 1：使用封装函数（推荐）

```python
from lingnexus.config import init_agentscope

# 初始化 AgentScope，连接到 Studio
init_agentscope(
    project="LingNexus",
    name="docx_agent_run",
    studio_url="http://localhost:3000",  # Studio URL
    logging_path="./logs",
    logging_level="INFO",
)
```

### 方式 2：直接使用 agentscope.init()

```python
import agentscope

# 初始化 AgentScope，连接到 Studio
agentscope.init(
    project="LingNexus",
    name="docx_agent_run",
    studio_url="http://localhost:3000",
    logging_path="./logs",
    logging_level="INFO",
)
```

## 完整示例

### 示例 1：基础集成

```python
from lingnexus.config import init_agentscope
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

# 1. 启动 Studio（在终端中运行: as_studio）

# 2. 初始化 AgentScope，连接到 Studio
init_agentscope(
    project="LingNexus",
    name="docx_agent_demo",
    studio_url="http://localhost:3000",
    logging_path="./logs",
)

# 3. 创建 Agent（正常使用）
agent = create_docx_agent(
    model_type=ModelType.QWEN,
    model_name="qwen-max",
)

# 4. 使用 Agent（运行情况会在 Studio 中显示）
response = agent.call("请帮我创建一个 Word 文档")
print(response)
```

### 示例 2：在示例代码中使用

更新 `examples/docx_agent_example.py`：

```python
from lingnexus.config import init_agentscope, ModelType
from lingnexus.agent import create_docx_agent

# 可选：连接到 Studio（如果 Studio 正在运行）
# init_agentscope(
#     project="LingNexus",
#     name="docx_example",
#     studio_url="http://localhost:3000",
# )

# 创建和使用 Agent
agent = create_docx_agent(model_type=ModelType.QWEN)
response = agent.call("请创建一个 Word 文档")
```

## 使用流程

### 步骤 1：启动 Studio

```bash
# 在终端中启动 Studio
as_studio
```

**输出示例**：
```
AgentScope Studio is running at http://localhost:3000
```

### 步骤 2：在代码中连接 Studio

```python
from lingnexus.config import init_agentscope

init_agentscope(
    project="LingNexus",
    studio_url="http://localhost:3000",
)
```

### 步骤 3：运行你的应用

```bash
uv run python examples/docx_agent_example.py
```

### 步骤 4：在 Studio 中查看

1. 打开浏览器访问 `http://localhost:3000`
2. 在 Studio 界面中可以看到：
   - 项目列表
   - 运行记录
   - Agent 的执行过程
   - 消息追踪
   - 性能指标

## Studio 界面功能

### 1. 项目管理

- **项目列表**：查看所有项目
- **运行记录**：查看每次运行的详细信息
- **运行比较**：比较不同运行的结果

### 2. 实时监控

- **消息流**：实时查看 Agent 之间的消息传递
- **推理过程**：查看 Agent 的思考过程
- **工具调用**：监控工具的使用情况

### 3. 调试功能

- **断点调试**：在关键点暂停执行
- **消息查看**：查看每条消息的详细内容
- **状态追踪**：追踪 Agent 的状态变化

## 配置选项

### init_agentscope() 参数说明

```python
init_agentscope(
    project="LingNexus",           # 项目名称（在 Studio 中显示）
    name="run_001",                # 运行名称（可选）
    run_id="unique_id",            # 运行 ID（可选，自动生成）
    studio_url="http://localhost:3000",  # Studio URL
    logging_path="./logs",          # 日志保存路径
    logging_level="INFO",          # 日志级别
    tracing_url=None,              # 追踪 URL（可选）
)
```

### 参数说明

- **project**: 项目名称，用于在 Studio 中组织运行记录
- **name**: 运行名称，便于识别不同的运行
- **run_id**: 运行 ID，如果不提供会自动生成
- **studio_url**: Studio 的 URL，通常是 `http://localhost:3000`
- **logging_path**: 日志保存路径，用于持久化日志
- **logging_level**: 日志级别（DEBUG, INFO, WARNING, ERROR）
- **tracing_url**: 追踪 URL，用于连接到第三方追踪平台

## 注意事项

### 1. Studio 必须先启动

在使用 `studio_url` 参数之前，确保 Studio 已经启动：

```bash
# 先启动 Studio
as_studio

# 然后在代码中连接
init_agentscope(studio_url="http://localhost:3000")
```

### 2. Studio 是可选的

如果不需要可视化功能，可以不使用 Studio：

```python
# 不使用 Studio，只使用日志
init_agentscope(
    project="LingNexus",
    logging_path="./logs",
    # studio_url 不设置
)
```

### 3. 性能影响

使用 Studio 会有轻微的性能开销，因为需要发送数据到 Studio。在生产环境中，建议关闭 Studio 连接。

### 4. 端口冲突

如果 3000 端口被占用，Studio 会自动使用其他端口。检查启动日志确认实际端口。

## 故障排查

### 问题 1: 无法连接到 Studio

**错误信息**：连接失败或超时

**解决方法**：
1. 确认 Studio 已启动：`as_studio`
2. 检查端口是否正确：默认是 3000
3. 检查防火墙设置
4. 尝试使用 `http://127.0.0.1:3000` 代替 `http://localhost:3000`

### 问题 2: Studio 中看不到运行记录

**可能原因**：
1. `studio_url` 未正确设置
2. `init_agentscope()` 在创建 Agent 之前未调用
3. Studio 未启动

**解决方法**：
1. 确保在创建 Agent 之前调用 `init_agentscope()`
2. 确认 `studio_url` 参数正确
3. 检查 Studio 是否正在运行

### 问题 3: 性能问题

**症状**：应用运行变慢

**解决方法**：
1. 在生产环境中关闭 Studio 连接
2. 只在开发/调试时使用 Studio
3. 调整日志级别减少输出

## 最佳实践

### 1. 开发环境

```python
# 开发时启用 Studio
init_agentscope(
    project="LingNexus",
    studio_url="http://localhost:3000",
    logging_path="./logs",
    logging_level="DEBUG",  # 开发时使用 DEBUG
)
```

### 2. 生产环境

```python
# 生产环境不使用 Studio
init_agentscope(
    project="LingNexus",
    logging_path="./logs",
    logging_level="INFO",  # 生产环境使用 INFO
    # studio_url 不设置
)
```

### 3. 条件启用

```python
import os

# 根据环境变量决定是否启用 Studio
studio_url = None
if os.getenv("ENABLE_STUDIO", "false").lower() == "true":
    studio_url = "http://localhost:3000"

init_agentscope(
    project="LingNexus",
    studio_url=studio_url,
    logging_path="./logs",
)
```

## 相关资源

- [AgentScope Studio GitHub](https://github.com/agentscope-ai/agentscope-studio)
- [AgentScope 官方文档](https://doc.agentscope.io/)
- [AgentScope Studio 教程](https://doc.agentscope.io/tutorial/task_studio.html)

## 总结

AgentScope Studio 是一个强大的可视化工具，可以帮助你：

- ✅ 实时监控 Agent 的执行过程
- ✅ 调试和优化 Agent 行为
- ✅ 管理项目运行记录
- ✅ 分析 Agent 性能

在 LingNexus 项目中，你可以通过 `init_agentscope()` 函数轻松集成 Studio，提升开发和调试效率。

