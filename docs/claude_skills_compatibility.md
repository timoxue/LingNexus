# Claude Skills 与 AgentScope AgentSkill 兼容性分析

## 设计理念对比

### Claude Skills 设计理念
1. **渐进式披露（Progressive Disclosure）**：三层加载架构
   - 元数据层（约 100 tokens/Skill）
   - 指令层（< 5k tokens）
   - 资源层（按需加载）

2. **模块化设计**：每个 Skill 独立封装特定功能
3. **跨平台可移植性**：可在不同平台间无缝工作

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
LLM 规划：根据 SKILL.md 的说明，生成代码
    ↓
生成 Python 代码（使用 python-docx 库）
```

**阶段 4: 执行脚本（非 LLM 调用）**

```
执行生成的代码
    ↓
创建 .docx 文件
    ↓
返回结果
```

#### 关键点

1. **LLM 调用在使用 Skill 之前**
   - 第一次调用：判断是否需要使用 Skill（基于元数据）
   - 第二次调用：规划如何使用 Skill（基于完整指令）

2. **Skill 脚本的执行在 LLM 调用之后**
   - LLM 生成代码
   - 然后执行代码（不是 LLM 调用）

这个设计确保了：
- **Token 效率**：初始只加载元数据，节省 tokens
- **智能选择**：LLM 可以根据任务需求智能选择 Skills
- **按需加载**：只在需要时加载完整指令，避免浪费

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

