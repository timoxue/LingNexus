# Skill 优先级加载机制

## 概述

LingNexus 支持自定义技能覆盖机制，允许项目覆盖外部技能，以适应当前项目的特殊需求。

## 优先级规则

```
优先级从高到低：
1. internal/  (项目自定义技能)
2. external/  (外部 Claude Skills)
```

## 工作原理

### 自动优先级检查

当加载技能时，系统会自动检查：

1. **如果 `internal/` 下存在同名技能** → 使用 `internal/` 版本
2. **否则** → 使用 `external/` 版本

### 示例

```
skills/
├── external/
│   └── docx/          # 原始 docx skill
│       └── SKILL.md
└── internal/
    └── docx/          # 覆盖版本（优先级高）
        └── SKILL.md
```

当调用 `load_skill("docx")` 时：
- ✅ 自动使用 `skills/internal/docx/`（优先级高）
- ❌ 不使用 `skills/external/docx/`

## 使用场景

### 场景 1：修复技能问题

**问题**：Agent 使用 docx 技能时生成的代码有错误（使用 `\n` 换行）

**解决方案**：
1. 拷贝 `external/docx/` 到 `internal/docx/`
2. 修改 `internal/docx/SKILL.md`，添加显眼的换行规则警告
3. Agent 会自动使用修改后的版本

```bash
# 1. 拷贝技能
cp -r skills/external/docx skills/internal/docx

# 2. 修改 SKILL.md，添加关键规则
# 编辑 skills/internal/docx/SKILL.md

# 3. 完成！Agent 会自动使用新版本
```

### 场景 2：定制技能行为

**需求**：项目需要修改某个技能的默认行为

**解决方案**：
1. 拷贝技能到 `internal/`
2. 根据项目需求修改 SKILL.md
3. 不影响 `external/` 原始技能

### 场景 3：添加项目特定的示例

**需求**：为项目添加特定的使用示例

**解决方案**：
1. 在 `internal/skill-name/` 添加项目特定的示例
2. Agent 会看到项目特定的示例和说明

## 实现细节

### SkillLoader 优先级检查

```python
def _resolve_skill_type(self, skill_name: str, skill_type: str = "external") -> str:
    """
    解析技能类型（优先级检查：internal > external）

    如果指定了 skill_type，直接使用。
    如果 skill_type 为 "external" 或未指定，会先检查 internal 目录是否存在该技能。
    """
    if skill_type == "internal":
        return "internal"

    # 检查 internal 目录是否存在该技能
    internal_path = self.skills_base_dir / "internal" / skill_name
    if internal_path.exists() and (internal_path / "SKILL.md").exists():
        return "internal"

    return skill_type  # 默认返回 external
```

### 使用方法

所有技能加载方法都自动支持优先级：

```python
from lingnexus.utils.skill_loader import SkillLoader

loader = SkillLoader()

# 自动使用 internal 优先
metadata = loader.load_skill_metadata_only("docx", skill_type="external")
# 如果 internal/docx 存在，会自动使用它

# 加载完整指令
instructions = loader.load_skill_full_instructions("docx")
# 同样会优先使用 internal 版本
```

## 优势

### 1. **不修改原始文件**
- ✅ `external/` 保持原样
- ✅ 方便更新上游技能
- ✅ 可以对比差异

### 2. **项目特定定制**
- ✅ 每个项目可以有独立的定制
- ✅ 不影响其他项目
- ✅ 易于维护

### 3. **向后兼容**
- ✅ 不破坏现有代码
- ✅ 无需修改调用方式
- ✅ 自动优先级检查

### 4. **渐进式迁移**
- ✅ 可以逐步迁移到 internal
- ✅ 不需要一次性复制所有技能
- ✅ 按需覆盖

## 最佳实践

### DO ✅

1. **只覆盖需要修改的技能**
   ```
   internal/
   ├── docx/          # 需要修改
   └── pdf/           # 需要修改
   ```

2. **保持 SKILL.md 结构一致**
   - 保留 YAML front matter
   - 保留主要章节结构
   - 只修改需要的内容

3. **在 SKILL.md 顶部添加修改说明**
   ```markdown
   ---
   name: docx
   description: "..."
   ---

   # 项目定制版本

   **修改说明**：
   - 添加了显眼的换行规则警告（2026-01-04）
   - 原始版本：external/docx/SKILL.md
   ```

4. **定期同步更新**
   ```bash
   # 定期检查上游是否有更新
   diff -r skills/external/docx skills/internal/docx
   ```

### DON'T ❌

1. **不要修改 external/ 下的任何文件**
   - external/ 应该保持只读
   - 所有修改都在 internal/ 进行

2. **不要覆盖不需要修改的技能**
   - 只复制需要修改的技能
   - 保持 internal/ 目录精简

3. **不要破坏 SKILL.md 的基本结构**
   - 必须保留 YAML front matter
   - 必须有 name 和 description 字段

## 当前实现

### 已覆盖的技能

当前项目已经覆盖以下技能：

1. **docx**
   - 路径：`skills/internal/docx/`
   - 修改：添加了显眼的换行规则警告
   - 原因：Agent 生成的代码经常错误使用 `\n` 换行

### 内部技能

项目特定的内部技能：

1. **js-checker**
   - 路径：`skills/internal/js-checker/`
   - 用途：JavaScript 代码检查和修复

## 文件结构

```
skills/
├── external/          # 外部 Claude Skills（不要修改）
│   ├── docx/
│   ├── pdf/
│   ├── pptx/
│   └── ...
│
└── internal/          # 项目自定义技能（优先级高）
    ├── docx/          # 覆盖 external/docx
    │   ├── SKILL.md   # 修改后的技能文件
    │   ├── docx-js.md
    │   └── ooxml.md
    └── js-checker/    # 项目特定技能
        └── scripts/
```

## 总结

Skill 优先级机制提供了一种优雅的方式来定制和修复技能，而不需要修改原始的 external 文件。

**关键要点**：
1. ✅ `internal/` 优先级高于 `external/`
2. ✅ 自动检查，无需修改代码
3. ✅ 只覆盖需要修改的技能
4. ✅ 保持 external/ 不变

这个机制特别适合：
- 修复上游技能的 bug
- 添加项目特定的规则和示例
- 定制技能行为以适应项目需求
