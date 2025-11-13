# A/B 测试框架使用指南

## 📖 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [使用场景](#使用场景)
4. [CLI 命令](#cli-命令)
5. [Python API](#python-api)
6. [评估标准](#评估标准)
7. [最佳实践](#最佳实践)
8. [示例](#示例)

---

## 概述

A/B 测试框架允许您系统化地对比不同的配置，以找到最优方案。

### ✨ 支持的对比维度

- **🎯 Prompt 版本**：测试不同的 Prompt 设计
- **🤖 LLM 提供商**：DeepSeek vs Claude vs OpenAI
- **🌡️ Temperature**：不同的随机性参数
- **🔧 Model 参数**：max_tokens, top_p 等

### 📊 自动收集的指标

| 指标 | 说明 | 重要性 |
|------|------|--------|
| **Success** | 是否无错误完成 | ⭐⭐⭐⭐⭐ |
| **Duration** | 总执行时间 | ⭐⭐⭐⭐ |
| **TCC Count** | 识别的冲突链数量 | ⭐⭐⭐⭐ |
| **TCC Confidence** | 平均置信度 | ⭐⭐⭐⭐⭐ |
| **Stage Durations** | 各阶段耗时分布 | ⭐⭐⭐ |
| **Errors** | 错误数量和类型 | ⭐⭐⭐⭐⭐ |

---

## 快速开始

### 5 分钟教程

#### 场景：对比两个 Temperature 设置

```bash
# 对比 temperature=0.0 (确定性) vs temperature=0.7 (创造性)
python -m src.cli ab-test examples/golden/百妖_ep09_s01-s05.json \
  --temperatures 0.0,0.7
```

**预期输出**：

```
🚀 Starting A/B Test: ab-test-20251113-140530
📄 Script: 百妖_ep09_s01-s05
🔬 Variants: 2
🔁 Runs per variant: 1

============================================================
🧪 Testing Variant: temp-0.0
   Provider: deepseek
   Temperature: 0.0
============================================================
✅ Identified 2 TCCs
✅ DISCOVERER completed in 95.23s
...

============================================================
📊 A/B TEST COMPARISON REPORT
============================================================

Variant         Success     Duration     TCCs     Confidence  Errors
--------------------------------------------------------------------------------
temp-0.0        ✅          124.41s       2       95.00%        0
temp-0.7        ✅          131.20s       2       92.50%        0

🏆 Winner: temp-0.0

💡 RECOMMENDATION
================================================================================
Based on the test results, 'temp-0.0' is recommended.
✅ Success rate: 100%
⏱️  Average duration: 124.41s
🎯 TCC confidence: 95.00%
================================================================================
```

---

## 使用场景

### 场景 1：选择最佳 LLM 提供商

**目标**：在 DeepSeek、Claude、OpenAI 中选择性价比最高的

```bash
python -m src.cli ab-test script.json \
  --providers deepseek,anthropic,openai
```

**评估维度**：
- ✅ 成功率（必须 100%）
- ⏱️ 速度（越快越好）
- 🎯 TCC 置信度（越高越好）
- 💰 成本（需单独计算）

**决策逻辑**：
```
1. 过滤掉成功率 <100% 的
2. 选择置信度最高的
3. 如果置信度相近（±2%），选择速度快的
4. 考虑成本因素（手动）
```

---

### 场景 2：优化 Prompt

**目标**：测试新版本 Prompt 是否比基线版本更好

```bash
python -m src.cli ab-test script.json \
  --variants baseline,optimized \
  --runs 3
```

**使用多次运行（`--runs 3`）的原因**：
- LLM 输出有随机性
- 多次运行取平均，结果更可靠
- 能发现稳定性问题

**判断标准**：
```python
# 新版本需要满足以下条件才算成功：
1. 成功率 >= baseline
2. TCC 置信度 > baseline + 2%
3. 速度不慢于 baseline * 1.2
```

---

### 场景 3：调优 Temperature

**目标**：找到最佳的随机性参数

```bash
python -m src.cli ab-test script.json \
  --temperatures 0.0,0.3,0.5,0.7 \
  --provider deepseek
```

**Temperature 效果**：
- **0.0**：完全确定性，适合需要一致性的场景
- **0.3-0.5**：轻微随机，平衡创造性和稳定性
- **0.7+**：高度创造性，可能产生意外结果

**推荐**：
- 生产环境：0.0（可复现）
- 实验探索：0.5-0.7

---

## CLI 命令

### 完整语法

```bash
python -m src.cli ab-test <script.json> [OPTIONS]
```

### 必需参数

| 参数 | 说明 |
|------|------|
| `script.json` | 待测试的剧本文件 |

### 可选参数（三选一）

| 参数 | 说明 | 示例 |
|------|------|------|
| `--variants` | 对比命名变体 | `baseline,optimized` |
| `--providers` | 对比 LLM 提供商 | `deepseek,anthropic` |
| `--temperatures` | 对比温度参数 | `0.0,0.5,0.7` |

### 其他选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--provider` / `-p` | 基础提供商 | `deepseek` |
| `--runs` / `-r` | 每个变体运行次数 | `1` |
| `--output` / `-o` | 保存详细结果到文件 | 无 |

### 示例命令

```bash
# 1. 对比提供商（最简单）
python -m src.cli ab-test script.json --providers deepseek,anthropic

# 2. 对比变体，运行 3 次取平均
python -m src.cli ab-test script.json --variants v1,v2 --runs 3

# 3. 对比温度，使用 Claude
python -m src.cli ab-test script.json \
  --temperatures 0.0,0.7 \
  --provider anthropic

# 4. 保存详细结果
python -m src.cli ab-test script.json \
  --variants baseline,new \
  --output results.json
```

---

## Python API

### 基础用法

```python
from src.ab_testing import ABTestRunner, PromptVariant
from prompts.schemas import Script
import json

# 1. 加载剧本
with open("script.json") as f:
    script = Script(**json.load(f))

# 2. 定义变体
variants = [
    PromptVariant(name="baseline", provider="deepseek", temperature=0.0),
    PromptVariant(name="creative", provider="deepseek", temperature=0.7),
]

# 3. 运行测试
runner = ABTestRunner()
results = runner.compare_variants(script, variants)

# 4. 查看结果
runner.print_comparison(results)

# 5. 访问数据
print(f"Winner: {results.winner}")
for result in results.results:
    print(f"{result.variant.name}: {result.duration:.2f}s")
```

### 高级用法

#### 自定义变体配置

```python
variants = [
    PromptVariant(
        name="fast",
        provider="deepseek",
        temperature=0.0,
        max_tokens=2048,
        metadata={"description": "快速模式"}
    ),
    PromptVariant(
        name="quality",
        provider="anthropic",
        model="claude-sonnet-4-5",
        temperature=0.0,
        max_tokens=4096,
        metadata={"description": "高质量模式"}
    ),
]
```

#### 批量测试多个剧本

```python
from pathlib import Path

runner = ABTestRunner()
scripts = list(Path("examples/golden").glob("*.json"))

for script_path in scripts:
    with open(script_path) as f:
        script = Script(**json.load(f))

    results = runner.compare_variants(
        script,
        variants,
        script_name=script_path.stem
    )

    print(f"\n{script_path.stem}: Winner = {results.winner}")
```

#### 访问详细指标

```python
results = runner.compare_variants(script, variants)

for result in results.results:
    print(f"\nVariant: {result.variant.name}")
    print(f"  Success: {result.success}")
    print(f"  Duration: {result.duration:.2f}s")
    print(f"  TCC Count: {result.tcc_count}")
    print(f"  TCC Confidence: {result.tcc_confidence_avg:.2%}")

    # 阶段分解
    for stage, duration in result.stage_durations.items():
        print(f"  {stage}: {duration:.2f}s")

    # 错误信息
    if result.errors:
        print(f"  Errors: {result.errors}")
```

---

## 评估标准

### 自动选择 Winner 的逻辑

系统使用以下优先级确定获胜者：

```python
优先级 1: Success（成功率）
  ↓ 过滤掉有错误的变体

优先级 2: TCC Confidence（置信度）
  ↓ 选择置信度最高的

优先级 3: Duration（速度）
  ↓ 如果置信度相近，选择更快的
```

**具体实现**：

```python
# 源码：src/ab_testing.py:_determine_winner()
def _determine_winner(results):
    # 1. 只考虑成功的
    successful = [r for r in results if r.success]

    # 2. 按置信度降序，速度升序排序
    sorted_results = sorted(
        successful,
        key=lambda r: (-r.tcc_confidence_avg, r.duration)
    )

    return sorted_results[0].variant.name
```

### 手动评估建议

除了自动选择的 winner，您还应该考虑：

#### 1. 成本因素

```python
from src.monitoring import CostEstimator

# 估算每个变体的成本
for result in results.results:
    tokens = result.metrics.get("total_tokens", 15000)  # 估算值
    cost = CostEstimator.estimate_cost(
        provider=result.variant.provider,
        input_tokens=tokens,
        output_tokens=tokens // 2
    )
    print(f"{result.variant.name}: ${cost:.4f}")
```

#### 2. 业务指标

- **TCC 数量**：太多或太少都可能有问题
- **TCC 类型**：是否识别出了关键冲突
- **可解释性**：输出是否符合业务逻辑

#### 3. 稳定性

- 如果 `--runs > 1`，检查标准差
- 置信度波动 >5% 可能不稳定

---

## 最佳实践

### 1. 设计良好的实验

**✅ 好的实验设计**：
```bash
# 一次只改变一个变量
python -m src.cli ab-test script.json --temperatures 0.0,0.7

# 使用多次运行增加可靠性
python -m src.cli ab-test script.json --variants v1,v2 --runs 3

# 使用代表性的测试数据
python -m src.cli ab-test examples/golden/百妖_ep09_s01-s05.json
```

**❌ 不好的实验设计**：
```bash
# 同时改变多个变量（无法知道哪个因素起作用）
variants = [
    PromptVariant("v1", provider="deepseek", temperature=0.0),
    PromptVariant("v2", provider="anthropic", temperature=0.7),  # ❌ 改了两个
]

# 只测试一次（结果可能不稳定）
python -m src.cli ab-test script.json --variants v1,v2  # ❌ 应该加 --runs 3

# 使用不具代表性的数据
python -m src.cli ab-test tiny_test.json  # ❌ 数据太简单
```

### 2. 解读结果

#### 关注相对差异，而非绝对值

```
❌ 错误理解：
  "temp-0.0 用时 124s，temp-0.7 用时 131s，
   所以 temp-0.0 更好"

✅ 正确理解：
  "两个变体速度相近（差异 <10%），
   但 temp-0.0 置信度更高（95% vs 92.5%），
   所以选择 temp-0.0"
```

#### 考虑实际应用场景

```python
# 生产环境：追求稳定性
if production:
    prefer_temperature = 0.0

# 研究探索：追求多样性
if research:
    prefer_temperature = 0.5

# 预算有限：追求性价比
if budget_limited:
    prefer_provider = "deepseek"
```

### 3. 记录和版本化

**创建实验日志**：

```bash
# experiments_log.md

## 2025-11-13 - Temperature 优化

**目标**：找到最佳 temperature 参数

**测试**：
```bash
python -m src.cli ab-test百妖_ep09.json \
  --temperatures 0.0,0.3,0.5,0.7 \
  --runs 3
```

**结果**：
- Winner: temp-0.0
- 置信度: 95.2%
- 速度: 124.41s

**结论**：
生产环境使用 temperature=0.0
```

---

## 示例

### 示例 1：Prompt 迭代优化

**背景**：你改进了 Stage 1 的 Prompt，想验证是否更好

**步骤**：

1. **备份原 Prompt**：
```bash
cp prompts/stage1_discoverer.md prompts/stage1_discoverer_v2.0.md
```

2. **编辑新 Prompt**：
```bash
vim prompts/stage1_discoverer.md  # 做你的改进
```

3. **运行对比**（需要自定义代码加载不同 Prompt）：
```python
# 简化版：使用相同 Prompt，对比 temperature
python -m src.cli ab-test script.json \
  --variants baseline,new \
  --runs 5  # 多次运行
```

4. **分析结果**：
```python
# 查看保存的结果
import json
with open("ab_tests/ab-test-*.json") as f:
    data = json.load(f)

# 对比关键指标
baseline = data["results"][0]
new_version = data["results"][1]

confidence_improved = new_version["tcc_confidence_avg"] > baseline["tcc_confidence_avg"]
speed_acceptable = new_version["duration"] < baseline["duration"] * 1.2

if confidence_improved and speed_acceptable:
    print("✅ 新版本 Prompt 更优，可以部署")
else:
    print("❌ 新版本未达到预期，继续优化")
```

---

### 示例 2：成本优化

**背景**：Claude 质量好但贵，DeepSeek 便宜但不确定质量

**步骤**：

```python
from src.ab_testing import ABTestRunner, PromptVariant
from src.monitoring import CostEstimator

# 1. 运行对比
variants = [
    PromptVariant("deepseek", provider="deepseek"),
    PromptVariant("claude", provider="anthropic"),
]

runner = ABTestRunner()
results = runner.compare_variants(script, variants)

# 2. 计算性价比
for result in results.results:
    tokens = 15000  # 估算
    cost = CostEstimator.estimate_cost(
        result.variant.provider,
        tokens,
        tokens // 2
    )

    # 质量得分（0-1）
    quality = result.tcc_confidence_avg

    # 性价比 = 质量 / 成本
    value = quality / cost

    print(f"{result.variant.name}:")
    print(f"  质量: {quality:.2%}")
    print(f"  成本: ${cost:.4f}")
    print(f"  性价比: {value:.2f}")
```

**预期输出**：
```
deepseek:
  质量: 95.00%
  成本: $0.0044
  性价比: 215.91

claude:
  质量: 97.50%
  成本: $0.0450
  性价比: 21.67
```

**结论**：DeepSeek 性价比高 10 倍，且质量差距小（2.5%），选择 DeepSeek

---

## 高级话题

### 统计显著性（未来功能）

当前版本使用简单的平均值对比。未来可能添加：

```python
# 计划中的功能
from src.ab_testing import statistical_significance

p_value = statistical_significance(
    baseline_results,
    new_results
)

if p_value < 0.05:
    print("✅ 差异具有统计显著性")
else:
    print("⚠️  差异可能是随机波动")
```

### 自定义评估函数

```python
def custom_scorer(result):
    """自定义评分函数"""
    # 权重配置
    weights = {
        "confidence": 0.5,  # 50% 权重
        "speed": 0.3,       # 30% 权重
        "tcc_count": 0.2    # 20% 权重
    }

    # 归一化指标
    confidence_score = result.tcc_confidence_avg  # 0-1
    speed_score = 1 / (result.duration / 100)     # 越快越好
    tcc_count_score = min(result.tcc_count / 3, 1)  # 期望 2-3 个

    # 加权求和
    return (
        weights["confidence"] * confidence_score +
        weights["speed"] * speed_score +
        weights["tcc_count"] * tcc_count_score
    )

# 应用自定义评分
for result in results.results:
    score = custom_scorer(result)
    print(f"{result.variant.name}: {score:.2f}")
```

---

## 故障排查

### 问题：所有变体都失败

**可能原因**：
- API Key 无效
- 剧本格式错误
- 网络问题

**解决**：
```bash
# 先用单个分析测试
python -m src.cli analyze script.json

# 如果成功，再运行 A/B 测试
python -m src.cli ab-test script.json --variants v1,v2
```

### 问题：结果不稳定

**症状**：同样的配置，多次运行结果差异大

**原因**：Temperature > 0

**解决**：
```bash
# 增加运行次数取平均
python -m src.cli ab-test script.json \
  --variants v1,v2 \
  --runs 5  # 至少 3-5 次
```

### 问题：No clear winner

**原因**：所有变体质量相近

**解决**：
```bash
# 1. 查看详细报告
cat ab_tests/ab-test-*.json

# 2. 手动评估其他因素（成本、速度等）

# 3. 如果确实无显著差异，选择速度快的或成本低的
```

---

## 总结

### ✅ 何时使用 A/B 测试

- ✅ 优化 Prompt
- ✅ 选择 LLM 提供商
- ✅ 调整模型参数
- ✅ 验证改进效果

### ❌ 何时不需要 A/B 测试

- ❌ 只是想快速分析一个剧本
- ❌ 已经有明确的最佳配置
- ❌ 变体之间差异微小

### 📚 相关文档

- [LangSmith 集成](./langsmith-integration.md) - 追踪 A/B 测试的详细过程
- [监控指南](../src/monitoring.py) - 成本估算和指标分析
- [Pipeline 文档](../src/pipeline.py) - 理解系统工作原理

---

**文档版本**：1.0.0
**最后更新**：2025-11-13
**维护者**：剧本分析系统开发团队
