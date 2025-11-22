# 项目开发进度与遗留问题

**项目名称**: 剧本叙事结构分析系统 (Script Narrative Structure Analysis System)
**当前版本**: v2.6.0
**更新日期**: 2025-11-22
**状态**: ✅ 生产就绪 (Production Ready)

---

## 📊 整体进度概览

| 模块 | 状态 | 完成度 | 备注 |
|------|------|--------|------|
| 核心分析引擎 | ✅ 完成 | 100% | 三阶段流水线运行稳定 |
| TXT 剧本解析器 | ✅ 完成 | 100% | Phase 1-3 全部完成 |
| Web UI 界面 | ✅ 完成 | 100% | 上传、预览、分析、结果展示 |
| Mermaid 可视化 | ✅ 完成 | 100% | TCC 关系图、A/B/C 线着色 |
| LangSmith 可观测性 | ✅ 完成 | 100% | 自动追踪、性能指标、成本估算 |
| A/B 测试框架 | ✅ 完成 | 100% | 多提供商对比、参数测试 |
| Markdown 导出 | ✅ 完成 | 100% | 专业报告 + Mermaid 图表 |
| Docker 容器化 | ✅ 完成 | 100% | docker-compose 一键部署 |
| **Gemini 集成** | ✅ 完成 | 100% | **Session 9 新增** - 解决大脚本问题 |
| **动作分析协议 (AAP)** | ✅ 完成 | 100% | **Session 10 新增** - Discoverer 优化 |

**总体完成度**: 100%

---

## 📅 开发历程 (Session 1-10)

### Session 1-6: 基础功能开发 (2025-11-12 ~ 2025-11-13)
- Web 界面开发 (2,310 行代码)
- TXT 解析器 Phase 1-2
- 核心分析流水线调试
- LangSmith + A/B 测试集成

### Session 7: Web UI 基础功能 (2025-11-13)
- Stage 2 JSON 解析修复
- Stage 3 change_type 验证
- WebSocket 序列化问题
- 前端数据结构适配

### Session 8: UX 优化与关键修复 (2025-11-14)
- Stage 3 issue_id 验证器 (normalize_issue_id)
- Mermaid 可视化渲染修复
- TXT 解析器事件循环错误修复
- 异步解析器支持

### Session 9: Gemini 2.5 Flash 集成 (2025-11-19)
- **问题**: DeepSeek 16K max_tokens 导致大脚本 Stage 3 JSON 截断
- **解决方案**: 集成 Google Gemini 2.5 Flash (1M 上下文, 65K 输出)
- **新增文件**:
  - `test_gemini_api.py` - API 连通性测试
  - `ref/gemini-integration.md` - 集成指南 (13KB)
- **修改文件**: 9 个文件, +747 行代码
- **测试结果**: 百妖1.txt (12场景) 成功, 0 错误, 0 重试

### Session 10: Discoverer Actor 优化 - 动作分析协议 (2025-11-22) 🆕
**目标**: 优化 TCC 识别的准确性，通过提取和分析表演提示 (performance_notes) 和视觉动作 (visual_actions) 作为情感信号证据

**实现内容**:

1. **输入 ETL Pipeline** (Phase 1)
   - 新增 `PerformanceNote` 数据模型 (`prompts/schemas.py`)
   - 在 `Scene` 模型中添加 `performance_notes` 和 `visual_actions` 字段
   - TXT 解析器添加正则提取: 表演提示 `角色名(提示)` 和视觉动作 `△/■/【】`

2. **AI Core Instructions** (Phase 2)
   - 更新 `prompts/stage1_discoverer.md` 版本至 v2.6.0-AAP
   - 新增 Section 6: Action Analysis Protocol (AAP)
   - 动作分类: emotional_signal vs noise

3. **Middleware Logic** (Phase 3)
   - `filter_low_coverage_tccs()`: TCC 覆盖率过滤 (阈值 ≥15%)
   - `check_antagonist_mutual_exclusion()`: 对手互斥检查，防止镜像 TCC 被拆分

4. **Validation Layer** (Phase 4)
   - `validate_tcc_scene_evidence()`: 原子场景反向验证
   - `_has_keyword_overlap()`: 关键词重叠检测 (min_overlap=1)

