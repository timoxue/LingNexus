# LingNexus 项目重构指南

> 将现有项目重构为 Monorepo 架构

---

## 📋 重构概述

### 重构目标

将现有的单仓库结构重构为 Monorepo 架构：

```
重构前:
LingNexus/
├── lingnexus/           # 混合的代码
├── skills/
├── examples/
└── tests/

重构后:
LingNexus/
├── packages/
│   ├── framework/       # 框架包（lingnexus-framework）
│   └── platform/        # 平台包（lingnexus-platform）
├── docs/
├── scripts/
└── [其他保持不变]
```

### 重构原则

1. **增量式**: 分阶段进行，每个阶段都可独立验证
2. **可回滚**: 每个阶段结束后打 tag，随时可回滚
3. **不破坏功能**: 确保现有功能不受影响
4. **保持兼容**: CLI 和现有代码继续工作

---

## 🎯 重构阶段

### 阶段概览

```
阶段1: 仓库结构准备（1-2天）
  ↓
阶段2: Framework 包重组（2-3天）
  ↓
阶段3: Platform 包创建（3-5天）
  ↓
阶段4: 工作区配置（1天）
  ↓
阶段5: 测试和验证（2-3天）
  ↓
阶段6: 文档更新（1天）
```

**总计**: 约 10-15 个工作日

---

## 📦 阶段1: 仓库结构准备（第1-2天）

### 1.1 创建备份

```bash
# 1. 创建备份分支
git checkout -b backup-before-refactor
git push origin backup-before-refactor

# 2. 打标签
git tag v0.1.9-backup
git push origin v0.1.9-backup

# 3. 返回主分支
git checkout main
```

### 1.2 创建新分支

```bash
# 创建重构分支
git checkout -b refactor/monorepo-structure
```

### 1.3 创建 packages 目录

```bash
# 在项目根目录
mkdir -p packages/framework packages/platform

# 验证
tree -L 2 packages/
# packages/
# ├── framework/
# └── platform/
```

### 1.4 提交初始结构

```bash
git add packages/
git commit -m "refactor: create packages directory for monorepo structure"
```

---

## 🔧 阶段2: Framework 包重组（第2-3天）

### 2.1 移动 Framework 代码

```bash
# 1. 移动 lingnexus 核心代码
mkdir -p packages/framework/lingnexus

# 移动现有模块（保持目录结构）
cp -r lingnexus/agent packages/framework/lingnexus/
cp -r lingnexus/config packages/framework/lingnexus/
cp -r lingnexus/storage packages/framework/lingnexus/
cp -r lingnexus/scheduler packages/framework/lingnexus/
cp -r lingnexus/utils packages/framework/lingnexus/  # 临时保留
cp -r lingnexus/cli packages/framework/lingnexus/

# 2. 移动其他资源
cp -r skills packages/framework/skills
cp -r examples packages/framework/examples
cp -r tests packages/framework/tests

# 3. 复制配置文件
cp pyproject.toml packages/framework/
cp README.md packages/framework/README-framework.md
```

### 2.2 创建 Skill 模块（新）

```bash
# 创建 skill 模块（从 utils 迁移）
mkdir -p packages/framework/lingnexus/skill

# 创建 __init__.py
cat > packages/framework/lingnexus/skill/__init__.py << 'EOF'
"""
Skill 管理模块
"""

from .loader import SkillLoader
from .registry import SkillRegistry

__all__ = ["SkillLoader", "SkillRegistry"]
EOF

# 创建 loader.py（从 utils/skill_loader.py 迁移）
# TODO: 后续迁移
```

**注意**: 暂时保留 utils 模块，后续逐步迁移。

### 2.3 更新 Framework 配置

创建 `packages/framework/pyproject.toml`:

```toml
[project]
name = "lingnexus-framework"
version = "0.2.0"
description = "Multi-agent system framework for pharmaceutical industry"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "agentscope>=0.0.9",
    "dashscope>=1.0.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.5.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
# 监控系统
monitoring = [
    "playwright>=1.40.0",
    "beautifulsoup4>=4.12.0",
    "requests>=2.31.0",
    "tabulate>=0.9.0",
]

# 向量数据库
vector = [
    "chromadb>=0.4.0",
]

# 开发依赖
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

# 全部
all = [
    "lingnexus-framework[monitoring,vector,dev]"
]

[project.scripts]
# CLI 命令
lingnexus = "lingnexus.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = []

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
```

### 2.4 更新 Framework 导出

创建 `packages/framework/lingnexus/__init__.py`:

```python
"""
LingNexus Framework
多智能体系统框架，支持渐进式披露机制
"""

__version__ = "0.2.0"

# 核心 API
from lingnexus.agent import (
    create_progressive_agent,
    create_docx_agent,
)
from lingnexus.storage import (
    RawStorage,
    StructuredDB,
)
from lingnexus.scheduler import (
    DailyMonitoringTask,
)

# 兼容性导入（保持向后兼容）
try:
    from lingnexus.utils.skill_loader import SkillLoader
except ImportError:
    from lingnexus.skill import SkillLoader

__all__ = [
    "create_progressive_agent",
    "create_docx_agent",
    "RawStorage",
    "StructuredDB",
    "DailyMonitoringTask",
    "SkillLoader",
]
```

### 2.5 移动测试文件

```bash
# Framework 专属测试
mkdir -p packages/framework/tests

# 移动相关测试
find tests/ -name "*test*.py" -exec cp {} packages/framework/tests/ \;

# 保留集成测试在根目录
mkdir -p tests/integration
```

### 2.6 验证 Framework

```bash
# 进入 framework 目录
cd packages/framework

# 测试导入
uv run python -c "from lingnexus import create_progressive_agent; print('✅ Import OK')"

# 运行测试
uv run pytest tests/ -v

# 如果测试通过，提交
cd ../..
git add packages/framework
git commit -m "refactor: reorganize framework code into packages/framework"
```

---

## 🌐 阶段3: Platform 包创建（第3-5天）

### 3.1 初始化 Platform Backend

```bash
# 创建后端目录结构
mkdir -p packages/platform/backend/{api,models,services,core,db,scripts}

# 初始化 Python 项目
cd packages/platform/backend
uv init --name lingnexus-platform
```

### 3.2 配置 Platform Backend 依赖

创建 `packages/platform/backend/pyproject.toml`:

```toml
[project]
name = "lingnexus-platform"
version = "1.0.0"
description = "Low-code platform for building AI agents"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.5.0",
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    # 依赖本地 framework（通过工作区）
    "lingnexus-framework",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "httpx>=0.25.0",
    "ruff>=0.1.0",
]

[project.scripts]
dev = "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv.sources]
lingnexus-framework = { workspace = true }
```

### 3.3 初始化 Platform Frontend

```bash
# 创建前端目录
mkdir -p packages/platform/frontend

# 初始化 Vue 项目
cd packages/platform/frontend
npm create vite@latest . -- --template vue-ts
```

更新 `packages/platform/frontend/package.json`:

```json
{
  "name": "@lingnexus/frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "axios": "^1.6.0",
    "@vue-flow/core": "^1.33.0",
    "@vue-flow/background": "^1.3.0",
    "@vue-flow/controls": "^1.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0"
  }
}
```

### 3.4 创建 Platform 基础代码

**Backend 基础文件**:

```bash
# packages/platform/backend/main.py
cat > packages/platform/backend/main.py << 'EOF'
"""
LingNexus Platform Backend
FastAPI 应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="LingNexus Platform",
    description="Low-code platform for building AI agents",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LingNexus Platform API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF
```

**Frontend 基础文件**:

```bash
# packages/platform/frontend/src/main.ts
cat > packages/platform/frontend/src/main.ts << 'EOF'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
EOF
```

### 3.5 提交 Platform 初始结构

