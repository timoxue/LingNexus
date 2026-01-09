# 部署指南

## 环境要求

### 开发环境
- **Python**: 3.10+
- **Node.js**: 18.0+
- **Git**: 2.30+

### 生产环境
- **Python**: 3.10+
- **服务器**: 1GB+ RAM, 10GB+ 磁盘
- **操作系统**: Linux (Ubuntu 20.04+) 或 Windows Server

---

## 开发环境部署

### 1. 克隆项目

```bash
git clone https://github.com/your-org/LingNexus.git
cd LingNexus
git checkout skills_market
```

### 2. 后端部署

```bash
# 进入后端目录
cd platform/backend

# 使用 uv 安装依赖
pip install uv
uv sync

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库路径、API密钥等

# 启动开发服务器
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**环境变量配置 (.env)**：
```bash
# 数据库
DATABASE_URL=sqlite:///./data/skills.db

# API密钥
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# JWT配置
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 文件存储
SKILLS_BASE_PATH=skills/
UPLOAD_MAX_SIZE=10485760  # 10MB

# AgentScope配置
AGENTSCOPE_MODEL_NAME=qwen-max
AGENTSCOPE_TEMPERATURE=0.3

# 日志
LOG_LEVEL=INFO
LOG_FILE=logs/platform.log
```

### 3. 前端部署

```bash
# 进入前端目录
cd platform/frontend

# 安装依赖
npm install

# 复制环境变量文件
cp .env.example .env.local
# 编辑 .env.local，配置API地址

# 启动开发服务器
npm run dev
```

**前端环境变量 (.env.local)**：
```bash
# API地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用配置
VITE_APP_NAME=LingNexus
VITE_APP_VERSION=1.0.0

# 其他配置
VITE_UPLOAD_MAX_SIZE=10485760
```

### 4. 初始化数据库

```bash
# 自动创建数据库表和初始数据
cd platform/backend
uv run python -m scripts.init_db
```

### 5. 访问应用

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 生产环境部署

### 方案1: Docker Compose (推荐)

**1. 创建 docker-compose.yml**：

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./platform/backend
      dockerfile: Dockerfile
    container_name: lingnexus-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./skills:/app/skills
      - ./logs:/app/logs
    environment:
      - DATABASE_URL=sqlite:///./data/skills.db
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./platform/frontend
      dockerfile: Dockerfile
    container_name: lingnexus-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: lingnexus-nginx
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

**2. 创建后端 Dockerfile**：

```dockerfile
# platform/backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装Python依赖
RUN uv sync --frozen

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p data skills logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**3. 创建前端 Dockerfile**：

```dockerfile
# platform/frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源码
COPY . .

# 构建应用
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**4. 启动服务**：

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

### 方案2: 传统部署 (Systemd + Nginx)

#### 1. 后端部署

**创建 systemd 服务**：

```bash
# /etc/systemd/system/lingnexus-backend.service
[Unit]
Description=LingNexus Backend API
After=network.target

[Service]
Type=notify
User=www-data
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

**启动服务**：

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

#### 2. 前端部署

```bash
# 构建前端
cd platform/frontend
npm run build

# 复制到nginx目录
sudo cp -r dist /var/www/lingnexus/frontend
```

#### 3. Nginx 配置

```nginx
# /etc/nginx/sites-available/lingnexus
server {
    listen 80;
    server_name your-domain.com;

    # 前端文件
    location / {
        root /var/www/lingnexus/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 文件上传大小限制
    client_max_body_size 10M;
}

# HTTPS配置 (使用Let's Encrypt)
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 其他配置同上...
}
```

**启用配置**：

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/lingnexus /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载nginx
sudo systemctl reload nginx
```

---

## 备份策略

### 1. 数据库备份

**自动备份脚本**：

```bash
#!/bin/bash
# /usr/local/bin/backup-lingnexus.sh

