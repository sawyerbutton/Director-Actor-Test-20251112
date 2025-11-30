# Claude Code Reference Documentation

This file provides quick navigation to all project documentation for AI-assisted development.

## Project Overview

**Name**: 剧本叙事结构分析系统 (Script Narrative Structure Analysis System)

**Purpose**: Multi-agent LLM system for analyzing and correcting narrative structure in screenplays using a three-stage pipeline (Discover → Audit → Modify).

**Technology Stack**: Python, LangChain, LangGraph, Pydantic, DeepSeek/Claude/OpenAI/Gemini

**Current Version**: 2.9.0 (2025-11-30)
**Last Updated**: 2025-11-30
**Completion**: 100% (All three stages + TXT Parser + Web UI + Mermaid Visualization + LangSmith observability + A/B testing + Markdown export + Action Analysis Protocol + Gemini Model Selection + Chinese Scene Format + Gemini 3 API Key + Gemini Thinking Mode Optimization)

---

## Quick Start

### For First-Time Users
1. Read: [`ref/getting-started.md`](ref/getting-started.md) - Installation, setup, and basic usage
2. Run: `pip install -r requirements.txt` - Install dependencies (✅ Done)
3. Configure: Copy `.env.example` to `.env` and add your DeepSeek API key (✅ Done)
4. Run: `pytest tests/ -v` - Verify installation (✅ 44/44 tests passing)
5. Try: `python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json` (✅ All stages working)

### For Developers
1. Read: [`ref/architecture.md`](ref/architecture.md) - System design and components
2. Read: [`prompts/README.md`](prompts/README.md) - Prompt engineering guide
3. Review: [`tests/`](tests/) - Test examples

---

## Current Status (2025-11-30)

### ✅ What's Working (100% Complete)
- **Unit Tests**: 44/44 passing (100% pass rate)
- **Stage 1 (Discoverer)**: ✅ Successfully identifies TCCs with 85-95% confidence
- **Stage 2 (Auditor)**: ✅ Ranks TCCs as A/B/C-lines with proper scoring
- **Stage 3 (Modifier)**: ✅ Fixes structural issues with normalized issue_id validation
- **Dependencies**: All packages installed (LangChain 1.0.5, LangGraph 1.0.3, LangSmith 0.1+)
- **DeepSeek Integration**: Configured and operational
- **Gemini 3 Pro Integration**: ✅ 1M context, 64K output, advanced reasoning (solves Stage 3 token limits)
- **Documentation**: Complete reference docs (120KB+ across 15+ files)
- **Error Handling**: Intelligent JSON parsing and schema validation with 0 retries
- **TXT Script Parser** (v2.4.0): ✅ Convert TXT scripts to JSON (Phase 1-3 complete)
- **LLM Enhancement**: ✅ Semantic extraction with async progress callbacks
- **Web UI Integration**: ✅ TXT upload, preview, continue-to-analysis workflow
- **Mermaid Visualization** (v2.4.1): ✅ Interactive TCC relationship diagrams with A/B/C color coding
- **LangSmith Observability**: ✅ Auto-tracing, performance metrics, cost estimation
- **A/B Testing Framework**: ✅ Compare providers, prompts, and parameters
- **Markdown Export** (v2.3.0): ✅ Professional reports + Mermaid visualization
- **🆕 Action Analysis Protocol (AAP)** (v2.6.0): ✅ Performance notes & visual actions extraction
- **🆕 TCC Middleware Layer** (v2.6.0): ✅ Coverage filter + antagonist mutual exclusion
- **🆕 Scene Validation Layer** (v2.6.0): ✅ Atomic reverse verification
- **🆕 Chinese Output Enforcement** (v2.6.0): ✅ All prompts enforce Chinese output
- **🆕 Version Tracking** (v2.7.0): ✅ Centralized version info, health endpoint, UI footer display
- **🆕 Gemini Model Selection** (v2.8.0): ✅ Web UI supports 4 Gemini models (2.5 Flash/Pro, 2.0 Flash, 3 Pro Preview)
- **🆕 Chinese Scene Format** (v2.8.1): ✅ TXT parser supports `1、场景名` format (Chinese 顿号)
- **🆕 Gemini 3 Dedicated API Key** (v2.8.1): ✅ Dual API key support (`GOOGLE_GEMINI3_API_KEY`)
- **🆕 Gemini Thinking Mode Optimization** (v2.9.0): ✅ 95% speed improvement via thinking_level=LOW

### 🎉 Recent Fixes (2025-11-30)

#### Session 14: Gemini Thinking Mode Optimization (v2.9.0)
1. **Custom ChatGemini3 Wrapper** (✅ NEW - Session 14)
   - **Problem**: LangChain `langchain-google-genai` doesn't support `thinking_level` parameter (GitHub Issue #1366)
   - **Solution**: Created custom `ChatGemini3` wrapper using `google-genai` SDK directly
   - **New File**: `src/gemini3_llm.py` (168 lines)
   - **Features**: Full LangChain compatibility, supports `thinking_level="LOW"` or `"HIGH"`

2. **Gemini 2.5 Thinking Budget Optimization** (✅ NEW - Session 14)
   - **Problem**: Gemini 2.5 models use expensive "thinking" by default
   - **Solution**: Set `thinking_budget=0` to disable thinking for fast responses
   - **Location**: `src/pipeline.py:276-286`
   - **Result**: 98% speed improvement (90s → 1.57s for Gemini 2.5 Flash)

3. **Gemini 3 Thinking Level Optimization** (✅ NEW - Session 14)
   - **Problem**: Gemini 3 Pro default thinking is very slow (~100s per request)
   - **Solution**: Use `thinking_level="LOW"` via ChatGemini3 wrapper
   - **Location**: `src/pipeline.py:288-306`, `src/gemini3_llm.py`
   - **Result**: 95% speed improvement (100s → 4.58s per request)

4. **Performance Improvements** (✅ VERIFIED - Session 14)
   | Model | Before | After | Improvement |
   |-------|--------|-------|-------------|
   | Gemini 2.5 Flash | ~90s | ~1.57s | 98% faster |
   | Gemini 2.5 Pro | ~10s | ~2.57s | 74% faster |
   | Gemini 3 Pro | ~100s | ~4.58s | 95% faster |

5. **Dependencies Update** (✅ NEW - Session 14)
   - Added `google-genai>=1.52.0` to `requirements.txt`
   - Required for `ChatGemini3` wrapper to access `thinking_level` parameter

6. **Web UI Model Hints Update** (✅ NEW - Session 14)
   - Updated `templates/index.html` with accurate timing info
   - Gemini 2.5 Flash: ~1-2s/请求, Thinking 已禁用
   - Gemini 2.5 Pro: ~2-3s/请求, Thinking 最小化
   - Gemini 3 Pro: ~4-5s/请求, 快速模式

#### Session 13: TXT Parser Enhancement + Gemini 3 API Key (v2.8.1)
1. **Chinese Scene Format Support** (✅ NEW - Session 13)
   - **Problem**: TXT parser only detected 1 scene instead of 15 for scripts using `1、场景名` format
   - **Solution**: Added regex pattern `r'^(\d+)[、，,]\s*(.+)'` to `SCENE_PATTERNS`
   - **Location**: `src/parser/txt_parser.py:35`
   - **Supports**: Chinese 顿号 `、`, Chinese comma `，`, English comma `,`

