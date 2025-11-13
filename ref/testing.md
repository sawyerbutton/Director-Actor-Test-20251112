# Testing Guide

## Overview

The project includes comprehensive testing across multiple layers:
- Schema validation tests
- Golden dataset integration tests
- Performance benchmarks
- LLM interaction tests

## Test Structure

```
tests/
├── __init__.py
├── test_schemas.py           # Unit tests for schemas and validators
└── test_golden_dataset.py    # Integration tests with golden data

benchmarks/
└── run_benchmark.py          # Performance benchmarking
```

## Running Tests

### Quick Start
```bash
# Run all tests (excluding LLM tests)
./run_tests.sh

# Run specific test categories
./run_tests.sh schemas
./run_tests.sh golden
```

### Using pytest Directly
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_schemas.py -v

# Specific test function
pytest tests/test_schemas.py::test_tcc_validation -v

# With coverage
pytest tests/ --cov=prompts --cov=src --cov-report=html
```

### Test Markers
```bash
# Skip LLM tests (saves API costs)
pytest tests/ -m "not llm"

# Run only LLM tests
pytest tests/ -m "llm"

# Run only unit tests
pytest tests/ -m "unit"

# Run only integration tests
pytest tests/ -m "integration"
```

## Test Categories

### 1. Schema Tests (`test_schemas.py`)

#### Purpose
Validate Pydantic models and utility functions without LLM calls.

#### What's Tested
- Model instantiation and validation
- Field constraints (patterns, ranges, required fields)
- Validation functions (setup-payoff integrity, TCC independence)
- Calculation functions (spine score, heart score)
- Edge cases and error handling

#### Example Tests
```python
def test_tcc_validation():
    """Test TCC model validation"""
    # Valid TCC
    tcc = TCC(
        tcc_id="TCC_01",
        super_objective="Character goal",
        core_conflict_type="interpersonal",
        evidence_scenes=["S01", "S02"],
        confidence=0.95
    )
    assert tcc.tcc_id == "TCC_01"

    # Invalid TCC ID format
    with pytest.raises(ValidationError):
        TCC(
            tcc_id="INVALID",  # Must match TCC_\d{2}
            super_objective="Goal",
            core_conflict_type="interpersonal",
            evidence_scenes=["S01"],
            confidence=0.95
        )

def test_spine_score_calculation():
    """Test spine score calculation"""
    score = calculate_spine_score(
        scene_count=15,
        setup_payoff_density=0.80,
        drives_climax=True
    )
    assert score == 41.2  # (15*2) + (0.8*1.5) + 10
```

#### Running Schema Tests
```bash
pytest tests/test_schemas.py -v
```

---

### 2. Golden Dataset Tests (`test_golden_dataset.py`)

#### Purpose
Integration tests using real script data with expected outputs.

#### What's Tested
- End-to-end pipeline execution
- Output format validation
- Result accuracy vs. expected outputs
- Error recovery and retry logic

#### Golden Dataset Structure
```
examples/golden/
├── 百妖_ep09_s01-s05.json          # Input script
├── 百妖_ep09_s01-s05_expected.json  # Expected outputs
└── ...
```

#### Example Tests
```python
@pytest.mark.llm
@pytest.mark.integration
def test_full_pipeline_golden():
    """Test full pipeline with golden dataset"""
    # Load golden script
    with open("examples/golden/百妖_ep09_s01-s05.json") as f:
        script = Script(**json.load(f))

    # Run pipeline
    final_state = run_pipeline(script, provider="deepseek")

    # Validate outputs
    assert final_state["discoverer_output"] is not None
    assert len(final_state["discoverer_output"].tccs) >= 1

    assert final_state["auditor_output"] is not None
    assert final_state["auditor_output"].rankings.a_line is not None

    assert final_state["modifier_output"] is not None
    assert len(final_state["modifier_output"].modification_log) >= 0

def test_compare_with_expected():
    """Compare actual output vs. expected"""
    # Load expected outputs
    with open("examples/golden/百妖_ep09_s01-s05_expected.json") as f:
        expected = json.load(f)

    # Run analysis
    final_state = run_pipeline(script, provider="deepseek")

    # Compare TCC IDs
    actual_tcc_ids = {tcc.tcc_id for tcc in final_state["discoverer_output"].tccs}
    expected_tcc_ids = set(expected["discoverer"]["tcc_ids"])
    assert actual_tcc_ids == expected_tcc_ids
