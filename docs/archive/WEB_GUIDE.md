# Web 界面使用指南

## 📋 目录
- [快速开始](#快速开始)
- [功能特性](#功能特性)
- [使用流程](#使用流程)
- [技术架构](#技术架构)
- [API 文档](#api-文档)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装 Web 相关依赖
pip install -r requirements-web.txt
```

### 2. 配置环境变量

确保 `.env` 文件已配置好 API 密钥：

```bash
# 复制示例文件
cp .env.example .env

# 编辑并添加你的 API 密钥
# LLM_PROVIDER=deepseek
# DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 启动 Web 服务器

```bash
# 使用启动脚本（推荐）
./run_web_server.sh

# 或直接使用 uvicorn
python -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 Web 界面

在浏览器中打开：`http://localhost:8000`

---

## ✨ 功能特性

### 核心功能
- ✅ **文件上传**: 支持 JSON 格式剧本文件上传
- ✅ **实时进度**: WebSocket 实时显示分析进度
- ✅ **三阶段分析**:
  - Stage 1: 发现戏剧冲突链（TCC）
  - Stage 2: 审计 A/B/C 线分级
  - Stage 3: 修正结构问题
- ✅ **结果可视化**:
  - TCC 详情展示
  - A/B/C 线排序可视化
  - Mermaid 流程图
- ✅ **报告导出**: 下载 Markdown 格式完整报告
- ✅ **多 LLM 支持**: DeepSeek、Anthropic、OpenAI

### 界面特色
- 🎨 现代化 Bootstrap 5 UI
- 📱 响应式设计，支持移动端
- 🔄 实时进度更新
- 📊 交互式数据展示
- 🎯 直观的用户体验

---

## 📖 使用流程

### 1. 上传剧本

1. 访问首页 `http://localhost:8000`
2. 点击"选择剧本文件"上传 JSON 格式的剧本
3. 选择 LLM 提供商（推荐 DeepSeek）
4. （可选）展开"高级选项"配置模型名称
5. 点击"开始分析"

### 2. 查看进度

- 自动跳转到分析页面
- 实时显示三阶段流程进度
- WebSocket 推送进度更新
- 每个阶段完成后显示绿色对勾

### 3. 查看结果

分析完成后自动跳转到结果页面，包含：

#### 概览标签
- TCC 总数统计
- A/B/C 线分布
- 三阶段执行摘要
- 性能指标（耗时、Token、成本）

#### TCC 详情标签
- 每个 TCC 的完整信息
- 超级目标
- 力量列表
- 证据场景

#### 线级排序标签
- A 线（主线）详情
- B 线（副线）列表
- C 线（点缀）列表
- 各项评分（Spine、Density、Coherence）

#### 结构修正标签
- 发现的问题列表
- 修正状态（已修复/已跳过）
- 修正理由说明

#### 可视化标签
- Mermaid 流程图
- TCC 关系展示
- A/B/C 线颜色编码

### 4. 下载报告

点击"下载 Markdown 报告"按钮，获取完整的分析报告文件。

---

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 现代 Web 框架
- **Uvicorn**: ASGI 服务器
- **WebSocket**: 实时通信
- **Pydantic**: 数据验证
- **LangChain/LangGraph**: LLM 编排

### 前端技术栈
- **HTML5 + CSS3**: 标准 Web 技术
- **Bootstrap 5**: UI 框架
- **Vanilla JavaScript**: 前端交互
- **Mermaid.js**: 流程图渲染

### 架构设计

```
┌─────────────┐
│   Browser   │
│  (Client)   │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────────┐
│   FastAPI App   │
│  (src/web/app)  │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│  Core Pipeline   │
│ (src/pipeline.py)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   LLM Provider   │
│ (DeepSeek/etc.)  │
└──────────────────┘
```

### 文件结构

```
src/web/
├── __init__.py
├── app.py              # FastAPI 主应用

templates/
├── base.html           # 基础模板
├── index.html          # 首页/上传
├── analysis.html       # 分析进度
└── results.html        # 结果展示

static/
├── css/
│   └── custom.css      # 自定义样式
├── js/
│   ├── upload.js       # 上传逻辑
│   ├── analysis.js     # 进度追踪
│   └── results.js      # 结果渲染
└── uploads/            # 临时文件存储
```

---

## 🔌 API 文档

### REST API 端点

#### 1. 上传剧本
```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: JSON 文件
- provider: LLM 提供商 (deepseek/anthropic/openai)
- model: 模型名称（可选）
- export_markdown: 是否导出 Markdown（默认 true）

Response:
{
  "job_id": "uuid-string",
  "status": "queued",
  "message": "Analysis job started successfully"
}
```

#### 2. 获取任务状态
```http
GET /api/job/{job_id}

Response:
{
  "job_id": "uuid-string",
  "filename": "script.json",
  "status": "completed",
  "progress": 100,
  "result": { ... }
}
```

#### 3. 下载报告
```http
GET /api/download/report/{job_id}

Response: Markdown 文件下载
```

### WebSocket 端点

#### 实时进度推送
```
WS /ws/progress/{job_id}

Messages:
- type: "progress" - 进度更新
- type: "complete" - 分析完成
- type: "error" - 错误信息
```

### 交互式 API 文档

启动服务器后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🛠️ 开发指南

### 添加新功能

1. **后端路由**: 编辑 `src/web/app.py`
2. **前端页面**: 在 `templates/` 添加新模板
3. **JavaScript**: 在 `static/js/` 添加交互逻辑
4. **样式**: 在 `static/css/custom.css` 添加自定义样式

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG

# 启动服务器（自动重载）
uvicorn src.web.app:app --reload --log-level debug
```

### 测试上传

使用项目中的示例文件：

```bash
# 在浏览器中上传
examples/golden/百妖_ep09_s01-s05.json
```

---

## ❓ 常见问题

### Q1: 服务器无法启动
**A**: 检查依赖是否安装：
```bash
pip install -r requirements.txt -r requirements-web.txt
```

### Q2: WebSocket 连接失败
**A**: 确保没有防火墙阻止 WebSocket 连接，尝试在浏览器开发者工具中查看错误信息。

### Q3: 上传文件后无响应
**A**:
1. 检查 `.env` 中的 API 密钥是否正确
2. 查看服务器日志输出
3. 确认 JSON 文件格式正确

### Q4: 分析失败
**A**:
1. 检查 LLM API 密钥是否有效
2. 确认网络连接正常
3. 查看错误日志：`tail -f logs/app.log`

### Q5: 如何更改端口？
**A**: 编辑启动命令：
```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 9000
```

### Q6: 如何清理临时文件？
**A**:
```bash
rm -rf static/uploads/*
```

### Q7: 如何部署到生产环境？
**A**: 使用 Gunicorn + Nginx：
```bash
# 安装 Gunicorn
pip install gunicorn

# 运行
gunicorn src.web.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🔒 安全建议

1. **生产环境配置**:
   - 使用 HTTPS
   - 配置 CORS
   - 限制文件上传大小
   - 添加用户认证

2. **API 密钥管理**:
   - 不要提交 `.env` 到版本控制
   - 使用环境变量或密钥管理服务
   - 定期轮换 API 密钥

3. **文件上传安全**:
   - 验证文件类型
   - 限制文件大小（当前 10MB）
   - 定期清理临时文件

---

## 📊 性能优化

### 建议配置

```python
# 调整 Uvicorn 工作进程数
uvicorn src.web.app:app --workers 4

# 启用 HTTP/2
uvicorn src.web.app:app --http h11

# 配置超时
uvicorn src.web.app:app --timeout-keep-alive 30
```

### 缓存策略

- 静态文件使用 CDN
- API 响应添加缓存头
- 使用 Redis 缓存任务状态

---

## 📝 许可证

与主项目保持一致。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 联系方式

如有问题，请提交 GitHub Issue。

---

**最后更新**: 2025-11-13
**版本**: 1.0.0