2. **Gemini 3 Dedicated API Key** (✅ NEW - Session 13)
   - **Problem**: Gemini 3 Pro Preview free tier quota exhausted (429 errors)
   - **Solution**: Use `GOOGLE_GEMINI3_API_KEY` for Gemini 3 models, fallback to `GOOGLE_API_KEY`
   - **Location**: `src/pipeline.py:299-308`
   - **Config**: Set `GOOGLE_GEMINI3_API_KEY` in `.env` for paid Gemini 3 access

3. **ModificationValidation Import Fix** (✅ FIXED - Session 13)
   - **Problem**: `NameError: name 'ModificationValidation' is not defined` in Stage 3
   - **Solution**: Added missing import statement
   - **Location**: `src/pipeline.py:625`

4. **End-to-End Testing** (✅ VERIFIED - Session 13)
   - **蓝1 第三版.txt**: 15 scenes, 3 TCCs, 100.24s total, 0 errors
   - **百妖1.txt**: 12 scenes, 3 TCCs, 191.44s total, 0 errors
   - **Model**: Gemini 2.5 Pro (stable, recommended)

#### Session 12: Gemini Model Selection (v2.8.0)
1. **Gemini Model Selection UI** (✅ NEW - Session 12)
   - **Feature**: Web UI dropdown to select Gemini model version
   - **Available Models**:
     - `gemini-2.5-flash` - Fast response, recommended
     - `gemini-2.5-pro` - Advanced reasoning
     - `gemini-2.0-flash` - Previous generation
     - `gemini-3-pro-preview` - Gemini 3 Pro preview
   - **Location**: `templates/index.html:113-128`, `static/js/upload.js`

2. **Model-Specific Timeout** (✅ NEW - Session 12)
   - Pro/Gemini 3 models: 120s timeout
   - Flash models: 60s timeout
   - **Location**: `src/pipeline.py:303-310`

3. **Deployment Fix** (✅ FIXED - Session 12)
   - **Problem**: docker-compose not receiving APP_VERSION
   - **Solution**: `APP_VERSION=${APP_VERSION} docker-compose up -d`
   - **New Command**: `./scripts/deploy.sh rebuild` for force rebuild
   - **Location**: `scripts/deploy.sh:117-122`

#### Session 11: Gemini 3 Pro + Version Tracking (v2.7.0)
1. **Gemini 3 Pro Integration** (✅ NEW - Session 11)
   - **Upgrade**: From Gemini 2.5 Flash to Gemini 3 Pro Preview
   - **Model ID**: `gemini-3-pro-preview`
   - **Features**: 1M context, 64K output, built-in advanced reasoning
   - **New Config**: `GOOGLE_GEMINI3_API_KEY` environment variable
   - **Fallback**: Uses `GOOGLE_API_KEY` if Gemini 3 key not set
   - **Location**: `src/pipeline.py:290-310`, `scripts/test_gemini_api.py`
   - **Reference**: https://ai.google.dev/gemini-api/docs/gemini-3

2. **Gemini Multi-Part Response Fix** (✅ FIXED - Session 11)
   - **Problem**: `the JSON object must be str, bytes or bytearray, not list`
   - **Cause**: Gemini 3 Pro returns `response.content` as list: `[{'type': 'text', 'text': '...'}]`
   - **Solution**: Updated `_parse_json_response()` to handle list-type responses
   - **Location**: `src/parser/llm_enhancer.py:411-428`

3. **Version Tracking System** (✅ NEW - Session 11)
   - **New File**: `src/version.py` - Centralized version info
   - **Health Endpoint**: Returns version, git commit, branch info
   - **Web UI**: Footer displays `v2.7.0 [commit]`
   - **Deploy Script**: New `version` command
   - **Reference**: [`ref/version-tracking.md`](ref/version-tracking.md)

#### Session 10: Discoverer Optimization - Action Analysis Protocol
1. **Action Analysis Protocol (AAP)** (✅ NEW - Session 10)
   - **Feature**: Extract performance_notes and visual_actions as TCC evidence
   - **New Models**: `PerformanceNote` in `prompts/schemas.py`
   - **New Fields**: `Scene.performance_notes`, `Scene.visual_actions`
   - **TXT Parser**: Regex extraction for `角色名(提示)` and `△/■/【】` patterns

2. **TCC Middleware Layer** (✅ NEW - Session 10)
   - **Coverage Filter**: `filter_low_coverage_tccs()` - threshold ≥15%
   - **Antagonist Check**: `check_antagonist_mutual_exclusion()` - prevent mirror TCCs
   - **Location**: `prompts/schemas.py`, `src/pipeline.py`

3. **Scene Validation Layer** (✅ NEW - Session 10)
   - **Function**: `validate_tcc_scene_evidence()` - atomic reverse verification
   - **Helper**: `_has_keyword_overlap()` - keyword matching (min_overlap=1)
   - **Purpose**: Prevent semantic hallucination in TCC identification

4. **Chinese Output Enforcement** (✅ FIXED - Session 10)
   - **Problem**: LLM outputs mixed English/Chinese (e.g., "玉鼠精's e-commerce funding")
   - **Solution**: Added Language Requirement section to all Stage prompts
   - **Location**: `prompts/stage1_discoverer.md`, `stage2_auditor.md`, `stage3_modifier.md`
   - **Result**: All TCC content now in pure Chinese

5. **Frontend Display Fix** (✅ FIXED - Session 10)
   - **Problem**: Stage 3 shows "理由: N/A" for applied modifications
   - **Solution**: Generate meaningful descriptions from field/new_value
   - **Location**: `static/js/results.js:296-317`
   - **Result**: Shows "详情: 添加了 xxx" instead of "N/A"

6. **RelationChange Attribute Fix** (✅ FIXED - Session 10)
   - **Problem**: `'RelationChange' object has no attribute 'from_state'`
   - **Solution**: Use correct Pydantic field name `from_` instead of `from_state`
   - **Location**: `prompts/schemas.py`

#### Session 9: Gemini Integration (2025-11-19)

### 🎉 Previous Fixes (2025-11-14)

#### Session 8: UX Optimization & Bug Fixes
1. **Stage 3 issue_id Validation** (✅ FIXED - Session 8)
   - **Problem**: LLM returns `ISS_001_corrected`, `ISS_002_fixed` not matching `^ISS_\d{3}$` pattern
   - **Solution**: Added `normalize_issue_id()` validator to extract ISS_XXX pattern
   - **Location**: `prompts/schemas.py:260-273`
   - **Result**: First attempt success, no retries needed, accurate modification counts

2. **Mermaid Visualization Not Rendering** (✅ FIXED - Session 8)
   - **Problem**: Visualization tab shows only code text, not rendered diagram
   - **Solution**:
     - Upgraded to Mermaid 10+ API: `mermaid.render()` instead of deprecated `mermaid.init()`
     - Changed initialization: `startOnLoad: false` to allow dynamic rendering
   - **Location**: `static/js/results.js:348-382`, `templates/results.html:5-16`
   - **Result**: Correct display of colored TCC relationship diagrams (A-line yellow, B-line blue, C-line gray)

