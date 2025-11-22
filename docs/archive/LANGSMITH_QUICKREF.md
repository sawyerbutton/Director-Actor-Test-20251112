# LangSmith 快速参考卡

## 🚀 一键启用

```bash
# 1. 配置 .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key
LANGCHAIN_PROJECT=screenplay-analysis-dev

# 2. 运行分析
python -m src.cli analyze script.json
```

---

## 📊 查看指标

### 终端输出
自动显示性能报告：
```
📊 PERFORMANCE METRICS SUMMARY
Total Duration: 124.41s
Total LLM Calls: 3
Total Retries: 0
```

### 程序化访问
```python
result = run_pipeline(script)
metrics = result["_metrics"]
print(metrics["total_duration"])
```

### Dashboard
访问：https://smith.langchain.com/

---

## 💰 成本估算

```python
from src.monitoring import CostEstimator

CostEstimator.print_cost_breakdown(
    provider="deepseek",
    input_tokens=15000,
    output_tokens=8000
)
# 输出: Estimated Cost: $0.0044
```

---

## 📈 趋势分析

```python
from src.monitoring import MetricsStore

store = MetricsStore()
store.print_report(last_n=10)
```

---

## 🔧 故障排查

| 问题 | 解决方案 |
|------|---------|
| 追踪未启用 | 检查 `.env` 中 `LANGCHAIN_TRACING_V2=true` |
| 403 Forbidden | 验证 `LANGCHAIN_API_KEY` 格式正确 |
| 无运行记录 | 确认 Project 名称匹配 |

---

## 📚 文档链接

- [5分钟快速入门](./docs/langsmith-quickstart.md)
- [完整集成指南](./docs/langsmith-integration.md)
- [功能说明](./docs/LANGSMITH_FEATURES.md)
- [完成报告](./LANGSMITH_INTEGRATION_SUMMARY.md)

---

**提示**：首次使用建议先阅读 [快速入门](./docs/langsmith-quickstart.md)
