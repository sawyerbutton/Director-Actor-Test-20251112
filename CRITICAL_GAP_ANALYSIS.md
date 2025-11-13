# ⚠️ 关键缺失分析：剧本解析器

## 🚨 严重问题

**发现日期**: 2025-11-13
**问题级别**: **P0 - 阻塞性问题**
**影响范围**: 整个系统无法处理真实编剧的输入

---

## 📋 问题描述

### 当前状态
项目只能处理 **JSON 格式**的剧本数据，但编剧使用的是：
- ✍️ 纯文本格式 (`.txt`)
- 📄 Word 文档 (`.docx`)
- 🎬 Final Draft (`.fdx`)
- ⛲ Fountain 格式 (`.fountain`)

### 缺失的功能
**没有任何模块**能够将真实剧本转换为系统要求的 JSON 格式。

---

## 🔍 详细分析

### 1. 系统要求的 JSON 结构

```json
{
  "scenes": [
    {
      "scene_id": "S01",
      "scene_mission": "场景目标描述",
      "key_events": ["事件1", "事件2"],
      "characters": ["角色1", "角色2"],
      "setup_payoff": [
        {
          "setup_scene": "S01",
          "payoff_scene": "S03",
          "element": "元素描述"
        }
      ],
      "relation_change": [
        {
          "character_a": "角色1",
          "character_b": "角色2",
          "change_type": "冲突升级",
          "description": "关系变化描述"
        }
      ],
      "info_change": [
        {
          "character": "角色1",
          "info_type": "发现真相",
          "description": "信息描述"
        }
      ]
    }
  ]
}
```

**复杂度分析**：
- ❌ **高度结构化** - 需要精确的字段和嵌套
- ❌ **语义理解** - 需要识别 setup-payoff、关系变化等
- ❌ **剧本分析能力** - 需要理解戏剧理论
- ❌ **手工创建几乎不可能** - 对于编剧来说太复杂

### 2. 编剧的真实输入格式

#### TXT 格式示例
```
第一场 酒吧 - 夜

悟空坐在吧台，手里拿着一杯酒。玉鼠精走了进来。

玉鼠精：悟空，好久不见！
悟空：（冷淡）你来干什么？
玉鼠精：我有个生意要和你谈。

---

第二场 办公室 - 日

悟空查看着玉鼠精的商业计划书...
```

#### Final Draft (.fdx) 格式
```xml
<FinalDraft>
  <Content>
    <Scene>
      <SceneHeading>
        <Text>INT. 酒吧 - 夜</Text>
      </SceneHeading>
      <Action>
        <Text>悟空坐在吧台...</Text>
      </Action>
      <Dialogue>
        <Character>玉鼠精</Character>
        <Text>悟空，好久不见！</Text>
      </Dialogue>
    </Scene>
  </Content>
</FinalDraft>
```

**差距**：
- 纯文本剧本 ⇄ 复杂的 JSON 结构
- **需要智能解析和语义理解**

---

## 🎯 当前项目能做什么 vs 不能做什么

### ✅ 能做的（已实现）
1. **分析 JSON 剧本** - 三阶段流程完美运行
2. **Web 界面** - 上传、进度、结果展示
3. **报告导出** - Markdown + Mermaid
4. **多 LLM 支持** - DeepSeek/Anthropic/OpenAI
5. **性能监控** - LangSmith 集成
6. **A/B 测试** - 参数对比

### ❌ 不能做的（缺失）
1. **解析 TXT 剧本** - 无法处理
2. **解析 Word 文档** - 无法处理
3. **解析 Final Draft** - 无法处理
4. **解析 Fountain** - 无法处理
5. **自动提取场景** - 无法实现
6. **自动识别角色** - 无法实现
7. **自动生成 setup-payoff** - 无法实现

---

## 💔 实际影响

### 对用户（编剧）的影响
```
编剧有一个 TXT 剧本
    ↓
想用系统分析
    ↓
发现需要 JSON 格式
    ↓
不知道如何转换
    ↓
❌ 放弃使用系统
```

**结论**: **系统目前无法被真实用户使用！**

---

## 🛠️ 解决方案设计

### 方案 1: 规则解析器（简单但有限）
```
TXT 剧本
  ↓ 正则表达式
场景分割（通过场景标题识别）
  ↓ 模式匹配
角色提取（通过对话格式识别）
  ↓ 结构化
基础 JSON（只有场景和角色）
```

**优点**: 快速实现，不依赖 LLM
**缺点**: 无法提取 setup-payoff、relation-change 等语义信息

### 方案 2: LLM 智能解析器（推荐）
```
TXT 剧本
  ↓ LLM (第一次调用)
场景分割 + 场景目标提取
  ↓ LLM (第二次调用)
角色识别 + 对话分析
  ↓ LLM (第三次调用)
Setup-Payoff 识别
  ↓ LLM (第四次调用)
Relation-Change 识别
  ↓ 合并
完整 JSON
```

**优点**: 能提取所有语义信息，质量高
**缺点**: 需要多次 LLM 调用，成本较高

### 方案 3: 混合方案（平衡）
```
TXT 剧本
  ↓ 规则解析器
基础结构（场景、角色、对话）
  ↓ LLM 增强
语义信息（setup-payoff、relation-change）
  ↓ 验证 + 修正
完整 JSON
```

**优点**: 成本和质量平衡
**缺点**: 需要更复杂的工程实现

---

## 📊 实现优先级