3. **TXT Parser Event Loop Error** (✅ FIXED - Session 8)
   - **Problem**: `RuntimeError: no running event loop` during TXT upload
   - **Solution**:
     - Converted `LLMEnhancedParser.parse()` to async method
     - Properly await async parser in `run_parsing_job()`
   - **Location**: `src/parser/llm_enhancer.py:82-125`, `src/web/app.py:560-567`
   - **Result**: TXT parsing works correctly, progress callbacks trigger properly

#### Session 7: Web UI Foundation
4. **Stage 2 JSON Parsing** (✅ FIXED - Session 7)
   - **Solution**: Enhanced `clean_json_response()` with bracket-stack matching algorithm
   - **Location**: `src/pipeline.py:155-215`
   - **Result**: Extracts first complete JSON object, ignoring trailing text

5. **Stage 3 change_type Validation** (✅ FIXED - Session 7)
   - **Solution**: Extended allowed values and added normalization validator
   - **Location**: `prompts/schemas.py:275-289`
   - **Result**: Supports "remove" and "delete" operations with smart normalization

6. **Web UI WebSocket Serialization** (✅ FIXED - Session 7)
   - **Problem**: WebSocket couldn't send Script objects in progress updates
   - **Solution**: Restructured to send only serializable summary data
   - **Location**: `src/web/app.py:408-441`
   - **Result**: Real-time progress updates working correctly

7. **Frontend Data Structure Mismatch** (✅ FIXED - Session 7)
   - **Problem**: JavaScript expected flat fields, backend returns nested `reasoning` object
   - **Solution**: Modified frontend to use optional chaining for nested fields
   - **Location**: `static/js/results.js:252-278`
   - **Result**: Results page displays correctly without JavaScript errors

#### Session 9: Gemini 2.5 Flash Integration
8. **DeepSeek Token Limit Issues** (✅ SOLVED - Session 9)
   - **Problem**: DeepSeek's 16K max_tokens insufficient for Stage 3 large script analysis, causing JSON truncation
   - **Solution**: Integrated Google Gemini 2.5 Flash with 1M context + 65K output
   - **Implementation**:
     - Added `langchain-google-genai>=2.0.0` dependency
     - Extended `create_llm()` in `src/pipeline.py:288-303` to support Gemini
     - Updated `.env.example` and `docker-compose.yml` with GOOGLE_API_KEY
     - Modified Web UI to pass `default_provider` from environment to template
   - **Location**: `src/pipeline.py:288-303`, `templates/index.html:94-110`, `.env`, `requirements.txt`
   - **Result**: Successful analysis of large scripts (12+ scenes) with 0 errors, 0 retries
   - **Test File**: `test_gemini_api.py` - Pre-business API connectivity testing

9. **Gemini Model Selection** (✅ RESOLVED - Session 9)
   - **Problem**: Initial attempts used wrong model names (gemini-3-pro, gemini-2.0-flash-thinking-exp)
   - **Solution**: Corrected to official model name `gemini-2.5-flash`
   - **Reference**: https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash
   - **Result**: API test passed, full pipeline working

### 📊 Test Results Summary
```bash
# Unit Tests
pytest tests/ -v
# Result: 44 passed, 3 skipped (LLM integration tests)
# Status: ✅ 100% pass rate

# Complete Pipeline Test (End-to-End)
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json
# Stage 1: ✅ Success (3 TCCs identified with 0.80-0.95 confidence)
# Stage 2: ✅ Success (A-line: TCC_01, B-line: TCC_02, C-line: TCC_03)
# Stage 3: ✅ Success (4/4 issues fixed: removed invalid scene references)
# Errors: 0
# Retries: 0
# Status: ✅ Production Ready
```

### 🎯 System Status
**Status**: ✅ **Production Ready**
- All three stages operational
- Zero-retry success rate
- Comprehensive error handling
- Complete documentation
- Ready for real-world screenplay analysis

---

## Core Documentation

### 1. Project Overview
**File**: [`ref/project-overview.md`](ref/project-overview.md)

**Contents**:
- Project description and goals
- Key features and capabilities
- Technology stack
- Project status and metrics

**When to read**: Getting context about the project

---

### 2. Architecture
**File**: [`ref/architecture.md`](ref/architecture.md)

**Contents**:
- Director-Actor pattern design
- Three-stage pipeline explanation
- Data flow diagrams
- Component descriptions
- Error handling strategies
- LLM provider integration

**When to read**: Understanding system design, extending functionality

**Key sections**:
- Three-Stage Pipeline (lines 13-90)
- Data Flow (lines 92-125)
- Error Handling (lines 183-203)

---

### 3. Getting Started
**File**: [`ref/getting-started.md`](ref/getting-started.md)

**Contents**:
- Installation instructions
- API key setup
- Basic usage examples
- Configuration guide
- Common workflows
- Troubleshooting

**When to read**: First-time setup, configuration issues

**Key sections**:
- Quick Start (lines 5-35)
- API Key Setup (lines 60-96)
- Common Workflows (lines 182-261)

---

### 4. API Reference
**File**: [`ref/api-reference.md`](ref/api-reference.md)

**Contents**:
- Complete function signatures
- Parameter descriptions
- Return types
- Usage examples
- CLI commands
- Data models
- Validation functions
- Environment variables

**When to read**: Writing code, API integration

**Key sections**:
- Core Functions (lines 7-138)
- Data Models (lines 176-265)
- Validation Functions (lines 267-336)
- Calculation Functions (lines 338-407)

---

### 5. Testing Guide
**File**: [`ref/testing.md`](ref/testing.md)

**Contents**:
- Test structure overview
- Running tests
- Test categories (unit, integration, benchmarks)
- Test-driven development workflow
- Mocking strategies
- Coverage reporting
- CI/CD integration

**When to read**: Writing tests, debugging test failures

**Key sections**:
- Running Tests (lines 17-51)
- Schema Tests (lines 55-123)
- Golden Dataset Tests (lines 127-195)
- Benchmarks (lines 199-263)

---

### 6. Prompts Guide
**File**: [`ref/prompts-guide.md`](ref/prompts-guide.md)

**Contents**:
- Prompt architecture overview
- Stage-by-stage breakdown
- Prompt engineering best practices
- Customization strategies
- Testing prompts
- Versioning and migration

**When to read**: Modifying prompts, adding new stages

**Key sections**:
- Stage 1: Discoverer (lines 41-156)
- Stage 2: Auditor (lines 160-293)
- Stage 3: Modifier (lines 297-395)
- Customizing Prompts (lines 499-599)

---

### 7. Gemini Integration Guide
**File**: [`ref/gemini-integration.md`](ref/gemini-integration.md)

**Contents**:
- Why Gemini (token limit comparison)
- Quick start and API key setup
- Implementation details and code changes
- Model selection guide
- API key management and security
- Testing and troubleshooting
- Performance characteristics and best practices
- Migration guide (DeepSeek ↔ Gemini)

**When to read**: Setting up Gemini, debugging API issues, choosing LLM provider for large scripts

**Key sections**:
- Token Limit Comparison - Why Gemini solves Stage 3 issues
- Quick Start - 5 steps to get Gemini working
- Troubleshooting - Common errors and solutions (including v2.7.0 multi-part response fix)
- Best Practices - When to use Gemini vs DeepSeek

