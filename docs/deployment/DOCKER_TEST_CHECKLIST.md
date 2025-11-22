# Docker 容器化测试清单

## 📋 测试前准备

### 1. 环境要求确认
- [ ] Docker 已安装（版本 20.10+）
  ```bash
  docker --version
  ```
- [ ] Docker Compose 已安装（可选，推荐）
  ```bash
  docker-compose --version
  ```
- [ ] 有足够的磁盘空间（至少 10GB）
  ```bash
  df -h
  ```

### 2. 配置文件准备
- [ ] 复制 `.env.example` 到 `.env`
  ```bash
  cp .env.example .env
  ```
- [ ] 在 `.env` 中配置 API key
  ```bash
  nano .env
  # 至少配置 DEEPSEEK_API_KEY
  ```

---

## 🏗️ 构建测试

### 步骤 1: 构建镜像
```bash
# 方法 1: 使用部署脚本
./deploy.sh build

# 方法 2: 使用 Docker Compose
docker-compose build

# 方法 3: 使用 Docker 命令
docker build -t screenplay-analysis:latest .
```

**预期结果：**
- [ ] 构建成功，无错误
- [ ] 镜像大小合理（< 1GB）
  ```bash
  docker images | grep screenplay-analysis
  ```

**检查点：**
```bash
# 查看镜像详情
docker inspect screenplay-analysis:latest

# 预期：
# - 暴露端口：8000
# - 健康检查：配置正确
# - 工作目录：/app
# - 用户：appuser (非 root)
```

---

## 🚀 启动测试

### 步骤 2: 启动容器

```bash
# 方法 1: 使用部署脚本（推荐）
./deploy.sh deploy

# 方法 2: 使用 Docker Compose
docker-compose up -d

# 方法 3: 使用 Docker 命令
docker run -d \
  --name screenplay-web \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env:ro \
  -v screenplay-data:/data \
  screenplay-analysis:latest
```

**预期结果：**
- [ ] 容器成功启动
  ```bash
  docker ps | grep screenplay-web
  ```
- [ ] 容器状态为 "Up"
- [ ] 端口映射正确：0.0.0.0:8000->8000/tcp

---

## 🔍 健康检查测试

### 步骤 3: 验证健康端点

```bash
# 等待容器启动（约 5-10 秒）
sleep 10

# 测试健康端点
curl http://localhost:8000/health
```

**预期结果：**
- [ ] HTTP 状态码：200
- [ ] 返回 JSON：
  ```json
  {
    "status": "healthy",
    "service": "screenplay-analysis",
    "version": "2.4.0",
    "timestamp": "2025-11-14T..."
  }
  ```

**如果失败：**
```bash
# 查看容器日志
docker logs screenplay-web

# 查看容器状态
docker inspect screenplay-web | grep -A 5 Health
```

---

## 🌐 Web UI 测试

### 步骤 4: 访问 Web 界面

**测试 4.1: 首页访问**
```bash
# 命令行测试
curl -I http://localhost:8000/

# 浏览器测试
open http://localhost:8000
```

**预期结果：**
- [ ] HTTP 状态码：200
- [ ] 页面标题：上传剧本 - 剧本叙事结构分析系统
- [ ] 可以看到上传表单

**测试 4.2: 静态资源加载**
```bash
# 测试 CSS
curl -I http://localhost:8000/static/css/custom.css

# 测试 JS
curl -I http://localhost:8000/static/js/upload.js
```

**预期结果：**
- [ ] 所有静态资源返回 200
- [ ] CSS 和 JS 文件正常加载

---

## 📤 文件上传测试

### 步骤 5: 测试 JSON 文件上传

```bash
# 使用 curl 上传测试文件
curl -X POST http://localhost:8000/api/upload \
  -F "file=@examples/golden/百妖_ep09_s01-s05.json" \
  -F "provider=deepseek" \
  -F "export_markdown=true"
```

**预期结果：**
- [ ] HTTP 状态码：200
- [ ] 返回 job_id
- [ ] 返回 status: "processing" 或 "queued"

**如果成功：**
```bash
# 查看容器日志，观察分析进度
docker logs -f screenplay-web
```

---

## 🧪 TXT 解析测试

### 步骤 6: 测试 TXT 文件解析

**测试 6.1: 基础 TXT 解析**
```bash
curl -X POST http://localhost:8000/api/parse-txt \
  -F "file=@examples/test_scripts/simple_script.txt" \
  -F "use_llm=false"
```

**预期结果：**
- [ ] HTTP 状态码：200
- [ ] 返回 job_id
- [ ] Parse job 创建成功

**测试 6.2: LLM 增强解析（需要 API key）**
```bash
curl -X POST http://localhost:8000/api/parse-txt \
  -F "file=@examples/test_scripts/simple_script.txt" \
  -F "use_llm=true"
```

**预期结果：**
- [ ] HTTP 状态码：200
- [ ] 返回包含语义信息的 JSON
- [ ] 场景有 scene_mission, key_events 等字段

---

## 📊 日志和监控测试

