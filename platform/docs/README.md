# LingNexus Skill Platform - 技术文档

基于 AgentScope 的低代码智能体构建平台，面向无编程技能的业务人员。

## 📚 文档目录

### 快速开始
- **[架构设计](00-architecture.md)** - 系统架构、技术栈选型、数据流设计
- **[部署指南](04-deployment-guide.md)** - 开发/生产环境部署、Docker配置

### 核心设计
- **[数据库Schema](01-database-schema.md)** - SQLite数据库设计、表结构、索引优化
- **[API接口设计](02-api-design.md)** - RESTful API定义、认证授权、接口规范
- **[前端设计](03-frontend-design.md)** - Vue3组件设计、状态管理、路由配置

### 开发指南
- **[开发指南](05-development-guide.md)** - 开发环境搭建、代码规范、测试、调试

---

## 🎯 项目概述

LingNexus Skill Platform 是一个无代码/低代码智能体构建平台，让业务人员无需编程知识即可创建、组合和分享 AI Skills。

### 核心特性

- 🎨 **可视化编辑** - 拖拽式构建智能体
- 📦 **Skill 市场** - 创建、分享、复用技能
- 🔐 **权限管控** - 私有/团队/公开三级权限
- 💾 **纯本地存储** - 零云成本，数据完全可控
- 🚀 **AgentScope 集成** - 成熟的多智能体运行时

### 技术栈

**后端**：
- FastAPI (Python 3.10+)
- SQLite (元数据)
- AgentScope (Agent运行时)

**前端**：
- Vue 3 + TypeScript
- Element Plus (UI组件)
- React Flow (流程图编辑器)

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-org/LingNexus.git
cd LingNexus
git checkout skills_market
```

### 2. 后端启动

```bash
cd platform/backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

### 3. 前端启动

```bash
cd platform/frontend
npm install
npm run dev
```

### 4. 访问应用

- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 📖 文档阅读顺序

### 对于新开发者
1. [架构设计](00-architecture.md) - 了解整体架构
2. [开发指南](05-development-guide.md) - 搭建开发环境
3. [数据库Schema](01-database-schema.md) - 理解数据模型
4. [API接口设计](02-api-design.md) - 学习API设计

### 对于运维人员
1. [架构设计](00-architecture.md) - 了解系统架构
2. [部署指南](04-deployment-guide.md) - 部署到生产环境

### 对于产品经理
1. [架构设计](00-architecture.md) - 了解核心功能
2. [API接口设计](02-api-design.md) - 了解能力边界

---

## 📊 项目结构

```
platform/
├── backend/                  # 后端服务 (FastAPI)
│   ├── api/                 # API路由
│   ├── models/              # 数据模型
│   ├── services/            # 业务逻辑
│   ├── core/                # 核心配置
│   └── main.py              # 应用入口
│
├── frontend/                # 前端应用 (Vue3)
│   ├── src/
│   │   ├── api/            # API客户端
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   └── router/         # 路由配置
│   └── package.json
│
└── docs/                    # 技术文档
    ├── 00-architecture.md
    ├── 01-database-schema.md
    ├── 02-api-design.md
    ├── 03-frontend-design.md
    ├── 04-deployment-guide.md
    └── 05-development-guide.md
```

---

## 🔧 开发工具

### 必需工具
- Python 3.10+
- Node.js 18+
- Git

### 推荐工具
- VSCode (编辑器)
- Postman (API测试)
- Vue DevTools (前端调试)

### VSCode 扩展
```json
{
  "recommendations": [
    "vue.volar",
    "ms-python.python",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ]
}
```

---

## 🧪 测试

### 后端测试
```bash
cd platform/backend
uv run pytest
```

### 前端测试
```bash
cd platform/frontend
npm run test
```

---

## 📝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详见：[开发指南 - 贡献指南](05-development-guide.md#贡献指南)

---

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

## 🤝 联系方式

- 项目主页：https://github.com/your-org/LingNexus
- 问题反馈：https://github.com/your-org/LingNexus/issues
- 邮箱：support@lingnexus.com

---

**最后更新**：2024-01-15
