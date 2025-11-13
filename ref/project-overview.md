# Project Overview

## Project Name
剧本叙事结构分析系统 (Script Narrative Structure Analysis System)

## Description
A multi-agent LLM system for analyzing and correcting narrative structure in screenplays. The system identifies theatrical conflict chains (TCCs), ranks them by importance, and fixes structural issues.

## Core Purpose
Help screenwriters and production teams:
- Identify independent story threads (TCCs)
- Rank storylines as A/B/C-lines based on importance
- Fix structural problems in script data

## Key Features
- Three-stage analysis pipeline (Discover → Audit → Modify)
- Director-Actor architecture for task coordination
- Structured output with Pydantic validation
- Support for multiple LLM providers (DeepSeek, Anthropic, OpenAI)
- Comprehensive testing framework
- Performance benchmarking

## Technology Stack
- **Language**: Python 3.8+
- **LLM Framework**: LangChain + LangGraph
- **LLM Providers**: DeepSeek (default), Claude, OpenAI
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Observability**: LangSmith (optional)

## Project Status (Updated 2025-11-13)
- Requirements analysis: ✅ Complete
- Prompt engineering: ✅ Complete (v2.1)
- Core implementation: ✅ Complete
- Testing framework: ✅ Complete (44/44 tests passing)
- Documentation: ✅ Complete (CLAUDE.md + 7 reference docs)
- Dependencies: ✅ Installed and configured
- LLM Integration: ✅ Stage 1 verified, ⚠️ Stage 2 needs optimization
- **Overall Completion**: 90%

## Key Metrics
- 3 analysis stages (Stage 1 verified ✅)
- 8 Python modules (1976 lines of code)
- 44 unit tests (100% passing)
- 3 LLM integration tests (ready to enable)
- Support for 3 LLM providers (DeepSeek configured)
- 7 reference documentation files (72KB)

## Recent Achievements (2025-11-13)
- ✅ Installed LangChain 1.0.5, LangGraph 1.0.3
- ✅ Fixed LangGraph START node import
- ✅ Added JSON cleaning for markdown-wrapped responses
- ✅ Fixed Pydantic schema validation issues
- ✅ Stage 1 successfully identifies TCCs (85-95% confidence)
- ✅ Created comprehensive documentation system

## Known Issues
- ⚠️ Stage 2 JSON parsing needs enhancement (trailing characters)
- ⚠️ TCC overlap detection may need refinement

## Version
Current: 2.1.0
Last Updated: 2025-11-13
Latest Commit: 1a9f882