### 8. Version Tracking Guide
**File**: [`ref/version-tracking.md`](ref/version-tracking.md)

**Contents**:
- Centralized version file (`src/version.py`)
- Health endpoint version info
- Web UI footer display
- Deploy script version command
- Docker image tagging
- Version update workflow

**When to read**: Understanding deployed version, debugging deployment issues, releasing new versions

**Key sections**:
- Version Information Sources - 4 ways to check version
- Version Update Workflow - Steps for releasing
- Troubleshooting - Version mismatch fixes

### 9. TXT Script Parser Guide
**File**: [`ref/txt-parser-guide.md`](ref/txt-parser-guide.md)

**Contents**:
- TXT to JSON conversion system
- Three-phase development (Basic Parser → LLM Enhancement → Web Integration)
- Parser architecture and implementation
- TXT format requirements
- Web UI workflow
- API reference
- Performance characteristics
- Troubleshooting guide

**When to read**: Working with TXT scripts, integrating parser, understanding Web upload flow

**Key sections**:
- Phase 1: Basic TXT Parser - Rule-based parsing
- Phase 2: LLM Enhancement - Semantic extraction
- Phase 3: Web Integration - Upload and preview workflow
- TXT Format Requirements - How to format scripts
- API Reference - Using parsers programmatically
- Testing - Automated test suite
- Performance - Timing and cost analysis

---

## Important Files

### Source Code

#### Core Implementation
- **[`src/pipeline.py`](src/pipeline.py)** (20,000+ bytes)
  - LangGraph pipeline
  - Actor implementations (DiscovererActor, AuditorActor, ModifierActor)
  - LLM provider integration (DeepSeek, Claude, OpenAI, Gemini)
  - State management
  - **Key section**: Lines 288-303 - Gemini LLM factory
  - **Start here for**: Pipeline logic, actor behavior, LLM configuration

- **[`src/cli.py`](src/cli.py)** (11,500+ bytes)
  - Command-line interface
  - Commands: analyze, validate, benchmark, ab-test
  - **Start here for**: CLI usage, command implementation

- **[`src/monitoring.py`](src/monitoring.py)** (12,000+ bytes)
  - Metrics storage and analysis
  - Cost estimation utilities
  - Performance tracking
  - **Start here for**: Observability, cost tracking

- **[`src/ab_testing.py`](src/ab_testing.py)** (16,000+ bytes)
  - A/B testing framework
  - Variant comparison
  - Automated evaluation
  - **Start here for**: Testing different configurations

- **🆕 [`src/gemini3_llm.py`](src/gemini3_llm.py)** (168 lines, v2.9.0)
  - Custom LangChain-compatible wrapper for Gemini 3
  - Uses `google-genai` SDK directly (bypasses LangChain limitations)
  - Supports `thinking_level="LOW"` or `"HIGH"` parameter
  - **Key feature**: 95% speed improvement via thinking mode optimization
  - **Start here for**: Gemini 3 integration, thinking mode configuration

#### 🆕 TXT Script Parser (v2.4.0)
- **[`src/parser/base.py`](src/parser/base.py)** (80 lines)
  - Abstract base class for all parsers
  - Defines parse() and validate_output() interface
  - **Start here for**: Understanding parser architecture

- **[`src/parser/txt_parser.py`](src/parser/txt_parser.py)** (320 lines)
  - Basic rule-based TXT parser (Phase 1)
  - Scene splitting, character extraction
  - Multi-format scene header support
  - **Start here for**: Basic TXT parsing logic

- **[`src/parser/llm_enhancer.py`](src/parser/llm_enhancer.py)** (450 lines)
  - LLM-enhanced parser (Phase 2)
  - Semantic extraction (scene mission, key events, etc.)
  - 5 LLM prompts for semantic understanding
  - **Start here for**: LLM enhancement logic

- **[`src/parser/prompts/`](src/parser/prompts/)** (5 files, 11,500+ characters)
  - scene_mission_prompt.md - Extract scene objectives
  - key_events_prompt.md - Identify important events
  - setup_payoff_prompt.md - Find causal relationships
  - relation_change_prompt.md - Track character relations
  - info_change_prompt.md - Track information reveals
  - **Start here for**: Understanding LLM prompts

- **[`src/web/app.py`](src/web/app.py)** (Updated with ~200 lines)
  - TXT upload endpoint: `/api/parse-txt`
  - Preview page route: `/parse-preview/{job_id}`
  - Continue-to-analysis: `/analysis-from-parsed/{job_id}`
  - Background parsing task with WebSocket progress
  - **Start here for**: Web integration logic

- **[`templates/parse_preview.html`](templates/parse_preview.html)** (290 lines)
  - Parse preview interface
  - 4-tab layout (Overview, Scenes, Characters, Raw JSON)
  - WebSocket progress tracking
  - Continue and download buttons
  - **Start here for**: Preview UI implementation

- **[`static/js/upload.js`](static/js/upload.js)** (165 lines, rewritten)
  - Smart routing based on file type
  - TXT → parse preview flow
  - JSON → direct analysis flow
  - Form validation and error handling
  - **Start here for**: Frontend upload logic

- **[`test_web_integration.py`](test_web_integration.py)** (260 lines)
  - Automated test suite for Phase 3
  - 5 integration tests (100% pass rate)
  - Parser, serialization, API, and UI tests
  - **Start here for**: Testing TXT parser integration

#### 🆕 Export System (v2.3.0)
- **[`src/exporters/markdown_exporter.py`](src/exporters/markdown_exporter.py)** (232 lines)
  - Markdown report generator
  - Jinja2 template rendering
  - Intelligent findings and recommendations
  - **Start here for**: Report generation, customization

- **[`src/exporters/mermaid_generator.py`](src/exporters/mermaid_generator.py)** (178 lines)
  - Mermaid flowchart generator
  - TCC relationship visualization
  - A/B/C line color coding
  - **Start here for**: Diagram generation, color schemes

- **[`templates/report_template.md.j2`](templates/report_template.md.j2)** (211 lines)
  - Jinja2 report template
  - Markdown structure definition
  - Customizable report layout
  - **Start here for**: Report template modification

#### Prompt System
- **[`prompts/schemas.py`](prompts/schemas.py)**
  - Pydantic models for all data structures
  - Validation functions and middleware (v2.6.0)
  - `PerformanceNote` model, `filter_low_coverage_tccs()`, `check_antagonist_mutual_exclusion()`, `validate_tcc_scene_evidence()`
  - **Start here for**: Data models, validation logic, TCC middleware

- **[`prompts/stage1_discoverer.md`](prompts/stage1_discoverer.md)** (v2.6.0-AAP)
  - Stage 1 prompt (TCC identification)
  - Language Requirement for Chinese output
  - Action Analysis Protocol (AAP) section
  - **Start here for**: Understanding TCC discovery logic

- **[`prompts/stage2_auditor.md`](prompts/stage2_auditor.md)**
  - Stage 2 prompt (A/B/C-line ranking)
  - Language Requirement for Chinese output
  - **Start here for**: Understanding ranking criteria

