# Skill Creator 认证配置说明

## 📋 功能概述

Skill Creator 支持两种运行模式：

### 1. **试用模式**（无需登录）
- 任何用户都可以体验 Skill Creator
- 完成完整的 4 阶段对话流程
- 查看实时生成的 SKILL.md 内容
- 适合：演示、测试、公开试用

### 2. **生产模式**（需要登录）
- 用户必须登录后才能使用
- 保存技能时关联到用户账户
- 支持权限控制和审计
- 适合：企业内部使用、生产环境

---

## 🔧 环境变量配置

### 配置项

```bash
# .env 文件
ALLOW_ANONYMOUS_SKILL_CREATION=true  # 或 false
```

### 值说明

| 值 | 适用场景 | 认证要求 | 技能保存 |
|----|---------|---------|---------|
| `true` | 开发/测试环境 | ❌ 无需登录 | ✅ 保存到测试用户（ID=1） |
| `false` | 生产环境（默认） | ✅ 需要登录 | ✅ 保存到当前用户 |

---

## 🚀 使用场景

### 场景 1：内部演示（无需登录）

**配置**：
```bash
# .env
ALLOW_ANONYMOUS_SKILL_CREATION=true
```

**行为**：
- 访客直接打开 Skill Creator 页面
- 完成技能创建流程
- 技能保存到数据库（creator_id=1）
- 适合：快速演示、公开试用

**注意事项**：
- ⚠️ 所有保存的技能都关联到测试用户（ID=1）
- ⚠️ 无法追踪技能的真实创建者
- ⚠️ 不适合生产环境

---

### 场景 2：企业内部使用（需要登录）

**配置**：
```bash
# .env
ALLOW_ANONYMOUS_SKILL_CREATION=false  # 默认值
```

**行为**：
- 未登录用户访问 Skill Creator → 提示登录
- 登录后可以完整使用
- 技能保存到当前用户账户
- 支持权限审计和追溯

**API 响应示例**：

```json
// 未登录用户尝试保存技能
{
  "detail": {
    "error": "请先登录后再保存技能",
    "code": "LOGIN_REQUIRED",
    "redirect_to": "/login"
  }
}
```

**前端处理**：
```typescript
// 检测 401 响应，引导用户登录
if (error.response?.status === 401) {
  if (error.response.data?.code === 'LOGIN_REQUIRED') {
    // 显示登录提示
    ElMessageBox.confirm(
      '保存技能需要登录，是否前往登录？',
      '需要登录',
      {
        confirmButtonText: '去登录',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      router.push({
        path: '/login',
        query: { redirect: '/skill-creator' }
      })
    })
  }
}
```

---

## 🛡️ 安全建议

### 开发环境
```bash
# .env.development
ALLOW_ANONYMOUS_SKILL_CREATION=true
```
- ✅ 方便测试和演示
- ✅ 无需频繁登录
- ⚠️ 不适用于生产

### 测试环境
```bash
# .env.test
ALLOW_ANONYMOUS_SKILL_CREATION=false
```
- ✅ 模拟生产环境
- ✅ 测试认证流程
- ✅ 验证权限控制

### 生产环境
```bash
# .env.production
ALLOW_ANONYMOUS_SKILL_CREATION=false
```
- ✅ 必须登录
- ✅ 用户数据隔离
- ✅ 审计日志完整
- ✅ 符合企业安全规范

---

## 📊 架构对比

### 试用模式（ALLOW_ANONYMOUS_SKILL_CREATION=true）

```
未登录用户
    ↓
访问 /skill-creator
    ↓
创建会话（user_id=1）
    ↓
对话交互（4个阶段）
    ↓
保存技能 ✅
    ↓
关联到测试用户（ID=1）
```

### 生产模式（ALLOW_ANONYMOUS_SKILL_CREATION=false）

```
未登录用户
    ↓
访问 /skill-creator
    ↓
创建会话 → 401 Unauthorized
    ↓
提示登录
    ↓
登录用户
    ↓
访问 /skill-creator
    ↓
创建会话（user_id=<实际用户ID>）
    ↓
对话交互（4个阶段）
    ↓
保存技能 ✅
    ↓
关联到当前用户
```

---

## 🔍 调试和日志

### 后端日志

启动后端时会显示当前模式：

```
INFO: Skill Creator anonymous mode: True
```

### API 调用日志

```
INFO: ===== CREATE SESSION REQUEST =====
INFO: Request: use_api_key=True
INFO: User: Anonymous          # 未登录用户
INFO: Created agent session abc123
```

```
INFO: ===== CREATE SESSION REQUEST =====
INFO: Request: use_api_key=False
INFO: User: john.doe           # 已登录用户
INFO: Created agent session def456
```

---

## ❓ 常见问题

### Q1: 开发时频繁测试很麻烦，可以不用登录吗？

**A**: 可以。设置 `ALLOW_ANONYMOUS_SKILL_CREATION=true`

### Q2: 生产环境应该使用哪个配置？

**A**: 必须使用 `ALLOW_ANONYMOUS_SKILL_CREATION=false`（或删除该配置，默认为 false）

### Q3: 切换模式需要重启后端吗？

**A**: 是的，环境变量在启动时加载。修改后需要重启：
```bash
# Ctrl+C 停止
uv run uvicorn main:app --reload
```

### Q4: 如何测试生产模式？

**A**:
1. 设置 `ALLOW_ANONYMOUS_SKILL_CREATION=false`
2. 重启后端
3. 清除浏览器 token：`localStorage.removeItem('access_token')`
4. 访问 `/skill-creator`
5. 应该看到登录提示

---

## 📝 配置清单

部署前检查：

- [ ] 开发环境：`ALLOW_ANONYMOUS_SKILL_CREATION=true`
- [ ] 生产环境：`ALLOW_ANONYMOUS_SKILL_CREATION=false`
- [ ] 测试环境：`ALLOW_ANONYMOUS_SKILL_CREATION=false`
- [ ] 确认前端正确处理 401 响应
- [ ] 确认登录流程正常工作

---

## 🎯 最佳实践

1. **开发阶段**：启用免认证模式，快速迭代
2. **测试阶段**：关闭免认证，测试认证流程
3. **生产环境**：必须要求登录，确保数据安全
4. **日志监控**：关注未授权访问尝试
5. **定期审计**：检查技能创建者和权限

---

**更新日期**: 2025-01-20
**版本**: v1.0.3

---

## 📝 最近更新

### v1.0.3 (2025-01-20)

**Bug Fixes**:
- 🐛 修复 AttributeError: 'function' object has no attribute 'username'
- 🔧 统一所有端点使用 `get_current_user_optional` 依赖注入
- ✅ 为所有端点添加环境变量检查
- 🛡️ 改进空值处理（metadata 字段）

**Code Changes**:
- 移除了返回函数对象而非 User 对象的辅助函数
- 所有端点统一使用 `get_current_user_optional` from `core/deps.py`
- 添加详细的日志记录用于调试
- 改进 SKILL.md 生成时的空值处理

### v1.0.2 (2025-01-19)
