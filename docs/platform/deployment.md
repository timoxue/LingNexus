# Platform 部署指南

> LingNexus Platform 生产环境部署文档

---

## 目录

- [部署模式](#部署模式)
- [Docker 部署](#docker-部署)
- [传统部署](#传统部署)
- [数据库配置](#数据库配置)
- [安全配置](#安全配置)
- [监控和日志](#监控和日志)
- [备份策略](#备份策略)

---

## 部署模式

### 模式对比

| 模式 | 复杂度 | 成本 | 适用场景 |
|------|--------|------|---------|
| **单机部署** | ⭐ 低 | 低 | 个人/小团队试用 |
| **Docker Compose** | ⭐⭐ 中 | 中 | 中小团队生产环境 |
| **Kubernetes** | ⭐⭐⭐⭐ 高 | 高 | 大规模企业部署 |

### 推荐方案

- **开发环境**: 单机部署
- **测试环境**: Docker Compose
- **生产环境**: Docker Compose 或 Kubernetes

---

## Docker 部署

### 1. 准备工作

#### 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# CentOS/RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

#### 安装 Docker Compose

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 2. 构建镜像

```bash
# 从项目根目录
cd LingNexus

# 构建所有镜像
docker-compose -f docker/docker-compose.yml build

# 或单独构建
docker build -t lingnexus-platform-backend:1.0.0 -f docker/Dockerfile.backend packages/platform/backend
docker build -t lingnexus-platform-frontend:1.0.0 -f docker/Dockerfile.frontend packages/platform/frontend
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 复制示例配置
cp docker/.env.example docker/.env

# 编辑配置
vim docker/.env
```

**环境变量配置**:

```bash
# === 数据库 ===
POSTGRES_DB=lingnexus
POSTGRES_USER=lingnexus
POSTGRES_PASSWORD=your-secure-password-here

# === 后端配置 ===
BACKEND_PORT=8000
DATABASE_URL=postgresql://lingnexus:your-secure-password-here@db:5432/lingnexus
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# === 前端配置 ===
FRONTEND_PORT=80
VITE_API_BASE_URL=/api/v1

# === AgentScope ===
DASHSCOPE_API_KEY=your-dashscope-api-key

# === 存储路径 ===
DATA_PATH=/app/data
SKILLS_BASE_PATH=/app/skills

# === 日志 ===
LOG_LEVEL=INFO
LOG_FILE=/app/logs/platform.log
```

### 4. 启动服务

```bash
# 启动所有服务
docker-compose -f docker/docker-compose.yml up -d

# 查看服务状态
docker-compose -f docker/docker-compose.yml ps

# 查看日志
docker-compose -f docker/docker-compose.yml logs -f

# 停止服务
docker-compose -f docker/docker-compose.yml down
```

### 5. 访问应用

```
前端: http://your-domain.com
后端 API: http://your-domain.com/api/v1
API 文档: http://your-domain.com/api/docs
```

### 6. 初始化数据

```bash
# 进入后端容器
docker-compose -f docker/docker-compose.yml exec backend bash

# 初始化数据库
python -m scripts.init_db

# 创建管理员账户
python -m scripts.create_admin \
    --username admin \
    --password admin123 \
    --email admin@lingnexus.com

# 退出容器
exit
```

### 7. 配置 Nginx（可选）

如果使用 Nginx 反向代理：

```nginx
# /etc/nginx/sites-available/lingnexus
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # 前端文件
    location / {
        root /var/www/lingnexus/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 文件上传大小限制
    client_max_body_size 10M;
}
```

---

## 传统部署

### 1. 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Windows Server
- **Python**: 3.10+
- **Node.js**: 18+
- **数据库**: PostgreSQL 15+（可选，默认使用 SQLite）
- **Web 服务器**: Nginx 1.20+

### 2. 后端部署

#### 安装 Python 依赖

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 进入后端目录
cd packages/platform/backend

# 安装依赖
uv sync --extra all
```

#### 配置服务

创建 Systemd 服务 `/etc/systemd/system/lingnexus-backend.service`:

```ini
[Unit]
Description=LingNexus Backend API
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/lingnexus/backend
Environment="PATH=/var/www/lingnexus/backend/.venv/bin"
ExecStart=/var/www/lingnexus/backend/.venv/bin/gunicorn \
    main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/lingnexus/access.log \
    --error-logfile /var/log/lingnexus/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 启动服务

```bash
# 启用服务
sudo systemctl enable lingnexus-backend

# 启动服务
sudo systemctl start lingnexus-backend

# 查看状态
sudo systemctl status lingnexus-backend

# 查看日志
sudo journalctl -u lingnexus-backend -f
```

### 3. 前端部署

#### 构建前端

```bash
# 进入前端目录
cd packages/platform/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
```

#### 部署到 Nginx

```bash
# 复制构建产物
sudo cp -r dist /var/www/lingnexus/frontend

# 设置权限
sudo chown -R www-data:www-data /var/www/lingnexus/frontend
```

#### 配置 Nginx

```bash
# 创建 Nginx 配置
sudo vim /etc/nginx/sites-available/lingnexus
```

**Nginx 配置**:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端文件
    location / {
        root /var/www/lingnexus/frontend;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 文件上传大小限制
    client_max_body_size 10M;
}
```

#### 启用配置

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/lingnexus /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

---

## 数据库配置

### PostgreSQL（推荐用于生产环境）

#### 安装 PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 创建数据库和用户

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 在 psql 中执行
CREATE DATABASE lingnexus;
CREATE USER lingnexus WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE lingnexus TO lingnexus;
\q
```

#### 配置连接池

在 `.env` 文件中：

```bash
DATABASE_URL=postgresql://lingnexus:password@localhost:5432/lingnexus
```

### SQLite（默认，适合小型部署）

SQLite 无需额外配置，默认使用 `data/intelligence.db`。

#### SQLite 优化

```python
# 在应用启动时执行
import sqlite3

conn = sqlite3.connect('data/intelligence.db')
conn.execute('PRAGMA journal_mode=WAL')      # 启用 WAL
conn.execute('PRAGMA synchronous=NORMAL')     # 平衡性能和安全
conn.execute('PRAGMA cache_size=-64000')      # 64MB 缓存
conn.execute('PRAGMA temp_store=MEMORY')      # 临时表在内存
```

---

## 安全配置

### 1. SSL/TLS 配置

#### 使用 Let's Encrypt（免费）

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

#### 手动配置 SSL

如果有自己的证书：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
}
```

### 2. 防火墙配置

```bash
# UFW (Uncomplicated Firewall)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# 查看状态
sudo ufw status
```

### 3. 数据加密

#### 生成加密密钥

```bash
# 生成 32 字节随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 设置环境变量
export LINGNEXUS_ENCRYPTION_KEY="your-32-byte-key-here"
```

#### 在 .env 中配置

```bash
LINGNEXUS_ENCRYPTION_KEY=your-32-byte-key-here
```

---

## 监控和日志

### 1. 日志管理

#### 日志轮转

创建 `/etc/logrotate.d/lingnexus`:

```
/var/log/lingnexus/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload lingnexus-backend > /dev/null 2>&1 || true
    endscript
}
```

### 2. 监控脚本

创建健康检查脚本 `/usr/local/bin/monitor-lingnexus.sh`:

```bash
#!/bin/bash
# 监控 LingNexus 服务

# 检查服务状态
if ! systemctl is-active --quiet lingnexus-backend; then
    echo "ERROR: Backend service is not running"
    systemctl restart lingnexus-backend
fi

# 检查磁盘空间
DISK_USAGE=$(df /var/www/lingnexus | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "WARNING: Disk usage is ${DISK_USAGE}%"
fi

# 检查 API 响应
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $HTTP_CODE -ne 200 ]; then
    echo "ERROR: API health check failed with code $HTTP_CODE"
fi
```

设置定时任务：

```bash
# 编辑 crontab
sudo crontab -e

# 每5分钟检查一次
*/5 * * * * /usr/local/bin/monitor-lingnexus.sh >> /var/log/lingnexus-monitor.log 2>&1
```

### 3. 性能监控

使用 Prometheus + Grafana（可选）：

```yaml
# docker-compose.yml 添加
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 备份策略

### 1. 数据库备份

#### 自动备份脚本

创建 `/usr/local/bin/backup-lingnexus.sh`:

```bash
#!/bin/bash
# LingNexus 数据库备份脚本

BACKUP_DIR="/backup/lingnexus/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 备份数据库
if [ -f "/var/www/lingnexus/data/intelligence.db" ]; then
    cp /var/www/lingnexus/data/intelligence.db "$BACKUP_DIR/"
fi

# 备份 Skills 文件
tar -czf "$BACKUP_DIR/skills.tar.gz" /var/www/lingnexus/skills/

# 备份配置文件
cp /var/www/lingnexus/backend/.env "$BACKUP_DIR/"

# 清理30天前的备份
find /backup/lingnexus/ -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR"
```

设置定时任务：

```bash
# 每天凌晨2点执行备份
0 2 * * * /usr/local/bin/backup-lingnexus.sh >> /var/log/lingnexus-backup.log 2>&1
```

### 2. 恢复数据

```bash
#!/bin/bash
# LingNexus 数据恢复脚本

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: restore-lingnexus.sh <backup_directory>"
    exit 1
fi

# 停止服务
sudo systemctl stop lingnexus-backend

# 恢复数据库
cp "$BACKUP_DIR/intelligence.db" /var/www/lingnexus/data/

# 恢复 Skills 文件
tar -xzf "$BACKUP_DIR/skills.tar.gz" -C /

# 恢复配置文件
cp "$BACKUP_DIR/.env" /var/www/lingnexus/backend/

# 启动服务
sudo systemctl start lingnexus-backend

echo "Restore completed from: $BACKUP_DIR"
```

---

## 高可用配置（可选）

### 负载均衡

使用多实例 + Nginx 负载均衡：

```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

### 数据库主从复制

```bash
# 主服务器 (master)
# /etc/postgresql/15/main/postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 100

# 从服务器 (slave)
# /etc/postgresql/15/main/postgresql.conf
hot_standby = on
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 查看服务状态
sudo systemctl status lingnexus-backend

# 查看日志
sudo journalctl -u lingnexus-backend -n 50

# 检查端口占用
sudo netstat -tulpn | grep 8000
```

#### 2. 数据库连接失败

```bash
# 检查数据库是否运行
sudo systemctl status postgresql

# 测试连接
psql -U lingnexus -d lingnexus -h localhost

# 检查防火墙
sudo ufw status
```

#### 3. 前端页面空白

```bash
# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# 检查文件权限
ls -la /var/www/lingnexus/frontend
```

---

## 性能优化

### 1. 数据库优化

```sql
-- 定期 VACUUM
VACUUM ANALYZE;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_skills_author ON skills(author_id);
CREATE INDEX IF NOT EXISTS idx_skills_created ON skills(created_at DESC);
```

### 2. 应用优化

```bash
# 使用 Gunicorn 多进程
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### 3. 缓存优化

使用 Redis 缓存：

```bash
# 安装 Redis
sudo apt-get install redis-server

# 配置缓存
echo "CACHE_BACKEND=redis://localhost:6379/0" >> .env
```

---

## 下一步

- [管理员手册](admin-guide.md) - 系统管理
- [安全最佳实践](admin-guide.md#security) - 安全加固
- [监控和告警](admin-guide.md#monitoring) - 监控配置

---

**需要帮助？**
- 邮箱: support@lingnexus.com
- 文档: https://docs.lingnexus.com
