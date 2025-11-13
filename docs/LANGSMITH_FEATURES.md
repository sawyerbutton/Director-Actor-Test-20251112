# LangSmith 可观测性功能说明

## 📊 新增功能概览

本次更新（2025-11-13）为剧本叙事结构分析系统集成了 **LangSmith 可观测性平台**，提供生产级的监控和追踪能力。

---

## ✨ 核心特性

### 1. 自动追踪 (Auto-Tracing)

**功能**：自动追踪所有 LLM 调用和 Agent 执行过程

**实现位置**：
- `src/pipeline.py:40-41` - LangSmith 配置
- `src/pipeline.py:131-173` - 追踪装饰器
- `src/pipeline.py:776-779` - 追踪上下文管理

**使用方式**：
```bash
# 1. 在 .env 中启用
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key

# 2. 正常运行分析（自动追踪）
python -m src.cli analyze script.json
```

**可观测数据**：
- 每个 Actor 的执行时序
- LLM 调用的输入/输出
- 错误堆栈和重试记录
- 完整的调用链路

---

### 2. 性能指标收集 (Metrics Collection)

**功能**：自动收集和报告详细的性能指标

**实现位置**：
- `src/pipeline.py:48-129` - MetricsCollector 类
- `src/pipeline.py:800-801` - 自动生成报告

**收集的指标**：

#### 执行时间
```
Per-Stage Breakdown:
  discoverer  :  95.23s | 1 calls | 0 retries
  auditor     :  15.30s | 1 calls | 0 retries
  modifier    :  13.88s | 1 calls | 0 retries
```

#### 调用统计
- Total LLM Calls: 3
- Total Retries: 0
- Success Rate: 100%

#### Token 使用量
- Total Tokens: 15,420
- Per-Stage: discoverer(5,200) / auditor(4,800) / modifier(5,420)

**访问方式**：
```python
result = run_pipeline(script)
metrics = result["_metrics"]

print(f"总耗时: {metrics['total_duration']:.2f}s")
print(f"调用次数: {metrics['total_llm_calls']}")
```

---

### 3. 监控工具模块 (Monitoring Module)

**功能**：跨运行分析、成本估算、趋势检测

**实现位置**：`src/monitoring.py`

**组件**：

#### MetricsStore
持久化存储运行指标，支持历史分析

```python
from src.monitoring import MetricsStore

store = MetricsStore()  # 自动加载 .langsmith_metrics.json
store.print_report(last_n=10)  # 分析最近 10 次运行
```

**输出示例**：
```
📊 PERFORMANCE ANALYTICS REPORT
============================================================
Total Runs: 10
Success Rate: 90.0%
Average Duration: 118.32s

Stage-wise Performance:

  DISCOVERER:
    Avg Duration: 92.15s
    Avg LLM Calls: 1.0
    Avg Retries: 0.2

  AUDITOR:
    Avg Duration: 14.20s
    Avg LLM Calls: 1.0
    Avg Retries: 0.0

  MODIFIER:
    Avg Duration: 11.97s
    Avg LLM Calls: 1.0
    Avg Retries: 0.1
============================================================
```

#### CostEstimator
基于 Token 使用量估算成本

```python
from src.monitoring import CostEstimator

CostEstimator.print_cost_breakdown(
    provider="deepseek",
    input_tokens=15420,
    output_tokens=8000
)
```

**输出示例**：
```
💰 COST ESTIMATE
============================================================
Provider: DEEPSEEK
Total Tokens: 23,420

Pricing (per 1M tokens):
  Input: $0.14
  Output: $0.28

💵 Estimated Cost: $0.0044
============================================================
```

**支持的提供商定价**：
- DeepSeek: $0.14/$0.28 (输入/输出 per 1M tokens)
- Anthropic Claude: $3.00/$15.00
- OpenAI GPT-4: $10.00/$30.00

---

### 4. 增强的日志输出 (Enhanced Logging)

**功能**：结构化的日志输出，清晰展示执行过程

**实现位置**：
- `src/pipeline.py:145-147` - 阶段开始日志
- `src/pipeline.py:159` - 阶段完成日志
- `src/pipeline.py:102-119` - 性能总结

**输出格式**：
```
============================================================
🎬 Starting Stage: DISCOVERER
============================================================
INFO:src.pipeline:Calling LLM for TCC identification...
INFO:src.pipeline:✅ Identified 2 TCCs (after auto-merge)
  - TCC_01: 玉鼠精寻求创业办电商平台投资 (conf: 0.95)
  - TCC_02: 悟空因外表被误解的身份困境 (conf: 0.85)
INFO:src.pipeline:📊 discoverer duration: 95.23s
INFO:src.pipeline:✅ DISCOVERER completed in 95.23s
```

---

## 🛠️ 技术实现

### 架构设计

