# Reference Documentation

This directory contains comprehensive reference documentation for the Script Analysis System.

**Last Updated**: 2025-11-13
**Documentation Version**: 1.1
**Project Status**: 90% complete (Stage 1 verified, Stage 2 needs optimization)

## Documentation Files

### 1. [`project-overview.md`](project-overview.md) (1.4 KB)
High-level project summary including purpose, features, technology stack, and current status.

**Read this first** to understand what the project does.

---

### 2. [`architecture.md`](architecture.md) (7.5 KB)
Detailed system architecture including:
- Director-Actor pattern
- Three-stage pipeline design
- Data flow and state management
- Error handling strategies
- LLM provider integration
- Extension points

**Read this** to understand how the system works internally.

---

### 3. [`getting-started.md`](getting-started.md) (9.8 KB)
Step-by-step setup and usage guide including:
- Installation instructions
- API key configuration
- Basic usage examples
- Common workflows
- Troubleshooting tips

**Read this** to get the system running quickly.

---

### 4. [`api-reference.md`](api-reference.md) (15 KB)
Complete API documentation including:
- Function signatures and parameters
- Return types and examples
- CLI commands
- Data models (Pydantic schemas)
- Validation and calculation functions
- Environment variables

**Read this** when writing code or integrating with the system.

---

### 5. [`testing.md`](testing.md) (14 KB)
Comprehensive testing guide including:
- Test structure and categories
- Running tests (unit, integration, benchmarks)
- Test-driven development workflow
- Mocking strategies
- Coverage reporting
- CI/CD integration

**Read this** when writing or debugging tests.

---

### 6. [`prompts-guide.md`](prompts-guide.md) (15 KB)
Prompt engineering guide including:
- Prompt architecture and design principles
- Stage-by-stage breakdown
- Customization strategies
- Best practices
- Versioning and migration

**Read this** when modifying prompts or adding new analysis stages.

---

## Quick Navigation

### For Different Roles

#### New Users
1. [`project-overview.md`](project-overview.md) - What is this?
2. [`getting-started.md`](getting-started.md) - How do I use it?
3. Run example: `python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json`

#### Developers
1. [`architecture.md`](architecture.md) - System design
2. [`api-reference.md`](api-reference.md) - API docs
3. [`testing.md`](testing.md) - Testing guide
4. Review code: [`../src/pipeline.py`](../src/pipeline.py)

#### Prompt Engineers
1. [`prompts-guide.md`](prompts-guide.md) - Prompt engineering
2. [`../prompts/README.md`](../prompts/README.md) - Detailed prompt docs
3. Review prompts: [`../prompts/`](../prompts/)

#### QA/Testers
1. [`testing.md`](testing.md) - Testing guide
2. [`getting-started.md`](getting-started.md) - Setup
3. Run tests: `./run_tests.sh`

---

## Documentation Hierarchy

```
CLAUDE.md (Root navigation file)
    ├── ref/README.md (This file)
    ├── ref/project-overview.md
    ├── ref/architecture.md
    ├── ref/getting-started.md
    ├── ref/api-reference.md
    ├── ref/testing.md
    └── ref/prompts-guide.md
```

---

## External Documentation

### Project Documentation
- **Main README**: [`../README.md`](../README.md) - Business context (Chinese)
- **Usage Guide**: [`../USAGE.md`](../USAGE.md) - Detailed usage examples
- **DeepSeek Guide**: [`../README_DEEPSEEK.md`](../README_DEEPSEEK.md) - DeepSeek integration

### Code Documentation
- **Prompts**: [`../prompts/README.md`](../prompts/README.md) - Prompt system details
- **Source**: [`../src/`](../src/) - Implementation code
- **Tests**: [`../tests/`](../tests/) - Test suites

---

## Search by Topic

### Installation & Setup
- [`getting-started.md`](getting-started.md) lines 5-96

