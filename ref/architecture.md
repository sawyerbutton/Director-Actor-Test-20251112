# System Architecture

## Overview
The system uses a **Director-Actor pattern** implemented with LangGraph, where a Director orchestrates three specialized Actor agents.

## Director-Actor Pattern

```
┌─────────────────────────────────────┐
│         Director (LangGraph)         │
│   - Flow orchestration               │
│   - State management                 │
│   - Error handling & retries         │
└─────────┬───────────────────────────┘
          │
          ├──→ DiscovererActor (Stage 1)
          │     └─ Identifies all TCCs
          │
          ├──→ AuditorActor (Stage 2)
          │     └─ Ranks TCCs as A/B/C-lines
          │
          └──→ ModifierActor (Stage 3)
                └─ Fixes structural issues
```

## Three-Stage Pipeline

### Stage 1: Discoverer
**File**: `prompts/stage1_discoverer.md`
**Purpose**: Identify all independent Theatrical Conflict Chains (TCCs)

**Key Logic**:
- Scans scene cards for super objectives
- Distinguishes independent storylines vs. opposing forces
- Uses evidence-based detection with fallback modes
- Prevents mirror TCC detection

**Input**: Script JSON with scenes
**Output**: List of TCCs with confidence scores

### Stage 2: Auditor
**File**: `prompts/stage2_auditor.md`
**Purpose**: Rank TCCs by dramatic importance

**Key Logic**:
- Calculates spine/heart/flavor scores
- Identifies A-line (main plot), B-lines (subplots), C-lines (flavor)
- Analyzes force dynamics (protagonist/antagonist)
- Measures scene coverage

**Input**: Script JSON + TCC list from Stage 1
**Output**: Ranked TCCs with analysis

### Stage 3: Modifier
**File**: `prompts/stage3_modifier.md`
**Purpose**: Fix structural issues identified in audit

**Key Logic**:
- Applies surgical fixes to JSON structure
- Repairs setup-payoff chains
- Adds missing key events
- Logs all modifications

**Input**: Script JSON + Audit report
**Output**: Modified script JSON + change log

## Data Flow

```
Input: Script JSON
    ↓
[Director initializes state]
    ↓
[Stage 1: Discoverer]
  • Scans scenes for TCCs
  • Returns: TCCList
  • Validation: Schema check + independence check
    ↓
[Stage 2: Auditor]
  • Ranks TCCs (A/B/C)
  • Returns: AuditReport
  • Validation: Must have 1 A-line
    ↓
[Stage 3: Modifier]
  • Fixes structural issues
  • Returns: Modified Script + Changelog
  • Validation: JSON integrity + no new issues
    ↓
Output: Final script + complete report
```

## Core Components

### 1. Pipeline (`src/pipeline.py`)
- LangGraph state machine
- Three actor nodes (discoverer, auditor, modifier)
- Conditional routing with retry logic
- State management

### 2. CLI (`src/cli.py`)
- Command-line interface
- Commands: analyze, validate, benchmark
- LLM provider selection

### 3. Schemas (`prompts/schemas.py`)
- Pydantic models for all data structures
- Validation functions
- Utility calculators

### 4. Tests (`tests/`)
- Schema validation tests
- Golden dataset tests
- Integration tests

## State Management

### Pipeline State
```python
{
    "script": Script,              # Input script
    "discoverer_output": DiscovererOutput | None,
    "auditor_output": AuditorOutput | None,
    "modifier_output": ModifierOutput | None,
    "current_stage": str,          # Current execution stage
    "errors": List[str],           # Accumulated errors
    "retry_count": int,            # Retry counter
    "messages": List[BaseMessage]  # LLM conversation history
}
```

## Error Handling

### Retry Strategy
- Maximum 3 retries per stage
- Exponential backoff: 2s, 4s, 8s
- Validation errors included in retry prompts
- Human review requested after max retries

### Fallback Modes
- **Stage 1**: If setup_payoff missing → use scene_mission + key_events
- **Stage 2**: If B/C ranking fails → return A-line only
- **Stage 3**: If fix fails → log and continue with next fix

## Quality Assurance

### Validation Layers
1. **Schema Validation**: Pydantic type checking
2. **Business Logic**: Custom validation functions
3. **Output Quality**: Confidence thresholds, completeness checks

### Quality Checkpoints
| Stage | Validation | Action on Failure |
|-------|-----------|-------------------|
| Stage 1 | TCC independence, min 1 TCC | Retry with feedback |
| Stage 2 | Must have A-line | Retry with feedback |
| Stage 3 | JSON integrity, no new issues | Rollback + retry |

## LLM Provider Support

### Supported Providers
1. **DeepSeek** (default)
   - Model: `deepseek-chat`
   - API: OpenAI-compatible
   - Cost: Most economical

2. **Anthropic Claude**
   - Models: `claude-sonnet-4-5`, `claude-sonnet-3-5`
   - API: Native Anthropic API
   - Cost: Premium

3. **OpenAI**
   - Models: `gpt-4-turbo-preview`, etc.
   - API: OpenAI API
   - Cost: Variable

### Provider Selection
```python
# Via code
pipeline = create_pipeline(provider="deepseek", model="deepseek-chat")

# Via CLI
python -m src.cli analyze script.json --provider deepseek
```

## Performance Considerations

### Optimization Strategies
- Prompt caching for repeated executions
- Batch validation instead of individual checks
- Parallel processing for multiple scripts
- Minimal token usage in prompts

### Benchmarking
See `benchmarks/run_benchmark.py` for performance metrics:
- Execution time per stage
- Accuracy, precision, recall
- Consistency across multiple runs

## Observability

### Logging
- Stage execution logs
- Validation results
- Error traces
- Performance metrics

### LangSmith Integration (Optional)
- Real-time trace visualization
- Token usage tracking
- Error debugging
- Performance profiling

## File Organization

```
.
├── src/
│   ├── pipeline.py        # LangGraph pipeline + actors
│   ├── cli.py             # Command-line interface
│   └── __init__.py
├── prompts/
│   ├── stage1_discoverer.md
│   ├── stage2_auditor.md
│   ├── stage3_modifier.md
│   ├── schemas.py         # Pydantic models
│   └── README.md
├── tests/
│   ├── test_schemas.py    # Unit tests
│   └── test_golden_dataset.py  # Integration tests
├── benchmarks/
│   └── run_benchmark.py   # Performance tests
└── examples/
    └── golden/            # Test datasets
```

## Design Principles

### 1. Fault Tolerance
System must work even with incomplete data ("try your best, don't crash")

### 2. Structure Over Creativity
Modifiers fix structure, don't add creative content

### 3. First-Principles Thinking
Use quantitative metrics (stakes, coverage, impact) vs. subjective judgment

### 4. Separation of Concerns
- Prompts: Instructions + rules
- Schemas: Data structure + validation
- Code: Orchestration + execution

## Extension Points

### Adding New Stages
1. Create `prompts/stageN_name.md`
2. Define schemas in `prompts/schemas.py`
3. Add actor node in `src/pipeline.py`
4. Add validation functions
5. Write tests
6. Update documentation

### Custom Validation Rules
Extend validation functions in `prompts/schemas.py`:
```python
def validate_custom_rule(script: Script) -> List[str]:
    errors = []
    # Your validation logic
    return errors
```

### LLM Provider Integration
Add new provider in `src/pipeline.py`:
```python
def create_llm(provider: str, model: str):
    if provider == "new_provider":
        return NewProviderLLM(model=model, api_key=api_key)
```