- **[`prompts/stage3_modifier.md`](prompts/stage3_modifier.md)**
  - Stage 3 prompt (structural fixes)
  - Language Requirement for Chinese output
  - **Start here for**: Understanding modification logic

- **🆕 [`prompts/action_classifier.md`](prompts/action_classifier.md)** (v2.6.0)
  - Prompt A: Action classification (emotional_signal vs noise)
  - Decision flowchart for action categorization
  - **Start here for**: Understanding action filtering logic

- **🆕 [`prompts/action_analyzer.md`](prompts/action_analyzer.md)** (v2.6.0)
  - Prompt B: Action-to-TCC evidence analysis
  - Confidence boost rules and conflict mapping
  - **Start here for**: Understanding action-TCC relationship

- **[`prompts/README.md`](prompts/README.md)** (22,739 bytes)
  - Comprehensive prompt documentation
  - Usage patterns and examples
  - **Start here for**: Detailed prompt engineering guide

### Tests
- **[`tests/test_schemas.py`](tests/test_schemas.py)**
  - Unit tests for schemas and validators
  - **Start here for**: Schema testing patterns

- **[`tests/test_golden_dataset.py`](tests/test_golden_dataset.py)**
  - Integration tests with golden data
  - **Start here for**: End-to-end testing

- **[`benchmarks/run_benchmark.py`](benchmarks/run_benchmark.py)**
  - Performance benchmarking
  - **Start here for**: Performance testing

### Configuration
- **[`.env.example`](.env.example)** (1,500+ bytes)
  - Environment variable template
  - API key configuration (DeepSeek, Claude, OpenAI, Gemini)
  - LLM provider selection
  - **Copy to `.env`** and add your keys

- **[`requirements.txt`](requirements.txt)** (500+ bytes)
  - Core dependencies
  - Includes: langchain-google-genai>=2.0.0 for Gemini support
  - **Install with**: `pip install -r requirements.txt`

- **[`requirements-test.txt`](requirements-test.txt)** (392 bytes)
  - Test dependencies
  - **Install with**: `pip install -r requirements-test.txt`

### Documentation
- **[`README.md`](README.md)** (12,751 bytes, Chinese)
  - Main project documentation
  - Business context and theory
  - **Start here for**: Business understanding

- **[`USAGE.md`](USAGE.md)** (11,276 bytes)
  - Detailed usage guide
  - API examples
  - Troubleshooting
  - **Start here for**: Practical usage

- **[`README_DEEPSEEK.md`](README_DEEPSEEK.md)** (8,338 bytes)
  - DeepSeek integration guide
  - **Start here for**: DeepSeek setup

#### 🆕 Observability & Monitoring
- **[`docs/langsmith-quickstart.md`](docs/langsmith-quickstart.md)** (3 pages)
  - 5-minute LangSmith setup
  - **Start here for**: Quick observability setup

- **[`docs/langsmith-integration.md`](docs/langsmith-integration.md)** (15 pages)
  - Complete LangSmith guide
  - Configuration, usage, troubleshooting
  - **Start here for**: Full observability features

- **[`LANGSMITH_FEATURES.md`](docs/LANGSMITH_FEATURES.md)** (12 pages)
  - Technical implementation details
  - Architecture and design
  - **Start here for**: Understanding how tracing works

- **[`LANGSMITH_INTEGRATION_SUMMARY.md`](LANGSMITH_INTEGRATION_SUMMARY.md)** (11 pages)
  - Development summary
  - Completed features
  - **Start here for**: What was implemented

- **[`LANGSMITH_QUICKREF.md`](LANGSMITH_QUICKREF.md)** (1 page)
  - Quick reference card
  - **Start here for**: Command cheat sheet

#### 🆕 A/B Testing
- **[`docs/ab-testing-quickstart.md`](docs/ab-testing-quickstart.md)** (2 pages)
  - 3-minute A/B testing tutorial
  - **Start here for**: Quick A/B testing intro

- **[`docs/ab-testing-guide.md`](docs/ab-testing-guide.md)** (18 pages)
  - Complete A/B testing guide
  - Use cases, best practices, examples
  - **Start here for**: Comprehensive A/B testing

- **[`AB_TESTING_SUMMARY.md`](AB_TESTING_SUMMARY.md)** (10 pages)
  - A/B testing implementation summary
  - Features and architecture
  - **Start here for**: What was built

#### 🆕 Export & Reporting (v2.3.0)
- **[`docs/export-guide.md`](docs/export-guide.md)** (20+ pages)
  - Complete export functionality guide
  - Markdown report structure
  - Mermaid visualization usage
  - Report customization
  - **Start here for**: Generating and customizing reports

#### 🆕 TXT Parser Documentation (v2.4.0)
- **[`docs/development/PARSER_PHASE1_COMPLETE.md`](docs/development/PARSER_PHASE1_COMPLETE.md)** (15 pages)
  - Phase 1 completion report
  - Basic TXT parser implementation
  - Testing results and validation
  - **Start here for**: Understanding Phase 1 development

- **[`docs/development/PARSER_PHASE2_COMPLETE.md`](docs/development/PARSER_PHASE2_COMPLETE.md)** (18 pages)
  - Phase 2 completion report
  - LLM enhancement implementation
  - Prompt engineering details
  - **Start here for**: Understanding LLM enhancement

- **[`docs/development/PARSER_PHASE3_COMPLETE.md`](docs/development/PARSER_PHASE3_COMPLETE.md)** (25 pages)
  - Phase 3 completion report
  - Web integration implementation
  - User workflow and features
  - **Start here for**: Understanding Web integration

- **[`docs/development/PHASE3_TEST_RESULTS.md`](docs/development/PHASE3_TEST_RESULTS.md)** (12 pages)
  - Automated test results
  - 5/5 tests passing (100%)
  - Integration test coverage
  - **Start here for**: Testing methodology and results

- **[`docs/development/DEVELOPMENT_LOG.md`](docs/development/DEVELOPMENT_LOG.md)** (Session 1-9)
  - Complete development history
  - 9 development sessions documented
  - All decisions and implementations tracked
  - **Start here for**: Full development timeline

- **[`docs/development/CRITICAL_GAP_ANALYSIS.md`](docs/development/CRITICAL_GAP_ANALYSIS.md)** (15 pages)
  - Problem analysis (TXT vs JSON gap)
  - Solution design and alternatives
  - Decision rationale
  - **Start here for**: Understanding why TXT parser was needed

- **[`docs/development/PARSER_DEVELOPMENT_PLAN.md`](docs/development/PARSER_DEVELOPMENT_PLAN.md)** (20 pages)
  - 4-phase development plan
  - Technical architecture
  - Task breakdown (60+ subtasks)
  - **Start here for**: Development methodology

- **[`docs/development/TASKS_SUMMARY.md`](docs/development/TASKS_SUMMARY.md)**
  - Task tracking and milestones
  - Risk assessment
  - Progress monitoring
  - **Start here for**: Project management view

#### 🆕 Project Status (v2.5.0)
- **[`PROJECT_STATUS.md`](PROJECT_STATUS.md)** (331 lines) 🆕
  - 整体进度概览 (100% 完成)
  - 开发历程 (Session 1-9)
  - 已完成功能清单
  - **已知遗留问题**:
    1. 单场景剧本分析失败 (需最少 2 场景)
    2. Mermaid 渲染兼容性
    3. LLM 语义增强成本
    4. 大文件上传超时
    5. 错误信息国际化
  - 未来改进建议 (短期/中期/长期)
  - 关键文件索引和测试状态
  - 快速问题排查指南
  - 完整变更日志 (v2.1.0 - v2.5.0)
  - **Start here for**: 项目状态概览、遗留问题、未来规划

