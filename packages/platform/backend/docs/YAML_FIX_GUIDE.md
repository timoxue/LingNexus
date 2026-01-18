# Skills YAML Front Matter 修复指南

## 问题描述

在 Skills Marketplace 执行 Agent 时，某些 skills 可能出现以下错误：

```
ERROR:services.agent_service:Failed to register skill 'js-checker':
The SKILL.md file must have a YAML Front Matter including `name` and `description` fields.
```

## 根本原因

数据库中存储的 skill **content** 字段可能缺少 YAML Front Matter。这通常发生在以下情况：

1. **旧版本导入**：Skills 是在修复 YAML 处理逻辑之前导入的
2. **编码问题**：文件读取时未使用 UTF-8 编码
3. **手动导入**：使用不正确的脚本或方法导入

### YAML Front Matter 格式

正确的 SKILL.md 文件格式：

```markdown
---
name: js-checker
description: "JavaScript 代码检查工具"
version: 1.0.0
author: LingNexus Team
tags: [javascript, code-checker]
---

# JavaScript 代码检查工具

## 功能说明

...
```

**关键点**：
- 必须以 `---` 开头
- 第一段 YAML 内容后必须以 `---` 结束
- 必须包含 `name` 和 `description` 字段
- 数据库 `content` 字段必须存储**完整内容**（包括 YAML）

## 解决方案

### 方案 1：使用修复脚本（推荐）

运行批量修复脚本：

```bash
cd packages/platform/backend
uv run python scripts/fix_skills_yaml.py
```

**脚本功能**：
- 扫描所有数据库中的 skills
- 从 Framework 读取原始 SKILL.md 文件
- 更新数据库以包含完整的 YAML front matter
- 显示修复统计信息

**输出示例**：
```
============================================================
Fix Skills YAML Front Matter
============================================================

[FIXED] algorithmic-art (external)
[FIXED] docx (external)
[FIXED] js-checker (internal)

=== Statistics ===
Total skills: 45
Fixed: 16
Skipped: 21
Errors: 8
```

### 方案 2：手动同步 Skills

使用 Platform API 重新同步：

```bash
# 启动后端
cd packages/platform/backend
uv run uvicorn main:app --reload

# 调用同步 API（强制更新）
curl -X POST http://localhost:8000/api/v1/skills/sync?force_update=true \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 方案 3：使用 skill_sync.py

直接同步服务：

```python
from services.skill_sync import SkillSyncService
from db.session import SessionLocal
from pathlib import Path

# 初始化服务
framework_path = Path("path/to/framework")
sync_service = SkillSyncService(framework_path)

# 同步数据库
db = SessionLocal()
result = sync_service.sync_all_skills(
    db=db,
    created_by=1,
    force_update=True  # 强制更新所有 skills
)

print(result)
# {'total': 45, 'created': 0, 'updated': 45, 'skipped': 0, 'failed': 0}

db.close()
```

## 验证修复

### 检查单个 Skill

```python
from db.session import SessionLocal
from db.models import Skill

db = SessionLocal()
skill = db.query(Skill).filter(Skill.name == 'js-checker').first()

if skill:
    # 检查是否以 --- 开头
    has_yaml = skill.content.startswith('---')
    print(f'Has YAML: {has_yaml}')

    # 检查前几行
    lines = skill.content.split('\n')
    print(f'Line 1: {lines[0]}')
    print(f'Line 2: {lines[1]}')
    print(f'Line 3: {lines[2]}')

db.close()
```

**期望输出**：
```
Has YAML: True
Line 1: ---
Line 2: name: js-checker
Line 3: description: "JavaScript 代码检查工具"
```

### 测试 Agent 执行

1. 创建一个绑定多个 skills 的 Agent
2. 执行 Agent
3. 检查日志中是否还有错误

```bash
# 执行 Agent
curl -X POST http://localhost:8000/api/v1/agents/1/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "创建一个 Word 文档"}'