### Phase 1: 基础解析器（必须）
- [ ] TXT 格式解析器
  - [ ] 场景分割（通过标题识别）
  - [ ] 角色提取（通过对话格式）
  - [ ] 基础 JSON 生成

### Phase 2: LLM 增强（推荐）
- [ ] Setup-Payoff 自动识别
- [ ] Relation-Change 自动提取
- [ ] Info-Change 自动分析
- [ ] Scene-Mission 自动生成

### Phase 3: 多格式支持（可选）
- [ ] Final Draft (.fdx) 解析
- [ ] Fountain (.fountain) 解析
- [ ] Word (.docx) 解析
- [ ] PDF 解析

### Phase 4: Web 界面集成（必须）
- [ ] 上传 TXT 文件
- [ ] 实时解析进度
- [ ] 预览解析结果
- [ ] 手动编辑和修正
- [ ] 导出 JSON

---

## 🎯 推荐实现路径

### 短期方案（1-2 天）
1. **创建简单的 TXT 解析器**
   - 使用正则表达式分割场景
   - 提取角色和对话
   - 生成基础 JSON（缺少语义信息）

2. **添加到 Web 界面**
   - 支持上传 TXT 文件
   - 显示解析结果
   - 允许手动编辑

### 中期方案（3-5 天）
1. **LLM 增强解析**
   - 使用 LLM 提取 scene-mission
   - 使用 LLM 识别 setup-payoff
   - 使用 LLM 分析 relation-change

2. **可视化编辑器**
   - 场景卡片编辑
   - Setup-Payoff 连线
   - Relation-Change 标注

### 长期方案（1-2 周）
1. **多格式支持**
   - Final Draft 解析器
   - Fountain 解析器
   - Word 文档解析

2. **智能助手**
   - 自动补全缺失字段
   - 智能建议 setup-payoff
   - 关系变化推理

---

## 📝 技术实现建议

### 核心模块：Script Parser

```python
# src/parser/script_parser.py

class ScriptParser:
    """剧本解析器基类"""

    def parse(self, file_path: str) -> Script:
        """解析剧本文件"""
        raise NotImplementedError

class TXTScriptParser(ScriptParser):
    """TXT 格式解析器"""

    def parse(self, file_path: str) -> Script:
        # 1. 读取文件
        # 2. 分割场景
        # 3. 提取角色和对话
        # 4. 生成基础 JSON
        pass

class LLMEnhancedParser(ScriptParser):
    """LLM 增强解析器"""

    def __init__(self, base_parser: ScriptParser, llm_provider: str):
        self.base_parser = base_parser
        self.llm = create_llm(llm_provider)

    def parse(self, file_path: str) -> Script:
        # 1. 使用基础解析器获取结构
        basic_script = self.base_parser.parse(file_path)

        # 2. LLM 提取语义信息
        enhanced_script = self.enhance_with_llm(basic_script)

        return enhanced_script
```

---

## ⚡ 立即行动建议

### 优先级 P0（必须立即解决）
1. **创建 TXT 解析器** - 让系统能处理真实输入
2. **集成到 Web 界面** - 用户可以上传 TXT
3. **添加解析文档** - 告诉用户如何准备剧本

### 优先级 P1（尽快实现）
1. **LLM 增强解析** - 提升解析质量
2. **可视化编辑器** - 允许用户修正解析结果
3. **多格式支持** - 支持 Final Draft 等专业工具

---

## 🎓 经验教训

### 为什么会漏掉这个功能？

1. **测试数据误导**
   - 项目使用预制的 JSON 数据测试
   - 没有考虑真实用户的输入格式

2. **功能焦点偏移**
   - 专注于分析算法（Stage 1/2/3）
   - 忽略了数据输入环节

3. **用户场景假设错误**
   - 假设用户能提供 JSON
   - 没有考虑编剧的工作流程

---

## 📊 完整系统架构（修正后）

```
┌─────────────────────────────────────────────────────────┐
│  用户输入                                                 │
│  • TXT 剧本                                              │
│  • Word 文档                                             │
│  • Final Draft (.fdx)                                   │
│  • Fountain (.fountain)                                 │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  ⚠️ 缺失：剧本解析器（Script Parser）                    │
│  • 格式识别                                              │
│  • 场景分割                                              │
│  • 角色提取                                              │
│  • 对话分析                                              │
│  • LLM 语义增强（setup-payoff, relation-change）        │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  ✅ 已有：JSON 剧本                                      │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  ✅ 已有：三阶段分析                                     │
│  • Stage 1: 发现 TCC                                    │
│  • Stage 2: A/B/C 线分级                                │
│  • Stage 3: 结构修正                                    │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  ✅ 已有：报告导出                                       │
│  • Markdown 报告                                        │
│  • Mermaid 可视化                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 总结

### 当前状态
- **完成度**: 70%（分析部分完美，输入部分缺失）
- **可用性**: ❌ **无法被真实用户使用**
- **优先级**: **P0 - 必须立即解决**

### 下一步行动
1. ✅ 承认问题（已完成）
2. ⏭️ 设计解析器架构（待实施）
3. ⏭️ 实现 TXT 解析器（待实施）
4. ⏭️ 集成到 Web 界面（待实施）
5. ⏭️ 测试和优化（待实施）

---

**重要性**: ⭐⭐⭐⭐⭐ (5/5)
**紧急性**: ⭐⭐⭐⭐⭐ (5/5)
**影响范围**: 整个系统的实际可用性

**结论**: **这是一个阻塞性问题，必须立即解决！**

---

**创建日期**: 2025-11-13
**作者**: Claude Code
**状态**: 待解决
