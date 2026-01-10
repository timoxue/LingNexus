# 文档索引

> LingNexus 项目完整文档索引

---

## 📚 文档结构

```
docs/
├── README.md                           # 文档总览（首页）
│
├── framework/                          # Framework 文档
│   ├── getting-started.md              # 快速开始 ✅
│   └── api.md                          # API 参考 ✅
│
├── platform/                           # Platform 文档
│   ├── user-guide.md                   # 用户手册 ✅
│   ├── admin-guide.md                  # 管理员手册 ⏳
│   ├── api.md                          # Platform API ⏳
│   └── deployment.md                   # 部署指南 ✅
│
└── development/                        # 开发文档
    ├── architecture.md                 # 架构设计 ✅
    ├── setup.md                        # 开发环境搭建 ✅
    ├── testing.md                      # 测试指南 ⏳
    ├── release.md                      # 发布流程 ⏳
    └── contributing.md                 # 贡献指南 ⏳
```

✅ 已创建 | ⏳ 待创建

---

## 🗂️ 按角色查看

### 👔 业务人员

**入门**:
1. [README.md](README.md) - 项目总览
2. [platform/user-guide.md](platform/user-guide.md) - Platform 使用手册

**进阶**:
- Skill 开发指南
- Agent 工作流设计
- 常见问题解答

### 💻 IT 开发人员

**Framework 使用**:
1. [framework/getting-started.md](framework/getting-started.md) - 快速开始
2. [framework/api.md](framework/api.md) - API 参考
3. [platform/deployment.md](platform/deployment.md) - 部署指南

**Platform 集成**:
- Platform API 文档
- 数据库设计
- 认证和授权

### 🔧 平台管理员

1. [platform/admin-guide.md](platform/admin-guide.md) - 管理员手册
2. [platform/deployment.md](platform/deployment.md) - 部署指南
3. 系统监控和日志
4. 安全配置
5. 备份和恢复

### 🛠️ 框架开发者

1. [development/architecture.md](development/architecture.md) - 架构设计
2. [development/setup.md](development/setup.md) - 开发环境搭建
3. [development/testing.md](development/testing.md) - 测试指南
4. [development/release.md](development/release.md) - 发布流程
5. [development/contributing.md](development/contributing.md) - 贡献指南

---

## 📖 按主题查看

### 架构和设计

- [architecture.md](development/architecture.md) - 系统架构详解
- [Framework vs Platform](README.md#架构概览) - 架构对比

### 安装和配置

- [环境搭建](development/setup.md) - 开发环境
- [部署指南](platform/deployment.md) - 生产部署
- [环境变量](development/setup.md#环境变量配置) - 配置说明

### API 和开发

- [Framework API](framework/api.md) - 核心 API 文档
- [Platform API](platform/api.md) - 平台 API（待完成）
- [快速开始](framework/getting-started.md) - 基础用法

### 运维和管理

- [部署指南](platform/deployment.md) - 部署步骤
- [监控和日志](platform/deployment.md#监控和日志) - 系统监控
- [备份策略](platform/deployment.md#备份策略) - 数据备份

### 医药行业特性

- [合规性要求](README.md#医药行业专精) - FDA/GCP 合规
- [审计日志](platform/admin-guide.md#audit-logs) - 审计配置
- [数据安全](platform/admin-guide.md#security) - 加密和权限

---

## 📝 文档状态

### 已完成文档

| 文档 | 路径 | 状态 |
|------|------|------|
| 文档总览 | [README.md](README.md) | ✅ |
| 快速开始 | [framework/getting-started.md](framework/getting-started.md) | ✅ |
| API 参考 | [framework/api.md](framework/api.md) | ✅ |
| 用户手册 | [platform/user-guide.md](platform/user-guide.md) | ✅ |
| 部署指南 | [platform/deployment.md](platform/deployment.md) | ✅ |
| 架构设计 | [development/architecture.md](development/architecture.md) | ✅ |
| 环境搭建 | [development/setup.md](development/setup.md) | ✅ |

### 待完善文档

| 文档 | 路径 | 优先级 |
|------|------|--------|
| 管理员手册 | [platform/admin-guide.md](platform/admin-guide.md) | P1 |
| Platform API | [platform/api.md](platform/api.md) | P1 |
| 测试指南 | [development/testing.md](development/testing.md) | P2 |
| 发布流程 | [development/release.md](development/release.md) | P2 |
| 贡献指南 | [development/contributing.md](development/contributing.md) | P2 |

---

## 🚀 快速链接

### 新手入门
- 我要安装 Framework → [framework/getting-started.md](framework/getting-started.md)
- 我要部署 Platform → [platform/deployment.md](platform/deployment.md)
- 我要学习使用 Platform → [platform/user-guide.md](platform/user-guide.md)

### 开发者
- 我要了解架构 → [development/architecture.md](development/architecture.md)
- 我要搭建开发环境 → [development/setup.md](development/setup.md)
- 我要查看 API → [framework/api.md](framework/api.md)

### 管理员
- 我要部署到生产环境 → [platform/deployment.md](platform/deployment.md)
- 我要管理系统 → [platform/admin-guide.md](platform/admin-guide.md)
- 我要配置安全 → [platform/deployment.md#安全配置](platform/deployment.md)

---

## 🔍 搜索功能

### 按关键词搜索

**API 相关**:
- `create_progressive_agent` → [framework/api.md#create_progressive_agent](framework/api.md#create_progressive_agent)
- `SkillLoader` → [framework/api.md#skillloader](framework/api.md#skillloader)
- `DailyMonitoringTask` → [framework/api.md#scheduler-api](framework/api.md#scheduler-api)

**部署相关**:
- `Docker` → [platform/deployment.md#docker-部署](platform/deployment.md#docker-部署)
- `Nginx` → [platform/deployment.md#配置-nginx](platform/deployment.md#配置-nginx)
- `备份` → [platform/deployment.md#备份策略](platform/deployment.md#备份策略)

**开发相关**:
- `Monorepo` → [development/architecture.md#monorepo-结构](development/architecture.md#monorepo-结构)
- `uv sync` → [development/setup.md#安装依赖](development/setup.md#安装依赖)
- `测试` → [development/testing.md](development/testing.md)

---

## 📊 文档统计

- **总文档数**: 8（已完成）+ 5（待完成）= 13
- **总字数**: 约 80,000 字
- **代码示例**: 200+ 个
- **架构图**: 5 个

---

## 🤝 贡献文档

欢迎帮助完善文档！请阅读：

1. [贡献指南](development/contributing.md) - 如何贡献
2. [文档规范](development/contributing.md#文档规范) - 文档写作规范
3. [提交流程](development/contributing.md#提交流程) - 提交流程

---

## 📞 获取帮助

- **文档不清晰?** → 反馈: https://github.com/your-org/LingNexus/issues
- **遇到问题?** → 提问: https://github.com/your-org/LingNexus/discussions
- **需要支持?** → 邮箱: support@lingnexus.com

---

**最后更新**: 2025-01-15
