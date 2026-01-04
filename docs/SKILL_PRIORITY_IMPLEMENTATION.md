# Skill 优先级机制实现总结

## 实现时间
2026-01-04

## 问题背景

Agent 使用 docx 技能时生成的代码有错误：
- 使用 `\n` 字符串尝试换行
- 在 docx 库中，`\n` **不会**转换为换行
- 需要使用多个 `Paragraph` 对象或 `break` 属性

**问题**：不能修改 `external/` 下的任何文件（Claude Skills 原始文件）

## 解决方案

### 设计思路

实现一个 **override（覆盖）机制**：
```
优先级：internal/ > external/
```

### 工作流程

```
用户请求使用 docx 技能
    ↓
SkillLoader 检查 internal/docx/ 是否存在
    ↓
    ├─ 存在 → 使用 internal/docx/（优先级高）
    │
    └─ 不存在 → 使用 external/docx/（fallback）
```

## 实现内容

### 1. 拷贝技能到 internal

```bash
cp -r skills/external/docx skills/internal/docx
```

**文件结构**：
```
skills/
├── external/
│   └── docx/
│       ├── SKILL.md
│       ├── docx-js.md
│       └── ooxml.md
└── internal/
    └── docx/              # 覆盖版本
        ├── SKILL.md       # 已修改
        ├── docx-js.md
        └── ooxml.md
```

### 2. 修改 internal/docx/SKILL.md

添加了显眼的换行规则警告：

```markdown
### ⚠️ CRITICAL: LINE BREAK RULES

**NEVER use `\n` for line breaks in docx-js! It will NOT work!**

❌ **WRONG** - This will NOT create line breaks:
```javascript
new Paragraph({
  children: [
    new TextRun("Line 1\nLine 2\nLine 3"),  // ❌ \n does NOT work!
  ]
})
```

✅ **CORRECT Method 1** - Use separate Paragraph objects (RECOMMENDED):
```javascript
new Paragraph({ children: [new TextRun("Line 1")] }),
new Paragraph({ children: [new TextRun("Line 2")] }),
new Paragraph({ children: [new TextRun("Line 3")] })
```

✅ **CORRECT Method 2** - Use TextRun's `break` property:
```javascript
new Paragraph({
  children: [
    new TextRun("Line 1"),
    new TextRun({ text: "", break: 1 }),  // Line break
    new TextRun("Line 2"),
    new TextRun({ text: "", break: 1 }),  // Line break
    new TextRun("Line 3")
  ]
})
```
```

### 3. 修改 skill_loader.py

#### 添加优先级检查方法

```python
def _resolve_skill_type(self, skill_name: str, skill_type: str = "external") -> str:
    """
    解析技能类型（优先级检查：internal > external）
    """
    if skill_type == "internal":
        return "internal"

    # 检查 internal 目录是否存在该技能
    internal_path = self.skills_base_dir / "internal" / skill_name
    if internal_path.exists() and (internal_path / "SKILL.md").exists():
        return "internal"

    return skill_type  # 默认返回 external
```

#### 修改关键方法

所有技能加载方法都添加了优先级检查：
- `load_skill()`
- `load_skill_metadata_only()`
- `load_skill_full_instructions()`
- `_tool_load_skill_instructions()`

修改示例：
```python
def load_skill_metadata_only(self, skill_name: str, skill_type: str = "external") -> Dict:
    # 解析技能类型（internal 优先）
    skill_type = self._resolve_skill_type(skill_name, skill_type)
    # ... 继续处理
```

### 4. 创建文档和测试

**文档**：
- `docs/skill_priority_mechanism.md` - 优先级机制完整说明
- `docs/docx_line_break_guide.md` - docx 换行问题指南

**测试**：
- `tests/test_skill_priority.py` - 优先级机制测试

## 测试结果

### 所有测试通过 ✅

```
✅ 所有测试通过！

优先级机制正常工作：
  1. ✅ internal/ 优先级高于 external/
  2. ✅ 自动检查并使用 internal 版本
  3. ✅ docx 技能的修改已生效
  4. ✅ 两个版本的文件都存在（可以对比）
```

### 验证点

1. **优先级检查**：
   - `load_skill_metadata_only("docx")` → 返回 `skills/internal/docx`
   - `_resolve_skill_type("docx", "external")` → 返回 `"internal"`

2. **内容验证**：
   - internal/docx/SKILL.md 包含 `"CRITICAL: LINE BREAK RULES"`
   - 修改已生效

3. **文件存在性**：
   - ✅ internal/docx/SKILL.md 存在
   - ✅ external/docx/SKILL.md 存在（保持不变）

## 优势

### 1. **不修改原始文件**
- ✅ external/ 保持原样
- ✅ 方便更新上游技能
- ✅ 可以对比差异

### 2. **自动化优先级**
- ✅ 无需修改调用代码
- ✅ 自动检查并使用 internal 版本
- ✅ 向后兼容

### 3. **项目特定定制**
- ✅ 每个项目可以有独立的定制
- ✅ 不影响其他项目
- ✅ 易于维护

### 4. **渐进式迁移**
- ✅ 可以逐步迁移到 internal
- ✅ 不需要一次性复制所有技能
- ✅ 按需覆盖

## 使用建议

### 何时使用 internal 技能？

1. **修复上游 bug**（如本次 docx 换行问题）
2. **添加项目特定的规则和示例**
3. **定制技能行为以适应项目需求**
4. **添加项目特定的参考文档**

### 最佳实践

✅ **DO**：
- 只覆盖需要修改的技能
- 保持 SKILL.md 结构一致
- 在 SKILL.md 顶部添加修改说明
- 定期同步 upstream 更新

❌ **DON'T**：
- 不要修改 external/ 下的任何文件
- 不要覆盖不需要修改的技能
- 不要破坏 SKILL.md 的基本结构

## 当前状态

### 已实现的技能覆盖

1. **docx** - 已覆盖
   - 添加了显眼的换行规则警告
   - 路径：`skills/internal/docx/`

### 项目特定技能

1. **js-checker** - 内部技能
   - JavaScript 代码检查和修复
   - 路径：`skills/internal/js-checker/`

## 总结

成功实现了一个优雅的 **Skill 优先级机制**，解决了不能修改 external 文件的限制，同时允许项目定制技能行为。

**关键成果**：
1. ✅ 实现了 internal > external 的优先级机制
2. ✅ 修复了 docx 换行问题
3. ✅ 所有测试通过
4. ✅ 完整的文档和示例
5. ✅ 不破坏原有代码，向后兼容

**下一步**：
- 当 Agent 使用 docx 技能时，会自动看到换行规则警告
- Agent 应该生成正确的代码（使用多个 Paragraph 或 break）
- 如果仍有问题，可以进一步优化 internal/docx/SKILL.md 的说明

## 文件变更

### 新增文件
- `skills/internal/docx/` - docx 技能覆盖版本
- `docs/skill_priority_mechanism.md` - 优先级机制文档
- `tests/test_skill_priority.py` - 优先级测试

### 修改文件
- `lingnexus/utils/skill_loader.py` - 添加优先级检查逻辑
- `skills/internal/docx/SKILL.md` - 添加换行规则警告

### 保持不变
- `skills/external/` - 完全未修改
