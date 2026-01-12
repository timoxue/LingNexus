# Skills Marketplace 架构文档

## 概述

LingNexus Platform 的 Skills Marketplace 实现了完整的 Skills 闭环系统，从 Skills 定义到数据库存储，再到 Agent 执行和统计反馈，形成了一个完整的数据流。

## 完整数据流

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Skills Marketplace                             │
│                     (skills/external|internal/)                     │
│                        ┌────────────────┐                           │
│                        │  SKILL.md      │                           │
│                        │  - YAML meta   │                           │
│                        │  - Content     │                           │
│                        │  - scripts/    │                           │
│                        └────────────────┘                           │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ import_skills.py / skill_sync.py
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Database (SQLite)                            │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    skills 表                                 │    │
│  │  - id, name, category                                       │    │
│  │  - content (完整 SKILL.md，包含 YAML)                        │    │
│  │  - meta (解析后的元数据)                                     │    │
│  │  - usage_count, rating                                       │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    agents 表                                 │    │
│  │  - id, name, model_name, temperature                        │    │
│  │  - system_prompt                                            │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    agent_skills 表                           │    │
│  │  - agent_id, skill_id, enabled                              │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ agents.py (execute endpoint)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   agent_service.py                                  │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              1. 查询 Agent 绑定的 Skills                      │    │
│  │                 (完整配置: id, name, category, content)      │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              2. SkillRegistry 注册 Skills                    │    │
│  │                 - 创建临时 SKILL.md 文件                      │    │
│  │                 - Toolkit.register_agent_skill()             │    │
│  │                 - 动态加载 tools.py 工具函数                  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              3. TrackedToolkit 包装                           │    │
│  │                 - 监控 tool 调用                              │    │
│  │                 - 记录调用历史                                │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              4. 创建并执行 ReActAgent                        │    │
│  │                 - 传入 Toolkit                               │    │
│  │                 - 调用实际 tool 函数                          │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              5. 提取执行结果                                  │    │
│  │                 - used_skills (实际使用的 skills)            │    │
│  │                 - tool_calls (每个 skill 的工具调用统计)     │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ 返回 used_skills
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        数据库记录                                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              agent_executions 表                             │    │
│  │              - 记录执行状态、输出、耗时                        │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              agent_execution_skills 表                       │    │
│  │              - 记录实际使用的 skills                          │    │
│  │              - 记录每个 skill 的 tool 调用详情                │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              更新 skills.usage_count                         │    │
│  │              - 只统计实际使用的 skills                        │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Skill Registry (agent_service.py)

**作用**: 从数据库加载 Skills 并注册到 AgentScope Toolkit

**关键方法**:
- `register_skill_from_db()`: 创建临时 SKILL.md 文件并注册
- `register_tools_from_db()`: 动态加载 tools.py 中的工具函数
- `cleanup()`: 清理临时文件

**实现细节**:
```python
# 1. 创建临时目录
temp_dir = Path(tempfile.mkdtemp(prefix="lingnexus_skills_"))
skill_dir = temp_dir / category / skill_name

# 2. 写入 SKILL.md（包含完整 YAML front matter）
skill_md = skill_dir / "SKILL.md"
skill_md.write_text(skill_content, encoding='utf-8')

# 3. 注册到 AgentScope Toolkit
toolkit.register_agent_skill(skill_dir=str(skill_dir))

# 4. 动态加载工具函数
spec = importlib.util.spec_from_file_location(f"{skill_name}_tools", tools_file)
tools_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools_module)

# 5. 注册工具函数
for attr_name in dir(tools_module):
    attr = getattr(tools_module, attr_name)
    if inspect.isfunction(attr) and not attr_name.startswith('_'):
        toolkit.register_tool_function(attr)
```

### 2. TrackedToolkit (agent_service.py)

**作用**: 包装 AgentScope Toolkit 以监控 tool 调用

**关键功能**:
- 记录所有 tool 调用（name, arguments）
- 映射 tool 调用到对应的 skill
- 统计每个 skill 的工具使用次数

**实现细节**:
```python
class TrackedToolkit(Toolkit):
    def __init__(self):
        super().__init__()
        self.tool_call_history = []

    async def call_tool_function(self, tool_call: dict) -> Any:
        tool_name = tool_call.get("name", "")
        arguments = tool_call.get("arguments", {})

        # 记录调用
        self.tool_call_history.append({
            "name": tool_name,
            "arguments": arguments,
        })

        # 调用原始方法
        return await super().call_tool_function(tool_call)
```

### 3. Agent Execution API (api/v1/agents.py)

**作用**: 执行 Agent 并记录 Skills 使用情况