```bash
cd ../..
git add packages/platform
git commit -m "refactor: initialize platform package with backend and frontend"
```

---

## ⚙️ 阶段4: 工作区配置（第4-5天）

### 4.1 更新根项目配置

更新根目录的 `pyproject.toml`:

```toml
[project]
name = "lingnexus-workspace"
version = "0.0.0"
description = "LingNexus Monorepo Workspace"
requires-python = ">=3.10"

[tool.uv.workspace]
members = [
    "packages/framework",
    "packages/platform/backend",
]

# 共享开发依赖
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["packages/framework/tests", "packages/platform/backend/tests", "tests/integration"]
```

### 4.2 创建开发脚本

创建 `scripts/dev.sh`:

```bash
#!/bin/bash
# 启动开发环境

set -e

echo "🚀 启动 LingNexus 开发环境"

# 1. 安装依赖
echo "📦 安装依赖..."
uv sync

# 2. 初始化数据库
if [ ! -f "data/intelligence.db" ]; then
    echo "🗄️  初始化数据库..."
    cd packages/platform/backend
    uv run python -m scripts.init_db
    cd ../..
fi

# 3. 启动后端（后台运行）
echo "🔧 启动后端服务..."
cd packages/platform/backend
uv run uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# 4. 启动前端
echo "🎨 启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ 开发环境已启动！"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

wait
```

```bash
chmod +x scripts/dev.sh
```

创建其他脚本：

```bash
# scripts/test.sh
cat > scripts/test.sh << 'EOF'
#!/bin/bash
set -e

echo "🧪 运行所有测试"

# Framework 测试
echo "Framework 测试..."
cd packages/framework
uv run pytest

# Platform Backend 测试
echo "Platform Backend 测试..."
cd ../platform/backend
uv run pytest

echo "✅ 所有测试通过"
EOF

chmod +x scripts/test.sh

# scripts/build.sh
cat > scripts/build.sh << 'EOF'
#!/bin/bash
set -e

echo "📦 构建所有包"

# Framework
echo "构建 Framework..."
cd packages/framework
uv build

# Platform Backend
echo "构建 Platform Backend..."
cd ../platform/backend
uv build

# Platform Frontend
echo "构建 Platform Frontend..."
cd ../frontend
npm run build

echo "✅ 构建完成"
EOF

chmod +x scripts/build.sh
```

### 4.3 提交工作区配置

```bash
git add pyproject.toml scripts/
git commit -m "refactor: configure workspace and development scripts"
```

---

## 🧪 阶段5: 测试和验证（第5-6天）

### 5.1 测试 Framework

```bash
# 测试导入
cd packages/framework
uv run python -c "
from lingnexus import create_progressive_agent
from lingnexus.storage import RawStorage, StructuredDB
print('✅ Framework imports OK')
"

# 测试 CLI
uv run python -m lingnexus.cli --help

# 测试监控功能
uv run python -m lingnexus.cli status
```

### 5.2 测试 Platform

```bash
# 测试后端
cd packages/platform/backend
uv run uvicorn main:app --reload &

# 测试 API
curl http://localhost:8000/health

# 测试前端
cd ../frontend
npm run dev &

# 访问
# 前端: http://localhost:5173
# 后端: http://localhost:8000
```

### 5.3 集成测试

```bash
# 使用开发脚本
./scripts/dev.sh

# 验证功能
# 1. 创建 Skill
# 2. 构建 Agent
# 3. 运行 Agent
```

### 5.4 性能测试

```bash
# 测试渐进式披露
cd packages/framework
uv run pytest tests/test_progressive_disclosure.py -v
```

---

## 📝 阶段6: 文档和发布（第6-7天）

### 6.1 更新 README

更新根目录 `README.md`，添加 Monorepo 说明。

### 6.2 创建迁移指南

创建 `MIGRATION_GUIDE.md`:

```markdown
# 迁移到 Monorepo 架构

## 对现有用户的影响

### CLI 使用

**无变化**：命令保持不变

\`\`\`bash
# 旧方式（继续支持）
python -m lingnexus.cli monitor

# 新方式
uv run python -m lingnexus.cli monitor
\`\`\`

### 代码导入

**兼容性**：现有代码继续工作

\`\`\`python
# 旧导入（继续支持）
from lingnexus.utils.skill_loader import SkillLoader

# 新导入（推荐）
from lingnexus.skill import SkillLoader
\`\`\`

## 更新步骤

1. 更新依赖：`uv add lingnexus-framework>=0.2.0`
2. 更新导入：使用新的导入路径
3. 测试功能
\`\`\`
```

### 6.3 打标签和发布

```bash
# 打标签
git tag -a v0.2.0 -m "Release v0.2.0: Monorepo structure"
git push origin v0.2.0

# 发布到 PyPI（仅 Framework）
cd packages/framework
uv publish

# 发布 Platform（可选）
# Platform 通常作为私有部署，不发布到 PyPI
```

---

## ⚠️ 常见问题和解决方案

### Q1: 导入错误

**问题**: `ModuleNotFoundError: No module named 'lingnexus'`

**解决**:
```bash
# 确保在工作区根目录
cd /path/to/LingNexus

# 重新同步依赖
uv sync

# 验证工作区配置
cat pyproject.toml | grep -A5 "\[tool.uv.workspace\]"
```

### Q2: 前端无法连接后端

**问题**: 前端显示 "Network Error"

**解决**:
```bash
# 检查 CORS 配置
# packages/platform/backend/main.py
# 确保 CORS_ORIGINS 包含前端地址

# 检查环境变量
cat packages/platform/backend/.env
```

### Q3: 测试失败

**问题**: pytest 找不到模块

**解决**:
```bash
# 设置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/packages/framework"

# 或使用 pytest.ini 配置
# [pytest]
# pythonpath = packages/framework
```

### Q4: 工作区不生效

**问题**: 修改 framework 后 platform 中没有更新

**解决**:
```bash
# 验证 uv 工作区配置
uv workspace verify

# 重新同步
uv sync --reinstall
```

---

## ✅ 重构检查清单

### 阶段1: 仓库结构准备
- [ ] 创建备份分支和标签
- [ ] 创建 packages 目录
- [ ] 创建 framework 和 platform 子目录

### 阶段2: Framework 包
- [ ] 移动代码到 packages/framework
- [ ] 更新 pyproject.toml
- [ ] 更新导出（__init__.py）
- [ ] 测试导入和功能
- [ ] 提交代码

### 阶段3: Platform 包
- [ ] 初始化 backend
- [ ] 初始化 frontend
- [ ] 配置依赖
- [ ] 创建基础代码
- [ ] 测试启动
- [ ] 提交代码

### 阶段4: 工作区配置
- [ ] 更新根 pyproject.toml
- [ ] 创建开发脚本
- [ ] 测试本地依赖
- [ ] 提交配置

### 阶段5: 测试验证
- [ ] 测试所有 CLI 命令
- [ ] 测试监控功能
- [ ] 测试 Platform 启动
- [ ] 运行集成测试
- [ ] 性能测试

### 阶段6: 文档发布
- [ ] 更新 README
- [ ] 创建迁移指南
- [ ] 打标签
- [ ] 发布到 PyPI

---

## 🚀 开始重构

### 立即开始

```bash
# 1. 创建重构分支
git checkout -b refactor/monorepo-structure

# 2. 按照阶段1开始
mkdir -p packages/framework packages/platform

# 3. 提交
git add packages/
git commit -m "refactor: create packages directory"

# 4. 继续阶段2...
```

### 需要帮助？

- 查看 [架构设计](../docs/development/architecture.md)
- 查看 [开发环境搭建](../docs/development/setup.md)
- 提问: https://github.com/your-org/LingNexus/discussions

---

**记住**: 重构是增量式的，每个阶段都可以独立验证和回滚。不要急于求成，稳扎稳打！
