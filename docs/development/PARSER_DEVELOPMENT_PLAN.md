# 剧本解析器开发计划

## 📋 项目背景

**问题**: 当前系统只能处理 JSON 格式剧本，但编剧使用的是 TXT/Word/Final Draft 等格式。

**影响**: 系统无法被真实用户使用。

**解决方案**: 开发一个智能剧本解析器，将真实剧本转换为系统所需的 JSON 格式。

---

## 🎯 开发目标

### 核心目标
1. ✅ 支持 TXT 格式剧本输入
2. ✅ 自动识别场景、角色、对话
3. ✅ 使用 LLM 提取语义信息（setup-payoff、relation-change）
4. ✅ 生成符合系统要求的完整 JSON
5. ✅ 集成到 Web 界面

### 扩展目标（可选）
- [ ] 支持 Final Draft (.fdx)
- [ ] 支持 Fountain (.fountain)
- [ ] 支持 Word (.docx)
- [ ] 支持 PDF
- [ ] 可视化编辑器

---

## 📊 开发阶段

### Phase 1: 基础解析器（1-2 天）
**目标**: 实现 TXT 格式的基础解析

#### 任务清单
- [ ] 1.1 设计解析器架构
  - [ ] 定义 ScriptParser 基类
  - [ ] 设计 TXTScriptParser 实现
  - [ ] 设计解析流程

- [ ] 1.2 实现场景分割
  - [ ] 识别场景标题（正则表达式）
  - [ ] 提取场景编号
  - [ ] 提取场景设定（地点、时间）

- [ ] 1.3 实现角色提取
  - [ ] 识别对话格式
  - [ ] 提取角色名称
  - [ ] 提取角色台词

- [ ] 1.4 实现基础 JSON 生成
  - [ ] 构建 Scene 对象
  - [ ] 生成 characters 列表
  - [ ] 生成初始 JSON 结构

- [ ] 1.5 单元测试
  - [ ] 测试场景分割准确性
  - [ ] 测试角色提取准确性
  - [ ] 测试 JSON 格式正确性

**输出**: 基础解析器，可生成包含场景和角色的简单 JSON

---

### Phase 2: LLM 增强解析（2-3 天）
**目标**: 使用 LLM 提取语义信息

#### 任务清单
- [ ] 2.1 设计 LLM 提示词
  - [ ] Scene Mission 提取提示词
  - [ ] Setup-Payoff 识别提示词
  - [ ] Relation-Change 分析提示词
  - [ ] Info-Change 提取提示词
  - [ ] Key Events 总结提示词

- [ ] 2.2 实现 LLMEnhancedParser
  - [ ] 创建 LLM 增强器类
  - [ ] 实现批量 LLM 调用
  - [ ] 实现结果合并逻辑

- [ ] 2.3 实现语义信息提取
  - [ ] 提取 scene_mission
  - [ ] 识别 setup_payoff 关系
  - [ ] 分析 relation_change
  - [ ] 提取 info_change
  - [ ] 总结 key_events

- [ ] 2.4 优化和容错
  - [ ] 添加重试机制
  - [ ] 处理 LLM 输出格式错误
  - [ ] 添加验证逻辑

- [ ] 2.5 集成测试
  - [ ] 测试完整解析流程
  - [ ] 测试 LLM 提取准确性
  - [ ] 性能测试

**输出**: 完整的 LLM 增强解析器，可生成包含所有语义信息的 JSON

---

### Phase 3: Web 界面集成（1 天）
**目标**: 将解析器集成到 Web 界面

#### 任务清单
- [ ] 3.1 后端 API 开发
  - [ ] 添加 TXT 上传端点
  - [ ] 实现解析进度推送（WebSocket）
  - [ ] 添加解析结果预览端点
  - [ ] 添加 JSON 导出端点

- [ ] 3.2 前端页面开发
  - [ ] 修改上传页面（支持 TXT）
  - [ ] 创建解析进度页面
  - [ ] 创建预览/编辑页面
  - [ ] 添加"继续分析"按钮

- [ ] 3.3 用户体验优化
  - [ ] 实时解析进度展示
  - [ ] 解析结果可编辑
  - [ ] 错误提示和修正建议
  - [ ] 一键导出 JSON

- [ ] 3.4 集成测试
  - [ ] 测试完整工作流
  - [ ] 测试错误处理
  - [ ] 浏览器兼容性测试

**输出**: Web 界面支持 TXT 上传和解析

---

### Phase 4: 文档和示例（半天）
**目标**: 提供完整的使用文档