**关键流程**:
```python
# 1. 查询 Agent 绑定的 Skills（完整配置）
agent_skills = db.query(
    Skill.id, Skill.name, Skill.category, Skill.content
).join(
    AgentSkill, AgentSkill.skill_id == Skill.id
).filter(
    AgentSkill.agent_id == agent.id,
    AgentSkill.enabled == True,
    Skill.is_active == True
).all()

# 2. 构建技能配置列表
bound_skills = [
    {
        "id": skill_id,
        "name": skill_name,
        "category": skill_category,
        "content": skill_content,  # 完整 SKILL.md
    }
    for skill_id, skill_name, skill_category, skill_content in agent_skills
]

# 3. 调用 agent_service 执行
result = await run_agent(
    message=execute_request.message,
    skills=bound_skills,  # 传递完整配置
    ...
)

# 4. 记录实际使用的 Skills
used_skills = result.get("used_skills", {})
for skill_id, skill_data in used_skills.items():
    execution_skill = AgentExecutionSkill(
        agent_execution_id=execution.id,
        skill_id=skill_id,
        tool_calls=skill_data.get('tool_calls', {}),
        success=True,
    )
    db.add(execution_skill)

# 5. 更新使用统计
if skill["id"] in used_skills:
    skill_obj.usage_count += 1
```

## 数据库模型

### skills 表
```python
class Skill(Base):
    id: int
    name: str                      # Skill 名称
    category: str                  # external/internal
    content: str                   # 完整 SKILL.md 内容（含 YAML）
    meta: dict                     # 解析后的元数据
    usage_count: int               # 使用次数
    rating: Decimal                # 平均评分
    sharing_scope: str             # private/team/public
```

### agents 表
```python
class Agent(Base):
    id: int
    name: str
    model_name: str                # qwen-max, deepseek-chat
    temperature: Decimal
    system_prompt: str
```

### agent_skills 表
```python
class AgentSkill(Base):
    agent_id: int
    skill_id: int
    enabled: bool                  # 是否启用
```

### agent_executions 表
```python
class AgentExecution(Base):
    id: int
    agent_id: int
    input_message: str
    output_message: str
    status: str                    # pending/running/success/failed
    tokens_used: int
    execution_time: Decimal
```

### agent_execution_skills 表
```python
class AgentExecutionSkill(Base):
    id: int
    agent_execution_id: int
    skill_id: int
    tool_calls: dict               # {tool_name: call_count}
    success: bool                  # 该 skill 是否调用成功
```

## SKILL.md 格式

### 标准格式
```markdown
---
name: docx
description: Microsoft Word 文档处理技能
version: 1.0.0
author: LingNexus Team
tags: [docx, word, document]
---

# DOCX Skill

## 功能说明

此技能提供 Microsoft Word 文档的创建、编辑和格式化功能。

## 使用方法

### 创建文档
使用 `create_new_docx` 工具创建新文档。

### 编辑文档
使用 `add_paragraph` 工具添加段落。
```

### 关键要求
1. **必须包含 YAML front matter**（`---` 包围的部分）
2. **YAML 必须包含 name 和 description 字段**
3. **content 字段存储完整内容**（包括 YAML）
4. **meta 字段存储解析后的 YAML 数据**

## 工具函数实现

### tools.py 格式
```python
from agentscope.tool import ToolResponse

def create_new_docx(filename: str = "document.docx"):
    """创建一个新的空 Word 文档"""
    try:
        output_path = Path.cwd() / filename
        from docx import Document
        doc = Document()
        doc.save(output_path)
        return ToolResponse(f"成功创建空 Word 文档: {output_path}")
    except Exception as e:
        return ToolResponse(f"创建文档失败: {str(e)}", error=True)
```

### 关键要求
1. **必须返回 ToolResponse 对象**（不是字符串）
2. **使用 ToolResponse(message, error=False) 格式**
3. **函数必须有文档字符串**（用于生成工具描述）

## 统计和监控

### 使用统计
- `skills.usage_count`: 每次成功使用后递增
- 只统计实际被 Agent 调用的 skills
- 未被调用的 skills 不增加计数

### Tool 调用记录
- `agent_execution_skills.tool_calls`: 记录每个 skill 的工具调用详情
- 格式: `{"tool_name": call_count, ...}`
- 示例: `{"create_new_docx": 1, "add_paragraph": 3}`

### AgentScope Studio
- 默认启用: `http://localhost:3000`
- 可通过环境变量禁用: `AGENTSCOPE_STUDIO_ENABLED=false`
- 提供 Agent 执行可视化

## 关键实现细节

