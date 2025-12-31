# Claude Skills 与 AgentScope AgentSkill 兼容性分析

## 设计理念对比

### Claude Skills 设计理念
1. **渐进式披露（Progressive Disclosure）**：三层加载架构
   - **元数据层**（约 100 tokens/Skill）：name + description
   - **指令层**（< 5k tokens）：SKILL.md 完整内容
   - **资源层**（按需加载）：
     - **References**：参考文档（references/ 目录或根目录的 .md 文件）
     - **Assets**：资源文件（assets/ 目录，不加载到 context）
     - **Scripts**：可执行脚本（scripts/ 目录，通过文件系统访问）

2. **模块化设计**：每个 Skill 独立封装特定功能
3. **跨平台可移植性**：可在不同平台间无缝工作

### Claude Skills 工作流程

根据 Claude Skills 的设计，**LLM 的调用发生在使用 Skill 之前**。流程如下：

#### 渐进式披露（Progressive Disclosure）

Claude Skills 采用三层加载架构：

```
1. 元数据层（初始化时，~100 tokens/Skill）
   ↓ LLM 调用 #1：判断是否需要使用 Skill
2. 指令层（判断需要时加载，~5k tokens）
   ↓ LLM 调用 #2：根据指令规划如何使用 Skill
3. 资源层（按需加载）
   ├── References：参考文档（按需加载到 context）
   ├── Assets：资源文件（通过文件系统访问）
   └── Scripts：可执行脚本（通过文件系统访问或执行）
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
LLM 规划：根据 SKILL.md 的说明，生成代码
    ↓
生成 Python 代码（使用 python-docx 库）
```

**阶段 4: 资源层访问（按需）**

```
如果需要参考文档（如 SKILL.md 中引用了 docx-js.md）：
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

2. **资源层的按需访问**
   - **References**：参考文档按需加载到 context（如 docx-js.md, ooxml.md）
   - **Assets**：资源文件通过文件系统访问，不加载到 context
   - **Scripts**：可执行脚本通过文件系统访问或执行

3. **Skill 脚本的执行在 LLM 调用之后**
   - LLM 生成代码
   - 然后执行代码（不是 LLM 调用）

这个设计确保了：
- **Token 效率**：初始只加载元数据（~100 tokens/Skill），节省 tokens
- **智能选择**：LLM 可以根据任务需求智能选择 Skills
- **按需加载**：只在需要时加载完整指令（~5k tokens）和参考文档
- **资源访问灵活**：支持按需访问 references/, assets/, scripts/ 目录
- **完整实现**：符合 Claude Skills 的三层渐进式披露机制

### AgentScope AgentSkill 设计理念
1. **渐进式披露机制**：三阶段按需加载
   - 初始化时仅加载元数据（约 100 tokens/Skill）
   - AI 判断需要时加载完整指令（< 5k tokens）
   - 按需访问资源文件

2. **适应性设计**：通过工具动态发现和加载技能
3. **安全性**：重复注册保护机制

## 格式兼容性分析

### 文件结构对比

#### Claude Skills 结构
```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter
│   │   ├── name: (必需)
│   │   ├── description: (必需)
│   │   └── license: (可选)
│   └── Markdown 指令内容
└── 资源目录 (可选)
    ├── scripts/      - 可执行代码
    ├── references/   - 参考文档
    └── assets/       - 输出文件（模板、图标等）
```

#### AgentScope AgentSkill 结构
```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter
│   │   ├── name: (必需)
│   │   └── description: (必需)
│   └── Markdown 指令内容
└── 资源目录 (可选)
    ├── scripts/      - 可执行代码
    ├── references/   - 参考文档
    └── assets/       - 输出文件
```

### 兼容性结论

✅ **高度兼容**：两者格式几乎完全一致

1. **YAML Front Matter**：格式相同，字段兼容
   - `name`: 必需，兼容 ✅
   - `description`: 必需，兼容 ✅
   - `license`: Claude 可选，AgentScope 不要求，兼容 ✅

2. **Markdown 内容**：格式相同，兼容 ✅

3. **资源目录结构**：命名和用途相同，兼容 ✅
   - `scripts/`: 可执行代码
   - `references/`: 参考文档
   - `assets/`: 资源文件

## 兼容性方案

### 方案 1：直接使用（推荐）
Claude Skills 可以直接在 AgentScope 中使用，因为：
- 文件结构完全兼容
- YAML front matter 格式相同
- 资源目录结构一致

### 方案 2：适配器包装
如果需要额外的元数据或转换，可以使用适配器：
- 读取 Claude Skill 的 SKILL.md
- 提取元数据和内容
- 注册到 AgentScope

## 项目结构建议

```
skills/
├── external/          # Claude 格式的 Skills（可直接使用）
│   ├── algorithmic-art/
│   ├── brand-guidelines/
│   └── ...
├── internal/          # 自主开发的 Skills
│   └── ...
└── template/          # Skill 模板
    └── SKILL.md
```

## 使用建议

1. **直接加载**：Claude Skills 可以直接被 AgentScope 加载
2. **保持原样**：无需修改 SKILL.md 文件
3. **资源访问**：scripts/, references/, assets/ 目录会自动识别
4. **元数据验证**：确保 name 和 description 字段存在

## 注意事项

1. **License 字段**：AgentScope 不要求 license 字段，但保留它不影响使用
2. **文件大小**：建议 SKILL.md 保持在 5k tokens 以内
3. **资源组织**：详细文档放在 references/ 目录，而非 SKILL.md
4. **命名规范**：确保 skill 名称唯一，避免冲突

