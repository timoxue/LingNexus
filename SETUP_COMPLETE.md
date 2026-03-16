# LINGNEXUS 系统配置完成

## ✅ 已完成的配置

### 1. 目录结构
所有agent数据已迁移到项目目录：
```
D:\Projects\LingNexus\
├── agents/
│   ├── main/.openclaw/models.json
│   ├── coach/.openclaw/models.json
│   ├── investigator/.openclaw/models.json
│   ├── validator/.openclaw/models.json
│   └── deduplicator/.openclaw/models.json
├── scripts/
│   ├── claude-proxy.js          # Claude Code代理服务器
│   └── register-agents.sh
├── workflows/
│   └── biopharma-scouting.json
├── .env
└── openclaw.config.json
```

### 2. Claude Code认证解决方案
**问题**: OpenClaw的Anthropic SDK不支持Claude Code的OAuth token格式

**解决方案**: 
- 创建本地代理服务器 (`scripts/claude-proxy.js`)
- 代理监听端口: `18790`
- 功能: 将`x-api-key`头转换为`Authorization: Bearer`格式
- 配置: 在每个agent的`models.json`中添加anthropic provider配置

### 3. Agent配置

#### 模型分配
- **main**: claude-haiku-4-5-20251001 (轻量路由)
- **coach**: kimi-coding/kimi-k2-thinking (中文医药策略)
- **investigator**: google/gemini-2.5-flash (多语种极速)
- **validator**: claude-sonnet-4-6 (严格JSON遵循)
- **deduplicator**: openrouter/qwen/qwen3.5-27b (跨语种消歧)

#### API配置
所有agent的`models.json`包含:
```json
{
  "providers": {
    "anthropic": {
      "baseUrl": "http://host.docker.internal:18790",
      "api": "anthropic-messages",
      "apiKey": "ANTHROPIC_OAUTH_TOKEN"
    },
    "kimi-coding": { ... },
    "openrouter": { ... }
  }
}
```

### 4. Docker容器配置
```bash
docker run -d \
  --name openclaw-gateway \
  -p 18789:18789 \
  -v "D:/Projects/LingNexus:/workspace" \
  -v "C:/Users/ASUS/.openclaw:/home/node/.openclaw" \
  openclaw:local
```

## 🚀 启动流程

### 1. 启动代理服务器
```bash
cd D:\Projects\LingNexus
node scripts/claude-proxy.js &
```

### 2. 启动OpenClaw Gateway
```bash
docker start openclaw-gateway
```

### 3. 测试agent
```bash
# 测试main agent
docker exec openclaw-gateway bash -c 'cd /app && node openclaw.mjs agent --agent main --local -m "你好"'

# 测试其他agent
docker exec openclaw-gateway bash -c 'cd /app && node openclaw.mjs agent --agent coach --local -m "测试"'
```

## 📋 下一步

1. **测试完整workflow**: 运行`biopharma-scouting`工作流，验证5个agent的联动
2. **配置Feishu集成**: 绑定飞书渠道到main agent
3. **测试共享内存**: 验证blackboard在agent间的数据传递
4. **性能优化**: 根据实际使用情况调整模型和并发配置

## 🔧 故障排查

### 代理服务器未运行
```bash
# 检查进程
ps aux | grep claude-proxy

# 重启
cd D:\Projects\LingNexus
node scripts/claude-proxy.js &
```

### Agent认证失败
检查`D:\Projects\LingNexus\agents\{agent_name}\.openclaw\models.json`中的anthropic配置

### 容器无法访问代理
确保使用`host.docker.internal:18790`而不是`localhost:18790`

## 📝 配置文件位置

- **全局配置**: `C:\Users\ASUS\.openclaw\openclaw.json`
- **Agent配置**: `D:\Projects\LingNexus\agents\{agent_name}\.openclaw\models.json`
- **环境变量**: `D:\Projects\LingNexus\.env`
- **工作流定义**: `D:\Projects\LingNexus\workflows\biopharma-scouting.json`
