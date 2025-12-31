# Skill 集成指南

## 概述

LingNexus 支持集成 Claude Skills，可以直接使用 Claude 格式的 Skills 而无需修改。

## Claude Skills 兼容性

### 兼容性说明

LingNexus 与 Claude Skills **高度兼容**：

- ✅ **相同的文件结构**：`SKILL.md`, `scripts/`, `references/`, `assets/`
- ✅ **相同的元数据格式**：YAML front matter（`name`, `description`）
- ✅ **相同的设计理念**：Progressive Disclosure（渐进式披露）
- ✅ **可以直接使用**：无需修改 Claude Skills 的格式

### 目录结构

```
skills/
├── external/          # Claude 格式的 Skills
│   ├── docx/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── references/
│   │   └── assets/
│   └── ...
└── internal/          # 自主开发的 Skills
    └── ...
```

## Skill 注册

### 自动注册

使用 `load_claude_skills.py` 脚本自动发现并注册 Skills：

```bash
# 生成注册代码
uv run python scripts/load_claude_skills.py

# 这会生成 scripts/register_skills.py
```

### 手动注册

```python
from lingnexus.utils import SkillLoader

loader = SkillLoader()
loader.register_skill("docx", skill_type="external")
```

### 批量注册

```python
from lingnexus.utils import SkillLoader

loader = SkillLoader()
loader.register_skills(["docx", "pdf", "pptx"], skill_type="external")
```

## Skill 使用

### 方式 1: 传统方式（一次性加载）

Skills 会在创建 Agent 时自动加载：

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

# docx 技能会自动注册，完整指令会添加到系统提示词
agent = create_docx_agent(model_type=ModelType.QWEN)
```

**特点**：
- ✅ 简单直接，适合少量 Skills
- ⚠️ 所有 Skills 的完整指令都会加载到系统提示词
- ⚠️ Token 消耗较大，不适合大量 Skills

### 方式 2: 渐进式披露（推荐）

使用 `create_progressive_agent` 实现 Claude Skills 的渐进式披露机制：

```python
from lingnexus.agent import create_progressive_agent
import asyncio
from agentscope.message import Msg

# 创建支持渐进式披露的 Agent（使用 qwen-max 作为 orchestrator）
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,  # orchestrator 使用较低温度
)

# 使用 Agent
async def main():
    user_msg = Msg(
        name="user",
        role="user",
        content="请创建一个 Word 文档"
    )
    # Agent 会自动按需加载 docx 技能的完整指令
    response = await agent(user_msg)
    print(response.content)

asyncio.run(main())
```

**工作流程（完整的三层渐进式披露）**：

1. **阶段1：元数据层（初始化）** - 只加载所有 Skills 的元数据（~100 tokens/Skill）
   ```
   可用技能列表：
   - docx: "处理 Word 文档的技能"
   - pdf: "处理 PDF 文档的技能"
   - ...
   ```

2. **阶段2：指令层（按需加载）** - LLM 判断需要时，调用 `load_skill_instructions` 工具加载完整指令（~5k tokens）
   ```
   Agent 判断：需要 docx 技能
   → 调用 load_skill_instructions("docx")
   → 加载完整的 SKILL.md 内容
   ```

3. **阶段3：资源层（按需加载）** - 根据指令需要，加载参考文档和访问资源
   ```
   如果 SKILL.md 中引用了参考文档（如 docx-js.md, ooxml.md）
   → 调用 load_skill_reference("docx", "docx-js.md")
   → 加载参考文档内容
   
   如果需要访问 scripts/ 或 assets/ 目录
   → 调用 get_skill_resource_path("docx", "scripts")
   → 获取资源路径，通过文件系统访问
   ```

4. **阶段4：执行任务** - 根据完整指令、参考文档和资源规划并执行任务

**优势**：
- ✅ Token 效率高：初始只加载元数据（~100 tokens/Skill）
- ✅ 可扩展性强：支持大量 Skills，不会 token 爆炸
- ✅ 符合 Claude Skills 设计理念：完整实现三层渐进式披露
- ✅ 智能按需加载：只在需要时加载完整指令和参考文档
- ✅ 资源访问灵活：支持按需访问 references/, assets/, scripts/ 目录

**适用场景**：
- 大量 Skills（10+ 个）
- Token 预算有限
- 需要智能选择 Skills 的场景

### 技能提示词

传统方式会自动获取技能提示词并添加到系统提示词：

```python
from lingnexus.utils import SkillLoader

loader = SkillLoader()
loader.register_skill("docx", skill_type="external")
prompt = loader.get_skill_prompt()  # 获取技能提示词
```

渐进式披露方式通过工具动态加载：

```python
# Agent 会自动调用 load_skill_instructions 工具
# 无需手动获取提示词
```

## Skill 结构

### SKILL.md 格式

```markdown
---
name: docx
description: 处理 Word 文档的技能
---

# docx Skill

技能描述...

## 使用方法

...
```

### scripts/ 目录

包含技能的可执行脚本：

```python
# scripts/document.py
from docx import Document

def create_document(filename, content):
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)
```

## 创建自定义 Skill

### 1. 创建目录结构

```
skills/internal/my_skill/
├── SKILL.md
├── scripts/
│   └── my_script.py
├── references/
└── assets/
```

### 2. 编写 SKILL.md

```markdown
---
name: my-skill
description: 我的自定义技能
---

# My Skill

技能描述...
```

### 3. 注册 Skill

```python
from lingnexus.utils import SkillLoader

