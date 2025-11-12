# Script Analysis System - Usage Guide

This guide covers how to use the complete script analysis system, including testing, pipeline execution, and benchmarking.

## Table of Contents

1. [Installation](#installation)
2. [Running Tests](#running-tests)
3. [Using the Pipeline](#using-the-pipeline)
4. [Command-Line Interface](#command-line-interface)
5. [Benchmarking](#benchmarking)
6. [API Reference](#api-reference)

---

## Installation

### 1. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Test dependencies (optional)
pip install -r requirements-test.txt
```

### 2. Set Up API Key

The system supports multiple LLM providers. **DeepSeek is the default** (most cost-effective).

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env and add your API key
# For DeepSeek (default):
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# For Anthropic Claude (optional):
# ANTHROPIC_API_KEY=your_anthropic_key_here

# For OpenAI (optional):
# OPENAI_API_KEY=your_openai_key_here
```

**Get API Keys:**
- DeepSeek: https://platform.deepseek.com/
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/

---

## Running Tests

### Quick Start

```bash
# Run all tests (excluding LLM tests)
./run_tests.sh

# Run only schema tests
./run_tests.sh schemas

# Run only golden dataset tests
./run_tests.sh golden
```

### Using Pytest Directly

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_schemas.py -v

# Run tests with coverage
pytest tests/ --cov=prompts --cov-report=html
```

### Test Categories

- **Unit tests**: `tests/test_schemas.py` - Test individual functions and validators
- **Integration tests**: `tests/test_golden_dataset.py` - Test against golden dataset
- **LLM tests**: Marked with `@pytest.mark.llm` (skipped by default to save costs)

---

## Using the Pipeline

### Python API

```python
from prompts.schemas import Script
from src.pipeline import run_pipeline

# Load your script
script = Script(**your_script_data)

# Option 1: Use default provider (DeepSeek)
final_state = run_pipeline(script)

# Option 2: Specify provider
final_state = run_pipeline(script, provider="deepseek")  # or "anthropic", "openai"

# Option 3: Specify provider and model
final_state = run_pipeline(script, provider="anthropic", model="claude-sonnet-4-5")

# Access results
discoverer_output = final_state["discoverer_output"]
auditor_output = final_state["auditor_output"]
modifier_output = final_state["modifier_output"]

# Check for errors
if final_state["errors"]:
    print("Warnings:", final_state["errors"])
```

### Stage-by-Stage Execution

```python
from src.pipeline import create_pipeline, create_llm

# Option 1: Create pipeline with default provider (DeepSeek)
pipeline = create_pipeline()

# Option 2: Create pipeline with specific provider
pipeline = create_pipeline(provider="anthropic", model="claude-sonnet-4-5")

# Option 3: Create custom LLM and pass it
llm = create_llm(provider="deepseek", model="deepseek-chat")
pipeline = create_pipeline(llm=llm)

# Initialize state
initial_state = {
    "script": your_script,
    "discoverer_output": None,
    "auditor_output": None,
    "modifier_output": None,
    "current_stage": "initialized",
    "errors": [],
    "retry_count": 0,
    "messages": []
}

# Run pipeline
final_state = pipeline.invoke(initial_state)
```

---

## Command-Line Interface

### Analyze a Script

**Basic usage (uses DeepSeek by default):**
```bash
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json
```

**With output file:**
```bash
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json \
  --output results/analysis_results.json
```

**Specify LLM provider:**
```bash
# Use DeepSeek (default)
python -m src.cli analyze script.json --provider deepseek

# Use Anthropic Claude
python -m src.cli analyze script.json --provider anthropic

# Use OpenAI
python -m src.cli analyze script.json --provider openai
```

**Specify custom model:**
```bash
python -m src.cli analyze script.json --provider deepseek --model deepseek-chat
```

### Validate a Script

```bash
python -m src.cli validate examples/golden/百妖_ep09_s01-s05.json
```

This checks:
- JSON schema validity
- Setup-payoff chain integrity
- Scene ID references

### Run Benchmark

```bash
python -m src.cli benchmark examples/golden/百妖_ep09_s01-s05.json
```

Compares actual output vs. expected output from the golden dataset.

---

## Benchmarking

### Run Performance Benchmark

```bash
python benchmarks/run_benchmark.py examples/golden
```

**With custom number of runs:**
```bash
python benchmarks/run_benchmark.py examples/golden 5
```

### Benchmark Metrics

The benchmark measures:

| Metric | Description |
|--------|-------------|
| **Accuracy** | % of expected TCCs correctly identified |
| **Precision** | % of identified TCCs that are correct |
| **Recall** | % of actual TCCs that were identified |
| **Consistency** | How often multiple runs produce the same result |
| **Execution Time** | Average time per stage |

### Example Output

```
==================================================
Stage 1 (Discoverer) Benchmark
==================================================

Run 1/3...
  ✅ Execution time: 5.23s
  📊 TCCs identified: 3
  🎯 Accuracy: 100.00%
  ⚖️  Precision: 100.00%
  📈 Recall: 100.00%

──────────────────────────────────────────────────
Stage 1 Summary Statistics
──────────────────────────────────────────────────
  avg_accuracy             : 100.00%
  avg_precision            : 100.00%
  avg_recall               : 100.00%
  avg_execution_time       : 5.18s
  consistency_score        : 100.00%
```

---

## API Reference

### Core Modules

#### `prompts/schemas.py`

Data validation and utility functions:

```python
# Validation functions
from prompts.schemas import (
    validate_setup_payoff_integrity,
    validate_tcc_independence,
    validate_scene_references
)

# Calculation functions
from prompts.schemas import (
    calculate_spine_score,
    calculate_heart_score,
    calculate_a_line_interaction,
    calculate_setup_payoff_density
)

# Models
from prompts.schemas import (
    Script, Scene, TCC,
    DiscovererOutput, AuditorOutput, ModifierOutput
)
```

#### `src/pipeline.py`

Pipeline execution:

```python
from src.pipeline import (
    create_pipeline,       # Create LangGraph pipeline
    run_pipeline,          # Run complete pipeline
    DiscovererActor,       # Stage 1 actor
    AuditorActor,          # Stage 2 actor
    ModifierActor          # Stage 3 actor
)
```

### Configuration

#### Environment Variables

**Required (choose one based on provider):**
- `DEEPSEEK_API_KEY`: Your DeepSeek API key (default provider)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (if using Claude)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)

**Optional:**
- `DEEPSEEK_BASE_URL`: DeepSeek API base URL (default: `https://api.deepseek.com/v1`)
- `LLM_PROVIDER`: Default LLM provider (`deepseek`, `anthropic`, or `openai`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

**All environment variables can be set in `.env` file (recommended).**

#### Retry Configuration

The pipeline automatically retries failed stages up to 3 times. Configure in `src/pipeline.py`:

```python
# In conditional functions
if state["retry_count"] < 3:  # Change max retries here
    return "discoverer"  # Retry
else:
    return END  # Give up
```

---

## Examples

### Example 1: Validate Golden Dataset

```python
import json
from prompts.schemas import Script, validate_setup_payoff_integrity

# Load script
with open("examples/golden/百妖_ep09_s01-s05.json") as f:
    script = Script(**json.load(f))

# Validate
errors = validate_setup_payoff_integrity(script)
if errors:
    print(f"Found {len(errors)} errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ Script is valid!")
```

### Example 2: Calculate Metrics

```python
from prompts.schemas import calculate_spine_score

# Calculate spine score for a TCC
scene_count = 15
setup_payoff_density = 0.80
drives_climax = True

spine_score = calculate_spine_score(
    scene_count=scene_count,
    setup_payoff_density=setup_payoff_density,
    drives_climax=drives_climax
)

print(f"Spine score: {spine_score:.1f}")
# Output: Spine score: 33.2
```

### Example 3: Check TCC Independence

```python
from prompts.schemas import TCC, validate_tcc_independence

tccs = [
    TCC(
        tcc_id="TCC_01",
        super_objective="Character A wants X",
        core_conflict_type="interpersonal",
        evidence_scenes=["S01", "S02", "S03", "S04", "S05"],
        confidence=0.95
    ),
    TCC(
        tcc_id="TCC_02",
        super_objective="Character B opposes X",
        core_conflict_type="interpersonal",
        evidence_scenes=["S01", "S02", "S03", "S04"],  # 80% overlap!
        confidence=0.90
    )
]

warnings = validate_tcc_independence(tccs)
if warnings:
    print("⚠️ Potential mirror conflicts:")
    for warning in warnings:
        print(f"  - {warning}")
```

---

## Troubleshooting

### Issue: "No module named pytest"

**Solution:**
```bash
pip install -r requirements-test.txt
```

### Issue: "DEEPSEEK_API_KEY not found" (or other API key errors)

**Solution:**
```bash
# Option 1: Create .env file (recommended)
cp .env.example .env
# Then edit .env and add your API key

# Option 2: Export environment variable
export DEEPSEEK_API_KEY="your_key_here"

# For other providers:
export ANTHROPIC_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"
```

### Issue: DeepSeek API connection errors

**Solution:**
1. Check your API key is correct
2. Check your internet connection
3. Try setting a custom base URL if you're in a region with access restrictions:
   ```bash
   export DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
   ```
4. If issues persist, try using a different provider:
   ```bash
   python -m src.cli analyze script.json --provider openai
   ```

### Issue: Tests are slow

**Solution:**
- Skip LLM tests: `pytest tests/ -m "not llm"`
- Run specific tests: `pytest tests/test_schemas.py`
- Use parallel execution: `pytest tests/ -n auto` (requires `pytest-xdist`)

### Issue: Validation errors in LLM output

**Solution:**
The system automatically retries up to 3 times. If it still fails:
1. Check prompt templates in `prompts/`
2. Review LLM output in logs
3. Verify schema definitions in `prompts/schemas.py`

---

## Next Steps

1. **Customize prompts**: Edit files in `prompts/` to adjust system behavior
2. **Add new validations**: Extend `prompts/schemas.py` with custom validators
3. **Integrate with CI/CD**: Use `run_tests.sh` in your CI pipeline
4. **Create custom actors**: Extend `src/pipeline.py` with new analysis stages

---

## Support

- **Documentation**: See `prompts/README.md` for prompt system details
- **Issues**: Report bugs or request features in GitHub issues
- **Examples**: Check `examples/` for sample scripts and expected outputs

---

**Version**: 2.1.0
**Last Updated**: 2025-11-12
