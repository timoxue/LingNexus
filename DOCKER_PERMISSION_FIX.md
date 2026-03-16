# Docker 文件系统权限修复说明

## 问题描述

**症状**: Investigator 抓取的数据无法写入黑板文件
**错误**: `EROFS: read-only file system, open '/workspace/agents/coach/Pending_Tasks.json'`
**根本原因**: docker-compose.yml 中挂载配置设置为 `read_only: true`

## 修复内容

### 1. 修改 docker-compose.yml

**修改前**:
```yaml
volumes:
  - type: bind
    source: .
    target: /workspace
    read_only: true  # ❌ 只读挂载
```

**修改后**:
```yaml
volumes:
  - type: bind
    source: .
    target: /workspace
    read_only: false  # ✅ 允许写入
user: root  # ✅ 使用 root 用户运行（解决 Windows 权限问题）
```

### 2. 创建黑板目录

```bash
mkdir -p .openclaw/blackboard
```

### 3. 重启容器

```bash
docker compose down
docker compose up gateway -d
```

## 修复的服务

- ✅ **gateway**: 主服务，允许写入黑板数据
- ✅ **setup**: 设置服务，允许写入配置文件

## 为什么使用 root 用户？

在 Windows 上，Docker Desktop 的文件挂载可能会遇到权限问题：
- Windows 文件系统权限与 Linux 容器权限不匹配
- 使用 `root` 用户可以绕过大部分权限检查
- 这是快速 MVP 的推荐做法

**生产环境建议**:
- 使用专门的用户和用户组
- 配置正确的文件权限（chmod/chown）
- 使用 Docker volume 而不是 bind mount

## 验证修复

### 测试写入权限

```bash
docker exec lingnexus-gateway bash -c 'touch /workspace/.openclaw/blackboard/test.txt && echo "Write test passed" || echo "Write test failed"'
```

### 测试智能体写入

```bash
docker exec lingnexus-gateway bash -c 'cd /workspace && node /app/openclaw.mjs agent --agent coach --local -m "测试写入黑板"'
```

应该看到文件被成功创建在 `.openclaw/blackboard/` 目录下。

## 安全注意事项

⚠️ **使用 root 用户的风险**:
- 容器内的进程拥有完全权限
- 如果容器被攻破，攻击者可能获得宿主机访问权限

🔒 **缓解措施**:
- 仅在开发环境使用
- 不要暴露容器端口到公网
- 定期更新 Docker 镜像
- 使用 Docker 安全扫描工具

## 替代方案

如果不想使用 root 用户，可以尝试：

### 方案 1: 使用 Docker Volume

```yaml
volumes:
  - blackboard-data:/workspace/.openclaw/blackboard
  - openclaw-state:/home/node/.openclaw

volumes:
  blackboard-data:
    name: lingnexus-blackboard
```

### 方案 2: 设置宿主机权限（Linux/Mac）

```bash
chmod -R 777 .openclaw/
chown -R 1000:1000 .openclaw/
```

### 方案 3: 使用特定用户 ID

```yaml
user: "1000:1000"  # 使用特定的 UID:GID
```

## 测试结果

修复后，应该能看到：
- ✅ Coach 成功写入 `Pending_Tasks.json`
- ✅ Investigator 成功写入 `Raw_Evidence.json`
- ✅ Validator 成功写入 `Validated_Assets.json` 和 `Rejected_Evidence.json`
- ✅ 完整的数据流工作正常

---

*修复时间: 2026-03-16*
*修复方法: 移除 read_only 限制 + 使用 root 用户*