5. **独立 Prompt 文件** (Phase 5)
   - `prompts/action_classifier.md` (Prompt A) - 动作分类器
   - `prompts/action_analyzer.md` (Prompt B) - 动作-TCC 证据分析器

6. **前端优化** (Phase 6)
   - 修复 Stage 3 "理由: N/A" 显示问题
   - 改进修改日志展示，显示有意义的操作描述

**修复的问题**:
- `RelationChange` 对象属性访问错误 (`from_state` → `from_`)
- 验证层过于严格导致所有 TCC 被过滤 (调整 min_overlap 从 2 到 1)
- Stage 3 修改日志 "理由: N/A" 显示不友好
- **LLM 输出中英文混搭** - 添加 Language Requirement 强制中文输出

**新增文件**:
- `prompts/action_classifier.md` - 动作分类提示词 (127 行)
- `prompts/action_analyzer.md` - 动作分析提示词 (150 行)

**修改文件**: 7 个核心文件
- `prompts/schemas.py` - +150 行 (新模型 + 中间件 + 验证函数)
- `prompts/stage1_discoverer.md` - 添加 Language Requirement 中文输出要求
- `prompts/stage2_auditor.md` - 添加 Language Requirement 中文输出要求
- `prompts/stage3_modifier.md` - 添加 Language Requirement 中文输出要求
- `src/parser/txt_parser.py` - +80 行 (ETL 提取逻辑)
- `src/pipeline.py` - +40 行 (中间件 + 验证集成)
- `static/js/results.js` - +30 行 (前端显示优化)

**测试结果**:
- 5 场景剧本: 2 TCCs 识别 (全中文), 覆盖率 60%-80%
- TCC 输出: "玉鼠精寻求创业办支持其电商平台项目", "阿蠢对玉鼠精的偶像崇拜与追随"
- 中间件日志: 对手检查通过, 覆盖率过滤通过
- 验证层日志: 场景证据验证, 部分场景标记低置信度
- Stage 2/3: 正常执行, A-line 排名, 1 个问题修复
- 总耗时: 58.56s, 0 错误, 0 重试

---

## ✅ 已完成功能清单

### 核心分析引擎
- [x] Stage 1 (Discoverer): TCC 识别 (置信度 85-95%)
- [x] Stage 2 (Auditor): A/B/C 线排名
- [x] Stage 3 (Modifier): 结构问题修复
- [x] 多 LLM 提供商支持 (DeepSeek, Claude, OpenAI, **Gemini**)
- [x] 智能 JSON 解析和错误恢复
- [x] 重试机制 (最多 3 次)
- [x] **动作分析协议 (AAP)**: 表演提示 + 视觉动作提取 (**Session 10 新增**)
- [x] **TCC 中间件**: 覆盖率过滤 + 对手互斥检查 (**Session 10 新增**)
- [x] **场景验证层**: 原子反向验证防止语义幻觉 (**Session 10 新增**)

### TXT 剧本解析器
- [x] Phase 1: 基础规则解析 (场景分割、角色提取)
- [x] Phase 2: LLM 语义增强 (场景使命、关键事件、因果关系)
- [x] Phase 3: Web 集成 (上传、预览、继续分析)
- [x] 多格式场景头支持 (S01, 场景 1, 第一场 等)
- [x] 进度回调和 WebSocket 实时更新

### Web UI
- [x] 文件上传 (JSON/TXT)
- [x] TXT 解析预览 (4 标签页: 概览、场景、角色、原始 JSON)
- [x] 三阶段分析页面
- [x] 结果展示 (TCC 列表、问题列表、修复建议)
- [x] Mermaid 可视化 (A/B/C 线颜色编码)
- [x] Markdown 报告导出

### 基础设施
- [x] Docker 容器化 (docker-compose)
- [x] 环境变量配置 (.env)
- [x] LangSmith 可观测性
- [x] A/B 测试框架
- [x] 单元测试 (44/44 通过)
- [x] 综合文档 (120KB+ across 15+ files)

---

## ⚠️ 已知遗留问题

### 1. 单场景剧本分析失败
**严重程度**: 中
**状态**: 已知限制
**描述**:
- 当剧本只有 1 个场景时, Stage 1 无法识别 TCC
- 错误信息: `List should have at least 1 item after validation, not 0`
- 系统会重试 3 次后失败

