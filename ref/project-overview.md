# Project Overview

## Project Name
剧本叙事结构分析系统 (Script Narrative Structure Analysis System)

## Description
A production-ready multi-agent LLM system for analyzing and correcting narrative structure in screenplays. The system identifies theatrical conflict chains (TCCs), ranks them by importance, fixes structural issues, and generates professional analysis reports.

## Core Purpose
Help screenwriters and production teams:
- Identify independent story threads (TCCs)
- Rank storylines as A/B/C-lines based on importance
- Fix structural problems in script data
- Generate professional analysis reports with visualizations

## Key Features

### Core Pipeline
- **Three-stage analysis pipeline** (Discover → Audit → Modify)
- **Director-Actor architecture** for task coordination
- **Structured output** with Pydantic validation
- **Multi-LLM support** (DeepSeek, Anthropic, OpenAI)
- **Intelligent error handling** with automatic retries

### Observability & Testing (v2.2.0)
- **LangSmith integration** for tracing and monitoring
- **A/B testing framework** for comparing configurations
- **Performance metrics** and cost estimation
- **Comprehensive test suite** (44 unit tests, 100% passing)

### Export & Reporting (v2.3.0) 🆕
- **Markdown report export** with professional formatting
- **Mermaid visualization** for TCC relationships
- **Auto-generated insights** and recommendations
- **Multi-platform support** (GitHub, Obsidian, Typora, VS Code)

## Technology Stack
- **Language**: Python 3.8+
- **LLM Framework**: LangChain 1.0.5 + LangGraph 1.0.3
- **LLM Providers**: DeepSeek (default), Gemini 3 Pro, Claude Sonnet 4.5, OpenAI GPT-4
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Templating**: Jinja2 (for report generation)
- **Observability**: LangSmith
- **Visualization**: Mermaid.js

## Project Status (Updated 2025-11-13)

### ✅ Completed Features (100%)
- ✅ **Stage 1 (Discoverer)**: TCC identification with auto-deduplication
- ✅ **Stage 2 (Auditor)**: A/B/C-line ranking with scoring
- ✅ **Stage 3 (Modifier)**: Structural issue correction
- ✅ **LangSmith Observability**: Auto-tracing and performance monitoring
- ✅ **A/B Testing**: Configuration comparison and evaluation
- ✅ **Markdown Export**: Professional report generation
- ✅ **Mermaid Visualization**: TCC relationship diagrams
- ✅ **Documentation**: Complete reference docs + guides
- ✅ **Testing**: 44/44 unit tests passing, 0 errors, 0 retries

### 🎯 Production Readiness
- **Status**: ✅ **Production Ready**
- **Success Rate**: 100% (0 errors, 0 retries)
- **Test Coverage**: 44/44 tests passing
- **Performance**: ~2 minutes per analysis
- **Reliability**: Zero-downtime error handling

## Key Metrics

### Code Base
- **Python modules**: 12 files
- **Lines of code**: ~3,500+ lines
- **Export system**: 628 lines (v2.3.0)
- **A/B testing**: 400+ lines (v2.2.0)
- **Monitoring**: 350+ lines (v2.2.0)

### Testing
- **Unit tests**: 44 (100% passing)
- **Integration tests**: 3 (LLM-dependent, skipped in CI)
- **End-to-end tests**: ✅ Verified with golden dataset
- **Test coverage**: Schema validation, calculation functions, pipeline logic

### Documentation
- **Reference docs**: 7 files in `/ref` (~75KB)
- **Feature guides**: 3 files (LangSmith, A/B testing, Export)
- **Total documentation**: 15+ files (~150KB)
- **Languages**: English (technical) + Chinese (business context)

### LLM Integration
- **Providers supported**: 3 (DeepSeek, Anthropic, OpenAI)
- **Default provider**: DeepSeek (best cost/performance)
- **Average API calls**: 3 per analysis
- **Retry rate**: 0% (intelligent error handling)

## Recent Achievements

### v2.7.0 (2025-11-24) - Gemini 3 Pro + Version Tracking 🆕
- ✅ Upgraded to Gemini 3 Pro for advanced reasoning (1M context, 64K output)
- ✅ Fixed Gemini multi-part response format handling in LLM enhancer
- ✅ Added centralized version tracking (`src/version.py`)
- ✅ Health endpoint now returns version, git commit, branch info
- ✅ Web UI footer displays version and commit hash
- ✅ Deploy script auto-reads version with `version` command

### v2.6.0 (2025-11-22) - Action Analysis Protocol
- ✅ Action Analysis Protocol (AAP) for performance notes extraction
- ✅ TCC middleware layer (coverage filter, antagonist mutual exclusion)
- ✅ Scene validation layer for atomic reverse verification
- ✅ Chinese output enforcement in all prompts

### v2.5.0 (2025-11-19) - Gemini Integration
- ✅ Integrated Google Gemini 2.5 Flash for large script support
- ✅ Solved Stage 3 token limit issues (JSON truncation)

### v2.4.0 (2025-11-14) - TXT Parser + Web UI
- ✅ TXT script parser (rule-based + LLM enhancement)
- ✅ Web UI for upload, preview, and analysis
- ✅ Mermaid visualization in results page