### Testing & Utilities
- **[`scripts/test_gemini_api.py`](scripts/test_gemini_api.py)** (90 lines) 🆕
  - Gemini API connectivity test script
  - Pre-business verification before running analysis
  - Tests model availability, API key, and basic inference
  - **Use for**: Debugging Gemini setup, validating API keys
  - **Run**: `python scripts/test_gemini_api.py`

- **[`scripts/test_web_integration.py`](scripts/test_web_integration.py)** (260 lines)
  - Automated test suite for Web UI integration
  - Parser, serialization, API, and UI tests
  - **Run**: `python scripts/test_web_integration.py`

- **[`scripts/run_tests.sh`](scripts/run_tests.sh)** - Test runner script
- **[`scripts/run_web_server.sh`](scripts/run_web_server.sh)** - Web server launcher
- **[`scripts/deploy.sh`](scripts/deploy.sh)** - Deployment script

### Examples
- **[`examples/golden/`](examples/golden/)**
  - Golden dataset scripts for testing
  - Example: `百妖_ep09_s01-s05.json`
  - **Use for**: Testing and validation

---

## Common Tasks

### Task: Understand the System
1. Read [`ref/project-overview.md`](ref/project-overview.md)
2. Read [`ref/architecture.md`](ref/architecture.md)
3. Review [`README.md`](README.md) for business context

### Task: Set Up Development Environment
1. Follow [`ref/getting-started.md`](ref/getting-started.md) - Installation section
2. Configure API key using [`.env.example`](.env.example)
3. Run tests: `./run_tests.sh`

### Task: Analyze a Script (JSON)
1. Check [`USAGE.md`](USAGE.md) - "Using the Pipeline" section
2. Use CLI: `python -m src.cli analyze script.json`
3. Or use API from [`ref/api-reference.md`](ref/api-reference.md)

### Task: Parse TXT Script
1. Read [`ref/txt-parser-guide.md`](ref/txt-parser-guide.md) - TXT format requirements
2. Basic parsing:
   ```python
   from src.parser import TXTScriptParser
   parser = TXTScriptParser()
   script = parser.parse("script.txt")
   ```
3. With LLM enhancement:
   ```python
   from src.parser import LLMEnhancedParser
   from src.pipeline import create_llm
   llm = create_llm(provider="deepseek")
   parser = LLMEnhancedParser(llm=llm)
   script = parser.parse("script.txt")
   ```

### Task: Use Web UI for TXT Upload
1. Start Web server: `bash run_web_server.sh`
2. Open browser: `http://localhost:8000`
3. Select "TXT (原始剧本)" file type
4. Toggle "使用 LLM 语义增强" as needed
5. Upload TXT file
6. Preview parsed results (4 tabs)
7. Click "Continue to Analysis"
8. View three-stage analysis results

### Task: Add New Feature
1. Read [`ref/architecture.md`](ref/architecture.md) - Extension Points
2. Review existing code in [`src/pipeline.py`](src/pipeline.py)
3. Follow TDD workflow from [`ref/testing.md`](ref/testing.md)
4. Update schemas in [`prompts/schemas.py`](prompts/schemas.py)

### Task: Modify Prompts
1. Read [`ref/prompts-guide.md`](ref/prompts-guide.md)
2. Edit files in [`prompts/`](prompts/) directory
3. Update [`prompts/schemas.py`](prompts/schemas.py) if needed
4. Test changes using [`tests/test_golden_dataset.py`](tests/test_golden_dataset.py)

### Task: Debug Test Failure
1. Check [`ref/testing.md`](ref/testing.md) - Troubleshooting section
2. Review test file: [`tests/test_schemas.py`](tests/test_schemas.py) or [`tests/test_golden_dataset.py`](tests/test_golden_dataset.py)
3. Run with verbose: `pytest tests/ -v -s`

### Task: Optimize Performance
1. Read [`ref/architecture.md`](ref/architecture.md) - Performance section
2. Run benchmarks: `python benchmarks/run_benchmark.py examples/golden`
3. Check [`USAGE.md`](USAGE.md) - Performance tips

### Task: Integrate New LLM Provider
1. Read [`ref/architecture.md`](ref/architecture.md) - LLM Provider Support
2. Edit [`src/pipeline.py`](src/pipeline.py) - `create_llm()` function
3. Update [`.env.example`](.env.example) with new variables
4. Test integration

### 🆕 Task: Enable LangSmith Tracing
1. Read [`docs/langsmith-quickstart.md`](docs/langsmith-quickstart.md) - 5-minute setup
2. Get API key from https://smith.langchain.com/
3. Update `.env`: `LANGCHAIN_TRACING_V2=true` and add API key
4. Run analysis - tracing is automatic

### 🆕 Task: Run A/B Test
1. Read [`docs/ab-testing-quickstart.md`](docs/ab-testing-quickstart.md) - 3-minute tutorial
2. Compare providers: `python -m src.cli ab-test script.json --providers deepseek,anthropic,gemini`
3. Compare temperatures: `python -m src.cli ab-test script.json --temperatures 0.0,0.7`
4. Review results in terminal and `ab_tests/` directory

### 🆕 Task: Use Gemini for Large Scripts (v2.8.0+)
1. Set environment: `LLM_PROVIDER=gemini` in `.env`
2. Add API key: `GOOGLE_API_KEY=your_key_here`
3. Available Gemini models (select from Web UI):
   - `gemini-2.5-flash` - Fast response, recommended for general analysis
   - `gemini-2.5-pro` - Advanced reasoning, for complex analysis
   - `gemini-2.0-flash` - Previous generation Flash
   - `gemini-3-pro-preview` - Gemini 3 Pro preview, advanced reasoning
4. All models offer 1M context + 64K output (solves Stage 3 JSON truncation)
5. Test API: `python scripts/test_gemini_api.py`
6. Run analysis: Web UI shows model selector when Gemini is selected

### 🆕 Task: Analyze Performance Metrics
1. Run analysis with LangSmith enabled
2. Check terminal output for performance summary
3. View detailed metrics in `_metrics` field of result
4. Use `src/monitoring.py` for historical analysis

### 🆕 Task: Generate Report (v2.3.0)
1. Read [`docs/export-guide.md`](docs/export-guide.md) - Complete export guide
2. Analyze script with export flag: `python -m src.cli analyze script.json --export report.md`
3. View report in Markdown editor (VS Code, Obsidian, Typora)
4. Customize template in `templates/report_template.md.j2` if needed

---

## Key Concepts

### Theatrical Conflict Chain (TCC)
Independent narrative thread with super objective, forces, and evidence.
- **Details**: [`README.md`](README.md) lines 302-314
- **Schema**: [`prompts/schemas.py`](prompts/schemas.py)
- **Prompt**: [`prompts/stage1_discoverer.md`](prompts/stage1_discoverer.md)

