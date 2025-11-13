# Claude Code Reference Documentation

This file provides quick navigation to all project documentation for AI-assisted development.

## Project Overview

**Name**: 剧本叙事结构分析系统 (Script Narrative Structure Analysis System)

**Purpose**: Multi-agent LLM system for analyzing and correcting narrative structure in screenplays using a three-stage pipeline (Discover → Audit → Modify).

**Technology Stack**: Python, LangChain, LangGraph, Pydantic, DeepSeek/Claude/OpenAI

**Current Version**: 2.1.0 (2025-11-12)

---

## Quick Start

### For First-Time Users
1. Read: [`ref/getting-started.md`](ref/getting-started.md) - Installation, setup, and basic usage
2. Run: `./run_tests.sh` - Verify installation
3. Try: `python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json`

### For Developers
1. Read: [`ref/architecture.md`](ref/architecture.md) - System design and components
2. Read: [`prompts/README.md`](prompts/README.md) - Prompt engineering guide
3. Review: [`tests/`](tests/) - Test examples

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

## Important Files

### Source Code

#### Core Implementation
- **[`src/pipeline.py`](src/pipeline.py)** (18,954 bytes)
  - LangGraph pipeline
  - Actor implementations (DiscovererActor, AuditorActor, ModifierActor)
  - LLM provider integration
  - State management
  - **Start here for**: Pipeline logic, actor behavior

- **[`src/cli.py`](src/cli.py)** (8,255 bytes)
  - Command-line interface
  - Commands: analyze, validate, benchmark
  - **Start here for**: CLI usage, command implementation

#### Prompt System
- **[`prompts/schemas.py`](prompts/schemas.py)**
  - Pydantic models for all data structures
  - Validation functions
  - Calculation utilities
  - **Start here for**: Data models, validation logic

- **[`prompts/stage1_discoverer.md`](prompts/stage1_discoverer.md)**
  - Stage 1 prompt (TCC identification)
  - **Start here for**: Understanding TCC discovery logic

- **[`prompts/stage2_auditor.md`](prompts/stage2_auditor.md)**
  - Stage 2 prompt (A/B/C-line ranking)
  - **Start here for**: Understanding ranking criteria

- **[`prompts/stage3_modifier.md`](prompts/stage3_modifier.md)**
  - Stage 3 prompt (structural fixes)
  - **Start here for**: Understanding modification logic

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
- **[`.env.example`](.env.example)** (1,374 bytes)
  - Environment variable template
  - API key configuration
  - **Copy to `.env`** and add your keys

- **[`requirements.txt`](requirements.txt)** (426 bytes)
  - Core dependencies
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

### Task: Analyze a Script
1. Check [`USAGE.md`](USAGE.md) - "Using the Pipeline" section
2. Use CLI: `python -m src.cli analyze script.json`
3. Or use API from [`ref/api-reference.md`](ref/api-reference.md)

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
│   └── __init__.py
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
│   └── golden/                 # Test datasets
│
├── docs/                        # Development docs
│   ├── development-plan.md
│   └── test-script-conversion-plan.md
│
├── .env.example                 # Environment template
├── requirements.txt             # Core dependencies
├── requirements-test.txt        # Test dependencies
├── pytest.ini                   # Pytest configuration
└── run_tests.sh                # Test runner script
```

---

## Environment Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example`
- [ ] API key added to `.env` (DeepSeek/Anthropic/OpenAI)
- [ ] Tests passing: `./run_tests.sh`
- [ ] Example analysis works: `python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json`

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

---

## External Resources

### LLM Providers
- DeepSeek: https://platform.deepseek.com/
- Anthropic Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/

### Technical Documentation
- LangChain: https://python.langchain.com/docs/
- LangGraph: https://langchain-ai.github.io/langgraph/
- Pydantic: https://docs.pydantic.dev/
- pytest: https://docs.pytest.org/

### Narrative Theory
- Robert McKee - "Story": Narrative structure principles
- "The Art of Dramatic Writing": Multi-line storytelling

---

## Version Information

**Project Version**: 2.1.0
**Prompt Version**: 2.1-Refactored
**Documentation Version**: 1.0
**Last Updated**: 2025-11-12

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

4. **Testing approach**:
   - Unit tests: [`tests/test_schemas.py`](tests/test_schemas.py)
   - Integration: [`tests/test_golden_dataset.py`](tests/test_golden_dataset.py)
   - Examples: [`examples/golden/`](examples/golden/)

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