### v2.3.0 (2025-11-13) - Export & Reporting
- ✅ Implemented Markdown report export with Jinja2 templates
- ✅ Created Mermaid diagram generator for TCC visualization
- ✅ Added intelligent findings and recommendations generation
- ✅ Integrated export into CLI with `--export` parameter
- ✅ Created comprehensive export guide (20+ pages)

### v2.2.0 (2025-11-13) - Observability & Testing
- ✅ Integrated LangSmith for automatic tracing
- ✅ Implemented A/B testing framework
- ✅ Added performance metrics and cost estimation
- ✅ Created observability and A/B testing guides

### v2.1.0 (2025-11-13) - Core Completion
- ✅ Fixed Stage 2 JSON parsing (bracket-stack matching)
- ✅ Fixed Stage 3 validation (field normalization)
- ✅ Implemented TCC auto-deduplication (mirror detection)
- ✅ Achieved 100% end-to-end success rate
- ✅ Created complete documentation system

## Version History

| Version | Date | Features | Status |
|---------|------|----------|--------|
| **v2.7.0** | 2025-11-24 | Gemini 3 Pro + Version tracking | ✅ Current |
| **v2.6.0** | 2025-11-22 | Action Analysis Protocol (AAP) | ✅ Stable |
| **v2.5.0** | 2025-11-19 | Gemini integration | ✅ Stable |
| **v2.4.0** | 2025-11-14 | TXT Parser + Web UI | ✅ Stable |
| **v2.3.0** | 2025-11-13 | Markdown export + Mermaid visualization | ✅ Stable |
| **v2.2.0** | 2025-11-13 | LangSmith observability + A/B testing | ✅ Stable |
| **v2.1.0** | 2025-11-13 | TCC auto-merge + 100% pipeline success | ✅ Stable |
| **v2.0.0** | 2025-11-13 | Three-stage pipeline complete | ✅ Stable |
| **v1.0.0** | 2025-11-12 | Initial prompt engineering | ✅ Stable |

## Current Version
**Version**: v2.7.0
**Last Updated**: 2025-11-24
**Latest Commit**: f5ec6dc (fix: handle Gemini 3 Pro multi-part response format)
**Completion**: 100% (Production Ready with Full Delivery Capability)

## Usage

### Basic Analysis
```bash
python -m src.cli analyze script.json
```

### With Report Export
```bash
python -m src.cli analyze script.json --export reports/analysis.md
```

### A/B Testing
```bash
python -m src.cli ab-test script.json --temperatures 0.0,0.7
```

### With LangSmith Tracing
```bash
# Set in .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key

# Run analysis (auto-traced)
python -m src.cli analyze script.json
```

## Architecture Highlights

### Director-Actor Pattern
- **Director** (LangGraph): Orchestrates workflow and manages state
- **Discoverer Actor**: Identifies independent TCCs
- **Auditor Actor**: Ranks TCCs as A/B/C-lines
- **Modifier Actor**: Fixes structural issues

### Error Handling
- **Intelligent JSON parsing**: Bracket-stack matching algorithm
- **Field normalization**: Auto-converts LLM output variations
- **Retry mechanism**: Exponential backoff with tenacity
- **Graceful degradation**: Fallback strategies for missing data

### Quality Assurance
- **Input validation**: Pydantic schema enforcement
- **Output validation**: JSON parsing + field checking
- **Logic validation**: Business rule verification
- **Mirror detection**: Auto-merge overlapping TCCs (>90% overlap)

## Business Value

### For Screenwriters
- ✅ Identify structural issues in multi-threaded narratives
- ✅ Clarify main/sub plot relationships
- ✅ Quantify storyline strength with scores

### For Production Teams
- ✅ Rapid script structure assessment
- ✅ Actionable improvement suggestions
- ✅ Risk reduction in script development
- ✅ Professional reports for stakeholders

### For AI Systems
- ✅ Validate long-context reasoning capabilities
- ✅ Test multi-agent collaboration mechanisms
- ✅ Explore structured creative analysis

## Future Enhancements (Optional)

### Performance Optimization
- [ ] Parallel processing for multiple scripts
- [ ] Result caching for repeat analyses
- [ ] Streaming output for large scripts

### Additional Formats
- [ ] PDF report generation (via pandoc)
- [ ] Excel data export for analytics
- [ ] Interactive web dashboard

### Advanced Features
- [ ] Human-in-the-loop review workflow
- [ ] Batch processing CLI
- [ ] Custom prompt templates

## References

### Narrative Theory
- Robert McKee - "Story": Narrative structure principles
- "The Art of Dramatic Writing": Multi-line storytelling theory

### Technical Documentation
- LangChain: https://python.langchain.com/
- LangGraph: https://langchain-ai.github.io/langgraph/
- LangSmith: https://docs.smith.langchain.com/
- Pydantic: https://docs.pydantic.dev/
- Mermaid: https://mermaid.js.org/

## Support

- **Documentation**: See `/ref` directory and `CLAUDE.md`
- **Usage Guide**: `USAGE.md`
- **API Reference**: `ref/api-reference.md`
- **Testing Guide**: `ref/testing.md`
- **Export Guide**: `docs/export-guide.md`

---

**Last Updated**: 2025-11-13
**Maintainer**: AI-Assisted Development Team
**License**: [Project License]
