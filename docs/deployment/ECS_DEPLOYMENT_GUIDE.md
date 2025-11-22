# ECS 部署指南 - 剧本叙事结构分析系统

## 📋 目录

- [环境要求](#环境要求)
- [部署前准备](#部署前准备)
- [部署步骤](#部署步骤)
- [Nginx 配置](#nginx-配置)
- [验证部署](#验证部署)
- [故障排查](#故障排查)
- [维护管理](#维护管理)

---

## 🖥️ 环境要求

### ECS 服务器配置
- **系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **CPU**: 2 核心或更多
- **内存**: 4GB 或更多
- **磁盘**: 20GB 可用空间
- **已安装**: Docker, Docker Compose, Nginx

### 端口配置
- **容器内部端口**: 8000 (FastAPI 应用)
- **主机映射端口**: 8014 (配置为此端口以避免与其他服务冲突)
- **Nginx 监听端口**: 80 (HTTP) 或 443 (HTTPS)

---

## 📦 部署前准备

### 1. 检查端口占用

在部署前，确保端口 8014 未被占用：

```bash
# 检查端口 8014 是否被占用
sudo ss -tuln | grep 8014

# 如果端口被占用，找出占用进程
sudo lsof -i :8014

# 或者使用 netstat
sudo netstat -tuln | grep 8014
```

**如果端口被占用**，有两个选择：
1. 停止占用端口的服务
2. 修改配置文件使用其他端口（见下文"更改端口"部分）

### 2. 检查其他服务

查看正在运行的服务，避免冲突：

```bash
# 查看所有监听的端口
sudo ss -tuln

# 查看运行中的 Docker 容器
docker ps

# 查看 Nginx 配置的端口
sudo nginx -T | grep listen
```

### 3. 准备部署文件

将项目文件上传到 ECS 服务器：

```bash
# 方法 1: 使用 Git (推荐)
git clone <your-repository-url>
cd Director-Actor-Test-20251112

# 方法 2: 使用 SCP
scp -r /path/to/Director-Actor-Test-20251112 user@your-ecs-ip:/path/to/destination

# 方法 3: 使用 rsync
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /path/to/Director-Actor-Test-20251112 user@your-ecs-ip:/path/to/destination
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加 API key
nano .env

# 至少需要配置以下变量：
# DEEPSEEK_API_KEY=your_api_key_here
# LLM_PROVIDER=deepseek
```

---

## 🚀 部署步骤

### 步骤 1: 停止已有的测试容器（如果有）

```bash
# 停止并删除旧容器
docker-compose down

# 或者手动停止
docker stop screenplay-web
docker rm screenplay-web
```

### 步骤 2: 构建 Docker 镜像

```bash
# 方法 1: 使用 deploy.sh 脚本（推荐）
chmod +x deploy.sh
./deploy.sh build

# 方法 2: 使用 docker-compose
docker-compose build

# 方法 3: 直接使用 Docker
docker build -t screenplay-analysis:latest .
```

**预期输出**:
- 构建时间: 约 2-3 分钟
- 最终镜像大小: 约 356MB

### 步骤 3: 启动容器

```bash
# 方法 1: 使用 deploy.sh 脚本（推荐）
./deploy.sh deploy

# 方法 2: 使用 docker-compose
docker-compose up -d

# 方法 3: 使用 Docker 命令
docker run -d \
  --name screenplay-web \
  -p 8014:8000 \
  -v $(pwd)/.env:/app/.env:ro \
  -v screenplay-data:/data \
  --restart unless-stopped \
  screenplay-analysis:latest
```

### 步骤 4: 验证容器运行

```bash
# 检查容器状态
docker ps | grep screenplay-web

# 预期输出类似:
# CONTAINER ID   IMAGE                       STATUS                    PORTS
# abc123def456   screenplay-analysis:latest   Up 30 seconds (healthy)   0.0.0.0:8014->8000/tcp

# 检查日志
docker logs -f screenplay-web

# 测试健康端点
curl http://localhost:8014/health
```

**预期健康检查响应**:
```json
{
  "status": "healthy",
  "service": "screenplay-analysis",
  "version": "2.4.0",
  "timestamp": "2025-11-14T..."
}
```

---

## 🌐 Nginx 配置

### 选项 1: 直接访问（仅用于测试）

如果 ECS 安全组允许，可以直接通过端口 8014 访问：

```
http://your-ecs-ip:8014
```

**注意**: 需要在 ECS 安全组中开放端口 8014。

### 选项 2: 通过 Nginx 反向代理（推荐用于生产）

#### 2.1 安装 Nginx（如果未安装）

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx -y

# CentOS/RHEL
sudo yum install nginx -y
```

#### 2.2 配置 Nginx

**方法 A: 使用提供的配置文件**

```bash
# 复制配置文件到 Nginx 目录
sudo cp nginx.conf /etc/nginx/conf.d/screenplay.conf

# 或者 (Ubuntu/Debian)
sudo cp nginx.conf /etc/nginx/sites-available/screenplay
sudo ln -s /etc/nginx/sites-available/screenplay /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

**方法 B: 添加到现有 Nginx 配置**

如果你的 Nginx 已经服务其他应用，可以添加一个新的 `location` 块：

```nginx
# 编辑主配置文件或特定站点配置
sudo nano /etc/nginx/sites-available/default

# 在 server 块中添加以下内容：
location /screenplay/ {
    proxy_pass http://127.0.0.1:8014/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Long timeout for analysis
    proxy_read_timeout 600s;
}
```

#### 2.3 配置域名（可选）

如果有域名，修改 `nginx.conf` 中的 `server_name`:

```nginx
server {
    listen 80;
    server_name screenplay.yourdomain.com;  # 修改为你的域名
    # ...
}
```

#### 2.4 启用 HTTPS（可选但推荐）

使用 Let's Encrypt 免费 SSL 证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书并自动配置 Nginx
sudo certbot --nginx -d screenplay.yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run
```

或者手动配置 SSL（取消注释 `nginx.conf` 中的 HTTPS 部分）。

#### 2.5 验证 Nginx 配置

```bash
# 测试配置文件语法
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx

# 检查 Nginx 状态
sudo systemctl status nginx

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/screenplay_access.log
sudo tail -f /var/log/nginx/screenplay_error.log
```

---

## ✅ 验证部署

### 1. 检查容器状态

```bash
# 容器运行状态
docker ps | grep screenplay-web

# 容器资源使用
docker stats screenplay-web --no-stream

# 容器日志
docker logs --tail 50 screenplay-web
```

### 2. 测试 HTTP 端点

```bash
# 测试健康检查
curl http://localhost:8014/health

# 测试首页
curl -I http://localhost:8014/

# 通过 Nginx 测试（如果配置了）
curl http://your-ecs-ip/
# 或
curl http://screenplay.yourdomain.com/
```

### 3. 浏览器访问

打开浏览器，访问以下任一地址：

- 直接访问: `http://your-ecs-ip:8014`
- 通过 Nginx: `http://your-ecs-ip`
- 通过域名: `http://screenplay.yourdomain.com`

### 4. 功能测试

1. **上传测试文件**
   - 上传 `examples/golden/百妖_ep09_s01-s05.json`
   - 验证分析流程完整执行
   - 检查结果页面显示

2. **检查生成的报告**
   ```bash
   # 查看生成的报告文件
   docker exec screenplay-web ls -lh /app/static/uploads/
   ```

---

## 🔧 故障排查

### 问题 1: 端口 8014 已被占用

**症状**:
```
Error starting userland proxy: listen tcp4 0.0.0.0:8014: bind: address already in use
```

**解决方法**:

```bash
# 查找占用进程
sudo lsof -i :8014

# 停止占用进程
sudo kill <PID>

# 或者修改配置使用其他端口（见下文）
```

### 问题 2: 容器启动失败

**症状**: 容器不断重启或状态为 Exited

**排查步骤**:

```bash
# 查看详细日志
docker logs screenplay-web

# 检查容器配置
docker inspect screenplay-web

# 查看健康检查状态
docker inspect screenplay-web | grep -A 10 Health
```

**常见原因**:
- .env 文件缺失或配置错误
- API key 未配置
- 文件权限问题

### 问题 3: Nginx 502 Bad Gateway

**症状**: 通过 Nginx 访问返回 502 错误

**排查步骤**:

```bash
# 检查容器是否运行
docker ps | grep screenplay-web

# 检查端口 8014 是否监听
sudo ss -tuln | grep 8014

# 测试直接访问
curl http://localhost:8014/health

# 检查 Nginx 错误日志
sudo tail -f /var/log/nginx/screenplay_error.log
```

**解决方法**:
- 确保容器正在运行
- 确保 Nginx 配置中的 upstream 地址正确
- 检查防火墙规则

### 问题 4: WebSocket 连接失败

**症状**: 实时进度更新不工作

**解决方法**:

确保 Nginx 配置包含 WebSocket 支持：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### 问题 5: 文件上传失败

**症状**: 上传大文件时返回 413 错误

**解决方法**:

```nginx
# 在 Nginx 配置中增加上传限制
client_max_body_size 50M;
```

---

## 🔄 更改端口配置

如果需要使用 8014 以外的端口：

### 1. 修改 docker-compose.yml

```yaml
ports:
  - "YOUR_PORT:8000"  # 例如 "8015:8000"
```

### 2. 修改 deploy.sh

```bash
PORT=YOUR_PORT  # 例如 PORT=8015
```

### 3. 修改 nginx.conf

```nginx
upstream screenplay_backend {
    server 127.0.0.1:YOUR_PORT;  # 例如 127.0.0.1:8015
}
```

### 4. 重新部署

```bash
docker-compose down
./deploy.sh deploy
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 安全加固建议

### 1. 配置防火墙

```bash
# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 只允许本地访问 8014（如果使用 Nginx）
sudo ufw deny 8014/tcp

# 启用防火墙
sudo ufw enable
```

### 2. 配置 ECS 安全组

在 ECS 控制台配置安全组规则：

**入站规则**:
- HTTP: 端口 80, 来源 0.0.0.0/0
- HTTPS: 端口 443, 来源 0.0.0.0/0
- SSH: 端口 22, 来源 你的 IP

**不要开放**:
- 端口 8014（应该只允许本地访问）

### 3. 使用 HTTPS

参见上文"启用 HTTPS"部分。

### 4. 配置速率限制

在 Nginx 中添加速率限制：

```nginx
http {
    limit_req_zone $binary_remote_addr zone=screenplay_limit:10m rate=10r/s;

    server {
        location / {
            limit_req zone=screenplay_limit burst=20 nodelay;
            # ...
        }
    }
}
```

---

## 🛠️ 维护管理

### 日常管理命令

```bash
# 查看容器状态
docker ps | grep screenplay-web

# 查看日志
docker logs -f screenplay-web

# 重启容器
docker restart screenplay-web

# 停止容器
docker stop screenplay-web

# 启动容器
docker start screenplay-web

# 查看资源使用
docker stats screenplay-web

# 进入容器
docker exec -it screenplay-web bash
```

### 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 停止旧容器
docker-compose down

# 3. 重新构建镜像
docker-compose build --no-cache

# 4. 启动新容器
docker-compose up -d

# 5. 验证
docker logs -f screenplay-web
```

### 数据备份

```bash
# 备份数据卷
docker run --rm \
  -v screenplay-data:/data \
  -v $(pwd)/backups:/backups \
  alpine tar czf /backups/screenplay-backup-$(date +%Y%m%d).tar.gz -C /data .

# 恢复数据卷
docker run --rm \
  -v screenplay-data:/data \
  -v $(pwd)/backups:/backups \
  alpine tar xzf /backups/screenplay-backup-20251114.tar.gz -C /data
```

### 清理磁盘空间

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 清理所有未使用资源
docker system prune -a
```

### 监控和日志

```bash
# 实时监控容器资源
docker stats screenplay-web

# 查看应用日志
docker logs -f screenplay-web

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/screenplay_access.log

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/screenplay_error.log

# 分析日志（查找错误）
docker logs screenplay-web 2>&1 | grep -i error
```

---

## 📞 支持信息

### 相关文档

- [DOCKER_DEPLOYMENT_SUMMARY.md](DOCKER_DEPLOYMENT_SUMMARY.md) - Docker 部署总结
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - 快速开始指南
- [DOCKER_TEST_CHECKLIST.md](DOCKER_TEST_CHECKLIST.md) - 测试清单
- [CLAUDE.md](CLAUDE.md) - 项目总体文档

### 常用链接

- Docker 文档: https://docs.docker.com/
- Nginx 文档: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/

---

## 📝 检查清单

部署完成后，确认以下项目：

- [ ] Docker 容器正在运行（`docker ps`）
- [ ] 健康检查通过（`curl http://localhost:8014/health`）
- [ ] 可以访问首页
- [ ] 可以上传文件
- [ ] 分析流程正常完成
- [ ] Nginx 配置正确（如果使用）
- [ ] SSL 证书有效（如果使用 HTTPS）
- [ ] 防火墙规则正确
- [ ] 数据卷持久化配置
- [ ] 日志正常记录
- [ ] 自动重启配置生效

---

**版本**: v2.4.0
**最后更新**: 2025-11-14
**端口配置**: 8014 (主机) → 8000 (容器)
**状态**: ✅ 生产就绪
