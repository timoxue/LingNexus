# Skills Marketplace 2.0 测试指南

## 📋 系统状态

**最后更新**: 2026-01-12
**版本**: v1.0.0
**状态**: ✅ 生产就绪

### 服务状态

| 服务 | 地址 | 状态 | 说明 |
|------|------|------|------|
| **Frontend** | http://localhost:5173 | ✅ 运行中 | Vue 3 + Element Plus |
| **Backend** | http://localhost:8000 | ✅ 运行中 | FastAPI |
| **Database** | SQLite | ✅ 正常 | 8 个测试技能 |
| **API** | /api/v1/* | ✅ 正常 | 所有端点可访问 |

### 数据库统计

```
Total Skills: 8
Public Skills: 8 (100%)
Official Skills: 8 (100%)
External Skills: 5
Internal Skills: 3
```

**测试技能列表**:
1. docx-word - 创建 Word 文档
2. pdf-processor - 处理 PDF 文件
3. pptx-presentation - 生成 PowerPoint 演示
4. data-analyzer - 数据分析和可视化
5. web-scraper - 网站数据提取
6. email-assistant - 撰写专业邮件
7. code-reviewer - 代码审查
8. translator - 多语言翻译

---

## 🧪 测试流程

### 阶段 1: 无需登录的功能

#### 1.1 浏览技能市场

**访问**: http://localhost:5173/marketplace

**检查项**:
- ✅ 技能卡片正常显示（8 个技能）
- ✅ 每个卡片显示：
  - 官方认证标签（绿色）
  - 类别标签（外部/内部）
  - 技能名称
  - 技能描述
  - 创建者名称
  - 使用次数
  - 评分（如果有）
  - 共享范围标签

**预期结果**: 所有技能卡片样式统一，信息完整

#### 1.2 搜索功能

**操作**:
1. 在搜索框输入 "pdf"
2. 观察技能列表变化

**预期结果**:
- 只显示 "pdf-processor" 技能
- 搜索实时响应（无需点击按钮）

**其他测试搜索词**:
- "docx" → 应显示 "docx-word"
- "翻译" → 应显示 "translator"
- "data" → 应显示 "data-analyzer"

#### 1.3 筛选功能

**类别筛选**:
- 选择 "外部技能" → 应显示 5 个外部技能
- 选择 "内部技能" → 应显示 3 个内部技能

**排序功能**:
- "最新创建" → 按创建时间排序
- "评分最高" → 按评分排序（目前都是 null）
- "使用最多" → 按使用次数排序（目前都是 0）

**共享范围筛选**:
- 选择 "公开" → 应显示所有 8 个技能
- 选择 "团队" → 应显示 0 个技能

**官方筛选**:
- 勾选 "只看官方" → 应显示所有 8 个技能
- 取消勾选 → 应显示所有 8 个技能

#### 1.4 查看技能详情

**操作**:
1. 点击任意技能卡片的 "查看详情" 按钮
2. 或点击技能名称

**检查项**:
- ✅ 技能详情页加载
- ✅ 显示技能元数据（类别、共享范围、官方认证）
- ✅ 显示技能名称、创建者、使用次数、版本
- ✅ 显示技能描述
- ✅ 显示技能内容（markdown 格式）
- ✅ 显示统计信息（使用次数、评分人数、平均分）

**预期结果**: 详情页信息完整，样式美观

---

### 阶段 2: 需要登录的功能

#### 2.1 用户注册

**访问**: http://localhost:5173/register

**操作**:
1. 填写注册表单：
   - 用户名: testuser
   - 邮箱: test@example.com
   - 密码: Test123456
   - 全名: Test User
2. 点击 "注册" 按钮

**预期结果**:
- 注册成功，自动跳转到登录页或仪表板

#### 2.2 用户登录

**访问**: http://localhost:5173/login

**操作**:
1. 如果已注册，直接登录：
   - 用户名: testuser
   - 密码: Test123456
2. 点击 "登录" 按钮

**预期结果**:
- 登录成功，跳转到仪表板
- 右上角显示用户名

**或使用管理员账号**:
- 用户名: admin
- 密码: admin123

#### 2.3 收藏技能

**前提**: 已登录

**操作**:
1. 访问技能市场
2. 点击技能卡片右上角的星星图标（未收藏状态）
3. 观察星星变为实心（已收藏状态）

**预期结果**:
- 星星图标变为实心
- 显示提示 "收藏成功"
- 技能卡片的收藏状态更新

**测试取消收藏**:
1. 再次点击星星图标（已收藏状态）
2. 观察星星变为空心

**预期结果**:
- 星星图标变为空心
- 显示提示 "已取消收藏"

#### 2.4 查看我的收藏

**前提**: 已登录并收藏了至少 1 个技能

**操作**:
1. 访问技能市场
2. 点击右上角 "我的收藏" 按钮

**预期结果**:
- 弹出对话框
- 显示所有已收藏的技能列表
- 表格包含：名称、类别、使用次数、评分、操作

**测试操作**:
- 点击 "查看" → 跳转到技能详情
- 点击 "试用" → 打开试用对话框
- 点击 "取消收藏" → 从收藏列表移除

#### 2.5 评分技能

**前提**: 已登录

**操作**:
1. 访问任意技能详情页
2. 找到 "用户评分" 部分
3. 点击星星（1-5 星）
4. 选择评分

**预期结果**:
- 显示提示 "评分成功"
- 评分状态更新
- 技能的平均评分重新计算

**注意**: 每个用户只能对每个技能评分一次

#### 2.6 试用技能（需要登录）

**前提**: 已登录

**方式一：从技能市场**
1. 访问技能市场
2. 点击技能卡片的 "立即试用" 按钮

**方式二：从技能详情**
1. 访问技能详情页
2. 点击右侧 "操作" 面板的 "立即试用" 按钮

**操作**:
1. 在试用对话框中输入消息：
   - 例如：对于 translator 技能，输入 "请翻译：Hello World"
2. 点击 "执行" 按钮

**预期结果**:
- 显示加载状态
- 显示试用结果：
  - 状态（成功/失败）
  - 执行时间（秒）
  - 输出内容（成功时）
  - 错误信息（失败时）

**测试不同技能**:
- `translator`: 输入翻译任务
- `email-assistant`: 输入邮件主题
- `docx-word`: 输入文档生成请求

**注意**: 试用功能需要连接到 AgentScope Framework，如果 Framework 不可用会返回错误

---

### 阶段 3: Agent 创建

#### 3.1 从技能创建 Agent

**前提**: 已登录

**方式一：从技能市场**
1. 访问技能市场
2. 点击技能卡片的 "创建 Agent" 按钮

**方式二：从技能详情**
1. 访问技能详情页
2. 点击右侧 "操作" 面板的 "创建代理" 按钮

**操作**:
1. 填写创建表单：
   - Agent 名称: 自动填充为 "{技能名}助手"
   - 描述: 自动填充为 "使用 {技能名} 技能的 AI 助手"
   - 模型: 选择 "Qwen Max"（默认）
   - 温度: 调整滑块（默认 0.7）
2. 点击 "创建" 按钮

**预期结果**:
- 显示提示 "Agent 创建成功" 或 "代理创建成功"
- 对话框关闭
- 自动跳转到 Agent 列表页面

**测试跳转**:
- 应跳转到 http://localhost:5173/agents
- Agent 列表中应显示新创建的 Agent

**验证 Agent**:
1. 点击 Agent 名称进入详情页
2. 检查 Agent 配置：
   - 名称
   - 描述
   - 使用的技能
   - 模型配置

**测试 Agent 执行**:
1. 在 Agent 详情页
2. 输入测试消息
3. 执行 Agent

**预期结果**: Agent 使用配置的技能处理消息

---

## 🔍 API 测试

### 使用 curl 测试 API

#### 获取技能列表

```bash
# 获取所有技能
curl http://localhost:8000/api/v1/marketplace/skills

# 获取公开技能
curl http://localhost:8000/api/v1/marketplace/skills?sharing_scope=public

# 搜索技能
curl http://localhost:8000/api/v1/marketplace/skills?search=pdf

# 按类别筛选
curl http://localhost:8000/api/v1/marketplace/skills?category=external

# 排序
curl http://localhost:8000/api/v1/marketplace/skills?sort_by=created_at

# 分页
curl http://localhost:8000/api/v1/marketplace/skills?skip=0&limit=5
```

#### 获取技能详情

```bash
# 获取 ID 为 1 的技能
curl http://localhost:8000/api/v1/marketplace/skills/1
```

#### 试用技能（需要登录）

```bash
# 先登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 试用技能
curl -X POST http://localhost:8000/api/v1/marketplace/skills/1/try \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"测试消息"}'
```

#### 收藏技能（需要登录）

```bash
# 收藏
curl -X POST http://localhost:8000/api/v1/marketplace/skills/1/save \
  -H "Authorization: Bearer $TOKEN"

# 取消收藏
curl -X DELETE http://localhost:8000/api/v1/marketplace/skills/1/save \
  -H "Authorization: Bearer $TOKEN"
```

#### 评分技能（需要登录）

```bash
curl -X POST http://localhost:8000/api/v1/marketplace/skills/1/rate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rating":5}'
```

#### 创建 Agent（需要登录）

```bash
curl -X POST http://localhost:8000/api/v1/marketplace/skills/1/create-agent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "测试 Agent",
    "description": "这是一个测试 Agent",
    "model_name": "qwen-max",
    "temperature": 0.7
  }'
```

---

## 🐛 常见问题排查

### 问题 1: 技能市场页面空白

**可能原因**:
- 前端服务未启动
- 后端服务未启动
- API 连接失败

**排查步骤**:
1. 检查前端是否运行: http://localhost:5173
2. 检查后端是否运行: http://localhost:8000/docs
3. 检查浏览器控制台（F12）是否有错误

### 问题 2: 技能列表不显示

**可能原因**:
- 数据库为空
- API 返回错误

**排查步骤**:
1. 访问 http://localhost:8000/api/v1/marketplace/skills
2. 检查是否返回数据
3. 检查数据库文件是否存在: `packages/platform/backend/lingnexus_platform_new.db`

### 问题 3: 登录失败

**可能原因**:
- 用户不存在
- 密码错误
- 后端认证问题

**排查步骤**:
1. 确认使用正确的账号：
   - admin / admin123（管理员）
   - 或自己注册的账号
2. 检查后端日志
3. 使用 API 测试登录:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

### 问题 4: 试用功能失败

**可能原因**:
- AgentScope Framework 未运行
- 技能配置错误
- 模型 API key 未配置

**排查步骤**:
1. 检查后端日志
2. 确认 Framework 可用
3. 检查 `.env` 文件中的 API 配置

### 问题 5: 收藏/评分功能不工作

**可能原因**:
- 未登录
- Token 过期
- 权限问题

**排查步骤**:
1. 确认已登录
2. 检查浏览器 localStorage 中的 token
3. 重新登录获取新 token

---

## ✅ 测试检查清单

### 功能测试

- [ ] 浏览技能市场（8 个技能显示）
- [ ] 搜索技能（实时搜索）
- [ ] 类别筛选（外部/内部）
- [ ] 排序功能（最新/评分/使用）
- [ ] 共享范围筛选（公开/团队）
- [ ] 官方技能筛选
- [ ] 查看技能详情
- [ ] 用户注册
- [ ] 用户登录
- [ ] 收藏技能
- [ ] 取消收藏
- [ ] 查看我的收藏列表
- [ ] 评分技能
- [ ] 试用技能
- [ ] 从技能创建 Agent
- [ ] 查看 Agent 详情
- [ ] 执行 Agent

### UI/UX 测试

- [ ] 页面加载速度正常
- [ ] 响应式布局（不同屏幕尺寸）
- [ ] 按钮状态变化（hover/active/disabled）
- [ ] 加载状态显示
- [ ] 错误提示清晰
- [ ] 成功提示显示
- [ ] 表单验证生效
- [ ] 对话框打开/关闭动画流畅
- [ ] 路由跳转正常
- [ ] 面包屑导航（如有）

### 兼容性测试

- [ ] Chrome 浏览器
- [ ] Firefox 浏览器
- [ ] Edge 浏览器
- [ ] Safari 浏览器（如有 Mac）

### 性能测试

- [ ] 技能列表加载时间 < 1s
- [ ] 搜索响应时间 < 500ms
- [ ] API 请求重试机制生效
- [ ] 大量技能时渲染性能（50+ 技能）

---

## 📊 测试报告模板

### 测试环境

```
日期: _______________
测试人员: _______________
浏览器: _______________
操作系统: _______________
```

### 测试结果

| 功能 | 测试项 | 结果 | 备注 |
|------|--------|------|------|
| 浏览技能 | 列表显示 | ☐ 通过 ☐ 失败 | |
| 搜索 | 实时搜索 | ☐ 通过 ☐ 失败 | |
| 筛选 | 类别筛选 | ☐ 通过 ☐ 失败 | |
| 筛选 | 排序功能 | ☐ 通过 ☐ 失败 | |
| 详情 | 查看详情 | ☐ 通过 ☐ 失败 | |
| 认证 | 用户注册 | ☐ 通过 ☐ 失败 | |
| 认证 | 用户登录 | ☐ 通过 ☐ 失败 | |
| 收藏 | 收藏技能 | ☐ 通过 ☐ 失败 | |
| 收藏 | 取消收藏 | ☐ 通过 ☐ 失败 | |
| 评分 | 评分技能 | ☐ 通过 ☐ 失败 | |
| 试用 | 试用技能 | ☐ 通过 ☐ 失败 | |
| Agent | 创建 Agent | ☐ 通过 ☐ 失败 | |

### 发现的问题

1. **问题描述**:
   - 严重程度: ☐ 高 ☐ 中 ☐ 低
   - 重现步骤:
   - 期望结果:
   - 实际结果:

2. **问题描述**:
   - 严重程度: ☐ 高 ☐ 中 ☐ 低
   - 重现步骤:
   - 期望结果:
   - 实际结果:

### 改进建议

1.

2.

3.

---

## 🚀 部署检查清单

### 生产环境部署前

- [ ] 更改默认管理员密码
- [ ] 配置 HTTPS
- [ ] 设置 CORS 正确的源
- [ ] 配置数据库备份
- [ ] 设置日志记录
- [ ] 配置监控告警
- [ ] 性能优化（gzip, 缓存）
- [ ] 安全加固（CSRF, XSS 防护）
- [ ] API 限流配置
- [ ] 错误监控（Sentry 等）

---

## 📝 相关文档

- **项目 README**: `README.md`
- **开发指南**: `CLAUDE.md`
- **API 文档**: http://localhost:8000/docs
- **前端代码**: `packages/platform/frontend/`
- **后端代码**: `packages/platform/backend/`

---

## 🎉 测试完成

如果所有测试通过，Skills Marketplace 2.0 即可正式上线！

**下一步**:
1. 部署到生产环境
2. 添加更多技能
3. 收集用户反馈
4. 持续优化性能

**祝测试顺利！** 🚀
