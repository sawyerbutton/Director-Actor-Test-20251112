# 测试剧本转换与验证方案

## 📋 剧本基本信息

**剧本名称**：百妖创业指南 第九集
**场景数量**：43场
**复杂度**：高（三线叙事 + 复杂因果链）

## 🎯 剧本分析

### 识别出的TCCs（人工标注）

根据剧本内容，我识别出以下独立的戏剧冲突链：

#### TCC_01: 玉鼠精的电商融资计划 vs 悟空的尽职调查（A线 - 主线）
- **超级目标**：玉鼠精想获得创业办投资做电商平台
- **驱动力**：玉鼠精的商业野心 + 李家势力支持
- **主要阻抗力**：悟空的背景调查 + 女娲的审核标准
- **动态阻抗力**：
  - 哪吒的内部爆料（S10）
  - 玉面狐狸的反击（S26-S28）
  - 受害者出现（S29-S30）
  - 舆论战（S36-S39）
- **关键转折点**：
  - S05: 玉鼠精路演成功
  - S12: 哪吒爆料产品是假的
  - S34: 发现造假车间
  - S42: 记者会反转

#### TCC_02: 悟空因外表被误解的身份认同困境（B线）
- **超级目标**：悟空希望不因外表被歧视
- **驱动力**：悟空对公平对待的渴望
- **主要阻抗力**：社会对"凶恶外表"的偏见
- **情感核心**：与A线交叉（他对玉鼠精的偏见也部分源于此）
- **关键场景**：
  - S02: 女娲指出悟空吓到老师
  - S43: 女娲还他保温杯（接纳）

#### TCC_03: 阿蠢的偶像崇拜幻灭（C线）
- **超级目标**：阿蠢从盲目崇拜到认清真相
- **驱动力**：阿蠢的理想主义和粉丝心态
- **主要阻抗力**：玉鼠精的真实面目
- **关键转折**：
  - S03: 见到偶像（崇拜顶峰）
  - S12: 听到哪吒爆料（开始动摇）
  - S28: 了解玉面狐狸真相（彻底幻灭）

### 编剧标注的问题

根据剧本结尾的评论，已知问题：
1. **结构问题**：
   - "戏没有压着走，不能一步一步逼到高潮"
   - 废台词和过场戏略多（S16可能是一个例子）

2. **角色问题**：
   - 悟空人物立不住，缺少高光时刻

3. **细节问题**：
   - 笑梗不够
   - 信息量不足

## 🔄 转换策略

### Phase 1: 手工转换为JSON（建立Golden Dataset）

我建议采用**人工+AI辅助**的方式：

```python
# 转换流程
1. 人工阅读剧本 → 识别场景边界（43场）
2. 对每一场提取结构化信息：
   - scene_id: S01-S43
   - setting: 从场景描述中提取
   - characters: 列出登场角色
   - scene_mission: 总结这场戏的目的
   - key_events: 列出关键事件
   - info_change: 谁学到了什么信息
   - relation_change: 关系如何变化
   - key_object: 重要道具
   - setup_payoff: 这场戏为哪些场景埋伏笔/回收哪些伏笔
3. 保存为JSON格式
```

### Phase 2: 建立验证标准

为这个Golden Dataset准备标准答案：