```

#### Running Golden Dataset Tests
```bash
# Requires API key
pytest tests/test_golden_dataset.py -v

# Skip if no API key
pytest tests/test_golden_dataset.py -m "not llm"
```

---

### 3. Benchmarks (`benchmarks/run_benchmark.py`)

#### Purpose
Measure performance, accuracy, and consistency across multiple runs.

#### Metrics Measured
- **Execution Time**: Time per stage
- **Accuracy**: % of expected TCCs correctly identified
- **Precision**: % of identified TCCs that are correct
- **Recall**: % of actual TCCs that were identified
- **Consistency**: How often results match across runs

#### Running Benchmarks
```bash
# Single run
python benchmarks/run_benchmark.py examples/golden

# Multiple runs (for consistency)
python benchmarks/run_benchmark.py examples/golden 5

# Specific script
python benchmarks/run_benchmark.py examples/golden/百妖_ep09_s01-s05.json 3
```

#### Example Output
```
==================================================
Stage 1 (Discoverer) Benchmark
==================================================

Run 1/3...
  ✅ Execution time: 4.23s
  📊 TCCs identified: 3
  🎯 Accuracy: 100.00%
  ⚖️  Precision: 100.00%
  📈 Recall: 100.00%

Run 2/3...
  ✅ Execution time: 4.18s
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
  avg_execution_time       : 4.21s
  consistency_score        : 100.00%
```

---

## Test Data

### Creating Test Scripts

#### Minimal Test Script
```json
{
  "scenes": [
    {
      "scene_id": "S01",
      "scene_mission": "Introduce main character",
      "key_events": ["Character A enters", "Character A meets B"],
      "setup_payoff": {
        "setup_for": ["S05"],
        "payoff_from": []
      }
    },
    {
      "scene_id": "S05",
      "scene_mission": "Resolve conflict",
      "key_events": ["Character A achieves goal"],
      "setup_payoff": {
        "setup_for": [],
        "payoff_from": ["S01"]
      }
    }
  ]
}
```

#### Complete Test Script
See `examples/golden/百妖_ep09_s01-s05.json` for full example with:
- Multiple TCCs
- Setup-payoff chains
- Relationship changes
- Information changes
- Character interactions

### Creating Expected Outputs

#### Expected Output Structure
```json
{
  "discoverer": {
    "tcc_ids": ["TCC_01", "TCC_02"],
    "tccs": [
      {
        "tcc_id": "TCC_01",
        "super_objective": "Expected objective",
        "core_conflict_type": "interpersonal"
      }
    ]
  },
  "auditor": {
    "a_line": "TCC_01",
    "b_lines": ["TCC_02"],
    "c_lines": []
  },
  "modifier": {
    "expected_fixes": 5
  }
}
```

---

## Test-Driven Development Workflow

### 1. Write Test First
```python
def test_new_validation_rule():
    """Test new validation rule for X"""
    script = Script(scenes=[...])  # Invalid case
    errors = validate_new_rule(script)
    assert len(errors) > 0
    assert "expected error message" in errors[0]
```

### 2. Implement Function
```python
def validate_new_rule(script: Script) -> List[str]:
    """Validate rule X"""
    errors = []
    # Implementation
    return errors
```

### 3. Run Test
```bash
pytest tests/test_schemas.py::test_new_validation_rule -v
```

### 4. Iterate Until Passing
```bash
# Make changes
# Re-run test
pytest tests/test_schemas.py::test_new_validation_rule -v
```

---

## Test Fixtures

### Common Fixtures

#### `sample_script`
```python
@pytest.fixture
def sample_script():
    """Provide a sample valid script"""
    return Script(scenes=[
        Scene(
            scene_id="S01",
            scene_mission="Test scene",
            key_events=["Event 1"]
        )
    ])
```

#### `sample_tcc`
```python
@pytest.fixture
def sample_tcc():
    """Provide a sample TCC"""
    return TCC(
        tcc_id="TCC_01",
        super_objective="Test objective",
        core_conflict_type="interpersonal",
        evidence_scenes=["S01", "S02"],
        confidence=0.95
    )
```

#### Using Fixtures
```python
def test_with_fixture(sample_script, sample_tcc):
    """Test using fixtures"""
    # Fixtures automatically injected
    assert len(sample_script.scenes) > 0
    assert sample_tcc.confidence == 0.95
```

---

## Mocking LLM Calls

### Why Mock?
- Avoid API costs during development
- Speed up tests
- Ensure deterministic results

### Example Mocking
```python
from unittest.mock import Mock, patch

