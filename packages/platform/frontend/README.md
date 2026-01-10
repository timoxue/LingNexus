# LingNexus Platform Frontend

低代码平台前端服务，基于 Vue 3 + TypeScript + Vite 构建。

## 技术栈

- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全
- **Vite**: 极速前端构建工具
- **Element Plus**: Vue 3 组件库
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **Vue Flow**: 流程图编排组件
- **Axios**: HTTP 客户端

## 开发

```bash
# 安装依赖
cd packages/platform/frontend
npm install

# 启动开发服务器
npm run dev

# 访问前端
# http://localhost:5173
```

## 构建

```bash
# 构建生产版本
npm run build

# 预览构建产物
npm run preview
```

## 功能模块

- **Skills 管理**: Skills 的创建、编辑、删除和版本管理
- **Agents 编排**: 可视化 Agent 工作流设计器
- **任务调度**: 定时任务配置和监控
- **用户管理**: 用户、角色和权限管理
- **审计日志**: 符合 FDA 21 CFR Part 11 标准的审计追踪

## 部署

参考 [部署指南](../../../../docs/platform/deployment.md)。
