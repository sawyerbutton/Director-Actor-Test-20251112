# 项目开发进度与遗留问题

**项目名称**: 剧本叙事结构分析系统 (Script Narrative Structure Analysis System)
**当前版本**: v2.11.1
**更新日期**: 2025-12-02
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
| **TXT 报告导出** | ✅ 完成 | 100% | **Session 15 新增** - 纯文本报告格式 |
| Docker 容器化 | ✅ 完成 | 100% | docker-compose 一键部署 |
| **Gemini 集成** | ✅ 完成 | 100% | **Session 9 新增** - 解决大脚本问题 |
| **动作分析协议 (AAP)** | ✅ 完成 | 100% | **Session 10 新增** - Discoverer 优化 |
| **版本追踪系统** | ✅ 完成 | 100% | **Session 11 新增** - 部署版本识别 |
| **Gemini 模型选择** | ✅ 完成 | 100% | **Session 12 新增** - Web UI 模型切换 |
| **TXT 解析器中文格式** | ✅ 完成 | 100% | **Session 13 新增** - 支持中文顿号场景格式 |
| **Gemini 3 专用 API Key** | ✅ 完成 | 100% | **Session 13 新增** - 双 API Key 支持 |
| **Gemini Thinking 优化** | ✅ 完成 | 100% | **Session 14 新增** - 响应速度大幅提升 |
| **完整报告 Tab** | ✅ 完成 | 100% | **Session 15 新增** - 集中展示所有分析内容 |
| **Mermaid 关系图增强** | ✅ 完成 | 100% | **Session 15 新增** - TCC关系连接+图例 |
| **分析结果持久化** | ✅ 完成 | 100% | **Session 16 新增** - SQLite 缓存 + 历史记录 |
| **历史记录详情优化** | ✅ 完成 | 100% | **Session 17 新增** - 详情弹窗可视化增强 |

**总体完成度**: 100%

---

## 📅 开发历程 (Session 1-17)

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

### Session 11: 版本追踪系统 + Gemini 3 Pro 适配 (2025-11-24) 🆕
**目标**: 解决 ECS 部署时难以识别版本的问题，并适配 Gemini 3 Pro 的特性

**实现内容**:

1. **版本追踪系统**
   - 新增 `src/version.py` - 集中管理版本信息
   - 健康检查端点 `/health` 返回版本和 git 信息
   - Web UI 页脚显示版本号和 commit hash
   - `deploy.sh` 新增 `version` 命令查看版本
   - Docker 镜像支持 `APP_VERSION` 变量

2. **Gemini 3 Pro 响应格式适配**
   - 修复多部分响应解析 (`[{'type': 'text', 'text': '...'}]`)
   - `src/parser/llm_enhancer.py:_parse_json_response()` 支持列表格式

3. **Gemini 3 Pro 慢响应适配**
   - LLM 调用超时增至 120 秒
   - Docker healthcheck: interval 60s, timeout 30s, retries 5, start_period 120s

**新增文件**:
- `src/version.py` - 版本信息模块
- `ref/version-tracking.md` - 版本追踪指南

**修改文件**:
- `src/web/app.py` - 健康端点返回版本
- `templates/base.html` - 页脚版本显示
- `docker-compose.yml` - healthcheck 优化
- `src/pipeline.py` - LLM timeout 配置
- `src/parser/llm_enhancer.py` - 多部分响应处理
- `scripts/deploy.sh` - version 命令

### Session 12: Gemini 模型选择功能 (2025-11-24) ✅ 完成
**目标**: 在 Web UI 上支持选择不同的 Gemini 模型版本

**背景**:
- 用户需要根据场景选择合适的 Gemini 模型
- 不同模型有不同的速度和能力特性

**实现内容**:

1. **Web UI 修改** (`templates/index.html`)
   - 当选择 Gemini 提供商时，显示模型子选项下拉框
   - 选项: Gemini 2.5 Flash (推荐) / Gemini 2.5 Pro / Gemini 2.0 Flash / Gemini 3 Pro Preview
   - 动态显示/隐藏模型选择器

2. **前端逻辑** (`static/js/upload.js`)
   - 监听 provider 变化，自动显示/隐藏 Gemini 模型选择器
   - 提交时自动获取选中的 Gemini 模型
   - 更新 provider 提示信息

