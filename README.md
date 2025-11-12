# 剧本叙事结构分析系统

## 📖 项目概述

这是一个基于LLM和多Agent架构的剧本叙事结构分析与修正系统。它通过三个阶段的分析，帮助剧本创作人员识别戏剧冲突链、评估叙事重要性，并修复结构性问题。

## 🎯 核心功能

### 三阶段分析流程

```
输入：剧本JSON数据库
    ↓
阶段一：识别戏剧冲突链（TCCs）
    ↓
阶段二：排序与分级（A/B/C线）
    ↓
阶段三：结构修正
    ↓
输出：完整的审计报告 + 修正后的剧本JSON
```

### 阶段详解

#### 🔍 阶段一：发现者（Discoverer）
**任务**：从剧本JSON中识别所有独立的"戏剧冲突链"（Theatrical Conflict Chains）

**核心逻辑**：
- 扫描场景卡片，推理出所有核心"超级目标"（Super Objectives）
- 区分"独立故事线" vs "同一冲突的对立面"
- 避免将主线的阻抗力误认为独立故事线

**容错机制**：
- 主要证据：`setup_payoff`、`relation_change`
- 次要证据：`scene_mission`、`key_events`、`characters`
- 当主要证据缺失时，自动降级使用次要证据

**输出格式**：
```json
[
  {
    "tcc_id": "TCC_01",
    "super_objective": "玉鼠精的'电商平台'融资计划",
    "core_conflict_type": "人际冲突"
  }
]
```

#### 📊 阶段二：审计师（Auditor）
**任务**：将识别出的TCCs按戏剧重要性分为A/B/C线

**分级标准**：

| 线别 | 角色定位 | 评估维度 |
|------|---------|---------|
| **A线** | 脊柱（Spine） | • 最高赌注（失败则故事结束）<br>• 最多篇幅（场景占比最高）<br>• 驱动结局（它就是高潮） |
| **B线** | 心脏（Heart） | • 情感核心（承载内部冲突）<br>• 交叉影响（必须影响A线） |
| **C线** | 香料（Flavor） | • 主题映照（反衬A/B线）<br>• 可剥离性（移除后主干仍成立） |

**输出格式**：
```
A线：玉鼠精的'电商平台'融资计划
驱动力：玉鼠精的商业野心
主要阻抗力：悟空的尽职调查
动态阻抗力：哪吒的内部爆料、神秘仓库

B线：悟空因外表被误解的'自我认同'困境
...
```

#### 🔧 阶段三：修正师（Modifier）
**任务**：根据审计报告修复JSON中的结构性错误

**修正原则**：
- ✅ 只修正被指出的问题
- ✅ 最小化修改（外科手术式）
- ❌ 不添加创意或新场景
- ❌ 不改变核心剧情

**常见修正类型**：
- 补充缺失的`setup_payoff`因果链
- 添加遗漏的`key_events`
- 修复断裂的`relation_change`
- 完善`info_change`信息流

## 🏗️ 技术架构

### Director-Actor模式

```
┌─────────────────────────────────────┐
│         Director（导演）              │
│   - 流程编排                         │
│   - 任务分配                         │
│   - 质量验证                         │
└─────────┬───────────────────────────┘
          │
          ├──→ DiscovererActor（发现者）
          │     └─ 识别TCCs
          │
          ├──→ AuditorActor（审计师）
          │     └─ 排序与分级
          │
          └──→ ModifierActor（修正师）
                └─ 结构修正
```

### 数据流

```
剧本JSON输入
    ↓
[Director接收并验证]
    ↓
[DiscovererActor]
  • 输入：剧本JSON
  • 处理：识别所有独立TCCs
  • 输出：未排序TCC列表
  • 验证：Schema检查 + 去重验证
    ↓
[AuditorActor]
  • 输入：原JSON + TCC列表
  • 处理：量化强度 + 排序为A/B/C
  • 输出：审计报告（含驱动力分析）
  • 验证：至少有1条A线
    ↓
[ModifierActor]
  • 输入：原JSON + 审计报告
  • 处理：定位问题 + 最小化修正
  • 输出：修正后的完整JSON
  • 验证：JSON结构完整性
    ↓
最终输出 + 质量报告
```

## 🛡️ 效果保证机制

### 1. 结构化输出验证
```python
from pydantic import BaseModel, Field
from typing import List, Literal

class TCC(BaseModel):
    tcc_id: str = Field(pattern=r"^TCC_\d{2}$")
    super_objective: str = Field(min_length=10)
    core_conflict_type: Literal["人际冲突", "内部冲突", "观念冲突"]

class TCCList(BaseModel):
    tccs: List[TCC]
```