### 步骤 7: 验证日志输出

```bash
# 实时查看日志
docker logs -f screenplay-web

# 查看最近 100 行日志
docker logs --tail=100 screenplay-web

# 搜索错误日志
docker logs screenplay-web 2>&1 | grep -i error
```

**预期结果：**
- [ ] 日志格式正确
- [ ] 无严重错误（ERROR 级别）
- [ ] 可以看到请求处理日志

---

## 💾 数据持久化测试

### 步骤 8: 测试数据卷

```bash
# 查看数据卷
docker volume ls | grep screenplay

# 检查数据卷内容
docker run --rm -v screenplay-data:/data alpine ls -la /data
```

**预期结果：**
- [ ] 数据卷 `screenplay-data` 存在
- [ ] 上传的文件被保存

**测试持久化：**
```bash
# 1. 停止容器
docker stop screenplay-web

# 2. 重新启动
docker start screenplay-web

# 3. 验证数据仍然存在
docker exec screenplay-web ls -la /data/uploads
```

---

## 🔄 重启和恢复测试

### 步骤 9: 测试容器重启

```bash
# 重启容器
docker restart screenplay-web

# 等待启动
sleep 10

# 验证服务可用
curl http://localhost:8000/health
```

**预期结果：**
- [ ] 容器成功重启
- [ ] 健康检查通过
- [ ] 服务恢复正常

---

## 🛡️ 安全性测试

### 步骤 10: 验证安全配置

**测试 10.1: 非 root 用户**
```bash
# 检查容器运行用户
docker exec screenplay-web whoami
```
**预期：** 返回 `appuser`（不是 root）

**测试 10.2: 环境变量隔离**
```bash
# 查看环境变量（不应该暴露敏感信息）
docker exec screenplay-web env | grep -i key
```
**预期：** API keys 应该被加载，但不应该在容器日志中明文显示

**测试 10.3: 文件权限**
```bash
# 检查 .env 文件权限
docker exec screenplay-web ls -la /app/.env
```
**预期：** 只读权限

---

## ⚡ 性能测试

### 步骤 11: 基础性能测试

**测试 11.1: 容器资源使用**
```bash
# 实时监控
docker stats screenplay-web

# 单次检查
docker stats --no-stream screenplay-web
```

**预期结果：**
- [ ] CPU 使用率 < 50%（空闲时）
- [ ] 内存使用 < 2GB（空闲时）
- [ ] 无内存泄漏

**测试 11.2: 响应时间**
```bash
# 测试健康端点响应时间
time curl http://localhost:8000/health
```
**预期：** < 1 秒

**测试 11.3: 并发测试（可选）**
```bash
# 安装 apache bench
# sudo apt-get install apache2-utils

# 并发测试
ab -n 100 -c 10 http://localhost:8000/health
```

---

## 🧹 清理测试

### 步骤 12: 清理环境

```bash
# 停止容器
docker stop screenplay-web

# 删除容器
docker rm screenplay-web

# 删除镜像（可选）
docker rmi screenplay-analysis:latest

# 删除数据卷（可选，会丢失数据）
docker volume rm screenplay-data

# 清理所有未使用资源
docker system prune -a
```

---

## ✅ 测试总结

### 必须通过的测试（核心功能）
1. ✅ 镜像构建成功
2. ✅ 容器启动成功
3. ✅ 健康检查通过
4. ✅ Web UI 可访问
5. ✅ JSON 文件上传和分析
6. ✅ TXT 文件解析
7. ✅ 容器重启恢复

### 应该通过的测试（推荐）
8. ✅ 日志输出正常
9. ✅ 数据持久化
10. ✅ 安全配置正确

### 可选测试（性能优化）
11. ✅ 性能指标合理
12. ✅ 并发处理能力

---

## 🐛 常见问题排查

### 问题 1: 容器启动失败
```bash
# 检查端口占用
lsof -i :8000

# 检查 .env 文件
ls -la .env
cat .env | grep API_KEY

# 查看详细错误
docker logs screenplay-web
```

### 问题 2: 健康检查失败
```bash
# 检查容器内部网络
docker exec screenplay-web curl http://localhost:8000/health

# 检查进程
docker exec screenplay-web ps aux
```

### 问题 3: API 调用失败
```bash
# 检查 API key
docker exec screenplay-web env | grep DEEPSEEK_API_KEY

# 测试 API 连接
docker exec screenplay-web curl -I https://api.deepseek.com
```

---

## 📝 测试报告模板

测试完成后，请记录：

```
测试环境：
- 操作系统：_____________
- Docker 版本：_____________
- 可用内存：_____________

测试结果：
- 构建时间：_______ 秒
- 镜像大小：_______ MB
- 启动时间：_______ 秒
- 首次响应时间：_______ 毫秒

通过的测试：___/12
失败的测试（如有）：
1. _______________
2. _______________

备注：
_______________
```

---

**文档版本**: v2.4.0
**更新日期**: 2025-11-14
**下次更新**: 功能更新或发现新问题时
