# 🌐 Web 界面快速上手

## 一分钟启动指南

### 1️⃣ 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-web.txt
```

### 2️⃣ 启动服务器
```bash
./run_web_server.sh
```

或者：
```bash
python -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ 访问界面
在浏览器打开：**http://localhost:8000**

---

## 🎯 功能演示

### 首页 - 上传剧本
![首页界面](docs/screenshots/home.png)

1. 选择 JSON 格式的剧本文件
2. 选择 LLM 提供商（推荐 DeepSeek）
3. 点击"开始分析"

### 分析页面 - 实时进度
![分析页面](docs/screenshots/analysis.png)

- ✅ 阶段 1: 发现 TCC
- ✅ 阶段 2: 审计 A/B/C 线
- ✅ 阶段 3: 修正结构
- ✅ 生成报告

### 结果页面 - 可视化展示
![结果页面](docs/screenshots/results.png)

**5 个标签页**：
1. **概览** - 统计摘要和性能指标
2. **TCC 详情** - 每个戏剧冲突链的完整信息
3. **线级排序** - A/B/C 线分级和评分
4. **结构修正** - 发现的问题和修复建议
5. **可视化** - Mermaid 流程图

---

## 📦 项目结构

```
project/
├── src/web/
│   ├── app.py              # FastAPI 应用 (450+ 行)
│   └── __init__.py
│
├── templates/
│   ├── base.html           # 基础模板 (70+ 行)
│   ├── index.html          # 首页 (170+ 行)
│   ├── analysis.html       # 分析页 (140+ 行)
│   └── results.html        # 结果页 (200+ 行)
│
├── static/
│   ├── css/
│   │   └── custom.css      # 自定义样式 (220+ 行)
│   ├── js/
│   │   ├── upload.js       # 上传逻辑 (80+ 行)
│   │   ├── analysis.js     # 进度追踪 (150+ 行)
│   │   └── results.js      # 结果渲染 (330+ 行)
│   └── uploads/            # 临时上传文件
│
├── requirements-web.txt    # Web 依赖
├── run_web_server.sh       # 启动脚本
└── WEB_GUIDE.md            # 完整文档
```

**总代码量**: 约 1,800 行（后端 450 行 + 前端 1,350 行）

---

## 🚀 核心特性

### 后端 (FastAPI)
- ✅ 文件上传 API
- ✅ WebSocket 实时进度推送
- ✅ 异步任务处理
- ✅ 自动 Swagger 文档
- ✅ 完整的错误处理

### 前端 (Bootstrap 5)
- ✅ 响应式设计
- ✅ 实时进度条
- ✅ 交互式数据展示
- ✅ Mermaid 图表渲染
- ✅ Markdown 报告下载

### 核心流程
```
上传文件 → WebSocket 连接 → 后台分析 → 实时进度 → 结果展示 → 下载报告
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端** | FastAPI | 现代 Python Web 框架 |
| **服务器** | Uvicorn | ASGI 服务器 |
| **实时通信** | WebSocket | 进度推送 |
| **前端框架** | Bootstrap 5 | UI 组件库 |
| **图表** | Mermaid.js | 流程图渲染 |
| **模板引擎** | Jinja2 | HTML 模板 |

---

## 📖 详细文档

完整文档请查看：[WEB_GUIDE.md](WEB_GUIDE.md)

包含：
- ✅ API 文档
- ✅ 开发指南
- ✅ 部署说明
- ✅ 常见问题
- ✅ 性能优化

---

## 🎨 界面预览

### 响应式设计
- 📱 移动端优化
- 💻 桌面端体验
- 🎯 简洁直观的 UI

### 交互功能
- 🔄 实时进度更新
- 📊 动态图表展示
- 📥 一键下载报告
- 🔍 详细信息展开

---

## 🔧 开发模式

```bash
# 启用自动重载
uvicorn src.web.app:app --reload

# 启用调试日志
uvicorn src.web.app:app --reload --log-level debug
```

---

## 📝 测试文件

使用项目自带的测试文件：
```
examples/golden/百妖_ep09_s01-s05.json
```

---

## 🔒 生产部署

### 使用 Gunicorn
```bash
pip install gunicorn
gunicorn src.web.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 使用 Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt -r requirements-web.txt
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 💡 使用技巧

### 1. 快速测试
```bash
# 上传测试文件
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@examples/golden/百妖_ep09_s01-s05.json" \
  -F "provider=deepseek"
```

### 2. API 文档
访问 `http://localhost:8000/docs` 查看交互式 API 文档

### 3. 调试 WebSocket
使用浏览器开发者工具的网络面板查看 WebSocket 消息

---

## 🐛 故障排查

### 服务器启动失败
```bash
# 检查端口占用
lsof -i :8000

# 更换端口
uvicorn src.web.app:app --port 9000
```

### WebSocket 连接失败
1. 检查防火墙设置
2. 确认浏览器支持 WebSocket
3. 查看浏览器控制台错误

### 文件上传失败
1. 检查文件格式（必须是 JSON）
2. 检查文件大小（最大 10MB）
3. 验证 JSON 格式是否正确

---

## 📈 性能指标

### 分析速度
- 小型剧本（5 场景）：30-60 秒
- 中型剧本（20 场景）：60-120 秒
- 大型剧本（50+ 场景）：120-300 秒

### 资源占用
- 内存：约 200-500 MB
- CPU：分析时 50-80%，空闲时 <5%
- 磁盘：临时文件 <100 MB

---

## 🌟 后续计划

- [ ] 用户认证系统
- [ ] 分析历史记录
- [ ] 批量处理功能
- [ ] 导出 PDF 报告
- [ ] 多语言支持

---

## 🤝 反馈与贡献

欢迎提交 Issue 和 Pull Request！

---

**版本**: 1.0.0
**最后更新**: 2025-11-13
**作者**: Script Analysis System Team
