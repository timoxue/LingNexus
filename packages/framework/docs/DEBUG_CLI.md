# CLI 调试指南

本指南介绍在 Monorepo 架构下调试 LingNexus CLI 的方法。

## 目录

- [基本调试方法](#基本调试方法)
- [IDE 调试配置](#ide-调试配置)
- [日志调试](#日志调试)
- [常见调试场景](#常见调试场景)

---

## 基本调试方法

### 1. 直接运行 CLI

```bash
# 进入 framework 目录
cd packages/framework

# 运行不同命令
uv run python -m lingnexus.cli                    # 默认：交互模式
uv run python -m lingnexus.cli chat               # 交互模式
uv run python -m lingnexus.cli chat --mode test    # 测试模式
uv run python -m lingnexus.cli monitor            # 监控所有项目
uv run python -m lingnexus.cli status             # 查看状态
uv run python -m lingnexus.cli db --project "司美格鲁肽"  # 查询数据库
```

### 2. 使用 Python 调试器（pdb）

```bash
# 使用 pdb 调试
cd packages/framework
uv run python -m pdb -m lingnexus.cli chat

# 使用 ipdb（更友好，需先安装）
uv add ipdb
uv run python -m ipdb -m lingnexus.cli monitor --project "司美格鲁肽"
```

**pdb 常用命令**：
- `n` (next) - 执行下一行
- `s` (step) - 步入函数
- `c` (continue) - 继续执行到下一个断点
- `b <line>` - 在指定行设置断点
- `b <function>` - 在函数入口设置断点
- `p <variable>` - 打印变量值
- `l` - 显示当前位置代码
- `ll` - 显示更多代码
- `w` - 显示堆栈跟踪
- `u` / `d` - 在堆栈中向上/向下移动
- `q` - 退出调试器

### 3. 在代码中设置断点

在你想调试的代码位置添加：

```python
import pdb; pdb.set_trace()

# 或者使用 ipdb（更友好）
import ipdb; ipdb.set_trace()

# 或者条件断点
if some_condition:
    import pdb; pdb.set_trace()
```

**示例** - 在 `monitoring.py` 中添加断点：

```python
def cmd_monitor(args):
    """执行监控任务"""
    import pdb; pdb.set_trace()  # 在这里设置断点

    # 从配置文件加载项目
    config = load_config()
    ...
```

---

## IDE 调试配置

### Visual Studio Code

创建 `.vscode/launch.json`：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "CLI: Interactive Chat",
            "type": "debugpy",
            "request": "launch",
            "module": "lingnexus.cli",
            "args": ["chat", "--mode", "test"],
            "cwd": "${workspaceFolder}/packages/framework",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "CLI: Monitor",
            "type": "debugpy",
            "request": "launch",
            "module": "lingnexus.cli",
            "args": ["monitor", "--project", "司美格鲁肽"],
            "cwd": "${workspaceFolder}/packages/framework",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "CLI: Status",
            "type": "debugpy",
            "request": "launch",
            "module": "lingnexus.cli",
            "args": ["status"],
            "cwd": "${workspaceFolder}/packages/framework",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "CLI: Database Query",
            "type": "debugpy",
            "request": "launch",
            "module": "lingnexus.cli",
            "args": ["db", "--project", "司美格鲁肽"],
            "cwd": "${workspaceFolder}/packages/framework",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

**使用方法**：
1. 在 VS Code 中打开项目
2. 按 `F5` 或点击 "Run and Debug"
3. 选择对应的调试配置
4. 在代码中设置断点（点击行号左侧）
5. 按 `F5` 开始调试

### PyCharm

1. **创建运行配置**：
   - 打开 `Run` → `Edit Configurations...`
   - 点击 `+` → `Python`
   - 配置如下：

```
Name: CLI Interactive Chat
Module name: lingnexus.cli
Parameters: chat --mode test
Working directory: <project_path>/packages/framework
```

2. **设置断点**：
   - 在代码行号左侧点击设置断点

3. **开始调试**：
   - 点击调试按钮（虫子图标）
   - 或按 `Shift + F9`

---

## 日志调试

### 1. 添加日志语句

在 CLI 代码中添加 print 或 logging：

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def cmd_monitor(args):
    """执行监控任务"""
    logger.info(f"Starting monitor with args: {args}")
    logger.debug(f"Project: {args.project}")

    # 打印调试信息
    print(f"[DEBUG] Args received: {args}")
    ...
```

### 2. 使用 Python logging 模块

创建 `packages/framework/lingnexus/cli/logging_config.py`：

```python
import logging
import sys

def setup_logging(level=logging.INFO):
    """配置日志系统"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    return root_logger
```

在 CLI 中使用：

```python
from .logging_config import setup_logging

def main():
    # 设置日志级别
    setup_logging(logging.DEBUG)

    # 你的代码...
```

### 3. 环境变量控制日志级别

```python
import os
import logging

def main():
    # 从环境变量读取日志级别
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ...
```

使用：

```bash
# 设置日志级别为 DEBUG
export LOG_LEVEL=DEBUG
uv run python -m lingnexus.cli monitor

# Windows PowerShell
$env:LOG_LEVEL="DEBUG"
uv run python -m lingnexus.cli monitor
```

---

## 常见调试场景

### 场景 1: 调试监控命令

```bash
cd packages/framework

# 方法1: 使用 pdb
uv run python -m pdb -m lingnexus.cli monitor --project "司美格鲁肽"

# 方法2: 添加 print 调试
# 编辑 monitoring.py，在关键位置添加 print
print(f"[DEBUG] Scraping CDE for project: {project_name}")
```

**在 `monitoring.py` 中添加调试代码**：

```python
def cmd_monitor(args):
    """执行监控任务"""
    print(f"[DEBUG] cmd_monitor called with args: {args}")  # 调试输出

    project_name = args.project
    print(f"[DEBUG] Project name: {project_name}")  # 调试输出

    # 从配置文件加载项目
    config = load_config()
    print(f"[DEBUG] Config loaded: {config}")  # 调试输出
    ...
```

### 场景 2: 调试交互模式

```bash
# 使用 test 模式（更易调试）
cd packages/framework
uv run python -m lingnexus.cli chat --mode test

# 或直接调试 interactive.py
uv run python -m pdb lingnexus/cli/interactive.py
```

### 场景 3: 查看变量值

在代码中添加：

```python
def some_function():
    my_var = "some value"

    # 方法1: 使用 print
    print(f"[DEBUG] my_var = {my_var}")
    print(f"[DEBUG] my_var type = {type(my_var)}")

    # 方法2: 使用 pdb
    import pdb; pdb.set_trace()
    # 程序会在这里暂停，可以交互式检查变量
```

### 场景 4: 调试数据存储问题

```python
from lingnexus.storage.structured import StructuredDB

def cmd_db(args):
    """数据库查看命令"""
    print(f"[DEBUG] cmd_db called with args: {args}")

    db = StructuredDB()
    print(f"[DEBUG] Database connection established")

    if args.project:
        print(f"[DEBUG] Querying project: {args.project}")
        trials = db.get_project_trials(args.project)
        print(f"[DEBUG] Found {len(trials)} trials")

    if args.nct:
        print(f"[DEBUG] Querying NCT: {args.nct}")
        trial = db.get_trial_by_nct(args.nct)
        print(f"[DEBUG] Trial data: {trial}")
```

---

## 高级调试技巧

### 1. 使用 Python trace 模块

```bash
# 追踪代码执行
cd packages/framework
uv run python -m trace --trace lingnexus.cli status
```

### 2. 性能分析

```bash
# 使用 cProfile 分析性能
uv run python -m cProfile -s cumulative -m lingnexus.cli monitor

# 输出到文件
uv run python -m cProfile -o profile.stats -m lingnexus.cli monitor
uv run python -c "import pstats; p=pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

### 3. 内存分析

```bash
# 使用 memory_profiler（需先安装）
uv add memory-profiler
uv run python -m memory_profiler -m lingnexus.cli monitor
```

### 4. 异步代码调试

CLI 中的交互模式使用了 asyncio，调试时需要：

```python
import asyncio
import pdb

def some_async_function():
    # 在异步函数中设置断点
    asyncio.get_event_loop().call_soon(lambda: pdb.set_trace())
```

或者使用 `ipdb`：

```bash
uv add ipdb
uv run python -m ipdb -m lingnexus.cli chat
```

---

## 调试检查清单

在调试 CLI 问题时，检查以下内容：

- [ ] **工作目录**: 确保在 `packages/framework/` 目录
- [ ] **环境变量**: 检查 `DASHSCOPE_API_KEY` 是否设置
- [ ] **依赖安装**: 运行 `uv sync` 确保依赖完整
- [ ] **配置文件**: 检查 `config/projects_monitoring.yaml` 是否存在
- [ ] **日志级别**: 设置 `LOG_LEVEL=DEBUG` 查看详细日志
- [ ] **路径问题**: 确认相对路径从 `packages/framework/` 开始

---

## 快速调试命令

```bash
# 1. 进入 framework 目录
cd packages/framework

# 2. 设置调试环境变量
export LOG_LEVEL=DEBUG
export PYTHONASYNCIODEBUG=1  # 异步调试

# 3. 运行 CLI（选择一个）
uv run python -m lingnexus.cli status                    # 简单命令
uv run python -m pdb -m lingnexus.cli monitor            # 使用 pdb
uv run python -m ipdb -m lingnexus.cli db --project "x"  # 使用 ipdb
uv run python -m lingnexus.cli chat --mode test          # 测试模式

# 4. 查看日志
tail -f logs/*.log  # 如果有日志文件
```

---

## 获取帮助

如果以上方法都无法解决问题：

1. **查看完整日志**:
   ```bash
   export LOG_LEVEL=DEBUG
   uv run python -m lingnexus.cli <command> > debug.log 2>&1
   cat debug.log
   ```

2. **检查环境**:
   ```bash
   uv run python -c "from lingnexus import create_progressive_agent; print('OK')"
   uv run python -c "import agentscope; print(f'AgentScope: {agentscope.__version__}')"
   ```

3. **查看文档**:
   - [CLAUDE.md](../../../../CLAUDE.md)
   - [开发指南](../../../../docs/development/setup.md)
   - [架构设计](../../../../docs/development/architecture.md)
