# LingNexus 快速启动指南

> 5 分钟快速上手 LingNexus 智能多代理系统

## 📋 前置要求

- **Python**: 3.10 或更高版本
- **Node.js**: 18.0 或更高版本（仅 Platform 需要）
- **uv**: Python 包管理器（推荐）
- **API Key**: 阿里云通义千问 API Key

## 🚀 一键启动

### 1️⃣ 安装依赖

```bash
# 克隆仓库
git clone https://github.com/timoxue/LingNexus
cd LingNexus

# 安装依赖（推荐使用 uv）
uv sync
```

### 2️⃣ 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API Key
# DASHSCOPE_API_KEY=your_api_key_here
```

**获取 API Key**:
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API Key
4. 复制到 `.env` 文件中

### 3️⃣ 选择你的启动方式

---

## 🎯 方式一：使用 Framework（命令行）

适合场景：快速测试、脚本执行、数据采集

### 交互式对话

```bash
cd packages/framework
uv run python -m lingnexus.cli chat
```

### 竞品监控

```bash
# 监控所有项目
uv run python -m lingnexus.cli monitor

# 监控特定项目
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控状态
uv run python -m lingnexus.cli status

# 查询数据库
uv run python -m lingnexus.cli db --project "司美格鲁肽"
```

---

## 🌐 方式二：使用 Platform（Web 界面）

适合场景：可视化操作、团队协作、技能市场

### 启动后端

```bash
# 终端 1
cd packages/platform/backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

等待看到：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 启动前端

```bash
# 终端 2（新开一个窗口）
cd packages/platform/frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

等待看到：
```
VITE ready in xxx ms
➜  Local:   http://localhost:5173/
```

### 访问应用

- **前端界面**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **AgentScope Studio**: http://localhost:3000（自动启动）

### 注册账号

1. 打开 http://localhost:5173
2. 点击"注册"按钮
3. 填写用户名、邮箱、密码
4. 登录系统

### 核心功能

**技能市场** (`/marketplace`):
- 🔍 浏览 19+ 公开技能（无需登录）
- 🧪 试用技能（立即测试效果）
- ⭐ 收藏和评分技能
- 🚀 一键从技能创建 Agent

**技能创建器** (`/skill-creator`):
- 🤖 AI 驱动的渐进式问答
- 📊 LLM 智能评分系统
- 📝 自动生成技能元数据

**Agent 管理** (`/agents`):
- ➕ 创建和配置 Agent
- ▶️ 执行 Agent
- 📜 查看执行历史

---

## 📚 下一步

### 学习资源

- **[Framework 快速开始](docs/framework/getting-started.md)** - 深入了解 Framework
- **[Platform 用户手册](docs/platform/user-guide.md)** - Platform 完整指南
- **[架构设计](docs/development/architecture.md)** - 系统架构详解
- **[CLAUDE.md](CLAUDE.md)** - 开发者指南

### 常见问题

**Q: CDE 爬虫返回空白页面？**

A: 使用 CLI 监控系统自动触发：
```bash
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
```

**Q: asyncio loop 错误？**

A: 不要使用 `uv run` 运行 CDE 爬虫脚本，通过 CLI 调用即可。

**Q: 必须安装 ChromaDB 吗？**

A: 不必须。ChromaDB 是可选依赖，用于语义搜索。未安装时系统自动降级，核心功能完全可用。

**Q: 如何获取 API Key？**

A: 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)，注册/登录后创建 API Key。

---

## 🎉 开始使用

现在你已经准备好使用 LingNexus 了！

**推荐路径**：
1. 先尝试 **Framework CLI** 快速体验
2. 再使用 **Platform Web** 进行可视化操作
3. 阅读 **文档** 深入了解高级功能

**有问题？** 查看 [完整文档](docs/SUMMARY.md) 或提交 [Issue](https://github.com/timoxue/LingNexus/issues)

---

**祝你使用愉快！** 🚀
