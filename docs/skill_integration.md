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

### 在 Agent 中使用

Skills 会在创建 Agent 时自动加载：

```python
from lingnexus.agent import create_docx_agent

# docx 技能会自动注册
agent = create_docx_agent(model_type=ModelType.QWEN)
```

### 技能提示词

Agent 会自动获取技能提示词并添加到系统提示词中：

```python
from lingnexus.utils import SkillLoader

loader = SkillLoader()
loader.register_skill("docx", skill_type="external")
prompt = loader.get_skill_prompt()  # 获取技能提示词
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

## 相关文档

- [Claude Skills 兼容性说明](claude_skills_compatibility.md)
- [架构设计](architecture.md)
- [测试指南](testing.md)