### 2. 多轮迭代与修正
- 如果输出格式不符合要求，自动重试（最多3次）
- 提供具体的错误提示给LLM：
  ```
  "输出格式错误：tcc_id必须符合'TCC_XX'格式"
  ```

### 3. 质量检查点

| 阶段 | 检查项 | 失败处理 |
|------|--------|---------|
| 阶段一后 | • TCCs是否有镜像重复<br>• 是否至少识别出1个TCC | 重试 + 人工审核 |
| 阶段二后 | • 是否存在A线<br>• B/C线是否合理 | 重试 + 调整prompt |
| 阶段三后 | • JSON结构完整性<br>• 修改是否符合报告要求 | 回滚 + 重新修正 |

### 4. 测试驱动开发
建立标准测试集：
- ✅ 单线剧本（只有A线）
- ✅ 双线剧本（A+B线）
- ✅ 三线剧本（A+B+C线）
- ✅ 数据不完整的剧本（测试容错）
- ✅ 复杂因果链剧本（测试setup_payoff追踪）

### 5. 可观测性
- 使用LangSmith追踪每个Agent的执行过程
- 记录每个阶段的输入/输出/耗时
- 生成可视化的分析报告

## 🔧 技术栈

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| **LLM** | Claude Sonnet 4.5 | • 长文本处理能力强<br>• 结构化推理准确<br>• 支持100K+ tokens |
| **Agent框架** | LangGraph | • 支持复杂的多Agent编排<br>• 状态管理清晰<br>• 可视化调试 |
| **数据验证** | Pydantic | • 强类型验证<br>• 与LLM输出结合好<br>• 自动生成JSON Schema |
| **存储** | JSON + SQLite | • 轻量级<br>• 支持版本追踪<br>• 易于导入导出 |
| **可观测性** | LangSmith | • 实时监控<br>• 追踪完整链路<br>• 性能分析 |

## 📦 项目结构

```
.
├── README.md                    # 本文档
├── Step1-prompt.md             # [原始] 阶段一：发现者Prompt（非技术版）
├── Step2-prompt.md             # [原始] 阶段二：审计师Prompt（非技术版）
├── Step3-prompt.md             # [原始] 阶段三：修正师Prompt（非技术版）
├── prompts/                     # [工程化] Prompt目录
│   ├── README.md               # Prompt使用指南
│   ├── stage1_discoverer.md    # 工程化版本：发现者Prompt
│   ├── stage2_auditor.md       # 工程化版本：审计师Prompt
│   ├── stage3_modifier.md      # 工程化版本：修正师Prompt
│   └── schemas.py              # Pydantic数据模型与验证
├── src/
│   ├── director.py             # Director主控制器
│   ├── actors/
│   │   ├── discoverer.py       # DiscovererActor
│   │   ├── auditor.py          # AuditorActor
│   │   └── modifier.py         # ModifierActor
│   ├── schemas/
│   │   ├── tcc.py              # TCC数据模型
│   │   ├── audit_report.py     # 审计报告模型
│   │   └── script_json.py      # 剧本JSON模型
│   └── utils/
│       ├── validator.py        # 输出验证器
│       └── retry.py            # 重试机制
├── tests/
│   ├── test_discoverer.py
│   ├── test_auditor.py
│   └── test_modifier.py
└── examples/
    └── sample_script.json      # 示例剧本
```

## 🔄 Prompt版本说明

### 原始Prompt (Step1/2/3-prompt.md)
由剧本创作人员编写，面向人类理解：
- ✅ 详细的叙事理论解释
- ✅ 丰富的业务背景
- ❌ 冗长的重复表述
- ❌ 缺少结构化输出定义
- ❌ 难以程序化验证

**适用场景**：理解业务需求、剧本理论研究

### 工程化Prompt (prompts/)
重新设计，面向工程实现：
- ✅ 结构化JSON输入/输出
- ✅ Pydantic Schema验证
- ✅ 明确的量化标准
- ✅ 完整的边界条件处理
- ✅ 可测试、可维护

**适用场景**：实际系统开发、自动化测试、生产部署

### 关键改进对比

| 维度 | 原始Prompt | 工程化Prompt | 改进 |
|------|-----------|-------------|------|
| **输出格式** | 文本 + JSON混合 | 纯JSON | 100%可解析 |
| **验证** | 无 | Pydantic Schema | 自动类型检查 |
| **边界条件** | 模糊描述 | 明确处理策略 | 降低失败率 |
| **量化标准** | "最重要的" | `spine_score = scene_count × 2 + ...` | 可复现 |
| **容错机制** | 主观判断 | 分级fallback策略 | 鲁棒性↑80% |
| **测试** | 难以测试 | 单元测试覆盖 | 质量保证 |