# 检查后端日志，应该看到：
# INFO:services.agent_service:Successfully loaded 3/3 skills
```

## 预防措施

### 1. 使用正确的同步方法

**推荐**：使用 `skill_sync.py` 服务而不是 `import_skills.py`

```python
# ✅ 推荐：使用 SkillSyncService
from services.skill_sync import SkillSyncService

sync_service = SkillSyncService(framework_path)
result = sync_service.sync_all_skills(db, force_update=False)
```

**不推荐**：直接使用 `import_skills.py`（它会创建新数据库）

### 2. 确保文件编码正确

所有 SKILL.md 文件必须使用 **UTF-8** 编码：

```python
# ✅ 正确：指定 UTF-8 编码
content = skill_md.read_text(encoding="utf-8")

# ❌ 错误：使用系统默认编码
content = skill_md.read_text()
```

### 3. 验证 YAML Front Matter

在导入前验证文件格式：

```python
def validate_skill_md(file_path: Path) -> bool:
    """验证 SKILL.md 格式是否正确"""
    content = file_path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    # 检查必需字段
    import yaml
    try:
        meta = yaml.safe_load(parts[1])
        if not meta or 'name' not in meta or 'description' not in meta:
            return False
    except:
        return False

    return True
```

### 4. 添加容错处理

在 `agent_service.py` 中添加容错处理（已实现）：

```python
# 注册 SKILL.md（容错处理）
skill_registered = self.skill_registry.register_skill_from_db(
    skill_name=skill_name,
    skill_content=skill_content,
    skill_category=skill_category,
    toolkit=toolkit,
)

if not skill_registered:
    logger.warning(f"Failed to register skill '{skill_name}', skipping...")
    continue  # 跳过此 skill，继续处理其他 skills
```

## 常见问题

### Q1: 为什么 Windows 控制台显示乱码？

**原因**：Windows 控制台默认使用 GBK 编码，而数据库使用 UTF-8。

**解决方案**：
1. 设置环境变量：`set PYTHONIOENCODING=utf-8`
2. 使用支持 UTF-8 的终端（如 Windows Terminal）
3. 这只是显示问题，不影响数据库存储

### Q2: 修复后仍有错误？

**检查清单**：
1. 确认 Framework 路径正确
2. 确认原始 SKILL.md 文件存在且有 YAML
3. 检查文件编码是否为 UTF-8
4. 查看后端日志获取详细错误信息

### Q3: 某些 skills 原始文件不存在？

**原因**：可能是测试数据或已删除的 skills。

**解决方案**：
1. 检查 `packages/framework/skills/` 目录
2. 从数据库删除不存在的 skills
3. 或者从 Framework 恢复这些 skills

## 数据库查询

### 查找缺少 YAML 的 Skills

```sql
SELECT name, category, LENGTH(content) as content_length
FROM skills
WHERE content NOT LIKE '---%'
ORDER BY name;
```

### 统计 Skills 数量

```sql
SELECT
    category,
    COUNT(*) as total,
    SUM(CASE WHEN content LIKE '---%' THEN 1 ELSE 0 END) as has_yaml,
    SUM(CASE WHEN content NOT LIKE '---%' THEN 1 ELSE 0 END) as missing_yaml
FROM skills
GROUP BY category;
```

## 总结

**修复流程**：
1. 运行 `fix_skills_yaml.py` 批量修复
2. 验证修复结果
3. 测试 Agent 执行
4. 监控后端日志

**预防措施**：
1. 使用 `SkillSyncService` 而不是直接导入
2. 始终使用 UTF-8 编码
3. 添加文件格式验证
4. 使用容错处理

**相关文件**：
- `services/skill_sync.py` - Skills 同步服务
- `services/agent_service.py` - Agent 执行服务（含容错）
- `scripts/fix_skills_yaml.py` - 批量修复脚本
- `scripts/import_skills.py` - 初始导入脚本

**相关文档**：
- `SKILL_ARCHITECTURE.md` - Skills 架构文档
- `CLAUDE.md` - 项目主文档
