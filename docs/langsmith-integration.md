# LangSmith 可观测性集成指南

## 📋 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [配置说明](#配置说明)
4. [使用指南](#使用指南)
5. [监控指标](#监控指标)
6. [Dashboard 设置](#dashboard-设置)
7. [故障排查](#故障排查)
8. [最佳实践](#最佳实践)

---

## 概述

本系统集成了 LangSmith 可观测性平台，提供以下能力：

### ✨ 核心功能

- **🔍 实时追踪**：自动追踪每个 LLM 调用和 Agent 执行
- **📊 性能指标**：收集执行时间、Token 使用量、重试次数等
- **💰 成本追踪**：估算每次分析的成本
- **🐛 错误监控**：记录和分析失败原因
- **📈 趋势分析**：跨多次运行的性能对比

### 🎯 适用场景

- **开发阶段**：调试 Prompt，优化性能
- **测试阶段**：验证系统稳定性
- **生产环境**：监控服务健康度
- **成本控制**：追踪 API 使用成本

---

## 快速开始

### 1️⃣ 获取 LangSmith API Key

1. 访问 [LangSmith](https://smith.langchain.com/)
2. 注册/登录账户
3. 进入 Settings → API Keys
4. 创建新的 API Key
5. 复制 API Key（格式：`ls__...`）

### 2️⃣ 配置环境变量

编辑 `.env` 文件：

```bash
# 启用 LangSmith 追踪
LANGCHAIN_TRACING_V2=true

# LangSmith API Key
LANGCHAIN_API_KEY=ls__your_api_key_here

# 项目名称（用于组织运行记录）
LANGCHAIN_PROJECT=screenplay-analysis-prod

# （可选）自定义端点
# LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 3️⃣ 运行分析

```bash
# 使用 LangSmith 追踪的分析
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json

# 查看日志确认追踪已启用
# 输出会显示：📊 LangSmith Tracing: ✅ ENABLED
```

### 4️⃣ 查看追踪数据

1. 打开 [LangSmith Dashboard](https://smith.langchain.com/)
2. 选择项目：`screenplay-analysis-prod`
3. 查看最新的运行记录

---

## 配置说明

### 环境变量详解

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `LANGCHAIN_TRACING_V2` | 是 | `false` | 启用/禁用追踪 |
| `LANGCHAIN_API_KEY` | 是 | - | LangSmith API 密钥 |
| `LANGCHAIN_PROJECT` | 否 | `screenplay-analysis-dev` | 项目名称 |
| `LANGCHAIN_ENDPOINT` | 否 | LangSmith 默认 | API 端点 |

### 项目命名规范

建议使用不同的项目名称区分环境：

```bash
# 开发环境
LANGCHAIN_PROJECT=screenplay-analysis-dev

# 测试环境
LANGCHAIN_PROJECT=screenplay-analysis-test

# 生产环境
LANGCHAIN_PROJECT=screenplay-analysis-prod
```

---

## 使用指南

### 基础使用

#### 方式一：CLI 命令

```bash
# 自动使用 .env 配置
python -m src.cli analyze script.json

# 禁用追踪（临时）
LANGCHAIN_TRACING_V2=false python -m src.cli analyze script.json
```

#### 方式二：Python API

```python
from src.pipeline import run_pipeline
from prompts.schemas import Script

# 加载剧本
with open("script.json") as f:
    script = Script.model_validate_json(f.read())

# 运行分析（自动启用追踪）
result = run_pipeline(
    script=script,
    provider="deepseek",
    run_name="custom-run-name"  # 可选：自定义运行名称
)

# 访问性能指标
metrics = result.get("_metrics", {})
print(f"总耗时: {metrics['total_duration']:.2f}s")
print(f"LLM 调用: {metrics['total_llm_calls']}次")
```

### 自定义运行名称

为便于在 LangSmith 中识别，可以设置运行名称：

```python
result = run_pipeline(
    script=script,
    run_name="ep09-s01-s05-baseline"  # 包含剧本标识
)
```

---

## 监控指标

### 自动收集的指标

系统会自动收集以下指标：

#### 1. 性能指标

```
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

#### 2. 阶段指标

每个阶段（Discoverer/Auditor/Modifier）记录：

- ⏱️ **执行时间**：该阶段的总耗时
- 🔄 **LLM 调用次数**：调用大模型的次数
- 🔁 **重试次数**：因错误重试的次数
- 📝 **Token 使用量**：输入+输出 Token 数

#### 3. 错误指标

- ❌ **验证错误**：Schema 验证失败
- 🔄 **重试原因**：触发重试的错误类型
- 📋 **错误堆栈**：完整的异常信息

### 程序化访问指标

```python
result = run_pipeline(script)

# 获取指标摘要
metrics = result["_metrics"]

# 访问具体数据
total_time = metrics["total_duration"]
stage_times = metrics["stages"]
retry_count = metrics["total_retries"]
token_usage = metrics["total_tokens"]

# 按阶段分析
for stage in ["discoverer", "auditor", "modifier"]:
    print(f"{stage}: {stage_times.get(stage, 0):.2f}s")
```

### 持久化指标存储

使用 `MetricsStore` 跨运行分析：

```python
from src.monitoring import MetricsStore, RunMetrics
from datetime import datetime

# 创建存储
store = MetricsStore()  # 默认保存到 .langsmith_metrics.json

# 记录运行
run = RunMetrics(
    run_id="run-001",
    script_name="百妖_ep09.json",
    timestamp=datetime.now(),
    total_duration=result["_metrics"]["total_duration"],
    stage_durations=result["_metrics"]["stages"],
    llm_calls=result["_metrics"]["calls_per_stage"],
    retries=result["_metrics"]["retries_per_stage"],
    token_usage=result["_metrics"]["tokens_per_stage"],
    errors=result["errors"],
    success=len(result["errors"]) == 0
)

store.record_run(run)

# 查看统计报告
store.print_report(last_n=10)  # 最近 10 次运行
```

---

## Dashboard 设置

### LangSmith Web Dashboard

#### 1. 基础视图

访问 https://smith.langchain.com/ 后：

1. **Projects 页面**：查看所有项目
2. **选择项目**：点击 `screenplay-analysis-prod`
3. **Runs 列表**：查看所有运行记录

#### 2. 运行详情

点击任一运行记录，可查看：

- **Timeline**：执行时序图
- **Traces**：完整的调用链路
- **Inputs/Outputs**：每个 LLM 调用的输入输出
- **Metadata**：运行时长、Token 数等

#### 3. 过滤与搜索

```
# 按运行名称搜索
run_name = "ep09-s01-s05"

# 按状态过滤
status = "success" 或 "error"

# 按时间范围
last 24 hours / last 7 days
```

### 自定义 Dashboard（可选）

导出指标数据到可视化工具：

```python
from src.monitoring import MetricsStore, export_metrics_for_dashboard
from pathlib import Path

store = MetricsStore()
export_metrics_for_dashboard(
    store,
    output_path=Path("dashboard_data.json")
)
```

然后使用 Grafana、Metabase 等工具导入 `dashboard_data.json`。

---

## 故障排查

### 常见问题

#### ❌ 403 Forbidden Error

```
WARNING:langsmith.client:Failed to POST https://api.smith.langchain.com/runs/multipart
HTTPError('403 Client Error: Forbidden')
```

**原因**：API Key 无效或未设置

**解决方案**：
1. 检查 `.env` 中的 `LANGCHAIN_API_KEY`
2. 确认 API Key 格式正确（`ls__...`）
3. 在 LangSmith 网站验证 Key 是否激活

#### ❌ 追踪未启用

系统显示：`📊 LangSmith Tracing: ❌ DISABLED`

**原因**：环境变量配置错误

**解决方案**：
```bash
# 检查配置
cat .env | grep LANGCHAIN

# 确保设置为 true（小写）
LANGCHAIN_TRACING_V2=true
```

#### ⚠️ 指标不准确

Token 使用量显示为 0

**原因**：DeepSeek API 不返回 Token 计数

**解决方案**：
- 目前版本仅追踪调用次数
- Token 计数需要手动估算或使用 tiktoken 库
- 未来版本将集成自动计数

### 调试模式

启用详细日志：

```bash
# 设置日志级别
LOG_LEVEL=DEBUG python -m src.cli analyze script.json

# 查看追踪详情
LANGCHAIN_TRACING_V2=true \
LANGCHAIN_VERBOSE=true \
python -m src.cli analyze script.json
```

---

## 最佳实践

### 🎯 开发阶段

```bash
# 使用开发项目，方便隔离测试数据
LANGCHAIN_PROJECT=screenplay-analysis-dev

# 使用有意义的运行名称
run_name = f"test-{prompt_version}-{datetime.now():%Y%m%d}"
```

### 🧪 测试阶段

```python
# A/B 测试不同 Prompt 版本
for version in ["v2.0", "v2.1", "v2.2"]:
    result = run_pipeline(
        script,
        run_name=f"prompt-{version}-comparison"
    )
    # 对比 metrics["total_duration"]
```

### 🚀 生产环境

```bash
# 使用生产项目
LANGCHAIN_PROJECT=screenplay-analysis-prod

# 设置告警（在 LangSmith Dashboard）
# 1. 进入 Project Settings
# 2. 配置 Alerts：
#    - 执行时间 > 300s
#    - 错误率 > 5%
#    - Token 使用 > 50k
```

### 💰 成本优化

```python
from src.monitoring import CostEstimator

# 估算成本
CostEstimator.print_cost_breakdown(
    provider="deepseek",
    input_tokens=15000,
    output_tokens=8000
)

# 输出：
# 💰 COST ESTIMATE
# Provider: DEEPSEEK
# 💵 Estimated Cost: $0.0054
```

### 📊 定期分析

每周运行性能报告：

```python
from src.monitoring import MetricsStore

store = MetricsStore()

# 本周统计
stats = store.get_stats(last_n=50)

print(f"成功率: {stats['success_rate']:.1f}%")
print(f"平均耗时: {stats['avg_duration']:.2f}s")

# 识别异常
if stats['avg_duration'] > 200:
    print("⚠️ 警告：平均执行时间超过阈值")
```

---

## 高级用法

### 自定义追踪标签

```python
from langchain_core.tracers.context import tracing_v2_enabled

# 添加自定义元数据
with tracing_v2_enabled(
    project_name="screenplay-analysis-prod",
    tags=["experiment-A", "prompt-v2.1"],
    metadata={"user_id": "dev-001", "dataset": "golden"}
):
    result = run_pipeline(script)
```

### 并行分析追踪

```python
import concurrent.futures

scripts = load_multiple_scripts()

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = {
        executor.submit(
            run_pipeline,
            script,
            run_name=f"batch-{i}"
        ): i
        for i, script in enumerate(scripts)
    }

    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        print(f"完成: {result['_metrics']['total_duration']:.2f}s")
```

---

## 下一步

### 阶段二：性能分析仪表板

实施以下功能：

1. **Grafana 集成**：实时可视化
2. **Slack 告警**：自动通知异常
3. **趋势分析**：性能回归检测

详见：[Performance Dashboard Guide](./performance-dashboard.md)（待创建）

---

## 参考资料

- [LangSmith 官方文档](https://docs.smith.langchain.com/)
- [LangChain Tracing Guide](https://python.langchain.com/docs/langsmith/walkthrough)
- [项目架构文档](../ref/architecture.md)

---

**最后更新**：2025-11-13
**版本**：1.0.0
**状态**：生产就绪
