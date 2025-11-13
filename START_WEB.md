# 🚀 一键启动 Web 界面

## 快速开始（3 步）

### 1️⃣ 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-web.txt
```

### 2️⃣ 启动服务器
```bash
./run_web_server.sh
```

### 3️⃣ 访问界面
打开浏览器，访问：**http://localhost:8000**

---

## 🎬 功能演示

### 上传剧本
1. 点击"选择剧本文件"
2. 选择 `examples/golden/百妖_ep09_s01-s05.json`
3. 选择 LLM 提供商（推荐 DeepSeek）
4. 点击"开始分析"

### 查看进度
- 自动跳转到分析页面
- 实时显示进度（10% → 40% → 70% → 90% → 100%）
- WebSocket 推送阶段更新

### 查看结果
- 5 个标签页：概览、TCC 详情、线级排序、结构修正、可视化
- Mermaid 流程图
- 下载 Markdown 报告

---

## 📖 详细文档

- **快速上手**: [WEB_README.md](WEB_README.md)
- **使用指南**: [WEB_GUIDE.md](WEB_GUIDE.md)
- **实现总结**: [WEB_IMPLEMENTATION_SUMMARY.md](WEB_IMPLEMENTATION_SUMMARY.md)

---

## 🎯 技术栈

- 后端: FastAPI + Uvicorn + WebSocket
- 前端: HTML5 + Bootstrap 5 + JavaScript
- 图表: Mermaid.js
- 核心: LangChain + LangGraph

---

## 📊 项目统计

- 总代码: 2,310 行
- 文件数: 16 个
- 完成度: 100%

---

**Enjoy! 🎉**
