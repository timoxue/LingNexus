# 安装指南

本文档提供 LingNexus 项目的详细安装说明。

## 系统要求

- **Python**: 3.10 或更高版本
- **Node.js**: 18.0 或更高版本
- **操作系统**: Windows、Linux 或 macOS
- **uv**: Python 包管理器（推荐）

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd LingNexus
```

### 2. 安装 Python 依赖

使用 `uv` 安装 Python 依赖（推荐）：

```bash
# 安装 uv（如果尚未安装）
# Windows PowerShell:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

或者使用 pip：

```bash
pip install -r requirements.txt
```

### 3. 安装 Node.js 依赖

**重要**: 某些技能（如 docx、pdf、pptx、xlsx 等）依赖 Node.js 库，必须安装 Node.js 依赖才能正常使用。

```bash
# 使用 npm
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm
pnpm install
```

### 4. 设置 API Key

创建 `.env` 文件（在项目根目录）：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API Key：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

或设置环境变量：

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key"
```

### 5. 验证安装

运行测试脚本验证安装：

```bash
# 测试 Python 环境
uv run python tests/test_setup.py

# 测试 Node.js 环境（docx 技能）
npm run test:docx

# 或直接运行
node tests/test_docx_simple.js
```

## 依赖说明

### Python 依赖

主要 Python 依赖（在 `pyproject.toml` 中定义）：

- `agentscope` - 多智能体框架
- `pyyaml` - YAML 配置文件解析
- `python-dotenv` - 环境变量管理
- `python-docx` - Word 文档处理

### Node.js 依赖

主要 Node.js 依赖（在 `package.json` 中定义）：

- `docx` - Word 文档创建（docx 技能使用）

## 可选依赖

某些高级功能可能需要额外的依赖：

- `pandoc` - 文档格式转换（用于 pdf 技能）
- `LibreOffice` - 文档转换（用于 pptx 技能）
- `poppler-utils` - PDF 处理（用于 pdf 技能）

## 常见问题

### Q: 为什么需要同时安装 Python 和 Node.js 依赖？

A: LingNexus 使用 AgentScope 框架（Python）和 Claude Skills。某些技能（如 docx、pdf）使用 Node.js 库，因此需要两种运行环境。

### Q: Node.js 依赖可以全局安装吗？

A: 不建议。全局安装的模块无法在项目的 `require()` 中直接使用。请使用 `npm install` 在项目本地安装。

### Q: 如何检查依赖是否正确安装？

A: 运行以下命令：

```bash
# 检查 Python 依赖
uv run python -c "import agentscope; print('OK')"

# 检查 Node.js 依赖
npm run test:docx
```

### Q: 安装失败怎么办？

A: 常见解决方法：

1. 确保 Node.js 版本 >= 18.0：`node --version`
2. 确保 Python 版本 >= 3.10：`python --version`
3. 清除缓存后重试：
   ```bash
   # Python
   uv cache clean
   rm -rf .venv
   uv sync

   # Node.js
   rm -rf node_modules package-lock.json
   npm install
   ```

## 目录结构

安装后的项目结构：

```
LingNexus/
├── .venv/                  # Python 虚拟环境（uv 创建）
├── node_modules/           # Node.js 依赖
├── lingnexus/             # 核心代码
├── skills/                # 技能目录
│   ├── external/          # Claude Skills
│   └── internal/          # 自定义技能
├── tests/                 # 测试脚本
├── docs/                  # 文档
├── pyproject.toml         # Python 项目配置
├── package.json           # Node.js 项目配置
└── .env                   # 环境变量（需创建）
```

## 下一步

安装完成后，请参考：

- [快速开始](./quick_start.md) - 基本使用
- [CLI 使用指南](./cli_guide.md) - 交互式工具
- [架构设计](./architecture.md) - 系统架构

## 支持

如遇问题，请查看：
- [测试指南](./testing.md)
- [常见问题](./faq.md)（待创建）
- GitHub Issues