```json
{
  "script_name": "百妖创业指南_ep09",
  "source": "编剧团队提供",
  "human_annotated": {
    "expected_tccs": [
      {
        "tcc_id": "TCC_01",
        "super_objective": "玉鼠精的电商融资计划",
        "core_conflict_type": "interpersonal",
        "evidence_scenes": ["S03", "S04", "S05", "S10", "S12", "S28", "S34", "S42"],
        "confidence": 0.98,
        "annotator": "AI分析师",
        "notes": "主线，贯穿全剧，赌注最高"
      },
      {
        "tcc_id": "TCC_02",
        "super_objective": "悟空因外表被误解的身份认同困境",
        "core_conflict_type": "internal",
        "evidence_scenes": ["S02", "S43"],
        "confidence": 0.75,
        "annotator": "AI分析师",
        "notes": "B线，情感核心，但场景占比少（编剧也提到'丧感不够'）"
      },
      {
        "tcc_id": "TCC_03",
        "super_objective": "阿蠢的偶像崇拜幻灭",
        "core_conflict_type": "internal",
        "evidence_scenes": ["S03", "S12", "S28"],
        "confidence": 0.85,
        "annotator": "AI分析师",
        "notes": "C线，可剥离但增加戏剧层次"
      }
    ],
    "expected_rankings": {
      "a_line": "TCC_01",
      "a_line_reasoning": "占据最多场景（约30场），推动到结局，赌注最高",
      "b_lines": ["TCC_02"],
      "b_line_reasoning": "情感核心，与A线有交叉（悟空的偏见影响调查态度）",
      "c_lines": ["TCC_03"],
      "c_line_reasoning": "主题映照（都是关于'外表vs真相'），可剥离"
    },
    "known_issues": [
      {
        "issue_id": "ISS_001",
        "category": "narrative_pacing",
        "description": "S16场戏信息量不足，可能是过场戏",
        "severity": "medium",
        "suggested_fix": "压缩或删除"
      },
      {
        "issue_id": "ISS_002",
        "category": "character_development",
        "description": "悟空缺少高光时刻，B线场景太少",
        "severity": "high",
        "suggested_fix": "增加S02和S43之间的过渡场景"
      }
    ]
  }
}
```

## 📊 测试用途

### 1. Golden Dataset（黄金标准）

**用途**：验证系统准确性

```python
# 测试脚本
def test_with_golden_dataset():
    # 加载Golden Dataset
    script = load_json("examples/golden/百妖_ep09_script.json")
    expected = load_json("examples/golden/百妖_ep09_expected.json")

    # 运行Pipeline
    pipeline = ScriptAnalysisPipeline()
    result = pipeline.run(script)

    # 验证Stage 1: Discoverer
    assert len(result.discoverer_output.tccs) == 3, "应该识别出3个TCCs"

    tcc_ids = {tcc.tcc_id for tcc in result.discoverer_output.tccs}
    expected_ids = {"TCC_01", "TCC_02", "TCC_03"}
    assert tcc_ids == expected_ids, f"TCC识别错误: {tcc_ids} vs {expected_ids}"

    # 验证Stage 2: Auditor
    assert result.auditor_output.rankings.a_line.tcc_id == "TCC_01"
    assert len(result.auditor_output.rankings.b_lines) >= 1

    # 计算准确率
    accuracy = calculate_accuracy(result, expected)
    assert accuracy >= 0.85, f"准确率不达标: {accuracy}"
```

### 2. Regression Test（回归测试）

每次修改Prompt后，确保结果不变：

```bash
# 运行回归测试
pytest tests/test_golden_dataset.py --baseline

# 对比新旧结果
pytest tests/test_golden_dataset.py --compare
```

### 3. Prompt优化基准

对比不同Prompt版本的效果：

| Prompt版本 | TCC准确率 | A-line正确率 | 总分 |
|-----------|----------|-------------|------|
| v1.0-原始 | 67% | 100% | 75% |
| v2.0-工程化 | 100% | 100% | 100% |

## 🛠️ 实施步骤

### Step 1: 转换前5场戏作为POC（今天）

我先手工转换前5场戏，验证JSON Schema是否合理：