loader = SkillLoader()
loader.register_skill("my_skill", skill_type="internal")
```

## 渐进式披露详解

### Claude Skills 工作流程

根据 Claude Skills 的设计，**LLM 的调用发生在使用 Skill 之前**。流程如下：

#### 渐进式披露（Progressive Disclosure）

Claude Skills 采用三层加载架构：

```
1. 元数据层（初始化时）
   ↓ LLM 调用 #1：判断是否需要使用 Skill
2. 指令层（判断需要时加载）
   ↓ LLM 调用 #2：根据指令规划如何使用 Skill
3. 资源层（按需加载）
   ↓ 执行脚本/工具
```

#### 详细流程

**阶段 1: 元数据加载（初始化）**

```python
# 初始化时，只加载元数据（约 100 tokens）
skill_metadata = {
    "name": "docx",
    "description": "处理 Word 文档的技能"
}
```

此时 LLM 还未调用。

**阶段 2: LLM 判断是否需要 Skill（第一次 LLM 调用）**

```
用户请求："请创建一个 Word 文档"
    ↓
LLM 调用 #1（看到所有 Skills 的元数据）
    ↓
LLM 分析：需要 docx 技能
    ↓
加载 docx 技能的完整指令（SKILL.md 内容）
```

**阶段 3: LLM 规划如何使用 Skill（第二次 LLM 调用）**

```
LLM 调用 #2（看到 docx 技能的完整指令）
    ↓
LLM 分析：SKILL.md 中引用了 docx-js.md 和 ooxml.md
    ↓
按需加载参考文档（如果指令中引用了）
    ↓
LLM 规划：根据 SKILL.md 和参考文档的说明，生成代码
    ↓
生成 Python 代码（使用 python-docx 库）
```

**阶段 4: 资源访问（按需）**

```
如果需要参考文档：
    ↓
调用 load_skill_reference("docx", "docx-js.md")
    ↓
加载参考文档内容到 context

如果需要访问 scripts/ 或 assets/：
    ↓
调用 get_skill_resource_path("docx", "scripts")
    ↓
获取资源路径，通过文件系统访问
```

**阶段 5: 执行脚本（非 LLM 调用）**

```
执行生成的代码
    ↓
访问 scripts/ 目录中的脚本
    ↓
创建 .docx 文件
    ↓
返回结果
```

#### 关键点

1. **LLM 调用在使用 Skill 之前**
   - 第一次调用：判断是否需要使用 Skill（基于元数据）
   - 第二次调用：规划如何使用 Skill（基于完整指令）
   - 可能多次调用：按需加载参考文档

2. **资源层的按需加载**
   - **References**：参考文档按需加载到 context（如 docx-js.md, ooxml.md）
   - **Assets**：资源文件通过文件系统访问，不加载到 context
   - **Scripts**：可执行脚本通过文件系统访问或执行

3. **Skill 脚本的执行在 LLM 调用之后**
   - LLM 生成代码
   - 然后执行代码（不是 LLM 调用）

### 实现原理

渐进式披露通过以下组件实现：

1. **SkillLoader** - 扩展了元数据加载方法
   - `load_skill_metadata_only()` - 只加载元数据
   - `load_all_skills_metadata()` - 扫描所有 Skills 的元数据
   - `load_skill_full_instructions()` - 加载完整指令
   - `get_skills_metadata_prompt()` - 生成元数据提示词

2. **渐进式加载工具** - `SkillLoader` 类中的工具方法
   - **阶段1（元数据层）**：
     - `_tool_list_available_skills()` - 列出所有可用技能的元数据
   - **阶段2（指令层）**：
     - `_tool_load_skill_instructions()` - 动态加载完整指令（SKILL.md）
   - **阶段3（资源层）**：
     - `_tool_load_skill_reference()` - 加载参考文档（references/ 或根目录的 .md 文件）
     - `_tool_list_skill_resources()` - 列出技能的所有资源
     - `_tool_get_skill_resource_path()` - 获取资源路径（用于文件系统访问）

3. **Progressive Agent** - `create_progressive_agent()`
   - 使用 qwen-max 作为 orchestrator
   - 初始只加载元数据到系统提示词
   - 通过工具实现动态加载（指令层 + 资源层）

### 资源层工具使用示例

**加载参考文档**：

```python
# Agent 会自动调用
load_skill_reference("docx", "docx-js.md")  # 加载 docx-js.md
load_skill_reference("docx", "ooxml.md")    # 加载 ooxml.md
```

**列出技能资源**：

```python
# Agent 会自动调用
list_skill_resources("docx")  # 列出所有资源（references, assets, scripts）
```

**获取资源路径**：

```python
# Agent 会自动调用
get_skill_resource_path("docx", "scripts")   # 获取 scripts/ 目录路径
get_skill_resource_path("docx", "assets")    # 获取 assets/ 目录路径
get_skill_resource_path("docx", "references")  # 获取 references/ 目录路径
```

### 使用示例

完整示例请查看 `examples/progressive_agent_example.py`：

```python
import asyncio
from agentscope.message import Msg
from lingnexus.agent import create_progressive_agent
from lingnexus.config import init_agentscope

async def main():
    # 初始化 AgentScope
    init_agentscope()
    
    # 创建渐进式披露 Agent
    agent = create_progressive_agent(
        model_name="qwen-max",
        temperature=0.3,
    )
    
    # 用户请求
    user_msg = Msg(
        name="user",
        role="user",
        content="请创建一个 Word 文档，内容是关于 Python 编程的简介"
    )
    
    # Agent 会自动按需加载 docx 技能的完整指令
    response = await agent(user_msg)
    print(response.content)

if __name__ == "__main__":
    asyncio.run(main())
```

## 相关文档

- [Claude Skills 兼容性说明](claude_skills_compatibility.md)
- [架构设计](architecture.md)
- [测试指南](testing.md)