BACKUP_DIR="/backup/lingnexus/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 备份数据库
cp /var/www/lingnexus/data/skills.db "$BACKUP_DIR/"
cp /var/www/lingnexus/data/skills.db-wal "$BACKUP_DIR/"
cp /var/www/lingnexus/data/skills.db-shm "$BACKUP_DIR/"

# 备份Skills文件系统
tar -czf "$BACKUP_DIR/skills.tar.gz" /var/www/lingnexus/skills/

# 备份配置文件
cp /var/www/lingnexus/backend/.env "$BACKUP_DIR/"

# 清理30天前的备份
find /backup/lingnexus/ -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR"
```

**设置定时任务**：

```bash
# 编辑crontab
sudo crontab -e

# 每天凌晨2点执行备份
0 2 * * * /usr/local/bin/backup-lingnexus.sh >> /var/log/lingnexus-backup.log 2>&1
```

### 2. 恢复数据

```bash
#!/bin/bash
# /usr/local/bin/restore-lingnexus.sh

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: restore-lingnexus.sh <backup_directory>"
    exit 1
fi

# 停止服务
sudo systemctl stop lingnexus-backend

# 恢复数据库
cp "$BACKUP_DIR/skills.db" /var/www/lingnexus/data/
cp "$BACKUP_DIR/skills.db-wal" /var/www/lingnexus/data/
cp "$BACKUP_DIR/skills.db-shm" /var/www/lingnexus/data/

# 恢复Skills文件系统
tar -xzf "$BACKUP_DIR/skills.tar.gz" -C /

# 恢复配置文件
cp "$BACKUP_DIR/.env" /var/www/lingnexus/backend/

# 重启服务
sudo systemctl start lingnexus-backend

echo "Restore completed from: $BACKUP_DIR"
```

---

## 监控和日志

### 1. 日志管理

```bash
# 日志轮转配置 /etc/logrotate.d/lingnexus
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

```bash
#!/bin/bash
# /usr/local/bin/monitor-lingnexus.sh

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

# 检查数据库大小
DB_SIZE=$(du -h /var/www/lingnexus/data/skills.db | awk '{print $1}')
echo "Database size: $DB_SIZE"

# 检查API响应
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $HTTP_CODE -ne 200 ]; then
    echo "ERROR: API health check failed with code $HTTP_CODE"
fi
```

**设置定时任务**：

```bash
# 每5分钟检查一次
*/5 * * * * /usr/local/bin/monitor-lingnexus.sh >> /var/log/lingnexus-monitor.log 2>&1
```

---

## 性能优化

### 1. SQLite 优化

```python
# 在应用启动时配置SQLite
import sqlite3

conn = sqlite3.connect('data/skills.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.execute('PRAGMA synchronous=NORMAL')
conn.execute('PRAGMA cache_size=-64000')  # 64MB
conn.execute('PRAGMA temp_store=MEMORY')
```

### 2. Nginx 缓存

```nginx
# 在nginx配置中添加
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/v1/skills {
    proxy_cache api_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_methods GET HEAD;
    proxy_pass http://127.0.0.1:8000;
}
```

### 3. Gzip 压缩

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

---

## 安全加固

### 1. 防火墙配置

```bash
# UFW (Uncomplicated Firewall)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. 证书管理

```bash
# 使用Let's Encrypt免费SSL证书
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 安全头配置

```nginx
# 在nginx配置中添加
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

---

## 故障排查

### 常见问题

**1. 数据库锁定错误**
```bash
# 检查WAL文件
ls -lh data/skills.db*

# 重启服务清理锁
sudo systemctl restart lingnexus-backend
```

**2. 磁盘空间不足**
```bash
# 清理日志
sudo journalctl --vacuum-time=7d

# 清理备份
find /backup/lingnexus/ -type d -mtime +30 -exec rm -rf {} +
```

**3. API响应慢**
```bash
# 查看进程
ps aux | grep uvicorn

# 查看数据库性能
sqlite3 data/skills.db "PRAGMA integrity_check;"
```

---

## 下一步

查看开发指南：`05-development-guide.md`