```
┌─────────────────────────────────────────────┐
│         User Application                     │
│  (CLI / Python API)                         │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      run_pipeline()                          │
│  • 初始化 MetricsCollector                  │
│  • 启用 LangSmith 追踪上下文                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      LangGraph Pipeline                      │
│  ┌─────────────────────────────────────┐   │
│  │  DiscovererActor                     │   │
│  │  @trace_actor("discoverer")         │   │
│  │  • 自动记录开始/结束时间             │   │
│  │  • 自动记录 LLM 调用                 │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  AuditorActor                        │   │
│  │  @trace_actor("auditor")            │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  ModifierActor                       │   │
│  │  @trace_actor("modifier")           │   │
│  └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│     MetricsCollector                         │
│  • 聚合所有阶段的指标                        │
│  • 生成性能报告                              │
│  • 返回 _metrics 字段                        │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│     LangSmith Platform                       │
│  • 存储追踪数据                              │
│  • 提供 Web Dashboard                        │
│  • 支持查询和分析                            │
└─────────────────────────────────────────────┘
```

### 关键代码片段

#### 追踪装饰器实现

```python
def trace_actor(stage_name: str):
    """装饰器：自动追踪 Actor 执行"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # 记录指标
                metrics.record_stage_duration(stage_name, duration)
                metrics.record_llm_call(stage_name)

                return result
            except Exception as e:
                metrics.record_validation_error(stage_name, str(e))
                raise
        return wrapper
    return decorator
```

#### LangSmith 上下文管理

```python
if LANGSMITH_ENABLED:
    with tracing_v2_enabled(project_name=LANGSMITH_PROJECT):
        final_state = pipeline.invoke(initial_state, {"run_name": run_name})
else:
    final_state = pipeline.invoke(initial_state)
```

---

## 📈 使用场景

### 场景 1：性能优化

**问题**：识别最慢的阶段

**操作**：
```python
result = run_pipeline(script)
metrics = result["_metrics"]

# 找出最慢的阶段
slowest_stage = max(
    metrics["stages"].items(),
    key=lambda x: x[1]
)

print(f"最慢阶段: {slowest_stage[0]} ({slowest_stage[1]:.2f}s)")
```

### 场景 2：成本控制

**问题**：估算月度成本

**操作**：
```python
from src.monitoring import MetricsStore, CostEstimator

store = MetricsStore()
stats = store.get_stats()

# 假设每月 100 次分析
monthly_tokens = stats["avg_tokens"] * 100
monthly_cost = CostEstimator.estimate_cost(
    provider="deepseek",
    input_tokens=monthly_tokens,
    output_tokens=monthly_tokens // 2
)

print(f"预计月成本: ${monthly_cost:.2f}")
```

### 场景 3：质量监控

**问题**：检测性能回归

**操作**：
```python
store = MetricsStore()

# 对比最近 10 次和之前 10 次
recent = store.get_stats(last_n=10)
previous = store.get_stats(last_n=20)

if recent["avg_duration"] > previous["avg_duration"] * 1.2:
    print("⚠️ 警告: 执行时间增加 >20%")
```

---

## 🚀 快速开始

### 1 分钟配置

```bash
# 1. 编辑 .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key_here
LANGCHAIN_PROJECT=screenplay-analysis-dev

# 2. 运行分析
python -m src.cli analyze script.json

# 3. 查看 Dashboard
open https://smith.langchain.com/
```

详见：[快速入门指南](./langsmith-quickstart.md)

---

## 📚 文档索引

- **快速开始**：[LangSmith Quickstart](./langsmith-quickstart.md)
- **完整指南**：[LangSmith Integration](./langsmith-integration.md)
- **API 文档**：[monitoring.py](../src/monitoring.py)
- **配置模板**：[.env.example](../.env.example)

---

## 🎯 下一步计划

### 阶段二：性能分析仪表板

- [ ] Grafana 可视化集成
- [ ] 实时告警系统（Slack/Email）
- [ ] 自动性能基准测试
- [ ] A/B 测试框架

### 阶段三：高级分析

- [ ] Prompt 效能分析工具
- [ ] 自动回归检测
- [ ] 成本优化建议引擎
- [ ] 多剧本批量分析

---

## 🔄 版本历史

### v1.0.0 (2025-11-13)

**新增功能**：
- ✅ LangSmith SDK 集成
- ✅ 自动追踪装饰器
- ✅ MetricsCollector 类
- ✅ 监控工具模块 (monitoring.py)
- ✅ 成本估算器
- ✅ 指标持久化存储
- ✅ 完整文档

**修改文件**：
- `src/pipeline.py` - 添加追踪和指标收集
- `src/monitoring.py` - 新建监控工具模块
- `requirements.txt` - 添加 langsmith 依赖
- `.env.example` - 添加 LangSmith 配置

**测试结果**：
- ✅ 端到端测试通过
- ✅ 指标收集准确
- ✅ LangSmith 追踪正常（需有效 API Key）

---

## 🤝 贡献

如果你发现 Bug 或有功能建议，欢迎提交 Issue 或 Pull Request。

---

**文档版本**：1.0.0
**最后更新**：2025-11-13
**维护者**：剧本分析系统开发团队