@patch('src.pipeline.create_llm')
def test_pipeline_with_mock(mock_create_llm):
    """Test pipeline with mocked LLM"""
    # Create mock LLM
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(
        content='{"tccs": [...], "metadata": {...}}'
    )
    mock_create_llm.return_value = mock_llm

    # Run pipeline
    result = run_pipeline(script)

    # Verify LLM was called
    assert mock_llm.invoke.called
```

---

## Coverage

### Generating Coverage Reports
```bash
# Terminal report
pytest tests/ --cov=prompts --cov=src

# HTML report
pytest tests/ --cov=prompts --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Coverage Targets
- **Overall**: 80%+ coverage
- **Core modules**: 90%+ coverage
  - `prompts/schemas.py`
  - `src/pipeline.py`
- **CLI**: 70%+ coverage
  - `src/cli.py`

### Current Coverage (Example)
```
Name                      Stmts   Miss  Cover
---------------------------------------------
prompts/schemas.py          250     12    95%
src/pipeline.py             180     18    90%
src/cli.py                   85     15    82%
---------------------------------------------
TOTAL                       515     45    91%
```

---

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt -r requirements-test.txt
      - run: pytest tests/test_schemas.py -v
      - run: pytest tests/ --cov=prompts --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

---

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -v -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Specific Test
```bash
pytest tests/test_schemas.py::test_tcc_validation -v
```

### Debug with pdb
```python
def test_something():
    import pdb; pdb.set_trace()
    # Test code
```

### Logging in Tests
```python
import logging

def test_with_logging(caplog):
    with caplog.at_level(logging.DEBUG):
        # Test code
        pass
    assert "expected log message" in caplog.text
```

---

## Performance Testing

### Profiling Tests
```bash
# Install profiling tool
pip install pytest-profiling

# Run with profiling
pytest tests/ --profile
```

### Memory Testing
```bash
# Install memory profiler
pip install pytest-memprof memory_profiler

# Run with memory profiling
pytest tests/ --memprof
```

---

## Best Practices

### 1. Test Naming
```python
# Good
def test_tcc_validation_rejects_invalid_id()
def test_spine_score_calculation_with_climax()

# Bad
def test1()
def test_stuff()
```

### 2. Test Organization
```python
class TestTCCValidation:
    """Group related tests"""

    def test_valid_tcc(self):
        pass

    def test_invalid_tcc_id(self):
        pass

    def test_invalid_conflict_type(self):
        pass
```

### 3. Assertions
```python
# Good: Clear, specific assertions
assert tcc.tcc_id == "TCC_01"
assert len(errors) == 2
assert "setup reference" in errors[0]

# Bad: Vague assertions
assert tcc
assert errors
```

### 4. Test Independence
```python
# Good: Each test is independent
def test_a():
    script = Script(...)  # Create own data
    result = validate(script)
    assert result

def test_b():
    script = Script(...)  # Create own data
    result = validate(script)
    assert result

# Bad: Tests depend on each other
shared_state = None

def test_a():
    global shared_state
    shared_state = "value"

def test_b():
    assert shared_state == "value"  # Depends on test_a
```

### 5. Test Data
```python
# Good: Use fixtures or factories
@pytest.fixture
def valid_script():
    return Script(scenes=[...])

# Bad: Hardcoded data in tests
def test_something():
    script = Script(scenes=[Scene(...), Scene(...), ...])
```

---

## Troubleshooting

### Test Fails Only Sometimes
**Cause**: Non-deterministic behavior (e.g., unordered sets)
**Solution**: Sort results before comparing

```python
# Bad
assert tcc_ids == expected_ids

# Good
assert sorted(tcc_ids) == sorted(expected_ids)
```

### Test Timeout
**Cause**: LLM call taking too long
**Solution**: Add timeout or use mock

```python
@pytest.mark.timeout(30)  # 30 second timeout
def test_with_timeout():
    pass
```

### API Key Errors in CI
**Cause**: No API key in CI environment
**Solution**: Mark tests requiring API key

```python
@pytest.mark.skipif(
    os.getenv("DEEPSEEK_API_KEY") is None,
    reason="No API key available"
)
def test_with_api():
    pass
```

---

## References

- pytest docs: https://docs.pytest.org/
- pytest-cov docs: https://pytest-cov.readthedocs.io/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- Test fixtures: https://docs.pytest.org/en/stable/fixture.html