### A/B/C-Line Classification
Ranking system for story importance (A=main, B=subplot, C=flavor).
- **Details**: [`README.md`](README.md) lines 54-68
- **Criteria**: [`ref/prompts-guide.md`](ref/prompts-guide.md) lines 164-244
- **Prompt**: [`prompts/stage2_auditor.md`](prompts/stage2_auditor.md)

### Setup-Payoff Chain
Cause-effect relationships between scenes.
- **Validation**: [`prompts/schemas.py`](prompts/schemas.py) - `validate_setup_payoff_integrity()`
- **Fixing**: [`prompts/stage3_modifier.md`](prompts/stage3_modifier.md)

### Director-Actor Pattern
LangGraph-based orchestration with specialized agents.
- **Details**: [`ref/architecture.md`](ref/architecture.md) lines 13-35
- **Implementation**: [`src/pipeline.py`](src/pipeline.py)

---

## Project Structure

```
.
├── CLAUDE.md                    # This file - navigation guide
├── README.md                    # Main documentation (Chinese)
├── USAGE.md                     # Usage guide
├── README_DEEPSEEK.md          # DeepSeek integration
│
├── ref/                         # Reference documentation
│   ├── project-overview.md     # Project summary
│   ├── architecture.md         # System design
│   ├── getting-started.md      # Setup guide
│   ├── api-reference.md        # API docs
│   ├── testing.md              # Testing guide
│   └── prompts-guide.md        # Prompt engineering
│
├── src/                         # Source code
│   ├── pipeline.py             # Core pipeline
│   ├── cli.py                  # CLI interface
│   ├── parser/                 # 🆕 TXT Parser system (v2.4.0)
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract parser base class
│   │   ├── txt_parser.py       # Basic rule-based parser (Phase 1)
│   │   ├── llm_enhancer.py     # LLM-enhanced parser (Phase 2)
│   │   └── prompts/            # LLM prompts for enhancement
│   │       ├── scene_mission_prompt.md
│   │       ├── key_events_prompt.md
│   │       ├── setup_payoff_prompt.md
│   │       ├── relation_change_prompt.md
│   │       └── info_change_prompt.md
│   ├── web/                    # 🆕 Web UI (Phase 3)
│   │   ├── __init__.py
│   │   └── app.py              # FastAPI application
│   ├── exporters/              # 🆕 Export system (v2.3.0)
│   │   ├── __init__.py
│   │   ├── markdown_exporter.py # Markdown report generator
│   │   └── mermaid_generator.py # Mermaid diagram generator
│   └── __init__.py
│
├── templates/                   # 🆕 Web UI templates
│   ├── base.html               # Base layout template
│   ├── index.html              # Upload page (supports JSON & TXT)
│   ├── parse_preview.html      # 🆕 TXT parse preview (Phase 3)
│   ├── analysis.html           # Three-stage analysis page
│   ├── results.html            # Results display page
│   └── report_template.md.j2   # Jinja2 Markdown template (v2.3.0)
│
├── static/                      # 🆕 Web UI assets
│   ├── css/
│   │   └── custom.css          # Custom styles
│   └── js/
│       ├── upload.js           # Upload logic (JSON & TXT routing)
│       ├── analysis.js         # Analysis page logic
│       └── results.js          # Results page logic
│
├── prompts/                     # Prompt system
│   ├── stage1_discoverer.md    # Stage 1 prompt
│   ├── stage2_auditor.md       # Stage 2 prompt
│   ├── stage3_modifier.md      # Stage 3 prompt
│   ├── schemas.py              # Data models
│   └── README.md               # Prompt guide
│
├── tests/                       # Test suites
│   ├── test_schemas.py         # Unit tests
│   ├── test_golden_dataset.py  # Integration tests
│   └── __init__.py
│
├── benchmarks/                  # Performance tests
│   └── run_benchmark.py
│
├── examples/                    # Sample data
│   ├── golden/                 # Test datasets (JSON)
│   └── test_scripts/           # 🆕 TXT test scripts
│       └── simple_script.txt   # Example TXT script
│
├── docs/                        # Documentation (organized by category)
│   ├── development/             # 🆕 Development history and plans
│   │   ├── DEVELOPMENT_LOG.md   # Complete development history (Session 1-9)
│   │   ├── PARSER_DEVELOPMENT_PLAN.md
│   │   ├── PARSER_PHASE1_COMPLETE.md
│   │   ├── PARSER_PHASE2_COMPLETE.md
│   │   ├── PARSER_PHASE3_COMPLETE.md
│   │   ├── PHASE3_TEST_RESULTS.md
│   │   ├── CRITICAL_GAP_ANALYSIS.md
│   │   └── TASKS_SUMMARY.md
│   ├── deployment/              # 🆕 Deployment guides
│   │   ├── DEPLOYMENT.md
│   │   ├── DEPLOY_CHECKLIST.md
│   │   ├── DOCKER_QUICKSTART.md
│   │   ├── DOCKER_DEPLOYMENT_SUMMARY.md
│   │   ├── DOCKER_TEST_CHECKLIST.md
│   │   └── ECS_DEPLOYMENT_GUIDE.md
│   ├── summaries/               # 🆕 Feature summaries
│   │   ├── AB_TESTING_SUMMARY.md
│   │   ├── COMPLETION_SUMMARY.md
│   │   ├── LANGSMITH_INTEGRATION_SUMMARY.md
│   │   ├── SESSION_8_UX_OPTIMIZATION_SUMMARY.md
│   │   ├── WEB_IMPLEMENTATION_SUMMARY.md
│   │   └── PROJECT_STATUS_REPORT.md
│   ├── archive/                 # 🆕 Legacy/archived docs
│   │   ├── Step1-prompt.md, Step2-prompt.md, Step3-prompt.md
│   │   ├── WEB_*.md (old web guides)
│   │   └── LANGSMITH_QUICKREF.md
│   ├── langsmith-quickstart.md
│   ├── langsmith-integration.md
│   ├── ab-testing-quickstart.md
│   ├── ab-testing-guide.md
│   ├── export-guide.md
│   └── development-plan.md
│
├── scripts/                     # 🆕 Utility scripts (moved from root)
│   ├── run_tests.sh             # Test runner
│   ├── run_web_server.sh        # Web server launcher
│   ├── deploy.sh                # Deployment script
│   ├── test_gemini_api.py       # Gemini API test
│   └── test_web_integration.py  # Web integration tests
│
├── .env.example                 # Environment template
├── requirements.txt             # Core dependencies
├── requirements-test.txt        # Test dependencies
├── requirements-web.txt         # Web UI dependencies
├── pytest.ini                   # Pytest configuration
├── run_tests.sh -> scripts/     # Symlink for convenience
└── run_web_server.sh -> scripts/ # Symlink for convenience
```

---

## Environment Setup Checklist

- [x] Python 3.8+ installed ✅
- [x] Dependencies installed: `pip install -r requirements.txt` ✅
  - LangChain 1.0.5
  - LangGraph 1.0.3
  - Pydantic, tenacity, etc.
- [x] `.env` file created from `.env.example` ✅
- [x] API key added to `.env` (DeepSeek) ✅
- [x] Tests passing: `pytest tests/ -v` ✅ (44/44 passed)
- [x] Stage 1 working: `python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json` ✅
- [x] Stage 2 JSON parsing fixed ✅
- [x] Stage 3 validation fixed ✅
- [x] Complete 3-stage pipeline end-to-end test ✅ (0 errors, 0 retries)

