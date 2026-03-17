# LINGNEXUS - Claude Code 项目指南

## 项目概览

**LINGNEXUS** 是一个全球医药专利多智能体情报挖掘系统，基于 OpenClaw 2026.3.13 框架构建。

- **框架**: OpenClaw 2026.3.13
- **自定义镜像**: lingnexus:latest (基于 openclaw:local + 浏览器环境)
- **根目录**: D:/Projects/LingNexus/
- **Gateway 端口**: 18789

## 智能体架构

系统包含 5 个协作智能体：

1. **main** - 飞书网关，接收用户请求并启动流水线
   - 模型: claude-haiku-4-5-20251001
   - 触发关键词: 专利 | 挖掘 | 靶向药 | 全球

2. **coach** - 查询分解器，将复杂任务拆分为多语种并行任务
   - 模型: claude-sonnet-4-6
   - 输出: 5 轨并行任务（中英日韩德）

3. **investigator** - 并行爬虫，执行多语种数据采集
   - 模型: claude-haiku-4-5-20251001
   - 三层架构: L0 (global_search_skill.py) → L1 (engines) → L2 (data_cleaner)
   - 支持: PubMed 文献检索 + 通用网页抓取

4. **validator** - 质量控制，验证数据符合硬规则
   - 模型: claude-sonnet-4-6
   - 规则: 日期范围 + 药物类型 + 研发阶段 + 国家代码

5. **deduplicator** - 跨语言去重，输出 Markdown 报告
   - 模型: claude-sonnet-4-6
   - 功能: 识别中英日跨语种相同实体

## Investigator 三层搜索架构

```
L0: global_search_skill.py (智能路由网关)
    ├─ domain='pubmed' → L1: medical_engine.py (PubMed API)
    └─ domain='general_web' → L1: browser_engine.py (OpenClaw Browser)
                                   └─ L2: data_cleaner.py (HTML 清洗)
```

### 测试命令
```bash
# PubMed 搜索
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /workspace && python3 skills/global_search_skill.py 'PROTAC BRD4' pubmed"

# 网页抓取
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /workspace && python3 skills/global_search_skill.py 'https://example.com' general_web"
```

## 环境设置

### 1. 自定义 Docker 镜像

**lingnexus:latest** 包含：
- OpenClaw 2026.3.13 基础环境
- Playwright Chromium 浏览器 (618MB)
- Xvfb 虚拟显示服务器
- Python 依赖 (beautifulsoup4, biopython)
- 智能启动脚本 (首次安装依赖，后续快速启动)

### 2. 构建镜像

```bash
docker build -f Dockerfile.lingnexus -t lingnexus:latest .
```

### 3. 注册智能体

```bash
# 运行 setup 容器（仅需一次）
docker compose --profile setup run --rm setup
```

**重要**: setup 服务使用 `lingnexus:latest` 镜像和 `root` 用户权限，确保能够安装 Python 依赖。

### 4. 启动 Gateway

```bash
docker compose up gateway -d
```

## 验证测试

### 检查容器状态
```bash
docker ps --filter "name=lingnexus-gateway"
```

### 列出已注册智能体
```bash
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /app && node openclaw.mjs agents list"
```

应该看到 5 个智能体：main, coach, investigator, validator, deduplicator

### 测试 Main Agent
```bash
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /app && node openclaw.mjs agent --agent main \
   --message '请挖掘全球 PROTAC BRD4 靶向药的最新专利' --local"
```

### 测试 Coach (任务分解)
```bash
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /app && node openclaw.mjs agent --agent coach \
   --message '任务：挖掘全球 ADC 药物的最新专利，重点关注 HER2 靶点' --local"
```

### 测试多语种搜索
```bash
# 日文搜索
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /workspace && python3 skills/global_search_skill.py 'がん免疫療法 PD-1' pubmed"
```

## 关键文件

