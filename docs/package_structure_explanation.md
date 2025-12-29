# 包结构说明

## 当前结构

```
lingnexus/                    # 主包目录
├── __init__.py              # 包初始化文件
├── agent/                   # Agent 相关模块
│   ├── __init__.py
│   ├── agent_factory.py     # Agent 工厂类
│   └── react_agent.py       # ReActAgent 便捷函数
├── config/                  # 配置模块
│   ├── __init__.py
│   ├── model_config.py      # 模型配置
│   └── agent_config.py      # Agent 全局配置
└── utils/                   # 工具模块
    ├── __init__.py
    └── skill_loader.py      # Skill 加载器
```

## ✅ 为什么这个结构是 OK 的？

### 1. 符合 Python 包标准

这是**标准的 Python 包结构**，完全符合最佳实践：

- ✅ 顶层包名：`lingnexus`
- ✅ 子模块：`agent`, `config`, `utils`
- ✅ 每个目录都有 `__init__.py`（Python 包标识）
- ✅ 清晰的模块划分和职责分离

### 2. 导入方式

```python
# 导入子模块
from lingnexus.agent import AgentFactory
from lingnexus.config import create_model
from lingnexus.utils import SkillLoader

# 或者从子模块导入具体类/函数
from lingnexus.agent.agent_factory import AgentFactory
from lingnexus.config.model_config import create_model
```

### 3. 与 pyproject.toml 配置一致

```toml
[project]
name = "lingnexus"

[tool.hatch.build.targets.wheel]
packages = ["lingnexus"]  # 指定打包 lingnexus 包及其所有子模块
```

这确保了：
- ✅ `uv sync` 可以正确构建包
- ✅ 所有子模块都会被包含
- ✅ 导入路径清晰明确

## 结构优势

### 1. 模块化设计

```
lingnexus/
├── agent/      # Agent 相关功能
├── config/     # 配置相关功能
└── utils/      # 工具函数
```

**优点**：
- ✅ 职责清晰，易于维护
- ✅ 便于扩展新功能
- ✅ 避免命名冲突

### 2. 导入路径清晰

```python
# 清晰的命名空间
from lingnexus.agent import AgentFactory
from lingnexus.config import ModelType
from lingnexus.utils import SkillLoader
```

**优点**：
- ✅ 一眼就能看出功能归属
- ✅ 避免导入冲突
- ✅ 符合 Python 命名规范

### 3. 易于扩展

未来可以轻松添加新模块：

```
lingnexus/
├── agent/
├── config/
├── utils/
├── memory/     # 未来可以添加
├── pipeline/   # 未来可以添加
└── ...
```

## 与其他结构的对比

### ❌ 不推荐的结构

```
# 方式 1: 所有文件放在根目录
lingnexus/
├── agent_factory.py
├── model_config.py
├── skill_loader.py
└── ...

# 问题：文件太多，难以管理
```

```
# 方式 2: 不使用包结构
LingNexus/
├── agent_factory.py
├── model_config.py
└── ...

# 问题：不是 Python 包，无法正确导入
```

### ✅ 当前结构（推荐）

```
lingnexus/
├── agent/
├── config/
└── utils/
```

**优点**：
- ✅ 符合 Python 包标准
- ✅ 模块化清晰
- ✅ 易于维护和扩展
- ✅ 支持正确的导入

## 验证

当前结构已验证：
- ✅ 所有模块可以正确导入
- ✅ `uv sync` 可以正确构建
- ✅ 符合 Python 包规范

## 总结

**当前结构完全 OK！** ✅

这是标准的 Python 包结构，符合最佳实践：
1. ✅ 顶层包名清晰
2. ✅ 子模块职责明确
3. ✅ 导入路径规范
4. ✅ 易于维护和扩展

无需修改，继续保持当前结构即可。