### API Usage
- [`api-reference.md`](api-reference.md) lines 7-138 (Core functions)
- [`api-reference.md`](api-reference.md) lines 176-265 (Data models)

### Testing
- [`testing.md`](testing.md) lines 17-51 (Running tests)
- [`testing.md`](testing.md) lines 267-322 (Test-driven development)

### Architecture
- [`architecture.md`](architecture.md) lines 13-35 (Director-Actor pattern)
- [`architecture.md`](architecture.md) lines 37-125 (Pipeline stages)

### Prompts
- [`prompts-guide.md`](prompts-guide.md) lines 41-156 (Stage 1: Discoverer)
- [`prompts-guide.md`](prompts-guide.md) lines 160-293 (Stage 2: Auditor)
- [`prompts-guide.md`](prompts-guide.md) lines 297-395 (Stage 3: Modifier)

### Troubleshooting
- [`getting-started.md`](getting-started.md) lines 263-299 (Common issues)
- [`testing.md`](testing.md) lines 533-567 (Test debugging)
- [`prompts-guide.md`](prompts-guide.md) lines 645-683 (Prompt issues)

---

## Key Concepts Reference

| Concept | Primary Doc | Lines | Also See |
|---------|------------|-------|----------|
| TCC (Theatrical Conflict Chain) | [`../README.md`](../README.md) | 302-314 | [`prompts-guide.md`](prompts-guide.md) 46-73 |
| A/B/C-Line Classification | [`architecture.md`](architecture.md) | 52-68 | [`prompts-guide.md`](prompts-guide.md) 164-244 |
| Director-Actor Pattern | [`architecture.md`](architecture.md) | 13-35 | [`../README.md`](../README.md) 89-106 |
| Setup-Payoff Chain | [`api-reference.md`](api-reference.md) | 267-289 | [`../prompts/`](../prompts/) |
| LangGraph Pipeline | [`architecture.md`](architecture.md) | 37-90 | [`../src/pipeline.py`](../src/pipeline.py) |

---

## File Sizes & Content Density

| File | Size | Density | Best For |
|------|------|---------|----------|
| [`project-overview.md`](project-overview.md) | 1.4 KB | ⭐ Light | Quick context |
| [`getting-started.md`](getting-started.md) | 9.8 KB | ⭐⭐ Medium | Setup & basics |
| [`architecture.md`](architecture.md) | 7.5 KB | ⭐⭐ Medium | System design |
| [`api-reference.md`](api-reference.md) | 15 KB | ⭐⭐⭐ Dense | API details |
| [`testing.md`](testing.md) | 14 KB | ⭐⭐⭐ Dense | Testing details |
| [`prompts-guide.md`](prompts-guide.md) | 15 KB | ⭐⭐⭐ Dense | Prompt engineering |

---

## Documentation Standards

### Format
- All files in Markdown format
- GitHub-flavored markdown syntax
- Clear heading hierarchy
- Code examples with syntax highlighting
- Links to related documentation

### Structure
1. Overview/Purpose
2. Table of Contents (for long docs)
3. Main content with clear sections
4. Examples throughout
5. Troubleshooting section
6. References/External links

### Maintenance
- Update version numbers when code changes
- Add new sections for new features
- Keep examples current
- Link to new documentation files

---

## Contributing to Documentation

### Adding New Documentation
1. Create file in `ref/` directory
2. Follow existing format and structure
3. Add entry to this README.md
4. Update [`../CLAUDE.md`](../CLAUDE.md) with link
5. Cross-reference from related docs

### Updating Existing Documentation
1. Edit the relevant file
2. Update "Last Updated" date
3. Add entry to version history (if applicable)
4. Check all internal links still work

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-12 | Initial documentation set created via /initref |

---

## Feedback & Improvements

If you notice:
- Missing information
- Outdated examples
- Broken links
- Unclear explanations

Please update the relevant documentation file and this README.

---

**Last Updated**: 2025-11-12
**Documentation Version**: 1.0