```json
{
  "scenes": [
    {
      "scene_id": "S01",
      "setting": "日 内 创业办前台",
      "characters": ["阿蠢", "龙女"],
      "scene_mission": "建立创业办日常氛围，引入玉鼠精品牌",
      "key_events": [
        "阿蠢和龙女看妖界直播",
        "直播内容是玉面面膜涨价解释",
        "两人跟着念口号'护肤选鼠魅，肌肤会更美'"
      ],
      "info_change": [
        {
          "character": "观众",
          "learned": "玉鼠精有护肤品牌'鼠魅'，产品是'玉面面膜'"
        }
      ],
      "relation_change": [],
      "key_object": [
        {
          "object": "妖界直播",
          "status": "正在播放玉鼠精的产品广告"
        }
      ],
      "setup_payoff": {
        "setup_for": ["S03", "S05"],
        "payoff_from": []
      }
    },
    {
      "scene_id": "S02",
      "setting": "日 内 创业办办公室",
      "characters": ["悟空", "女娲"],
      "scene_mission": "展示悟空与女娲的关系模式，引入悟空的外表歧视困境",
      "key_events": [
        "女娲质问悟空迟到",
        "悟空抱怨辅导课老师不敢说话",
        "女娲指出是悟空恶狠狠盯人",
        "悟空抗议外表歧视",
        "女娲威胁让悟空提前去戒酒小组",
        "悟空夺门而出"
      ],
      "info_change": [
        {
          "character": "观众",
          "learned": "悟空因外表凶恶被人误解"
        },
        {
          "character": "观众",
          "learned": "悟空需要去戒酒小组"
        }
      ],
      "relation_change": [
        {
          "chars": ["悟空", "女娲"],
          "from": "上级/下属",
          "to": "管教者/被管教者（斗嘴模式）"
        }
      ],
      "key_object": [
        {
          "object": "悟空的保温杯",
          "status": "被女娲拿着，悟空逃跑时没拿"
        }
      ],
      "setup_payoff": {
        "setup_for": ["S43"],
        "payoff_from": []
      }
    }
    // ... S03-S05
  ]
}
```

### Step 2: 验证Schema合理性（1-2天）

- 转换前10场戏
- 检查是否有遗漏的字段
- 调整Schema定义

### Step 3: 完成全部43场转换（3-5天）

可以考虑：
- 人工转换（更准确，但耗时）
- AI辅助转换（快速，但需人工校验）

### Step 4: 准备标准答案（1天）

基于转换后的JSON，标注：
- 预期的TCCs
- 预期的A/B/C线划分
- 已知的结构性问题

## 🎯 验证指标

使用这个Golden Dataset验证系统时，我们期望：

### Stage 1: Discoverer
- ✅ 识别出3个TCCs
- ✅ TCC_01的confidence > 0.90（主线明显）
- ✅ TCC_02的confidence可能较低（场景少）
- ✅ 不应出现镜像TCC（如"女娲的审核 vs 玉鼠精的融资"是同一冲突）

### Stage 2: Auditor
- ✅ TCC_01被选为A-line（spine_score最高）
- ✅ TCC_02被选为B-line（有情感深度 + 与A线交叉）
- ✅ TCC_03被选为C-line（可剥离）

### Stage 3: Modifier
- ⚠️ 可能识别出的问题：
  - S02 setup for S43，但中间缺少过渡（编剧提到的"丧感不够"）
  - S16信息量不足（编剧明确指出）

## 💡 这个测试剧本的价值

### 优点
1. **真实性**：来自真实项目，有编剧标注
2. **复杂性**：43场戏，三线叙事，适合测试系统能力
3. **完整性**：有完整的起承转合
4. **参考答案**：编剧的评论可以作为验证参考

### 挑战
1. **转换工作量**：43场戏需要仔细标注
2. **主观性**：setup_payoff关系需要人工判断
3. **边界模糊**：有些场景的mission不明确

## 🚀 下一步行动

**我建议现在就开始转换前5场戏**，你觉得如何？

我可以：
1. **Option A**: 立即转换S01-S05为完整JSON，验证Schema
2. **Option B**: 先讨论转换规则（如何判断setup_payoff）
3. **Option C**: 你提供更多guidance，然后我批量转换

你希望我从哪个开始？另外，对于setup_payoff这种需要推理的字段，你希望我：
- 严格标注（只标注明确的因果）
- 宽松标注（标注所有可能的因果）
- 分级标注（标注并给出confidence）

请告诉我你的想法！
