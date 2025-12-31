# AgentScope 内置代码执行工具

## 查询结果总结

经过查询，**AgentScope 1.0.10 确实提供了内置的代码执行工具**：

### ✅ 已确认的内置工具

#### 1. `execute_python_code` - Python 代码执行器

**位置**: `agentscope.tool.execute_python_code`

**函数签名**:
```python
async execute_python_code(
    code: str, 
    timeout: float = 300, 
    **kwargs: Any
) -> ToolResponse
```

**功能**:
- 在临时文件中执行 Python 代码
- 捕获返回码、标准输出和错误
- 执行后自动删除临时文件
- 注意：需要使用 `print()` 来获取输出结果

**返回格式**:
```xml
<returncode>0</returncode>
<stdout>输出内容</stdout>
<stderr>错误信息</stderr>
```

**使用示例**:
```python
from agentscope.tool import execute_python_code

result = await execute_python_code("print('Hello World')")
print(result.content)
```

#### 2. `execute_shell_command` - Shell 命令执行器

**位置**: `agentscope.tool.execute_shell_command`

**函数签名**:
```python
async execute_shell_command(
    command: str, 
    timeout: int = 300, 
    **kwargs: Any
) -> ToolResponse
```

**功能**:
- 执行 Shell 命令
- 捕获返回码、标准输出和错误
- 支持超时设置（默认300秒）

**返回格式**:
```xml
<returncode>0</returncode>
<stdout>输出内容</stdout>
<stderr>错误信息</stderr>
```

**使用示例**:
```python
from agentscope.tool import execute_shell_command

result = await execute_shell_command("ls -l")
print(result.content)
```

### ❌ 未找到的工具

- **JavaScript 执行器**: AgentScope 目前没有提供 JavaScript 代码执行器
- **其他脚本执行器**: 没有找到其他脚本类型的执行器

## 在 LingNexus 中的使用建议

### 方案设计

对于 `scripts/` 目录的脚本执行，建议采用以下方案：

1. **Python 脚本**: 使用 `execute_python_code`
   - 读取脚本文件内容
   - 使用 `execute_python_code` 执行
   - 支持参数传递（通过修改代码或使用环境变量）

2. **Shell 脚本**: 使用 `execute_shell_command`
   - 直接执行脚本文件路径
   - 或读取脚本内容后通过 shell 执行

3. **JavaScript 脚本**: 使用 `execute_shell_command`
   - 通过 `node script.js` 命令执行
   - 需要确保系统已安装 Node.js

### 工具函数设计

```python
def _tool_execute_skill_script(
    self,
    skill_name: str,
    script_path: str,
    args: Optional[List[str]] = None,
    skill_type: str = "external",
) -> ToolResponse:
    """
    工具函数：执行技能的脚本（使用 AgentScope 内置工具）
    
    根据脚本类型自动选择：
    - .py 文件 → 使用 execute_python_code
    - .sh/.bash 文件 → 使用 execute_shell_command
    - .js/.ts 文件 → 使用 execute_shell_command (通过 node)
    """
    # 1. 读取脚本文件
    # 2. 根据文件类型选择执行方式
    # 3. 使用 AgentScope 内置工具执行
    # 4. 返回结果
```

## 优势

1. ✅ **使用官方工具**: 利用 AgentScope 的内置工具，更可靠
2. ✅ **安全性**: AgentScope 的工具可能有额外的安全措施
3. ✅ **一致性**: 与 AgentScope 生态系统保持一致
4. ✅ **维护性**: 跟随 AgentScope 的更新自动获得改进

## 注意事项

1. **异步函数**: 这两个工具都是异步函数，需要使用 `await`
2. **返回格式**: 返回的是 XML 格式的字符串，需要解析
3. **超时设置**: 默认超时是 300 秒，可以根据需要调整
4. **JavaScript**: 没有内置 JavaScript 执行器，需要通过 Shell 执行