3. **Pipeline 优化** (`src/pipeline.py`)
   - 默认模型: `gemini-2.5-flash`
   - 模型特定 timeout: Pro 模型 120s, Flash 模型 60s

4. **部署脚本修复** (`scripts/deploy.sh`)
   - 修复 APP_VERSION 未传递给 docker-compose 的问题
   - 新增 `rebuild` 命令强制重建镜像

**修复的问题**:
- 模型名称错误: `gemini-2.5-flash-preview-05-20` → `gemini-2.5-flash`
- docker-compose 未接收 APP_VERSION 导致使用错误镜像
- 新增 `--no-cache` 重建选项

**可用 Gemini 模型**:
- `gemini-2.5-flash`: 快速响应，推荐用于一般分析
- `gemini-2.5-pro`: 高级推理，适合复杂分析
- `gemini-2.0-flash`: 上一代 Flash 模型
- `gemini-3-pro-preview`: Gemini 3 Pro 预览版，高级推理能力

### Session 13: TXT 解析器增强 + Gemini 3 专用 API Key (2025-11-24) ✅ 完成
**目标**: 修复 TXT 解析器对中文顿号格式的支持，并实现 Gemini 3 专用 API Key

**背景**:
- 用户上传的剧本使用中文顿号格式 (`1、场景名`)，未被正确识别
- Gemini 3 Pro Preview 免费配额耗尽，需要使用专用付费 API Key

**发现的问题**:

1. **TXT 解析器只识别 1 个场景** (实际 15 个)
   - 原因: 剧本使用 `1、上海家卧室，日，内` 格式
   - 中文顿号 `、` 未在场景头模式中支持

2. **Stage 3 ModificationValidation 导入错误**
   - `NameError: name 'ModificationValidation' is not defined`
   - 缺失 import 语句

3. **Gemini 3 Pro Preview 配额超限 (429 错误)**
   - 免费 API Key 配额用完
   - 需要使用专用的 `GOOGLE_GEMINI3_API_KEY`

**实现内容**:

1. **TXT 解析器中文顿号支持** (`src/parser/txt_parser.py:35`)
   ```python
   # 新增场景头模式
   r'^(\d+)[、，,]\s*(.+)',  # 1、酒吧 - 夜 (中文顿号格式)
   ```
   - 支持中文顿号 `、`、中文逗号 `，`、英文逗号 `,`

2. **ModificationValidation 导入修复** (`src/pipeline.py:625`)
   ```python
   from prompts.schemas import ..., ModificationValidation
   ```

3. **Gemini 3 专用 API Key** (`src/pipeline.py:299-308`)
   ```python
   if "gemini-3" in model:
       api_key = os.getenv("GOOGLE_GEMINI3_API_KEY") or os.getenv("GOOGLE_API_KEY")
   ```
   - Gemini 3 模型优先使用 `GOOGLE_GEMINI3_API_KEY`
   - 如未设置则 fallback 到 `GOOGLE_API_KEY`

**测试结果**:

| 剧本 | 场景数 | Stage 1 | Stage 2 | Stage 3 | 总耗时 | 状态 |
|------|--------|---------|---------|---------|--------|------|
| 蓝1 第三版.txt | 15 | 3 TCCs (0.92-0.98) | A:1, B:2, C:0 | 10/10 fixed | 100.24s | ✅ |
| 百妖1.txt | 12 | 3 TCCs (0.90-0.98) | A:1, B:1, C:1 | 10/10 fixed | 191.44s | ✅ |

**识别的 TCC (百妖1.txt)**:
- TCC_01 (A-line): 玉鼠精为其电商平台项目寻求创业办投资 (conf: 0.98)
- TCC_02 (B-line): 悟空因外貌与过往经历产生的自我认同困境 (conf: 0.90)
- TCC_03 (C-line): 阿蠢对偶像玉鼠精从盲目崇拜到幻想破灭 (conf: 0.95)

**修改文件**:
- `src/parser/txt_parser.py:35` - 新增中文顿号场景格式
- `src/pipeline.py:299-308` - Gemini 3 专用 API Key 逻辑
- `src/pipeline.py:625` - 添加 ModificationValidation 导入

