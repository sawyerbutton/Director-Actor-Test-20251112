# Web UI 快速启动指南

## 🚀 一键启动

### 方式一：使用启动脚本 (推荐)
```bash
bash run_web_server.sh
```

### 方式二：手动启动
```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install -r requirements-web.txt

# 2. 检查 .env 文件
cp .env.example .env  # 如果还没有 .env 文件
# 编辑 .env 添加你的 DeepSeek API key

# 3. 启动服务器
python -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```

---

## 📍 访问地址

启动成功后，在浏览器中打开：
```
http://localhost:8000
```

---

## 🎬 使用流程

### 1️⃣ 上传 JSON 剧本
1. 在首页选择文件类型：**JSON (已结构化)**
2. 点击"选择文件"上传 JSON 剧本
3. 点击"开始分析"
4. 系统会自动进行三阶段分析

### 2️⃣ 上传 TXT 剧本
1. 在首页选择文件类型：**TXT (原始剧本)**
2. 选择是否启用"使用 LLM 语义增强"
   - ✅ 启用：更准确的语义提取 (较慢，消耗 API)
   - ⬜ 不启用：基础规则解析 (快速，免费)
3. 点击"选择文件"上传 TXT 剧本
4. 系统会先解析 TXT，然后显示预览页面
5. 在预览页面查看 4 个标签：
   - **总览**：基本信息
   - **场景列表**：所有解析的场景
   - **角色列表**：提取的角色
   - **Raw JSON**：原始 JSON 数据
6. 点击"Continue to Analysis"继续三阶段分析

### 3️⃣ 查看分析结果
1. 实时查看三个阶段的执行进度
2. 每个阶段完成后显示结果摘要
3. 最终显示完整分析报告
4. 支持导出 Markdown 报告

---

## 📂 测试文件

### JSON 测试文件
```bash
examples/golden/百妖_ep09_s01-s05.json
```

### TXT 测试文件
```bash
examples/test_scripts/simple_script.txt
```

---

## 🔧 功能特性

### 支持的文件格式
- ✅ **JSON**：已结构化的剧本数据
- ✅ **TXT**：原始剧本文本 (自动解析)

### TXT 解析功能
- ✅ 场景自动识别 (支持多种场景标记格式)
- ✅ 角色自动提取
- ✅ 对白解析
- ✅ LLM 语义增强 (可选)
  - 场景任务提取
  - 关键事件识别
  - Setup-Payoff 关系
  - 角色关系变化
  - 信息揭示追踪

### 三阶段分析
1. **Stage 1 - Discoverer**: 识别戏剧冲突链 (TCCs)
2. **Stage 2 - Auditor**: A/B/C 线分级
3. **Stage 3 - Modifier**: 结构修正建议

### 报告导出
- ✅ Markdown 格式
- ✅ Mermaid 关系图
- ✅ 完整分析详情

---

## 🐛 常见问题

### Q1: 启动失败 - 端口被占用
```bash
# 检查 8000 端口是否被占用
lsof -i :8000

# 杀死占用进程或使用其他端口
python -m uvicorn src.web.app:app --reload --port 8001
```

### Q2: .env 文件错误
```bash
# 确保 .env 文件存在
cp .env.example .env

# 编辑 .env 添加 API key
nano .env
```

### Q3: TXT 解析失败
**可能原因**:
- 场景标记格式不正确
- 文件编码问题

**解决方案**:
1. 检查 TXT 格式是否符合要求 (见 `ref/txt-parser-guide.md`)
2. 确保文件使用 UTF-8 编码
3. 查看预览页面的警告信息

### Q4: LLM 增强解析慢
**正常现象**: LLM 增强解析需要对每个场景调用 5 次 LLM

**优化建议**:
- 使用较小的剧本测试
- 关闭 LLM 增强，使用基础解析
- 使用更快的 LLM 模型 (如 DeepSeek)

---

## 📊 性能参考

### 基础 TXT 解析 (无 LLM)
- **速度**: < 1 秒
- **成本**: 免费
- **准确度**: 80-85%

### LLM 增强解析
- **速度**: 30-60 秒 (取决于场景数)
- **成本**: ~$0.10-0.50 per script (DeepSeek)
- **准确度**: 90-95%

### 三阶段分析
- **速度**: 2-5 分钟 (取决于剧本复杂度)
- **成本**: ~$0.50-2.00 per analysis (DeepSeek)

---

## 🎯 快速测试

### 测试 JSON 分析
```bash
# 1. 启动服务器
bash run_web_server.sh

# 2. 在浏览器打开 http://localhost:8000
# 3. 选择 "JSON (已结构化)"
# 4. 上传 examples/golden/百妖_ep09_s01-s05.json
# 5. 点击"开始分析"
```

### 测试 TXT 解析 + 分析
```bash
# 1. 启动服务器
bash run_web_server.sh

# 2. 在浏览器打开 http://localhost:8000
# 3. 选择 "TXT (原始剧本)"
# 4. 勾选或不勾选 "使用 LLM 语义增强"
# 5. 上传 examples/test_scripts/simple_script.txt
# 6. 查看预览页面
# 7. 点击 "Continue to Analysis"
```

---

## 📚 更多文档

- **完整使用指南**: `USAGE.md`
- **TXT 解析器指南**: `ref/txt-parser-guide.md`
- **API 参考**: `ref/api-reference.md`
- **开发指南**: `CLAUDE.md`

---

**更新时间**: 2025-11-13
**项目版本**: v2.4.0
