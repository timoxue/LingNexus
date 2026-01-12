# 技能自动导入 - 快速测试指南

## 🚀 快速开始

### 第一步：确保后端有管理员用户

```bash
# 在后端目录运行
cd packages/platform/backend

# 如果没有用户，先注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123"
  }'

# 然后在数据库中手动将用户设置为超级用户
# 或者使用 SQLite 工具打开数据库：
UPDATE users SET is_superuser = 1 WHERE username = 'admin';
```

### 第二步：测试 API 端点

#### 1. 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**响应：**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

#### 2. 查看同步状态

```bash
curl -X GET http://localhost:8000/api/v1/skills/sync/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "framework_path": "D:/internal/LingNexus/packages/framework",
  "skills_dir_exists": true,
  "external_skills_count": 15,
  "internal_skills_count": 3,
  "total_skills_count": 18
}
```

#### 3. 执行同步（仅新技能）

```bash
curl -X POST http://localhost:8000/api/v1/skills/sync \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "total": 18,
  "created": 18,
  "updated": 0,
  "skipped": 0,
  "failed": 0,
  "errors": [],
  "message": "创建 18 个新技能"
}
```

#### 4. 强制更新所有技能

```bash
curl -X POST "http://localhost:8000/api/v1/skills/sync?force_update=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 第三步：前端集成测试

#### 选项 A：在现有页面添加按钮

编辑技能市场或管理页面，添加同步按钮：

```vue
<template>
  <div class="page-header">
    <h1>技能市场</h1>
    <!-- 添加这行 -->
    <SkillSyncButton @success="loadSkills" />
  </div>
</template>

<script setup lang="ts">
import SkillSyncButton from '@/components/SkillSyncButton.vue'
// ... 其他代码
</script>
```

#### 选项 B：创建专用同步页面

```vue
<!-- src/views/admin/SkillSync.vue -->
<template>
  <div class="skill-sync-page">
    <PageHeader title="技能同步" />
    <SkillSyncButton @success="handleSuccess" />
  </div>
</template>

<script setup lang="ts">
import SkillSyncButton from '@/components/SkillSyncButton.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const handleSuccess = () => {
  router.push('/marketplace')
}
</script>
```

添加路由（如果需要）：

```typescript
// src/router/index.ts
{
  path: '/admin/skill-sync',
  name: 'SkillSync',
  component: () => import('@/views/admin/SkillSync.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
}
```

### 第四步：验证同步结果

#### 通过 API 查看

```bash
curl -X GET http://localhost:8000/api/v1/skills \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 通过前端查看

访问技能市场页面：http://localhost:5173/marketplace

应该能看到从 Framework 同步过来的所有技能。

## 📋 测试检查清单

- [ ] 后端服务正常运行
- [ ] 前端服务正常运行
- [ ] 已创建管理员用户
- [ ] Framework skills 目录存在
- [ ] 可以查看同步状态
- [ ] 可以执行同步操作
- [ ] 同步后技能列表更新
- [ ] 强制更新功能正常
- [ ] 错误处理正常

## 🐛 常见问题

### Q: 提示权限不足
**A**: 确保当前用户是超级用户（`is_superuser = 1`）

### Q: 找不到 Framework 路径
**A**: 检查 `packages/platform/backend/services/skill_sync.py` 第 130 行的路径计算逻辑

### Q: 同步成功但前端没显示
**A**:
1. 检查前端的 `@success` 回调是否正确
2. 确认技能列表刷新逻辑
3. 查看浏览器控制台是否有错误

### Q: 部分技能同步失败
**A**:
1. 查看返回的 `errors` 字段
2. 检查对应技能的 SKILL.md 文件格式
3. 确认 YAML front matter 格式正确

## 🎯 下一步

同步完成后，你可以：

1. **浏览技能市场** - 查看所有同步的技能
2. **创建 Agent** - 从技能一键创建 Agent
3. **试用技能** - 直接在技能市场试用
4. **评分收藏** - 对技能进行评分和收藏

## 📚 相关文档

- [完整使用指南](../frontend/docs/SKILL_SYNC_GUIDE.md)
- [后端 API 文档](http://localhost:8000/docs)
- [技能市场功能](../frontend/docs/marketplace.md)