**结论**:
- Gemini 2.5 Pro 运行稳定，无超时问题，推荐用于生产
- Gemini 3 Pro Preview 响应较慢 (15-20s/请求)，建议仅在需要高级推理时使用

### Session 14: Gemini Thinking 模式优化 (2025-11-30) ✅ 完成
**目标**: 优化 Gemini 模型的响应速度，通过配置 thinking 参数减少不必要的推理时间

**背景**:
- Gemini 2.5 Flash 默认启用 Thinking 模式，导致响应时间过长 (~90s)
- Gemini 3 Pro 默认使用深度推理模式，响应较慢 (~15-20s)
- 用户反馈 API 响应速度太慢，影响使用体验

**问题分析**:

根据 [Google Gemini Thinking 文档](https://ai.google.dev/gemini-api/docs/thinking)：
- **Gemini 2.5 Flash**: 支持 `thinking_budget` 参数 (0-24576)，设为 0 可完全禁用
- **Gemini 2.5 Pro**: 支持 `thinking_budget` 参数 (128-32768)，不能完全禁用
- **Gemini 3 Pro**: 官方推荐使用 `thinking_level` 参数 ("low"/"high")

**发现的问题**:

1. **LangChain thinking_level 不兼容** (GitHub Issue #1366)
   - LangChain 3.2.0 虽然定义了 `thinking_level` 参数
   - 但底层 Google SDK 尚未正确支持，报错: `Unknown field for ThinkingConfig: thinking_level`
   - 临时解决方案: Gemini 3 使用默认配置

2. **thinking_budget 有效**
   - Gemini 2.5 Flash 设置 `thinking_budget=0` 后响应时间从 ~90s 降至 ~1.5s
   - Gemini 2.5 Pro 设置 `thinking_budget=128` 后响应时间 ~2.5s

**实现内容**:

1. **Pipeline 优化** (`src/pipeline.py:311-347`)
   ```python
   # Gemini 2.5 Flash: 禁用 thinking
   thinking_config["thinking_budget"] = 0

   # Gemini 2.5 Pro: 最小化 thinking
   thinking_config["thinking_budget"] = 128

   # Gemini 3 Pro: 使用默认配置 (thinking_level 暂不支持)
   # TODO: 等 LangChain 修复后切换到 thinking_level="low"
   ```

2. **Web UI 提示更新** (`templates/index.html:121-127`)
   - 显示各模型的预期响应时间
   - Gemini 2.5 Flash: ~1-2s/请求
   - Gemini 2.5 Pro: ~5-10s/请求
   - Gemini 3 Pro: ~10-15s/请求

3. **依赖版本升级** (`requirements.txt`)
   - `langchain-google-genai>=3.2.0` (支持 thinking_budget)

**测试结果**:

| 模型 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| gemini-2.5-flash | ~90s | **1.57s** | **98%** |
| gemini-2.5-pro | ~10s | **2.57s** | **74%** |
| gemini-3-pro-preview | ~100s | **4.58s** | **95%** |

**解决方案**:

由于 LangChain 的 `thinking_level` 参数不可用 ([GitHub Issue #1366](https://github.com/langchain-ai/langchain-google/issues/1366))，
我们创建了自定义的 `ChatGemini3` 包装器，直接使用 `google-genai` SDK：

1. **自定义 LLM 包装器** (`src/gemini3_llm.py`)
   - 继承 LangChain 的 `BaseChatModel`，保持兼容性
   - 直接使用 `google-genai>=1.52.0` SDK
   - 支持 `thinking_level="LOW"` 参数
   - 性能提升 95% (从 ~100s 到 ~4.5s)

2. **Pipeline 集成** (`src/pipeline.py:325-336`)
   ```python
   if "gemini-3" in model:
       return ChatGemini3(
           api_key=api_key,
           model=model,
           thinking_level="LOW",
           temperature=temperature,
           max_output_tokens=max_tokens,
       )
   ```

**修改文件**:
- `src/gemini3_llm.py` - 新增自定义 Gemini 3 LLM 包装器
- `src/pipeline.py:21,325-336` - 导入和使用 ChatGemini3
- `templates/index.html:121-127` - Web UI 响应时间提示
- `requirements.txt` - 添加 google-genai>=1.52.0

**结论**:
- **Gemini 2.5 Flash**: 最快 (~1.5s/请求)，适合一般分析
- **Gemini 2.5 Pro**: 推理更强 (~2.5s/请求)，适合复杂分析
- **Gemini 3 Pro**: 最新模型 (~4.5s/请求)，快速模式已启用

### Session 16: 分析结果持久化 (2025-12-01) ✅ 完成
**目标**: 实现分析结果的 SQLite 持久化缓存，避免重复 LLM 调用，提供历史记录查看功能

**背景**:
- 当前分析结果存储在内存中，服务重启后丢失
- 每次分析都需要重新调用 LLM API，耗时且费钱
- 用户无法查看历史分析记录

**实现内容**:

1. **数据库模块** (`src/db/`)
   - `models.py`: SQLite 表定义，`AnalysisCache` 和 `CacheStats` 数据类
   - `cache.py`: `CacheManager` 类，提供缓存 CRUD 操作
   - `cleanup.py`: 过期记录自动清理调度器
   - 特性: SHA256 内容哈希、90天过期、命中率统计

2. **Web 应用集成** (`src/web/app.py`)
   - 分析前查询缓存，命中则直接返回
   - 分析后自动存储结果
   - 新增 API 端点:
     - `GET /api/cache/stats` - 缓存统计
     - `GET /api/history` - 历史记录列表 (分页、搜索、过滤)
     - `GET /api/history/{id}` - 单条记录详情
     - `DELETE /api/history/{id}` - 删除记录
     - `POST /api/cache/cleanup` - 清理过期记录
     - `GET /history` - 历史记录页面

3. **历史记录页面** (`templates/history.html`)
   - 缓存统计卡片 (总记录、命中率、命中/未命中数)
   - 搜索和过滤 (剧本名称、提供商、模型)
   - 分页表格展示历史记录
   - 查看详情模态框
   - 删除和清理功能

4. **CLI 缓存命令** (`src/cli.py`)
   ```bash
   python -m src.cli cache list              # 列出缓存记录
   python -m src.cli cache stats             # 查看缓存统计
   python -m src.cli cache cleanup           # 清理过期记录
   python -m src.cli cache clear             # 清空所有缓存
   python -m src.cli cache delete <id>       # 删除指定记录
   python -m src.cli analyze script.json --no-cache  # 忽略缓存强制分析
   ```

5. **单元测试** (`tests/test_cache.py`)
   - 31 个测试用例，覆盖所有功能
   - 测试 CRUD 操作、分页、过滤、统计、过期清理等

**新增文件**:
- `src/db/__init__.py` - 模块入口
- `src/db/models.py` - 数据模型和表定义 (~210 行)
- `src/db/cache.py` - 缓存管理器 (~475 行)
- `src/db/cleanup.py` - 清理调度器 (~60 行)
- `templates/history.html` - 历史记录页面 (~475 行)
- `tests/test_cache.py` - 单元测试 (~400 行)

**修改文件**:
- `src/web/app.py` - 缓存集成和 API 端点
- `src/cli.py` - CLI 缓存子命令
- `templates/base.html` - 导航栏添加历史记录入口
- `scripts/run_web_server.sh` - 修复 PYTHONPATH 设置

**预期效果**:

| 指标 | 首次分析 | 缓存命中 |
|------|----------|----------|
| 响应时间 | 60-180秒 | <1秒 |
| API 调用 | 15-75次 | 0次 |
| API 成本 | $0.05-0.20 | $0 |

**测试结果**:
- 单元测试: 31/31 通过 (100%)
- 全量测试: 100/100 通过 (4 跳过)
- API 验证: `/api/cache/stats`, `/api/history` 正常工作
- CLI 验证: `cache stats`, `cache list` 正常工作

**端到端验证** (2025-12-01):
| 测试项 | 状态 | 说明 |
|--------|------|------|
| 缓存 MISS | ✅ | 首次分析触发 LLM 调用，耗时 211 秒 |
| 缓存保存 | ✅ | 三阶段全部成功后自动保存 |
| 缓存 HIT | ✅ | 第二次上传立即返回，耗时 ~10 毫秒 |
| 缓存统计 | ✅ | 命中率 75%，准确统计 |
| 历史记录 | ✅ | 缓存条目可在 `/history` 页面查看 |

**修复的问题**:

1. **缓存保存逻辑** (`src/web/app.py:936-967`)
   - 问题: 即使 Stage 3 失败，不完整结果也会被缓存
   - 修复: 仅在三阶段全部完成时保存
   - 添加: 不完整结果的警告日志

2. **缓存命中/未命中日志** (`src/db/cache.py:116-144`)
   - 问题: 不完整条目被计入缓存命中
   - 改进: 区分 "Cache HIT (complete)" 和 "Cache HIT (incomplete, ignoring)"
   - 不完整条目正确计入未命中统计

3. **change_type 验证** (`prompts/schemas.py:291-308`)
   - 问题: LLM 返回无效值 ('none', 'N/A', 'skip') 导致验证失败
   - 修复: 添加 `normalize_change_type` 验证器，自动规范化为有效值

**性能对比**:
| 场景 | 耗时 | 加速比 |
|------|------|--------|
| 首次分析 (缓存 MISS) | 211 秒 | 基准 |
| 重复分析 (缓存 HIT) | ~10 毫秒 | **21,000x** |

### Session 17: 历史记录详情弹窗优化 (2025-12-02) ✅ 完成
**目标**: 优化历史记录页面的"查看详情"弹窗，提供更丰富的可视化展示

**背景**:
- 原有详情弹窗仅显示原始 JSON 数据，可读性差
- 用户反馈"页面展示内容样式和内容都很少"
- 需要与结果页面类似的可视化展示

**实现内容**:

1. **概览卡片区** (4 个统计卡片)
   - 场景数 (蓝色边框)
   - TCC 数 (黄色边框)
   - 处理时间 (绿色边框)
   - API 调用数 (青色边框)

2. **基本信息区** (Flexbox 布局优化)
   - 左侧: 记录 ID、内容哈希(截断显示)、提供商、模型
   - 右侧: 创建时间、过期时间、缓存状态、脚本名称
   - 样式优化: 使用 `d-flex align-items-center` 实现对齐
   - 哈希值截断为 16 位 + `...`，悬停显示完整值

3. **5 个 Tab 页**
   | Tab | 功能 | 辅助函数 |
   |-----|------|----------|
   | TCC 识别 | TCC 卡片，置信度徽章，证据场景标签 | `renderTCCsContent()` |
   | A/B/C 分级 | A线(黄)、B线(青)、C线(灰)卡片，评分和力量分析 | `renderRankingsContent()` |
   | 场景列表 | 手风琴式展开，显示场景使命、角色、关键事件 | `renderScenesContent()` |
   | 修改记录 | 验证统计卡片，修改日志列表 | `renderModificationsContent()` |
   | 原始数据 | 折叠式 JSON 展示 (Stage 1/2/3) | 内联实现 |

4. **辅助函数**
   - `escapeHtml(text)` - XSS 防护
   - `formatDate(dateStr)` - 日期格式化为中文

**修改文件**:
- `templates/history.html` - 重写 `renderDetailContent()` 函数 (+200 行)
  - 新增 4 个辅助函数: `renderTCCsContent()`, `renderRankingsContent()`, `renderScenesContent()`, `renderModificationsContent()`
  - 基本信息区从表格布局改为 Flexbox 布局

**UI 组件使用**:
- Bootstrap 5 Cards (统计卡片、信息卡片)
- Bootstrap 5 Tabs (5 个标签页)
- Bootstrap 5 Accordion (场景列表、原始数据)
- Bootstrap 5 Badges (置信度、状态、线级别)
- Bootstrap Icons (图标装饰)

**测试验证**:
- ✅ API 数据结构兼容性验证
- ✅ 页面加载正常
- ✅ JavaScript 函数完整嵌入
- ✅ 所有 Tab 页渲染正确

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
- [x] 单元测试 (100/100 通过, 4 跳过)
- [x] 综合文档 (120KB+ across 15+ files)
- [x] **分析结果缓存**: SQLite 持久化 + 历史记录 (**Session 16 新增**)

---

## ⚠️ 已知遗留问题

### 0. Gemini 3 Pro 响应时间慢 (v2.7.0 新增) 🆕
**严重程度**: 中
**状态**: 已适配 (v2.7.0)
**描述**:
- Gemini 3 Pro (`gemini-3-pro-preview`) 单次请求响应时间 ~15-20 秒
- 对比: DeepSeek ~2 秒/请求
- TXT LLM 增强解析 (3 场景 × 5 调用) 需要 4-5 分钟
- 可能导致 Docker healthcheck 超时，容器状态变为 unhealthy

**根本原因**:
- Gemini 3 Pro 是预览版，具有高级推理能力但响应较慢
- 每个场景需要 5 次 LLM 调用 (scene_mission, setup_payoff, relation_changes, info_changes, key_events)

**已实施的解决方案** (v2.7.0):
1. ✅ LLM 调用超时增加至 120 秒 (`src/pipeline.py:315`)
2. ✅ Docker healthcheck 调整:
   - `interval`: 30s → 60s
   - `timeout`: 10s → 30s
   - `retries`: 3 → 5
   - `start_period`: 40s → 120s
3. ✅ Gemini 多部分响应格式处理 (`src/parser/llm_enhancer.py:411-428`)

**潜在优化方向**:
1. 并行化 LLM 调用 (5 个提取任务可并行执行)
2. 添加进度指示器，显示预计剩余时间
3. 考虑使用 Gemini 2.5 Flash 作为 TXT 解析的备选（更快但推理能力稍弱）

**相关文件**:
- `src/pipeline.py:308-316` - Gemini LLM 配置
- `docker-compose.yml:52-57` - healthcheck 配置
- `src/parser/llm_enhancer.py:411-428` - 响应格式处理

---

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
4. [x] ~~**分析结果持久化**~~ (Session 16 已完成 ✅)

### 中期 (1-2 月)
1. [ ] 实现 LLM 调用批处理以降低成本
2. [x] ~~添加分析结果历史记录~~ (已纳入 Session 16)
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
| `src/web/app.py` | Web 后端 | 122-131: 提供商配置, 缓存集成 |
| `src/db/cache.py` | 缓存管理器 | **Session 16 新增** |
| `src/db/models.py` | 数据模型 | **Session 16 新增** |
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
| `tests/test_cache.py` | 缓存模块单元测试 (31 tests) **Session 16 新增** |

---

## 🧪 测试状态

### 单元测试
```bash
pytest tests/ -v
# Result: 100 passed, 4 skipped (LLM integration tests)
# Status: ✅ 100% pass rate
# 包括: test_cache.py (31 tests), test_schemas.py, test_golden_dataset.py 等
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

### v2.11.1 (2025-12-02) - Session 17 ✅ 完成
#### 历史记录详情弹窗优化
- 🎨 **详情弹窗重构**: 从原始 JSON 展示升级为富可视化界面
- 🆕 **概览卡片区**: 4 个统计卡片 (场景数、TCC数、处理时间、API调用)
- 🆕 **基本信息区优化**: Flexbox 布局，哈希截断显示，新增脚本名称字段
- 🆕 **5 个 Tab 页**: TCC识别、A/B/C分级、场景列表、修改记录、原始数据
- 🆕 **TCC 可视化卡片**: 置信度徽章、超级目标、证据场景标签
- 🆕 **A/B/C 分级展示**: 彩色边框区分 (A线黄、B线青、C线灰)
- 🆕 **场景手风琴**: 展开显示场景使命、角色、关键事件
- 🆕 **修改日志**: 验证统计卡片 + 修改状态徽章

#### 辅助函数
- 🆕 `renderTCCsContent()` - TCC 卡片渲染
- 🆕 `renderRankingsContent()` - A/B/C 分级渲染
- 🆕 `renderScenesContent()` - 场景列表渲染
- 🆕 `renderModificationsContent()` - 修改记录渲染

#### 文件变更
- 📄 更新 `templates/history.html` - 重写 renderDetailContent (+200 行)

### v2.11.0 (2025-12-01) - Session 16 ✅ 完成
#### 分析结果持久化
- 🆕 **SQLite 缓存系统**: 新增 `src/db/` 模块，实现分析结果持久化存储
- 🆕 **CacheManager 类**: 完整的缓存 CRUD 操作，支持 SHA256 内容哈希
- 🆕 **历史记录页面**: 新增 `/history` 页面，展示所有缓存的分析记录
- 🆕 **缓存统计**: 命中率、总记录数、按提供商/模型分组统计
- 🆕 **CLI 缓存命令**: `cache list/stats/cleanup/clear/delete` 子命令
- 🆕 **自动过期清理**: 90 天过期策略，支持手动和自动清理
- 🆕 **缓存命中提示**: 分析时显示缓存命中/未命中状态

#### 端到端测试修复
- 🔧 **缓存保存逻辑**: 仅在三阶段全部成功后保存，防止缓存不完整结果
- 🔧 **缓存命中/未命中统计**: 区分完整/不完整条目，准确统计命中率
- 🔧 **change_type 验证器**: 处理 LLM 返回的无效值 ('none', 'N/A', 'skip')
- 🔧 **日志改进**: 详细区分 "Cache HIT (complete)" 和 "Cache HIT (incomplete, ignoring)"

#### API 端点
- 🆕 `GET /api/cache/stats` - 缓存统计信息
- 🆕 `GET /api/history` - 历史记录列表 (分页、搜索、过滤)
- 🆕 `GET /api/history/{id}` - 单条记录详情
- 🆕 `DELETE /api/history/{id}` - 删除记录
- 🆕 `POST /api/cache/cleanup` - 清理过期记录

#### 文件变更
- 📄 新增 `src/db/__init__.py` - 模块入口
- 📄 新增 `src/db/models.py` - SQLite 表定义和数据类
- 📄 新增 `src/db/cache.py` - CacheManager 实现 (~475 行)
- 📄 新增 `src/db/cleanup.py` - 过期清理调度器
- 📄 新增 `templates/history.html` - 历史记录页面 (~475 行)
- 📄 新增 `tests/test_cache.py` - 单元测试 (31 tests)
- 📄 更新 `src/web/app.py` - 缓存集成和 API 端点
- 📄 更新 `src/cli.py` - CLI 缓存子命令
- 📄 更新 `templates/base.html` - 导航栏历史记录入口

#### 性能提升
| 指标 | 首次分析 | 缓存命中 | 提升 |
|------|----------|----------|------|
| 响应时间 | 60-180秒 | <1秒 | **99%+** |
| API 调用 | 15-75次 | 0次 | **100%** |
| API 成本 | $0.05-0.20 | $0 | **100%** |

### v2.10.0 (2025-11-30) - Session 15 ✅ 完成
#### TXT 报告导出
- 🆕 **TXT 报告导出**: 新增纯文本格式报告导出功能
- 🆕 **TXTExporter 类**: 新增 `src/exporters/txt_exporter.py` (210+ 行代码)
- 🆕 **TXT 报告模板**: 新增 `templates/report_template.txt.j2` (Jinja2 模板)
- 🆕 **CLI --export-txt 参数**: 支持 `--export-txt report.txt` 导出 TXT 报告
- 🆕 **Web UI TXT 下载按钮**: 结果页面新增 "下载 TXT 报告" 按钮
- 🆕 **TXT 下载接口**: `/api/download/report-txt/{job_id}` 端点

#### 完整报告 Tab
- 🆕 **完整报告 Tab**: 结果页面新增"完整报告"标签页，集中展示所有分析内容
- 🆕 **HTML 报告渲染**: `displayFullReport()` 函数生成完整的 HTML 报告视图
- 🆕 **自动生成关键发现**: `generateKeyFindings()` 基于分析数据自动生成摘要
- 🆕 **自动生成建议**: `generateRecommendations()` 智能生成改进建议

#### Mermaid 关系图增强
- 🔧 **TCC 关系连接**: 修复关系图只显示孤立节点的问题，添加三层关系推断：
  1. 基于证据场景重叠建立"场景交织"连接
  2. 基于叙事层级建立"主线驱动"和"情节呼应"连接
  3. 兜底机制：确保所有TCC都有关联线
- 🔧 **丰富节点信息**: 节点现在显示线级标签、超级目标摘要、置信度
- 🆕 **图例说明**: 添加清晰的颜色和连接类型图例
- 🎨 **样式优化**: A线红色、B线青色、C线绿色，区分度更高

#### 文件变更
- 📄 更新 `src/exporters/__init__.py` - 导出 TXTExporter
- 📄 更新 `src/cli.py` - 添加 --export-txt 参数和 export_txt 函数
- 📄 更新 `src/web/app.py` - 添加 TXT 生成和下载接口
- 📄 更新 `templates/results.html` - 添加 TXT 下载按钮、完整报告 Tab
- 📄 更新 `static/js/results.js` - 添加 displayFullReport、增强 displayMermaidDiagram (+200 行)

**TXT 报告特点**:
- 纯文本格式，无 Markdown 标记
- 使用 ASCII 边框和分隔线，适合终端查看
- 包含完整的三阶段分析结果
- UTF-8 编码，支持中文

### v2.9.0 (2025-11-30) - Session 14 ✅ 完成
- 🚀 **Gemini Thinking 优化**: 所有模型响应速度大幅提升 (74-98%)
- 🆕 **ChatGemini3 包装器**: 新增自定义 LLM 包装器绕过 LangChain 限制
- 🆕 **thinking_budget 配置**: Gemini 2.5 Flash/Pro 禁用或最小化 thinking
- 🆕 **thinking_level 支持**: Gemini 3 Pro 使用 google-genai SDK 实现快速模式
- 📊 **性能对比**: 2.5 Flash 1.57s, 2.5 Pro 2.57s, 3 Pro 4.58s
- 🔧 **依赖升级**: google-genai>=1.52.0, langchain-google-genai>=3.2.0
- 📄 新增 `src/gemini3_llm.py` - 自定义 Gemini 3 LLM 包装器
- 📄 更新 `src/pipeline.py:21,325-336` - 导入和使用 ChatGemini3
- 📄 更新 `templates/index.html:121-127` - Web UI 响应时间提示
- 📄 更新 `requirements.txt` - 添加 google-genai>=1.52.0

### v2.8.1 (2025-11-24) - Session 13 ✅ 完成
- 🆕 **TXT 解析器中文顿号支持**: 新增 `1、场景名` 格式识别
- 🆕 **Gemini 3 专用 API Key**: 支持 `GOOGLE_GEMINI3_API_KEY` 环境变量
- 🔧 **ModificationValidation 导入修复**: Stage 3 缺失 import 语句
- 🧪 **完整测试**: 蓝1 第三版.txt (15 场景) + 百妖1.txt (12 场景) 全部通过
- 📄 更新 `src/parser/txt_parser.py:35` - 新增中文顿号场景格式
- 📄 更新 `src/pipeline.py:299-308` - Gemini 3 API Key 逻辑
- 📄 更新 `src/pipeline.py:625` - 添加 ModificationValidation 导入

### v2.8.0 (2025-11-24) - Session 12 ✅ 完成
- 🆕 **Gemini 模型选择**: Web UI 支持选择 Gemini 2.5 Flash / 2.5 Pro / 2.0 Flash / 3 Pro Preview
- 🆕 **模型子选项**: 当选择 Gemini 时显示模型版本下拉框
- 🆕 **动态 timeout**: Pro/Gemini 3 模型 120s, Flash 模型 60s
- 🔧 **部署修复**: APP_VERSION 传递给 docker-compose
- 🔧 **模型名称修复**: 使用正确的模型 ID (gemini-2.5-flash)
- 🔧 **新增 rebuild 命令**: `./scripts/deploy.sh rebuild` 强制重建
- 📄 更新 `templates/index.html` - 添加模型选择 UI
- 📄 更新 `static/js/upload.js` - 前端模型选择逻辑
- 📄 更新 `src/pipeline.py` - 模型配置和 timeout
- 📄 更新 `scripts/deploy.sh` - rebuild 命令和 APP_VERSION 传递
- 📄 更新 `docker-compose.yml` - 默认版本 2.8.0

### v2.7.0 (2025-11-24) - Session 11
- 🆕 **版本追踪系统**: 集中管理版本信息，便于部署识别
- 🆕 新增 `src/version.py` - 版本信息模块
- 🆕 新增 `ref/version-tracking.md` - 版本追踪指南
- 🔧 健康端点 `/health` 返回版本和 git 信息
- 🔧 Web UI 页脚显示版本号和 commit hash
- 🔧 **Gemini 3 Pro 适配**: 修复多部分响应格式解析
- 🔧 **超时优化**: LLM 调用 120s，healthcheck 优化

### v2.6.0 (2025-11-22) - Session 10
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

**文档版本**: 1.9
**最后更新**: 2025-12-02
**维护者**: AI Assistant (Claude Code)
