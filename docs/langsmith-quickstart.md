# LangSmith 快速入门指南 (5 分钟)

## 🎯 目标

在 5 分钟内启用 LangSmith 追踪并查看第一个运行记录。

---

## 步骤 1：获取 API Key（2 分钟）

1. 打开浏览器访问：https://smith.langchain.com/
2. 使用 GitHub/Google 账号登录（或注册新账号）
3. 点击右上角头像 → **Settings**
4. 左侧菜单选择 **API Keys**
5. 点击 **Create API Key**
   - Name: `screenplay-analysis-key`
   - 点击 **Create**
6. 复制生成的 API Key（格式：`ls__...`）

⚠️ **重要**：API Key 只显示一次，请立即保存！

---

## 步骤 2：配置环境变量（1 分钟）

编辑项目根目录的 `.env` 文件：

```bash
# 启用追踪
LANGCHAIN_TRACING_V2=true

# 粘贴你的 API Key
LANGCHAIN_API_KEY=ls__your_actual_api_key_here

# 项目名称（可选，使用默认值）
LANGCHAIN_PROJECT=screenplay-analysis-dev
```

保存文件。

---

## 步骤 3：运行分析（1 分钟）

在终端执行：

```bash
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json
```

查看输出中的这些行：

```
INFO:src.pipeline:📊 LangSmith Tracing: ✅ ENABLED
INFO:src.pipeline:📊 Project: screenplay-analysis-dev
INFO:src.pipeline:📊 Run Name: screenplay-analysis-untitled
```

如果看到 `✅ ENABLED`，说明追踪已启用！

---

## 步骤 4：查看追踪数据（1 分钟）

1. 打开 https://smith.langchain.com/
2. 左侧菜单点击 **Projects**
3. 找到并点击 `screenplay-analysis-dev`
4. 查看 **Runs** 列表
5. 点击最新的运行记录

你将看到：

- **Timeline**：三个阶段的执行时序
- **Traces**：每个 LLM 调用的详情
- **Inputs/Outputs**：完整的输入输出数据
- **Metadata**：执行时间、成本等

🎉 **恭喜！** 你已成功启用 LangSmith 追踪。

---

## 下一步

### 查看性能指标

终端输出会显示详细的性能报告：

```
============================================================
📊 PERFORMANCE METRICS SUMMARY
============================================================
Total Duration: 124.41s
Total LLM Calls: 3
Total Retries: 0
Total Tokens: 15,420

Per-Stage Breakdown:
  discoverer  :  95.23s | 1 calls | 0 retries | 5,200 tokens
  auditor     :  15.30s | 1 calls | 0 retries | 4,800 tokens
  modifier    :  13.88s | 1 calls | 0 retries | 5,420 tokens
============================================================
```

### 估算成本

运行成本估算器：

```python
from src.monitoring import CostEstimator

CostEstimator.print_cost_breakdown(
    provider="deepseek",
    input_tokens=15420,
    output_tokens=8000
)
```

输出：

```
💰 COST ESTIMATE
============================================================
Provider: DEEPSEEK
Input Tokens: 15,420
Output Tokens: 8,000
Total Tokens: 23,420

Pricing (per 1M tokens):
  Input: $0.14
  Output: $0.28

💵 Estimated Cost: $0.0044
============================================================
```

### 探索更多功能

阅读完整文档：[LangSmith Integration Guide](./langsmith-integration.md)

---

## 常见问题

### ❌ 追踪显示 DISABLED

检查 `.env` 文件：

```bash
# 确保是 true（小写）
LANGCHAIN_TRACING_V2=true
```

### ❌ 403 Forbidden Error

检查 API Key 是否正确：

```bash
# 验证格式
echo $LANGCHAIN_API_KEY
# 应该输出：ls__xxxxxxxxxxxxxxxxxxxxx
```

### ⚠️ 没有看到运行记录

1. 确认 Project 名称匹配：`.env` 中的 `LANGCHAIN_PROJECT` 与 Dashboard 中的一致
2. 刷新 Dashboard 页面
3. 检查时间范围过滤器（默认显示最近 7 天）

---

## 故障排查

如果遇到问题，运行诊断：

```bash
# 检查环境变量
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Tracing:', os.getenv('LANGCHAIN_TRACING_V2'))
print('API Key:', os.getenv('LANGCHAIN_API_KEY', 'NOT SET')[:10] + '...')
print('Project:', os.getenv('LANGCHAIN_PROJECT'))
"
```

期望输出：

```
Tracing: true
API Key: ls__xxxxxx...
Project: screenplay-analysis-dev
```

---

## 禁用追踪（临时）

如果需要暂时禁用追踪：

```bash
# 方式 1：修改 .env
LANGCHAIN_TRACING_V2=false

# 方式 2：临时环境变量
LANGCHAIN_TRACING_V2=false python -m src.cli analyze script.json
```

---

**预计时间**：5 分钟
**前置要求**：已安装项目依赖（`pip install -r requirements.txt`）
**文档版本**：1.0.0
**最后更新**：2025-11-13
