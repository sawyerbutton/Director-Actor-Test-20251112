# Docker 快速开始指南

## 🚀 3 步部署

### 步骤 1: 配置环境变量
```bash
cp .env.example .env
nano .env  # 添加您的 DEEPSEEK_API_KEY
```

### 步骤 2: 一键部署
```bash
./deploy.sh
```

### 步骤 3: 访问应用
打开浏览器访问: http://localhost:8000

---

## 📦 包含的文件

本项目已包含完整的 Docker 配置：

```
├── Dockerfile                   # Docker 镜像定义
├── .dockerignore               # 构建排除文件
├── docker-compose.yml          # Docker Compose 配置
├── deploy.sh                   # 自动化部署脚本
├── DEPLOYMENT.md               # 完整部署文档
├── DOCKER_TEST_CHECKLIST.md   # 测试清单
└── DOCKER_QUICKSTART.md        # 本文件
```

---

## 🎯 快速命令参考

### 使用部署脚本（推荐）
```bash
./deploy.sh deploy   # 完整部署
./deploy.sh build    # 仅构建镜像
./deploy.sh start    # 启动容器
./deploy.sh stop     # 停止容器
./deploy.sh logs     # 查看日志
./deploy.sh status   # 检查状态
```

### 使用 Docker Compose
```bash
docker-compose up -d              # 启动
docker-compose down               # 停止
docker-compose logs -f web        # 查看日志
docker-compose restart            # 重启
```

### 使用 Docker 命令
```bash
# 构建
docker build -t screenplay-analysis:latest .

# 运行
docker run -d \
  --name screenplay-web \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env:ro \
  -v screenplay-data:/data \
  screenplay-analysis:latest

# 管理
docker logs -f screenplay-web     # 查看日志
docker stop screenplay-web        # 停止
docker start screenplay-web       # 启动
docker restart screenplay-web     # 重启
docker rm -f screenplay-web       # 删除
```

---

## ✅ 快速验证

部署完成后，运行以下命令验证：

```bash
# 1. 检查容器状态
docker ps | grep screenplay-web

# 2. 测试健康端点
curl http://localhost:8000/health

# 3. 访问 Web UI
open http://localhost:8000
```

预期输出：
```json
{
  "status": "healthy",
  "service": "screenplay-analysis",
  "version": "2.4.0",
  "timestamp": "2025-11-14T..."
}
```

---

## 📚 详细文档

- **完整部署指南**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **测试清单**: [DOCKER_TEST_CHECKLIST.md](DOCKER_TEST_CHECKLIST.md)
- **应用文档**: [CLAUDE.md](CLAUDE.md)

---

## 🆘 遇到问题？

### 常见问题快速修复

**问题 1: 端口 8000 已被占用**
```bash
# 使用不同端口
docker run -p 8001:8000 ...
```

**问题 2: .env 文件未找到**
```bash
cp .env.example .env
# 编辑 .env 并添加 API key
```

**问题 3: 容器启动失败**
```bash
# 查看日志
docker logs screenplay-web

# 检查配置
docker inspect screenplay-web
```

**问题 4: 健康检查失败**
```bash
# 等待容器完全启动
sleep 10
curl http://localhost:8000/health

# 检查应用日志
docker logs screenplay-web | tail -50
```

---

## 🌟 功能特性

容器化部署包含以下特性：

- ✅ **多阶段构建** - 优化镜像大小
- ✅ **非 root 用户** - 增强安全性
- ✅ **健康检查** - 自动监控
- ✅ **数据持久化** - 保存上传文件和输出
- ✅ **自动重启** - 容器崩溃后自动恢复
- ✅ **环境隔离** - 通过 .env 文件管理配置
- ✅ **日志管理** - 统一日志输出
- ✅ **热重载** - 开发模式支持代码热更新

---

## 🔧 开发模式

如果需要修改代码并实时测试：

```bash
# 挂载源代码目录
docker run -d \
  --name screenplay-dev \
  -p 8000:8000 \
  -v $(pwd):/app \
  -v $(pwd)/.env:/app/.env:ro \
  screenplay-analysis:latest \
  uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📊 生产部署建议

1. **使用反向代理（Nginx/Traefik）**
2. **启用 HTTPS**
3. **配置资源限制**
4. **设置日志轮转**
5. **启用 LangSmith 监控**
6. **定期备份数据卷**

详见 [DEPLOYMENT.md](DEPLOYMENT.md) 的 "生产部署" 章节。

---

**版本**: v2.4.0
**最后更新**: 2025-11-14
**支持**: 见 [DEPLOYMENT.md](DEPLOYMENT.md) 故障排查部分
