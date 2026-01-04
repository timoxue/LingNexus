# CLI 代码检测优化

## 改进时间
2026-01-04

## 问题描述

### 用户遇到的现象

```
============================================================
自动执行代码（检测到: bash）
============================================================
✅ Bash 代码提取成功
❌ Bash 代码执行失败
错误: Bash 执行尚未实现

✅ 发现 1 个 docx 文件:
   - ERP.docx (7882 字节)
```

### 疑问

> "代码执行成功了，为啥还显示 bash 执行失败？"

## 问题分析

### 实际执行流程

1. **Agent 调用 js-checker skill**
   ```javascript
   // Agent 生成 JavaScript 代码
   // Agent 调用 js-checker 检查和修复代码
   // js-checker 返回执行命令: node -e "..."
   // js-checker 执行代码 ✅ 成功
   // 创建了 ERP.docx 文件
   ```

2. **Agent 展示执行过程**
   ```
   Agent 响应包括：
   - 代码检查和修复完成的说明
   - 执行命令（作为 bash 代码块展示）
   - 结果说明
   ```

3. **CLI 检测并尝试执行**
   ```
   CLI 检测到响应中有 ```bash``` 代码块
   → 提取 bash 代码
   → 尝试执行（但功能未实现）
   → 显示失败 ❌
   ```

### 问题根源

**重复执行 + 误判**：
- ✅ JavaScript 代码已经被 js-checker skill 执行了
- ❌ CLI 检测到 Agent 展示的 bash 命令
- ❌ CLI 尝试再次执行（失败）
- ❌ 显示误导性的失败信息

## 解决方案

### 改进代码检测逻辑

在 `lingnexus/cli/interactive.py` 中添加智能过滤：

```python
# 过滤掉看起来像是"执行命令"的 bash 代码
if 'bash' in codes:
    bash_code = codes['bash']

    # 如果 bash 代码只是单行命令，跳过
    if bash_code and '\n' not in bash_code.strip():
        # 检查是否是常见的代码执行命令
        command_prefixes = ['node -e', 'python -c', 'python3 -c', 'php -r']
        if any(bash_code.strip().startswith(prefix) for prefix in command_prefixes):
            # 这是展示的执行命令，不是要执行的 bash 脚本
            del codes['bash']
```

### 过滤规则

**会跳过的 bash 代码**：
- 单行命令
- 以 `node -e` 开头
- 以 `python -c` 开头
- 以 `python3 -c` 开头
- 以 `php -r` 开头

**不会跳过的 bash 代码**：
- 多行脚本
- 真正的 bash 脚本（包含 if、for 等）

### 效果对比

**改进前**：
```
自动执行代码（检测到: bash）
✅ Bash 代码提取成功
❌ Bash 代码执行失败
✅ 发现 1 个 docx 文件
```

**改进后**：
```
⚠️ 检测到代码块，但无需执行的代码（可能是 Agent 展示的执行命令）

✅ 发现 1 个 docx 文件:
   - ERP.docx (7882 字节)
```

## 关键改进

### 1. 智能判断

不再盲目执行所有检测到的代码，而是：
- 判断代码的性质（是要执行的脚本，还是展示的命令）
- 避免重复执行已经执行过的代码

### 2. 更清晰的信息

改进后的提示更准确：
```
⚠️ 检测到代码块，但无需执行的代码
（可能是 Agent 展示的执行命令）
```

### 3. 避免误导

不再显示：
- ❌ "Bash 代码执行失败"
- ✅ 而是说明：这是 Agent 展示的命令，不需要再次执行

## 技术细节

### 检测逻辑

```python
# 1. 提取所有代码块
codes = extract_code_from_text(response_text)

# 2. 过滤掉展示性质的 bash 命令
if 'bash' in codes:
    bash_code = codes['bash']

    # 单行命令 + 常见前缀 = 展示命令
    if is_single_line_command(bash_code) and has_execution_prefix(bash_code):
        del codes['bash']

# 3. 如果没有需要执行的代码
if not codes:
    print("检测到代码块，但无需执行的代码")
```

### 判断标准

**展示命令的特征**：
1. 单行（没有换行符）
2. 以执行命令前缀开头（`node -e`, `python -c` 等）
3. 通常包含在一行内（如 `node -e "code"`）

**真实 bash 脚本的特征**：
1. 多行
2. 包含 bash 关键字（if, for, while, function 等）
3. 包含注释、变量定义等

## 测试场景

### 场景 1：Agent 展示执行命令（改进后）

```markdown
Agent 响应：
代码检查和修复已经完成

### 执行命令
```bash
node -e "const fs = require('fs'); ..."
```

### 结果
文档已成功创建！
```

**CLI 行为**：
- ✅ 检测到 bash 代码
- ✅ 识别为展示命令
- ✅ 跳过执行
- ✅ 显示："无需执行的代码（可能是 Agent 展示的执行命令）"

### 场景 2：真实的 bash 脚本

```markdown
Agent 响应：
```bash
#!/bin/bash
echo "Starting deployment..."
for file in *.js; do
    node "$file"
done
```
```

**CLI 行为**：
- ✅ 检测到 bash 代码
- ✅ 识别为真实脚本（多行）
- ⚠️ 尝试执行（但功能未实现）
- ❌ 显示失败（预期行为）

## 后续改进

### 短期

1. ✅ 添加展示命令过滤
2. ⏳ 实现基本的 Bash 代码执行
3. ⏳ 改进错误信息显示

### 长期

1. **智能检测代码执行状态**
   - 检查文件是否已经创建
   - 避免重复执行

2. **更精确的代码分类**
   - 区分"要执行的代码"和"展示的命令"
   - 支持更多前缀和模式

3. **执行历史追踪**
   - 记录哪些代码已经被执行
   - 避免重复执行

## 文件变更

### 修改的文件

- **`lingnexus/cli/interactive.py`**
  - 添加 bash 代码过滤逻辑（lines 284-295）
  - 改进提示信息（line 325）

## 总结

这个改进解决了一个常见的**误判问题**：

**问题**：
- Agent 展示执行命令（如 `node -e "..."`）
- CLI 误认为是需要执行的 bash 脚本
- 尝试执行失败，显示误导性的错误

**解决**：
- 智能识别"展示命令"vs"要执行的脚本"
- 跳过展示性质的命令
- 显示更准确的信息

**效果**：
- ✅ 不再显示误导性的失败信息
- ✅ 用户更清楚地知道发生了什么
- ✅ 避免重复执行已经执行的代码

这个改进虽然小，但显著改善了用户体验！