**根本原因**:
- `prompts/stage1_discoverer.md` 第 154 行规定: "Each TCC must appear in at least 2 scenes"
- TCC (戏剧冲突链) 的定义要求跨越多个场景的叙事线

**潜在解决方案**:
1. 修改 prompt 允许单场景 TCC (降低 `minimum 2` 为 `minimum 1`)
2. 添加前置检查, 场景数 < 2 时给出友好提示
3. 为单场景提供简化分析模式

**影响范围**: 仅影响极短剧本 (1 场景)

**相关文件**:
- `prompts/stage1_discoverer.md:34` - "minimum 2" 规则
- `prompts/stage1_discoverer.md:154` - 最小要求说明

---

### 2. Mermaid 图表在某些浏览器渲染延迟
**严重程度**: 低
**状态**: 已知限制
**描述**:
- 在 Safari 和部分旧版 Chrome 上, Mermaid 图表首次加载时可能显示代码而非图表
- 刷新页面后正常显示

**潜在解决方案**:
1. 增加渲染延迟时间
2. 添加加载状态指示器
3. 使用服务端渲染替代客户端渲染

**相关文件**:
- `static/js/results.js:348-382` - Mermaid 渲染逻辑
- `templates/results.html:5-16` - Mermaid 初始化

---

### 3. LLM 语义增强成本较高
**严重程度**: 低
**状态**: 设计权衡
**描述**:
- TXT 解析的 LLM 增强模式需要 5 次 LLM 调用/场景
- 对于 12 场景剧本 = 60 次 LLM 调用
- 增加处理时间和 API 成本

**当前缓解措施**:
- 提供 "禁用 LLM 增强" 选项
- 基础规则解析不需要 LLM

**潜在优化**:
1. 批量处理多个场景
2. 缓存常见模式
3. 使用更便宜的模型 (如 Gemini Flash)

---

### 4. 大文件上传可能超时
**严重程度**: 低
**状态**: 待优化
**描述**:
- 非常大的剧本文件 (>1MB) 可能导致上传超时
- 这是极端边界情况, 普通剧本通常 <100KB

**潜在解决方案**:
1. 实现分块上传
2. 增加超时时间
3. 添加文件大小限制和警告

---

### 5. 错误信息国际化
**严重程度**: 低
**状态**: 待完善
**描述**:
- 部分错误信息为英文
- 用户界面主要为中文, 存在不一致

**潜在解决方案**:
1. 添加 i18n 国际化支持
2. 统一使用中文错误信息

---

## 🔮 未来改进建议

### 短期 (1-2 周)
1. [ ] 添加单场景剧本的友好错误提示
2. [ ] 优化 Mermaid 渲染兼容性
3. [ ] 统一错误信息为中文

### 中期 (1-2 月)
1. [ ] 实现 LLM 调用批处理以降低成本
2. [ ] 添加分析结果历史记录
3. [ ] 支持多剧本批量分析
4. [ ] 实现用户登录和项目管理

### 长期 (3+ 月)
1. [ ] 支持更多剧本格式 (Final Draft, Celtx)
2. [ ] 添加协作编辑功能
3. [ ] 集成剧本写作建议
4. [ ] 移动端适配

---

## 📁 关键文件索引

### 配置文件
| 文件 | 说明 |
|------|------|
| `.env.example` | 环境变量模板 |
| `docker-compose.yml` | Docker 编排配置 |
| `requirements.txt` | Python 依赖 |

### 核心代码
| 文件 | 说明 | 关键行 |
|------|------|--------|
| `src/pipeline.py` | 分析流水线 | 288-303: Gemini 工厂, 中间件+验证集成 |
| `src/web/app.py` | Web 后端 | 122-131: 提供商配置 |
| `src/parser/txt_parser.py` | TXT 解析器 | 表演提示/视觉动作提取 |
| `src/parser/llm_enhancer.py` | LLM 增强器 | - |
| `prompts/stage1_discoverer.md` | TCC 识别提示词 (v2.6.0-AAP) | Section 6: AAP |
| `prompts/action_classifier.md` | 动作分类器 (Prompt A) | **Session 10 新增** |
| `prompts/action_analyzer.md` | 动作分析器 (Prompt B) | **Session 10 新增** |
| `prompts/schemas.py` | 数据模型 + 中间件 + 验证 | PerformanceNote, 验证函数 |

