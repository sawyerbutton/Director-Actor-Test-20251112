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

## Project Status
- Requirements analysis: ✅ Complete
- Prompt engineering: ✅ Complete (v2.1)
- Core implementation: ✅ Complete
- Testing framework: ✅ Complete
- Documentation: ✅ Complete

## Key Metrics
- 3 analysis stages
- 8 Python modules
- Multiple test suites
- Support for 3 LLM providers

## Version
Current: 2.1.0
Last Updated: 2025-11-12