#### 任务清单
- [ ] 4.1 编写使用指南
  - [ ] 剧本格式要求
  - [ ] 解析流程说明
  - [ ] 常见问题解答

- [ ] 4.2 创建示例文件
  - [ ] 示例 TXT 剧本
  - [ ] 解析前后对比
  - [ ] 最佳实践

- [ ] 4.3 更新项目文档
  - [ ] 更新 README.md
  - [ ] 更新 WEB_GUIDE.md
  - [ ] 更新 CLAUDE.md

**输出**: 完整的文档和示例

---

## 🏗️ 技术架构设计

### 模块结构
```
src/
├── parser/
│   ├── __init__.py
│   ├── base.py                 # ScriptParser 基类
│   ├── txt_parser.py           # TXT 格式解析器
│   ├── llm_enhancer.py         # LLM 增强器
│   └── prompts/
│       ├── scene_mission.md    # Scene Mission 提示词
│       ├── setup_payoff.md     # Setup-Payoff 提示词
│       ├── relation_change.md  # Relation-Change 提示词
│       └── info_change.md      # Info-Change 提示词
│
├── web/
│   └── app.py                  # 集成解析器 API
│
└── cli.py                      # 添加解析命令
```

### 核心类设计

#### 1. ScriptParser 基类
```python
class ScriptParser(ABC):
    """剧本解析器基类"""

    @abstractmethod
    def parse(self, file_path: str) -> Script:
        """解析剧本文件"""
        pass

    @abstractmethod
    def validate(self, script: Script) -> List[str]:
        """验证解析结果"""
        pass
```

#### 2. TXTScriptParser
```python
class TXTScriptParser(ScriptParser):
    """TXT 格式剧本解析器"""

    def parse(self, file_path: str) -> Script:
        # 1. 读取文件
        # 2. 分割场景
        # 3. 提取角色和对话
        # 4. 生成基础 JSON
        pass

    def _split_scenes(self, content: str) -> List[str]:
        """分割场景"""
        pass

    def _extract_characters(self, scene: str) -> List[str]:
        """提取角色"""
        pass

    def _extract_dialogues(self, scene: str) -> List[Dict]:
        """提取对话"""
        pass
```

#### 3. LLMEnhancedParser
```python
class LLMEnhancedParser(ScriptParser):
    """LLM 增强解析器"""

    def __init__(self, base_parser: ScriptParser, provider: str = "deepseek"):
        self.base_parser = base_parser
        self.llm = create_llm(provider)

    def parse(self, file_path: str) -> Script:
        # 1. 基础解析
        basic_script = self.base_parser.parse(file_path)

        # 2. LLM 增强
        enhanced_script = self._enhance_with_llm(basic_script)

        return enhanced_script

    def _extract_scene_missions(self, script: Script) -> Script:
        """提取场景目标"""
        pass

    def _identify_setup_payoffs(self, script: Script) -> Script:
        """识别 Setup-Payoff"""
        pass

    def _analyze_relation_changes(self, script: Script) -> Script:
        """分析关系变化"""
        pass
```

---

## 📝 剧本格式规范

### 支持的 TXT 格式

#### 标准格式（推荐）
```
场景 1: 酒吧 - 夜

悟空坐在吧台，手里拿着一杯酒。

玉鼠精：悟空，好久不见！
悟空：（冷淡）你来干什么？

---

场景 2: 办公室 - 日

悟空查看着商业计划书。
```

#### 编号格式
```
第一场 酒吧 - 夜

[场景描述]
角色A：台词
角色B：台词

===

第二场 办公室 - 日
...
```

#### Final Draft 风格
```
INT. 酒吧 - 夜

悟空坐在吧台。

玉鼠精
    悟空，好久不见！

悟空
    你来干什么？
```

### 识别规则

#### 场景分割标识
- `场景 N:`
- `第N场`
- `INT./EXT.`
- `---` (分隔符)
- `===` (分隔符)

#### 角色识别
- `角色名：` 后跟台词
- 独立一行的全大写/加粗文本
- 括号内的说明：`（动作）`

---

## 🧪 测试策略

### 单元测试
```python
# tests/test_parser.py

def test_txt_parser_scene_splitting():
    """测试场景分割"""
    parser = TXTScriptParser()
    script = parser.parse("tests/fixtures/simple_script.txt")
    assert len(script.scenes) == 5

def test_character_extraction():
    """测试角色提取"""
    parser = TXTScriptParser()
    script = parser.parse("tests/fixtures/dialogue_script.txt")
    assert "悟空" in script.scenes[0].characters

def test_llm_scene_mission():
    """测试 LLM 场景目标提取"""
    enhancer = LLMEnhancedParser(TXTScriptParser())
    script = enhancer.parse("tests/fixtures/complete_script.txt")
    assert script.scenes[0].scene_mission != ""
```