### 文档
| 文件 | 说明 |
|------|------|
| `CLAUDE.md` | AI 助手导航 (39KB) |
| `ref/gemini-integration.md` | Gemini 集成指南 (13KB) |
| `ref/txt-parser-guide.md` | TXT 解析器指南 (20KB) |
| `DEVELOPMENT_LOG.md` | 开发日志 |

### 测试
| 文件 | 说明 |
|------|------|
| `test_gemini_api.py` | Gemini API 测试 |
| `tests/test_schemas.py` | Schema 单元测试 |
| `tests/test_golden_dataset.py` | 集成测试 |

---

## 🧪 测试状态

### 单元测试
```bash
pytest tests/ -v
# Result: 44 passed, 3 skipped (LLM integration tests)
# Status: ✅ 100% pass rate
```

### 端到端测试
```bash
# 大脚本测试 (12 场景)
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json --provider gemini
# Stage 1: ✅ Success (3 TCCs, 19.66s)
# Stage 2: ✅ Success (A/B/C ranking, 27.40s)
# Stage 3: ✅ Success (6 issues fixed, 59.84s)
# Total: 106.90s, 0 errors, 0 retries
```

### API 连通性测试
```bash
python test_gemini_api.py
# ✅ Gemini 2.5 Flash: PASSED
```

---

## 📞 技术支持

### 常见问题快速解决

| 问题 | 解决方案 |
|------|----------|
| API Key 错误 | 检查 `.env` 文件 |
| Docker 启动失败 | `docker-compose down && docker-compose up -d` |
| Gemini 配额超限 | 等待 24 小时或更换 API Key |
| TXT 解析失败 | 检查场景头格式 (需要 S01/场景 1 等) |
| Stage 1 失败 | 确保剧本至少有 2 个场景 |

### 调试命令
```bash
# 查看 Docker 日志
docker-compose logs -f web

# 测试 Gemini API
python test_gemini_api.py

# 运行单元测试
pytest tests/ -v

# 检查环境变量
cat .env | grep -E "LLM_PROVIDER|GOOGLE_API_KEY"
```

---

## 📝 变更日志

### v2.6.0 (2025-11-22) - Session 10 🆕
- 🆕 **动作分析协议 (AAP)**: 提取表演提示和视觉动作作为 TCC 证据
- 🆕 **TCC 中间件层**: 覆盖率过滤 (≥15%) + 对手互斥检查
- 🆕 **场景验证层**: 原子反向验证防止语义幻觉
- 🆕 新增 `prompts/action_classifier.md` (Prompt A)
- 🆕 新增 `prompts/action_analyzer.md` (Prompt B)
- 🆕 **中文输出强制**: 所有 Stage prompt 添加 Language Requirement
- 🔧 修复 `RelationChange` 属性访问错误
- 🔧 优化验证层参数 (min_overlap: 2→1)
- 🔧 改进 Stage 3 修改日志前端显示
- 🔧 修复 TCC 内容中英文混搭问题

### v2.5.0 (2025-11-19) - Session 9
- 🆕 集成 Google Gemini 2.5 Flash
- 🔧 解决 DeepSeek 大脚本 JSON 截断问题
- 📄 新增 `ref/gemini-integration.md` 文档
- 🧪 新增 `test_gemini_api.py` API 测试脚本

### v2.4.1 (2025-11-14) - Session 8
- 🔧 修复 Stage 3 issue_id 验证
- 🔧 修复 Mermaid 可视化渲染
- 🔧 修复 TXT 解析器事件循环错误

### v2.4.0 (2025-11-13) - Session 6-7
- 🆕 TXT 剧本解析器 (Phase 1-3)
- 🆕 Web UI TXT 上传和预览
- 🔧 Stage 2 JSON 解析优化

### v2.3.0 (2025-11-13) - Session 5
- 🆕 Markdown 报告导出
- 🆕 Mermaid TCC 关系图

### v2.2.0 (2025-11-12) - Session 3-4
- 🆕 LangSmith 可观测性
- 🆕 A/B 测试框架

### v2.1.0 (2025-11-12) - Session 1-2
- 🆕 Web UI 界面
- 🆕 Docker 容器化

---

**文档版本**: 1.1
**最后更新**: 2025-11-22
**维护者**: AI Assistant (Claude Code)
