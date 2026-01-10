# Framework 快速开始

> LingNexus Framework 核心框架使用指南

---

## 目录

- [安装](#安装)
- [核心概念](#核心概念)
- [基础使用](#基础使用)
- [监控任务](#监控任务)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 安装

### 环境要求

- Python 3.10 或更高版本
- pip 或 uv 包管理器
- DashScope API Key

### 安装步骤

```bash
# 使用 pip 安装
pip install lingnexus-framework

# 或使用 uv（推荐）
uv add lingnexus-framework

# 安装可选依赖（监控系统）
pip install "lingnexus-framework[monitoring]"

# 安装可选依赖（向量数据库）
pip install "lingnexus-framework[vector]"

# 安装全部依赖
pip install "lingnexus-framework[all]"
```

### 配置 API Key

```bash
# 方式1: 环境变量
export DASHSCOPE_API_KEY="your-api-key-here"

# 方式2: .env 文件
echo "DASHSCOPE_API_KEY=your-api-key-here" > .env

# 方式3: 代码中设置
import os
os.environ["DASHSCOPE_API_KEY"] = "your-api-key-here"
```

---

## 核心概念

### 什么是 Agent?

Agent 是一个智能体实体，可以：
- 接收用户输入
- 使用多个 Skills 完成任务
- 返回结构化输出

**特点**：
- 🤖 基于大语言模型
- 🔧 可配置模型参数（温度、top_p 等）
- 📦 支持 Skill 组合
- 💾 支持记忆功能

### 什么是 Skill?

Skill 是 Agent 的能力模块，定义了特定的功能：

**结构**：
```
skill-name/
├── SKILL.md              # Skill 定义（必需）
├── scripts/              # 脚本文件（可选）
├── references/           # 参考文档（可选）
└── assets/               # 静态资源（可选）
```

**SKILL.md 格式**：
```markdown
---
name: "合同审查助手"
description: "审查合同法律风险，识别潜在问题条款"
category: "法务"
tags: ["合同", "风控", "法律"]
trigger_keywords: ["合同", "协议", "条款"]
---

## 功能

本 Skill 可以帮助您：

1. 识别合同中的法律风险条款
2. 提供修改建议
3. 生成风险报告

## 使用方法

直接上传合同文件，即可开始审查。
```

### 渐进式披露机制

LingNexus 采用三层渐进式披露，优化 Token 使用：

```
Phase 1: 元数据层 (~100 tokens/Skill)
  └─ 只加载 Skill 名称和描述
  └─ 用于 Skill 发现和选择

Phase 2: 指令层 (~5k tokens/Skill)
  └─ 按需加载完整 SKILL.md 内容
  └─ Agent 执行时动态加载

Phase 3: 资源层 (按需加载)
  └─ references/ 文档
  └─ assets/ 资源文件
  └─ scripts/ 脚本执行
```

---

## 基础使用

### 1. 创建简单的 Agent

```python
from lingnexus import create_progressive_agent
from agentscope.message import Msg

# 创建 Agent
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
)

# 运行
response = agent(Msg(name="user", content="你好"))
print(response.content)
```

### 2. 创建带 Skills 的 Agent

```python
from lingnexus import create_progressive_agent

# 创建 Agent 并指定 Skills
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
    skills=["合同审查助手", "风险评估工具"],  # Skill 名称列表
)

# Agent 会自动加载这些 Skills
response = agent(Msg(name="user", content="请审查这份合同"))
```

### 3. 使用 Skill Loader

```python
from lingnexus.skill import SkillLoader

# 初始化加载器
loader = SkillLoader(skills_base="skills")

# 注册所有 Skills
loader.register_all_skills()

# 获取 Skill 元数据（Phase 1 - 轻量级）
metadata = loader.get_skill_metadata("合同审查助手")
print(metadata)
# {
#     "name": "合同审查助手",
#     "description": "审查合同法律风险",
#     "category": "法务",
#     "tags": ["合同", "风控"]
# }

# 加载完整内容（Phase 2 - 按需）
instructions = loader.load_skill_instructions("合同审查助手")
print(instructions)
# 完整的 SKILL.md 内容

# 获取资源路径（Phase 3 - 按需）
resource_path = loader.get_skill_resource_path(
    "合同审查助手",
    "references/合同模板.docx"
)
```

### 4. 使用存储层

```python
from lingnexus.storage import RawStorage, StructuredDB

# 原始数据存储
raw_storage = RawStorage()
data_id = raw_storage.save(
    source="ClinicalTrials.gov",
    data="原始HTML内容",
    url="https://clinicaltrials.gov/...",
    project="司美格鲁肽"
)

# 结构化数据库
db = StructuredDB()
db.save_trial(
    raw_data_id=data_id,
    extracted_data={
        "nct_id": "NCT06989203",
        "title": "Semaglutide Treatment...",
        "phase": "III期",
        "status": "Recruiting",
    },
    project_name="司美格鲁肽"
)

# 查询数据
trials = db.get_project_trials("司美格鲁肽", limit=20)
for trial in trials:
    print(f"{trial['nct_id']}: {trial['title']}")
```

---

## 监控任务

### 配置监控项目

创建配置文件 `config/projects_monitoring.yaml`：

```yaml
monitored_projects:
  - name: "司美格鲁肽"
    keywords:
      - "Semaglutide"
      - "司美格鲁肽"
      - "Ozempic"
      - "Wegovy"
    data_sources:
      - source: "ClinicalTrials.gov"
        priority: 1
      - source: "CDE"
        priority: 2
```

### 运行监控任务

```python
from lingnexus.scheduler import DailyMonitoringTask

# 创建任务
task = DailyMonitoringTask()

# 监控所有项目
results = task.run()

# 监控特定项目
results = task.run(project_names=["司美格鲁肽"])

# 查看结果
for project_name, project_results in results.items():
    print(f"\n{project_name}:")
    for source, data in project_results.items():
        if "error" in data:
            print(f"  {source}: ❌ {data['error']}")
        else:
            print(f"  {source}: ✅ {data['count']} 条数据")
```

### 查看系统状态

```python
from lingnexus.scheduler import DailyMonitoringTask

task = DailyMonitoringTask()
status = task.get_status()

print(f"监控项目数: {status['monitored_projects_count']}")
print(f"结构化项目: {status['structured_projects']}")
print(f"向量数据库: {status['vector_db_count']} 条记录")
```

---

## 最佳实践

### 1. Skill 设计原则

**✅ 好的 Skill**：
- 单一职责，专注一个功能
- 清晰的触发关键词
- 详细的示例和使用说明
- 合理的参考文档

**❌ 避免的陷阱**：
- 功能过于宽泛
- 缺少具体示例
- 触发条件不明确
- 参考文档过大

### 2. Agent 配置建议

| 场景 | 模型选择 | 温度 | 建议 |
|------|---------|------|------|
| 事实性问答 | qwen-max | 0.1-0.3 | 低温度，准确优先 |
| 创意生成 | qwen-max | 0.7-0.9 | 高温度，多样性优先 |
| 代码生成 | deepseek-coder | 0.2-0.4 | 中低温度，逻辑性 |
| 数据分析 | qwen-plus | 0.3-0.5 | 中等温度 |

### 3. 存储层使用建议

```python
# ✅ 推荐：三层存储配合使用
from lingnexus.storage import RawStorage, StructuredDB, VectorDB

raw = RawStorage()      # 保存原始数据（HTML、JSON）
db = StructuredDB()      # 保存结构化数据（SQL 查询）
vector = VectorDB()      # 保存向量数据（语义搜索）

# ❌ 不推荐：只用一层存储
```

### 4. 错误处理

```python
from lingnexus import create_progressive_agent
from agentscope.message import Msg

agent = create_progressive_agent(model_name="qwen-max")

try:
    response = agent(Msg(name="user", content="分析数据"))
    print(response.content)
except Exception as e:
    # 记录错误
    print(f"Agent 执行失败: {e}")
    # 可以重试或使用默认响应
```

---

## 常见问题

### Q1: 如何添加自定义 Skill?

**A**: 将 Skill 放在 `skills/` 目录下：

```bash
skills/
└── my-custom-skill/
    └── SKILL.md
```

Framework 会自动发现并注册。

### Q2: Agent 如何访问外部文件?

**A**: 使用 Skill 的资源层：

```python
from lingnexus.skill import SkillLoader

loader = SkillLoader()
file_path = loader.get_skill_resource_path(
    "my-skill",
    "references/data.pdf"
)

# 现在可以使用 file_path 读取文件
```

### Q3: 如何调试 Agent 执行?

**A**: 使用日志和跟踪：

```python
import logging
from lingnexus import create_progressive_agent

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

agent = create_progressive_agent(
    model_name="qwen-max",
    debug=True,  # 启用调试模式
)
```

### Q4: 监控任务失败怎么办?

**A**: 检查以下几点：

1. **网络连接**: 确保可以访问数据源
2. **API Key**: 检查 DASHSCOPE_API_KEY 是否正确
3. **配置文件**: 检查 `projects_monitoring.yaml` 格式
4. **依赖安装**: 确保安装了可选依赖 `lingnexus-framework[monitoring]`

```bash
# 检查依赖
uv run python -c "from lingnexus.scheduler import DailyMonitoringTask; print('OK')"

# 测试数据源连接
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
```

### Q5: 如何提高 Agent 性能?

**A**: 优化建议：

1. **使用渐进式披露**：避免一次性加载所有 Skills
2. **缓存 Skill 元数据**：减少重复加载
3. **选择合适的模型**：非关键任务使用 qwen-turbo
4. **批量操作**：使用 `executemany` 而非循环

```python
# ✅ 批量操作
db.save_trials_batch([trial1, trial2, trial3])

# ❌ 循环操作
for trial in trials:
    db.save_trial(trial)
```

---

## 下一步

- [API 参考](api.md) - 完整的 API 文档
- [高级用法](advanced.md) - 渐进式披露、自定义数据源等
- [测试指南](../development/testing.md) - 如何测试你的代码

---

**需要帮助？**

- GitHub Issues: https://github.com/your-org/LingNexus/issues
- 邮箱: support@lingnexus.com
