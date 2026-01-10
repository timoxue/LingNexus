# JavaScript 代码检查工具

## 概述

这是一个内部开发的 Skill，用于检查和修复 JavaScript 代码，确保代码可以在本地 Node.js 环境中成功执行。

## 功能

1. **Node.js 版本检查** - 检查本地 Node.js 版本和兼容性
2. **代码语法检查** - 使用 `node --check` 验证语法
3. **自动修复** - 修复全角符号等常见问题
4. **代码验证** - 验证代码是否可以执行
5. **执行准备** - 生成执行命令供 `execute_shell_command` 使用

## 使用方法

### 方式 1: 使用完整检查流程

```python
from pathlib import Path
import subprocess
import json

# 读取 JavaScript 代码
js_code = "console.log('Hello，World！');"

# 运行完整检查
result = subprocess.run(
    ["python", "skills/internal/js-checker/scripts/check_and_fix_js.py", "-"],
    input=js_code,
    capture_output=True,
    text=True,
)

check_result = json.loads(result.stdout)

# 如果检查通过，使用 execute_shell_command 执行
if check_result["validation_ok"]:
    from agentscope.tool import execute_shell_command
    execute_command = check_result["execute_command"]
    # result = await execute_shell_command(execute_command)
```

### 方式 2: 分步使用

```python
# 1. 检查 Node.js 版本
from check_node_version import check_node_version
node_version = check_node_version()

# 2. 修复代码
from fix_js_code import fix_js_code
fix_result = fix_js_code(js_code)

# 3. 检查语法
from check_js_syntax import check_js_syntax
syntax_result = check_js_syntax(fix_result["fixed_code"], node_version)

# 4. 验证代码
from validate_js import validate_js
validation_result = validate_js(fix_result["fixed_code"])
```

## 脚本说明

### check_node_version.py

检查本地 Node.js 版本。

```bash
python skills/internal/js-checker/scripts/check_node_version.py
```

### fix_js_code.py

修复 JavaScript 代码中的全角符号等问题。

```bash
echo "console.log('Hello，World！');" | python skills/internal/js-checker/scripts/fix_js_code.py -
```

### check_js_syntax.py

检查 JavaScript 代码语法。

```bash
echo "const x = 1;" | python skills/internal/js-checker/scripts/check_js_syntax.py -
```

### validate_js.py

验证 JavaScript 代码是否可以执行。

```bash
echo "console.log('Hello');" | python skills/internal/js-checker/scripts/validate_js.py -
```

### check_and_fix_js.py

完整的检查和修复流程（推荐使用）。

```bash
echo "const x = 1; console.log(x);" | python skills/internal/js-checker/scripts/check_and_fix_js.py -
```

## 集成到主 Agent

在主 Agent 中，可以这样使用：

```python
# 1. 使用 js-checker 检查代码
check_result = check_and_fix_js(js_code)

# 2. 如果检查通过，使用 AgentScope 的 execute_shell_command 执行
if check_result["validation_ok"]:
    from agentscope.tool import execute_shell_command
    result = await execute_shell_command(check_result["execute_command"])
```

## 示例

### 示例 1: 修复全角符号

**输入**:
```javascript
console.log('Hello，World！');
```

**修复后**:
```javascript
console.log('Hello,World!');
```

### 示例 2: 完整检查流程

**输入**:
```javascript
const x = 1;
console.log(x);
```

**检查结果**:
```json
{
  "node_version": {
    "installed": true,
    "version": "22.18.0",
    "meets_requirement": true
  },
  "syntax_ok": true,
  "fixed_code": "const x = 1;\nconsole.log(x);",
  "validation_ok": true,
  "execute_command": "node -e \"const x = 1;\\nconsole.log(x);\""
}
```

## 注意事项

1. 需要安装 Node.js（>= 14.0.0）
2. 代码会在临时文件中执行，不会影响系统
3. 如果代码使用了外部依赖，需要先安装
4. 执行命令中的特殊字符会被转义