---

## Development Workflow

### Standard Workflow
1. Read relevant documentation from `/ref`
2. Review existing code in `/src` or `/prompts`
3. Write tests first (see [`ref/testing.md`](ref/testing.md))
4. Implement feature
5. Run tests: `pytest tests/ -v`
6. Update documentation if needed

### Prompt Modification Workflow
1. Read [`ref/prompts-guide.md`](ref/prompts-guide.md)
2. Edit prompt file in [`prompts/`](prompts/)
3. Update [`prompts/schemas.py`](prompts/schemas.py) if schema changed
4. Test with golden dataset: `pytest tests/test_golden_dataset.py -v`
5. Update [`prompts/README.md`](prompts/README.md) with changes

### Adding New Feature Workflow
1. Design: Review [`ref/architecture.md`](ref/architecture.md)
2. Test: Write tests in [`tests/`](tests/)
3. Implement: Add code to [`src/`](src/)
4. Validate: Run full test suite
5. Document: Update [`ref/api-reference.md`](ref/api-reference.md)

---

## Troubleshooting Quick Reference

### Issue: API Key Error
- **Solution**: Check [`.env`](.env) file, see [`ref/getting-started.md`](ref/getting-started.md) lines 60-96

### Issue: Test Failure
- **Solution**: See [`ref/testing.md`](ref/testing.md) lines 533-567

### Issue: Validation Error
- **Solution**: Check [`prompts/schemas.py`](prompts/schemas.py), see [`ref/api-reference.md`](ref/api-reference.md) lines 440-457

### Issue: LLM Output Format Wrong
- **Solution**: See [`ref/prompts-guide.md`](ref/prompts-guide.md) lines 645-664

### Issue: Performance Slow
- **Solution**: See [`USAGE.md`](USAGE.md) lines 445-450, [`ref/architecture.md`](ref/architecture.md) lines 336-348

### Issue: TXT Parser - No Scenes Found
- **Cause**: Scene headers not recognized
- **Solution**: See [`ref/txt-parser-guide.md`](ref/txt-parser-guide.md) - TXT Format Requirements section
- Check scene header format (S01, 场景 1, etc.)
- Ensure consistent formatting throughout script

### Issue: TXT Parser - Character Names Wrong
- **Cause**: False positives in character extraction
- **Solution**: Use LLM enhancement for better accuracy, or review and manually correct in preview

### Issue: TXT Parser - LLM Enhancement Slow
- **Cause**: 5 LLM calls per scene, sequential processing
- **Solution**: Disable LLM enhancement for faster basic parse, or use faster LLM model

### Issue: Web UI - Parse Preview Stuck on "Parsing in Progress..."
- **Cause**: WebSocket serialization error (Script object not JSON serializable)
- **Solution**: Fixed in Session 7 - WebSocket now sends summary stats instead of full Script object
- **Workaround**: Polling fallback mechanism automatically activates if WebSocket fails
- **Files**: `src/web/app.py:408-449, 490-497`, `templates/parse_preview.html:194-238`

### Issue: Web UI - Upload Page Not Redirecting After TXT Upload
- **Cause**: Browser caching old JavaScript, or JavaScript error preventing redirect
- **Solution**:
  1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
  2. Open browser DevTools Console (F12)
  3. Check for errors in console
  4. Verify debug logs show "Redirecting to: /parse-preview/..."
- **Files**: `static/js/upload.js:104-122` (debug logs added in Session 7)

### Issue: Web UI - WebSocket Connection Failed
- **Cause**: Network issues or browser compatibility
- **Solution**:
  - Check browser console for WebSocket errors
  - Polling fallback will automatically activate (every 2 seconds)
  - Try different browser
  - Check firewall settings

---

## External Resources

### LLM Providers
- DeepSeek: https://platform.deepseek.com/
- Anthropic Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/
- Google Gemini: https://ai.google.dev/ (API Key: https://aistudio.google.com/app/apikey)

### Technical Documentation
- LangChain: https://python.langchain.com/docs/
- LangGraph: https://langchain-ai.github.io/langgraph/
- LangSmith: https://docs.smith.langchain.com/
- Pydantic: https://docs.pydantic.dev/
- pytest: https://docs.pytest.org/

### Narrative Theory
- Robert McKee - "Story": Narrative structure principles
- "The Art of Dramatic Writing": Multi-line storytelling

---

## Version Information

**Project Version**: 2.9.0 (Session 14: Gemini Thinking Mode Optimization)
**Prompt Version**: 2.6.0-AAP (Action Analysis Protocol + Language Requirement)
**Documentation Version**: 2.3 (Added Gemini Thinking Mode Optimization, ChatGemini3 wrapper)
**Last Updated**: 2025-11-30
**Latest Commit**: 76e031a (feat: Session 13 - TXT parser enhancement + Gemini 3 API key support)
**Completion Status**: 100% (All stages + TXT Parser + Web UI + Mermaid + observability + A/B testing + export + Gemini Model Selection + AAP + Version Tracking + Thinking Mode Optimization - Production Ready)

---

## Contact & Support

- **Documentation Issues**: Review this file and linked docs
- **Code Issues**: Check [`tests/`](tests/) for examples
- **Prompt Issues**: See [`prompts/README.md`](prompts/README.md)
- **API Questions**: See [`ref/api-reference.md`](ref/api-reference.md)

---

## Notes for AI Assistants

### When Helping with This Project:

1. **Always start by reading**:
   - This file (CLAUDE.md) for navigation
   - [`ref/project-overview.md`](ref/project-overview.md) for context
   - [`ref/architecture.md`](ref/architecture.md) for design

2. **For specific tasks, consult**:
   - API questions → [`ref/api-reference.md`](ref/api-reference.md)
   - Testing → [`ref/testing.md`](ref/testing.md)
   - Prompts → [`ref/prompts-guide.md`](ref/prompts-guide.md)
   - Setup → [`ref/getting-started.md`](ref/getting-started.md)

3. **Code locations**:
   - Pipeline logic: [`src/pipeline.py`](src/pipeline.py)
   - Data models: [`prompts/schemas.py`](prompts/schemas.py)
   - Prompts: [`prompts/stage*.md`](prompts/)
   - TXT Parser: [`src/parser/`](src/parser/)
   - Web UI: [`src/web/app.py`](src/web/app.py)

4. **Testing approach**:
   - Unit tests: [`tests/test_schemas.py`](tests/test_schemas.py)
   - Integration: [`tests/test_golden_dataset.py`](tests/test_golden_dataset.py)
   - TXT Parser tests: [`test_web_integration.py`](test_web_integration.py)
   - Examples: [`examples/golden/`](examples/golden/) and [`examples/test_scripts/`](examples/test_scripts/)

5. **This project uses**:
   - Python 3.8+
   - DeepSeek as default LLM (most cost-effective)
   - LangGraph for orchestration
   - Pydantic for validation
   - pytest for testing

---

**This file was generated by**: /initref command
**Purpose**: Provide quick navigation and context for AI-assisted development
**Maintenance**: Update when adding new features or documentation
