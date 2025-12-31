# Windows 编码问题修复

## 问题描述

在 Windows 系统上，当使用 AgentScope 的 `execute_python_code` 或 `execute_shell_command` 工具时，可能会遇到以下错误：

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe6 in position 298: invalid continuation byte
```

这是因为 Windows 系统默认使用 GBK/CP936 编码，而 AgentScope 的子进程输出可能包含非 UTF-8 编码的字符。

## 修复方案

### 1. 在模块级别设置环境变量

在 `lingnexus/config/agent_config.py` 和 `lingnexus/utils/code_executor.py` 中，在模块导入时设置环境变量：

```python
# Windows 编码修复：设置环境变量，确保子进程使用 UTF-8 编码
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONLEGACYWINDOWSSTDIO', '0')
```

### 2. 在 subprocess 调用中添加编码错误处理

在所有 `subprocess.run()` 调用中，添加 `encoding='utf-8'` 和 `errors='replace'`：

```python
process = subprocess.run(
    [...],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',  # 处理编码错误，用替换字符代替无法解码的字节
    timeout=30,
)
```

### 3. 已修复的文件

- `lingnexus/config/agent_config.py` - 在模块级别设置环境变量
- `lingnexus/utils/code_executor.py` - 在模块级别和函数级别设置环境变量
- `lingnexus/utils/skill_loader.py` - 在 subprocess 调用中添加编码错误处理
- `skills/internal/js-checker/scripts/check_node_version.py` - 添加编码错误处理
- `skills/internal/js-checker/scripts/check_js_syntax.py` - 添加编码错误处理
- `skills/internal/js-checker/scripts/validate_js.py` - 添加编码错误处理

## 环境变量说明

- `PYTHONIOENCODING=utf-8`: 强制 Python 子进程使用 UTF-8 编码进行 I/O 操作
- `PYTHONLEGACYWINDOWSSTDIO=0`: 禁用 Windows 的遗留标准 I/O 处理，使用新的 UTF-8 支持

## 注意事项

1. 这些环境变量设置会影响当前进程及其所有子进程
2. 如果子进程仍然输出非 UTF-8 编码的内容，`errors='replace'` 会用替换字符代替无法解码的字节
3. 这不会影响代码的功能，只是可能丢失一些非 UTF-8 字符的显示

## 测试

修复后，可以正常执行包含中文字符的代码：

```python
code = """
print("测试中文")
print("Hello, World!")
"""
result = await execute_python_code_with_agentscope(code)
```