### 集成测试
```python
def test_complete_parsing_workflow():
    """测试完整解析流程"""
    # 1. 上传 TXT
    # 2. 解析
    # 3. 验证 JSON
    # 4. 运行三阶段分析
    pass
```

---

## 📊 性能指标

### 预期性能
- **基础解析**: < 1 秒（10 场景）
- **LLM 增强**: 30-60 秒（10 场景，使用 DeepSeek）
- **总耗时**: 约 1 分钟/10 场景

### 成本估算
- **基础解析**: 0 成本（纯规则）
- **LLM 增强**: 约 $0.01-0.05/剧本（DeepSeek）

---

## 🎯 验收标准

### Phase 1 验收
- [ ] 能正确分割场景（准确率 > 90%）
- [ ] 能提取所有角色（准确率 > 85%）
- [ ] 生成的 JSON 格式正确
- [ ] 通过 5+ 个单元测试

### Phase 2 验收
- [ ] 能提取 scene_mission（准确率 > 80%）
- [ ] 能识别 setup-payoff（准确率 > 70%）
- [ ] 能分析 relation-change（准确率 > 75%）
- [ ] 生成的 JSON 通过 Schema 验证

### Phase 3 验收
- [ ] Web 界面支持 TXT 上传
- [ ] 实时显示解析进度
- [ ] 可预览和编辑解析结果
- [ ] 可导出 JSON 并继续分析

### Phase 4 验收
- [ ] 文档完整（使用指南、示例、FAQ）
- [ ] 至少 3 个示例剧本
- [ ] 所有文档已更新

---

## 🚀 里程碑

### Milestone 1: 基础解析器（第 1-2 天）
**交付物**:
- TXTScriptParser 实现
- 单元测试覆盖率 > 80%
- 基础解析文档

### Milestone 2: LLM 增强（第 3-5 天）
**交付物**:
- LLMEnhancedParser 实现
- 5 个 LLM 提示词
- 集成测试通过

### Milestone 3: Web 集成（第 6 天）
**交付物**:
- Web 界面支持 TXT 上传
- 解析流程完整
- 用户可正常使用

### Milestone 4: 文档和发布（第 7 天）
**交付物**:
- 完整文档
- 示例文件
- 发布公告

---

## 📋 任务优先级

### P0 - 必须（阻塞性）
1. TXT 场景分割
2. 角色提取
3. 基础 JSON 生成
4. Web 界面集成

### P1 - 重要（核心功能）
1. LLM Scene Mission 提取
2. Setup-Payoff 识别
3. Relation-Change 分析
4. 解析结果编辑

### P2 - 可选（增强功能）
1. Info-Change 提取
2. Key Events 总结
3. 多格式支持
4. 可视化编辑器

---

## 🔄 迭代计划

### Sprint 1（第 1-2 天）
- 基础解析器开发
- 单元测试

### Sprint 2（第 3-5 天）
- LLM 增强开发
- 集成测试

### Sprint 3（第 6 天）
- Web 集成
- 端到端测试

### Sprint 4（第 7 天）
- 文档编写
- 发布准备

---

## 📚 参考资源

### 剧本格式参考
- Final Draft 格式规范
- Fountain 语法文档
- 中国电影剧本格式标准

### 技术参考
- LangChain Text Splitters
- 正则表达式最佳实践
- 剧本结构分析理论

---

## 🎉 成功标准

### 用户故事验证
```
作为编剧，
我想上传我的 TXT 剧本，
系统能自动分析并给出建议，
这样我就能改进我的剧本。
```

**验收条件**:
- ✅ 能上传 TXT 文件
- ✅ 能看到解析进度
- ✅ 能预览解析结果
- ✅ 能继续运行三阶段分析
- ✅ 能下载分析报告

---

## 📝 备注

### 风险和挑战
1. **格式多样性** - TXT 剧本格式不统一
2. **LLM 准确性** - 语义提取可能不准确
3. **性能问题** - LLM 调用耗时
4. **成本控制** - 多次 LLM 调用成本

### 应对措施
1. **支持多种格式识别规则**
2. **添加人工校验和编辑功能**
3. **使用批量调用和缓存优化**
4. **使用 DeepSeek 降低成本**

---

**计划创建日期**: 2025-11-13
**预计完成日期**: 2025-11-20（7 天）
**负责人**: Claude Code
**状态**: 📋 待开始