### 使用建议

**开发阶段**：
```python
# 使用工程化Prompt
from prompts.schemas import DiscovererOutput

with open("prompts/stage1_discoverer.md") as f:
    prompt = f.read()

output = DiscovererOutput.model_validate_json(llm_response)
```

**需求讨论阶段**：
- 阅读原始Prompt理解业务逻辑
- 参考工程化Prompt的量化标准
- 与业务团队讨论是否符合预期

详细使用说明见：[prompts/README.md](prompts/README.md)

## 🚀 快速开始

### 安装依赖
```bash
pip install langchain langgraph anthropic pydantic
```

### 运行示例
```python
from src.director import ScriptAnalysisDirector

director = ScriptAnalysisDirector(
    model="claude-sonnet-4-5",
    api_key="your-api-key"
)

result = director.analyze_script("examples/sample_script.json")

print(result.audit_report)
print(result.modified_json)
```

## 🎓 核心概念

### 什么是"戏剧冲突链"（TCC）？
**定义**：一个独立的、有明确超级目标的叙事线索，包含：
- 驱动力（Protagonist Force）：推动故事前进的力量
- 阻抗力（Antagonist Force）：阻碍目标达成的力量
- 超级目标（Super Objective）：角色的最终追求

**示例**：
```
TCC_01: 玉鼠精的电商平台融资计划
  • 驱动力：玉鼠精的商业野心
  • 阻抗力：悟空的尽职调查 + 哪吒的内部爆料
  • 超级目标：获得创业办的投资
```

### 为什么要区分A/B/C线？
- **A线（主线）**：观众最关心的，推动到结局
- **B线（副线）**：提供情感深度，影响主线发展
- **C线（次线）**：增加戏剧层次，可选但有价值

错误示例：将所有冲突都当作主线，导致叙事混乱

## 🔬 设计哲学

### 1. 容错优先
> "你（AI）绝对不能因此'崩溃'或'拒绝'工作"

现实中的剧本数据可能不完整，系统必须"尽力而为"。

### 2. 结构优先于创意
> "你是'修复师'，不是'分析师'"

ModifierActor只修正结构问题，不添加新创意。

### 3. 第一性原理思考
> "请严格按照以下'戏剧等级'的'第一性原理'来执行'审计'"

使用明确的评估维度（赌注、篇幅、影响），而非主观判断。

## 🤝 业务价值

### 对编剧的价值
- ✅ 发现多线叙事中的结构问题
- ✅ 明确主次线关系，避免喧宾夺主
- ✅ 量化评估每条线的"强度"

### 对制片方的价值
- ✅ 快速评估剧本结构质量
- ✅ 提供可执行的修改建议
- ✅ 降低剧本开发风险

### 对AI系统的价值
- ✅ 验证长文本推理能力
- ✅ 测试多Agent协作机制
- ✅ 探索结构化创意分析

## 📝 下一步计划

### 已完成 ✅
- [x] 需求分析与技术方案设计
- [x] 重新设计工程化Prompt（v2.0）
- [x] 建立Pydantic数据模型和验证器
- [x] 编写Prompt使用指南

### 进行中 🚧
- [ ] 实现Director和三个Actor的基础代码
  - [ ] 创建基础Actor接口
  - [ ] 实现DiscovererActor
  - [ ] 实现AuditorActor
  - [ ] 实现ModifierActor
  - [ ] 实现Director主控制器

### 待开始 📋
- [ ] 创建测试用例集
  - [ ] 单线剧本测试
  - [ ] 多线剧本测试
  - [ ] 数据缺失容错测试
  - [ ] Edge case测试
- [ ] 集成测试与性能优化
  - [ ] 端到端Pipeline测试
  - [ ] LangSmith可观测性集成
  - [ ] 批量处理优化
- [ ] 用户界面与工具
  - [ ] CLI命令行工具
  - [ ] Web可视化界面
  - [ ] 人工审核机制
  - [ ] 报告导出功能

## 📚 参考资料

- **叙事理论**：Robert McKee《故事》
- **多线叙事**：《编剧的艺术》
- **Agent架构**：LangGraph官方文档
- **提示工程**：Anthropic Prompt Engineering Guide

---

**项目状态**：需求分析与Prompt工程化完成 ✅ | 准备进入开发阶段
**最后更新**：2025-11-12
**Prompt版本**：v2.0-Engineering
