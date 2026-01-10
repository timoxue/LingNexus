# 开发环境搭建

> LingNexus Monorepo 开发环境配置指南

---

## 目录

- [环境要求](#环境要求)
- [克隆项目](#克隆项目)
- [安装依赖](#安装依赖)
- [开发脚本](#开发脚本)
- [IDE 配置](#ide-配置)
- [开发工作流](#开发工作流)

---

## 环境要求

### 必需工具

| 工具 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | Framework 开发 |
| **Node.js** | 18.0+ | Frontend 开发 |
| **uv** | 最新 | Python 包管理器 |
| **Git** | 2.30+ | 版本控制 |

### 可选工具

| 工具 | 版本 | 用途 |
|------|------|------|
| **Docker** | 20.0+ | 容器化部署 |
| **Chromium** | 最新 | CDE 爬虫（自动下载） |
| **ChromaDB** | 最新 | 向量数据库（可选） |

---

## 克隆项目

```bash
# 克隆仓库
git clone https://github.com/your-org/LingNexus.git
cd LingNexus

# 切换到开发分支
git checkout -b dev
```

---

## 安装依赖

### 1. 安装 uv（Python 包管理器）

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 验证安装
uv --version
```

### 2. 安装 Python 依赖

```bash
# 安装所有依赖（Framework + Platform Backend）
uv sync

# 安装可选依赖
uv sync --extra monitoring   # 监控系统
uv sync --extra vector       # 向量数据库
uv sync --extra all          # 全部
```

**项目结构**:
```
packages/
├── framework/           # 框架包
│   ├── lingnexus/       # 框架代码
│   ├── tests/           # 框架测试
│   └── pyproject.toml   # 包配置
│
└── platform/
    └── backend/         # 平台后端
        └── pyproject.toml
```

### 3. 安装前端依赖

```bash
cd packages/platform/frontend

# 安装依赖
npm install

# 或使用 pnpm（更快）
npm install -g pnpm
pnpm install
```

---

## 开发脚本

### 一键启动开发环境

```bash
# 从项目根目录执行
./scripts/dev.sh
```

**此脚本会**:
1. 安装所有依赖
2. 初始化数据库
3. 启动后端服务（http://localhost:8000）
4. 启动前端服务（http://localhost:5173）
5. 打开浏览器

**手动启动（可选）**:

```bash
# 终端 1: 启动后端
cd packages/platform/backend
uv run uvicorn main:app --reload --port 8000

# 终端 2: 启动前端
cd packages/platform/frontend
npm run dev

# 访问
# 前端: http://localhost:5173
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 其他开发脚本

```bash
# 运行测试
./scripts/test.sh

# 构建所有包
./scripts/build.sh

# 代码格式化
./scripts/format.sh

# 代码检查
./scripts/lint.sh
```

---

## IDE 配置

### VSCode

#### 推荐插件

创建 `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "vue.volar",
    "vue.vscode-typescript-vue-plugin",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "tamasfe.even-better-toml",
    "eamodio.gitlens"
  ]
}
```

#### 工作区设置

创建 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "files.associations": {
    "*.toml": "toml"
  }
}
```

#### 调试配置

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "cwd": "${workspaceFolder}/packages/platform/backend",
      "env": {
        "PYTHONUNBUFFERED": "1"
      },
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "cwd": "${workspaceFolder}/packages/framework",
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm

1. **打开项目**: `File` → `Open` → 选择 `LingNexus` 目录
2. **设置 Python 解释器**:
   - `File` → `Settings` → `Project` → `Python Interpreter`
   - 选择 `.venv` 中的 Python
3. **配置运行配置**:
   - `Run` → `Edit Configurations`
   - 添加 FastAPI 配置
   - Module name: `uvicorn`
   - Parameters: `main:app --reload`
   - Working directory: `$ProjectFileDir$/packages/platform/backend`

---

## 开发工作流

### 1. 功能开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/agent-builder

# 2. 开发功能
# ...编写代码...

# 3. 运行测试
./scripts/test.sh

# 4. 代码检查
./scripts/lint.sh

# 5. 提交代码
git add .
git commit -m "feat: 添加 Agent 可视化构建器"

# 6. 推送到远程
git push origin feature/agent-builder
```

### 2. 同时修改 Framework 和 Platform

**场景**: 你需要在 Framework 中添加新功能，然后在 Platform 中使用它。

```bash
# 1. 修改 Framework 代码
vim packages/framework/lingnexus/agent/react_agent.py

# 2. 在 Platform 中使用新功能
vim packages/platform/backend/services/agent_service.py

# 3. 测试
cd packages/platform/backend
uv run pytest

# 4. 一次性提交
git add packages/
git commit -m "feat: add agent streaming support
- framework: implement streaming in AgentFactory
- platform: add SSE endpoint for agent execution"
```

**优势**: 本地依赖自动生效，无需重新安装。

### 3. 查看 Framework 变更对 Platform 的影响

```bash
# 修改 Framework 代码
vim packages/framework/lingnexus/skill/loader.py

# 立即在 Platform 中测试
cd packages/platform/backend
uv run uvicorn main:app --reload

# ✅ 自动使用修改后的 Framework
```

---

## 环境变量配置

### Framework 环境变量

创建 `.env` 文件（项目根目录）：

```bash
# 模型 API
DASHSCOPE_API_KEY=your-api-key-here

# 日志级别
LOG_LEVEL=INFO

# 存储路径
DATA_PATH=data
SKILLS_BASE=skills

# 可选: 向量数据库
VECTOR_DB_ENABLED=false
VECTOR_DB_PATH=data/vectordb

# 可选: 加密
LINGNEXUS_ENCRYPTION_KEY=your-32-byte-encryption-key
```

### Platform Backend 环境变量

创建 `packages/platform/backend/.env`：

```bash
# 数据库
DATABASE_URL=sqlite:///./data/platform.db

# JWT 密钥
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 文件存储
SKILLS_BASE_PATH=skills/
UPLOAD_MAX_SIZE=10485760

# AgentScope
AGENTSCOPE_MODEL_NAME=qwen-max
AGENTSCOPE_TEMPERATURE=0.3
```

### Platform Frontend 环境变量

创建 `packages/platform/frontend/.env.local`：

```bash
# API 地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用配置
VITE_APP_NAME=LingNexus
VITE_APP_VERSION=1.0.0
```

---

## 常见问题

### Q1: uv sync 报错 "Failed to download"

**A**: 使用国内镜像：

```bash
# 设置镜像
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 或在 .uvrc 文件中配置
echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" > .uvrc
```

### Q2: 前端启动失败 "Cannot find module"

**A**: 清除缓存重新安装：

```bash
cd packages/platform/frontend
rm -rf node_modules package-lock.json
npm install
```

### Q3: 后端启动失败 "Module not found"

**A**: 确保在工作区根目录：

```bash
# 确保在项目根目录
cd /path/to/LingNexus

# 检查工作区配置
cat pyproject.toml | grep -A5 "\[tool.uv.workspace\]"

# 重新同步依赖
uv sync
```

### Q4: 如何调试 Framework 代码？

**A**: 在 VSCode 中配置调试：

1. 打开 `packages/framework/lingnexus/` 下的文件
2. 设置断点
3. 按 F5 开始调试
4. 选择 "Python: Tests" 或 "Python: FastAPI"

### Q5: 前端热重载不工作？

**A**: 检查 Vite 配置：

```javascript
// vite.config.ts
export default defineConfig({
  server: {
    watch: {
      usePolling: true,  // Windows 上可能需要
    },
  },
});
```

---

## 开发工具推荐

### Python 工具

```bash
# 代码格式化
uv add black
uv add ruff

# 类型检查
uv add mypy

# 测试覆盖率
uv add pytest-cov
```

### 前端工具

```bash
# 代码检查
npm install -D eslint @typescript-eslint/parser

# 代码格式化
npm install -D prettier

# Git hooks
npm install -D husky lint-staged
```

---

## 下一步

- [测试指南](testing.md) - 如何编写和运行测试
- [架构设计](architecture.md) - 深入理解系统架构
- [贡献指南](contributing.md) - 如何贡献代码

---

**需要帮助？**
- GitHub Issues: https://github.com/your-org/LingNexus/issues