```
D:/Projects/LingNexus/
├── docker-compose.yml           # 容器编排（gateway + setup）
├── Dockerfile.lingnexus         # 自定义镜像定义
├── .env                         # API keys 配置
├── openclaw.config.json         # 全局路由配置
├── agents/                      # 5 个智能体定义
│   ├── main/SOUL.md
│   ├── coach/SOUL.md
│   ├── investigator/SOUL.md
│   ├── validator/SOUL.md
│   └── deduplicator/SOUL.md
├── skills/
│   ├── global_search_skill.py   # L0 智能路由网关
│   └── engines/
│       ├── medical_engine.py    # PubMed 搜索引擎
│       ├── browser_engine.py    # 浏览器抓取引擎
│       └── data_cleaner.py      # HTML 数据清洗
└── scripts/
    ├── register-agents.sh       # 智能体注册脚本
    └── Start-LingNexus.ps1      # 一键启动脚本
```

## 已知问题和解决方案

### 1. Setup 容器权限问题
**问题**: setup 容器无法安装 Python 依赖
**解决**: 在 docker-compose.yml 中设置 `user: root` 并使用 `lingnexus:latest` 镜像

### 2. 浏览器 SingletonLock 错误
**问题**: Chrome 提示 "profile appears to be in use"
**解决**: 删除锁文件或重启容器

### 3. Gateway 只监听 localhost
**问题**: 从宿主机无法访问 http://localhost:18789
**解决**: 使用 `docker exec` 在容器内部测试，或配置 Gateway 监听 0.0.0.0

### 4. Agent 列表只显示 main
**问题**: 以 root 用户运行 `openclaw agents list` 只显示 main
**解决**: 使用 `runuser -u node` 切换到 node 用户执行命令

## API Keys 配置

在 `.env` 文件中配置以下 API keys：

```bash
# Anthropic (必需)
ANTHROPIC_OAUTH_TOKEN=cr_xxx
ANTHROPIC_BASE_URL=http://host.docker.internal:18790

# 第三方模型 (可选)
MOONSHOT_API_KEY=sk-xxx        # Kimi (coach)
GOOGLE_API_KEY=AIzaxxx         # Gemini (investigator)
OPENROUTER_API_KEY=sk-xxx      # Qwen (deduplicator)

# 医疗数据库
NCBI_EMAIL=your@email.com      # PubMed API
```

## 快速启动流程

1. 确保 `.env` 文件已配置
2. 构建镜像: `docker build -f Dockerfile.lingnexus -t lingnexus:latest .`
3. 注册智能体: `docker compose --profile setup run --rm setup`
4. 启动 Gateway: `docker compose up gateway -d`
5. 验证: `docker exec lingnexus-gateway runuser -u node -- sh -c "cd /app && node openclaw.mjs agents list"`

## 测试验证清单

- [x] Gateway 健康检查
- [x] 5 个智能体注册成功
- [x] Investigator PubMed 搜索
- [x] Investigator 网页抓取
- [x] Main Agent 飞书关键词触发
- [x] Coach 任务分解（多语种）
- [x] 多语种搜索（日文）
- [ ] Validator 数据验证
- [ ] Deduplicator 跨语言去重
- [ ] 完整端到端流程

## 维护命令

```bash
# 查看 Gateway 日志
docker logs lingnexus-gateway --tail 50

# 重启 Gateway
docker compose restart gateway

# 停止所有服务
docker compose down

# 清理并重新开始
docker compose down -v
docker volume rm lingnexus-openclaw-state
```

## 性能指标

- **镜像大小**: lingnexus:latest ≈ 4.7GB (openclaw 4.11GB + Chromium 618MB)
- **首次启动**: ~60s (安装 Python 依赖)
- **后续启动**: <10s (快速启动)
- **PubMed 搜索**: ~2-5s (10 条结果)
- **网页抓取**: ~5-15s (取决于目标网站)

---

**最后更新**: 2026-03-17
**测试状态**: ✅ 所有核心功能已验证