### 1. YAML Front Matter 处理
```python
# skill_sync.py 正确实现
full_content = skill_md.read_text(encoding="utf-8")

# 解析 YAML（用于 meta 字段）
meta = {}
if full_content.startswith("---"):
    parts = full_content.split("---", 2)
    if len(parts) >= 3:
        meta = yaml.safe_load(parts[1]) or {}

# 存储完整内容（包含 YAML）
existing_skill.content = full_content
existing_skill.meta = meta
```

### 2. 动态工具加载
```python
# 排除系统模块
excluded_modules = {
    'builtins', 'inspect', 'importlib', 'pathlib',
    'typing', 'io', 'zipfile', 'json', 'logging'
}

for attr_name in dir(tools_module):
    attr = getattr(tools_module, attr_name)
    if inspect.isfunction(attr) and not attr_name.startswith('_'):
        attr_module = getattr(attr, '__module__', None)
        # 只注册自定义函数
        if attr_module and attr_module not in excluded_modules:
            toolkit.register_tool_function(attr)
```

### 3. Tool Call 映射
```python
# 将 tool calls 映射到 skills
used_skills = {}
for call in tool_call_history:
    tool_name = call['name']

    # 遍历所有绑定的 skills
    for skill in skills:
        skill_id = skill['id']
        if skill_id not in used_skills:
            used_skills[skill_id] = {'tool_calls': {}}

        # 统计调用次数
        if tool_name not in used_skills[skill_id]['tool_calls']:
            used_skills[skill_id]['tool_calls'][tool_name] = 0
        used_skills[skill_id]['tool_calls'][tool_name] += 1
```

## 性能优化

### 1. 临时文件管理
- 使用 `tempfile.mkdtemp()` 创建临时目录
- Agent 执行完成后自动清理
- 避免污染文件系统

### 2. 模块缓存
- 动态加载的工具模块会被 Python 缓存
- 避免重复加载相同的工具
- 提高执行效率

### 3. 数据库查询优化
- 使用 JOIN 一次查询获取完整 skill 配置
- 避免 N+1 查询问题
- 减少数据库访问次数

## 调试和监控

### 日志级别
- `INFO`: 关键操作（注册 skills、执行 agent、更新统计）
- `DEBUG`: 详细信息（tool 调用参数、skill 细节）
- `WARNING`: 可恢复的错误（工具注册失败）
- `ERROR`: 严重错误（agent 执行失败）

### 监控端点
- `GET /api/v1/agents/{id}/executions`: 查询执行历史
- `GET /api/v1/agents/{id}/executions/{execution_id}`: 查询单次执行详情
- 返回 `agent_execution_skills` 关联数据

## 常见问题

### Q: 为什么 Agent 没有调用 Skills？
A: 检查以下几点：
1. skills 是否在数据库中标记为 `is_active=True`
2. agent_skills 表中 `enabled=True`
3. SKILL.md 格式是否正确（包含 YAML）
4. tools.py 中的函数是否返回 `ToolResponse`

### Q: 为什么 usage_count 没有更新？
A: 只有在 Agent **实际调用**了 skill 的工具函数时才会更新：
- 检查 `agent_execution_skills` 表是否有记录
- 检查 `tool_calls` 是否有数据
- Agent 可能只是"知道"这个 skill 但没有使用

### Q: 如何查看 Agent 执行过程？
A: 有三种方式：
1. AgentScope Studio: http://localhost:3000
2. 日志输出: 查看后端日志（TOOL_CALL 信息）
3. 数据库: 查询 `agent_execution_skills` 表

## 最佳实践

### 1. Skill 开发
- 使用标准 SKILL.md 格式
- 提供清晰的工具文档字符串
- 返回 ToolResponse 而不是字符串
- 处理异常并返回有意义的错误信息

### 2. Agent 配置
- 只绑定必要的 skills
- 设置合适的 temperature（0.3-0.7 用于生产）
- 提供明确的 system_prompt

### 3. 监控和分析
- 定期检查 usage_count 统计
- 分析 tool_calls 模式
- 优化低效的 skills

## 总结

LingNexus Skills Marketplace 实现了完整的闭环系统：

1. **定义**: Skills Marketplace 中的 SKILL.md 文件
2. **存储**: 数据库 skills 表（完整内容 + 元数据）
3. **绑定**: Agent 通过 agent_skills 表关联 skills
4. **加载**: agent_service.py 从数据库动态加载
5. **执行**: ReActAgent 调用实际工具函数
6. **追踪**: TrackedToolkit 记录 tool 调用
7. **统计**: 更新 usage_count 和 execution 记录

这个架构确保了 Skills 的可管理性、可追踪性和可优化性。
