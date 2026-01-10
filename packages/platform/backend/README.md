# LingNexus Platform Backend

低代码平台后端服务，基于 FastAPI 构建。

## 功能特性

- **Skill 管理**: 创建、编辑、删除 Skills
- **Agent 编排**: 可视化 Agent 工作流设计
- **任务调度**: 定时任务和事件触发
- **用户认证**: JWT 令牌认证和权限管理
- **审计日志**: 符合 FDA 21 CFR Part 11 标准

## 开发

```bash
# 安装依赖
cd packages/platform/backend
uv sync --extra dev

# 启动开发服务器
uv run dev

# 访问 API 文档
# http://localhost:8000/docs
```

## 部署

参考 [部署指南](../../../../docs/platform/deployment.md)。

## API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
