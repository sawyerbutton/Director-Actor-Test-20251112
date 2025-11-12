# Engineered Prompts for Script Analysis System

## Overview
This directory contains **engineering-optimized** prompts for the three-stage script analysis pipeline. Unlike the original prompts (Step1/2/3-prompt.md), these prompts are designed for:

- ✅ **Programmatic usage**: Structured inputs/outputs with JSON schemas
- ✅ **Testability**: Clear validation rules and edge case handling
- ✅ **Maintainability**: Modular, version-controlled, with examples
- ✅ **Reliability**: Explicit error handling and fallback strategies

## Directory Structure

```
prompts/
├── README.md                    # This file
├── stage1_discoverer.md         # Stage 1: TCC Identification
├── stage2_auditor.md            # Stage 2: TCC Ranking & Analysis
├── stage3_modifier.md           # Stage 3: Structural Correction
└── schemas.py                   # Pydantic schemas for validation
```

## Prompt Design Principles

### 1. Separation of Concerns
- **Prompt**: Contains instructions, rules, and examples
- **Schema**: Enforces data structure and validation
- **Data**: Passed separately (not embedded in prompt)

### 2. Structured Outputs
All outputs are **valid JSON** that can be parsed and validated:
```python
from schemas import DiscovererOutput
import json

# Parse LLM output
output = DiscovererOutput.model_validate_json(llm_response)

# Now you have type-safe access
for tcc in output.tccs:
    print(f"{tcc.tcc_id}: {tcc.super_objective}")
```

### 3. Explicit Edge Cases
Each prompt includes a dedicated section for edge cases:
- Insufficient data
- Ambiguous results
- Conflicting information
- Invalid inputs

### 4. Quantitative Criteria
Where possible, use numbers instead of subjective judgments:
- ❌ "The most important conflict"
- ✅ "The TCC with the highest spine_score (scene_count × 2 + setup_payoff_density × 1.5)"

## Stage-by-Stage Guide

### Stage 1: Discoverer (`stage1_discoverer.md`)

**Purpose**: Identify all independent TCCs from script data

**Key Features**:
- **Anti-mirror pattern**: Prevents identifying the same conflict twice
- **Fallback strategy**: Works even when `setup_payoff` data is missing
- **Confidence scoring**: Each TCC gets a confidence score (0.0-1.0)

**Usage**:
```python
from langchain_anthropic import ChatAnthropic
from schemas import Script, DiscovererOutput

# Load prompt
with open("prompts/stage1_discoverer.md") as f:
    prompt_template = f.read()

# Load script data
script = Script.model_validate(script_json)

# Call LLM
llm = ChatAnthropic(model="claude-sonnet-4-5")
response = llm.invoke([
    {"role": "system", "content": prompt_template},
    {"role": "user", "content": script.model_dump_json()}
])

# Validate output
output = DiscovererOutput.model_validate_json(response.content)
```

**Output Example**:
```json
{
  "tccs": [
    {
      "tcc_id": "TCC_01",
      "super_objective": "玉鼠精's e-commerce funding plan",
      "core_conflict_type": "interpersonal",
      "evidence_scenes": ["S03", "S05", "S10", "S12"],
      "confidence": 0.95
    }
  ],
  "metadata": {
    "total_scenes_analyzed": 50,
    "primary_evidence_available": true,
    "fallback_mode": false
  }
}
```

### Stage 2: Auditor (`stage2_auditor.md`)

**Purpose**: Rank TCCs as A/B/C-line and analyze force dynamics

**Key Features**:
- **Quantitative scoring**: Spine/heart/flavor scores with formulas
- **Force analysis**: Identifies protagonist/antagonist forces
- **Coverage metrics**: Tracks what % of scenes each TCC covers

**Usage**:
```python
from schemas import AuditorOutput

# Load prompt
with open("prompts/stage2_auditor.md") as f:
    prompt_template = f.read()

# Prepare input (script + TCCs from stage 1)
input_data = {
    "script": script.model_dump(),
    "tccs": discoverer_output.tccs
}

# Call LLM
response = llm.invoke([
    {"role": "system", "content": prompt_template},
    {"role": "user", "content": json.dumps(input_data)}
])

# Validate output
output = AuditorOutput.model_validate_json(response.content)
```

**Output Example**:
```json
{
  "rankings": {
    "a_line": {
      "tcc_id": "TCC_01",
      "super_objective": "玉鼠精's e-commerce funding plan",
      "spine_score": 22.5,
      "reasoning": {
        "scene_count": 15,
        "setup_payoff_density": 0.80,
        "drives_climax": true
      },
      "forces": {
        "protagonist": "玉鼠精's business ambition",
        "primary_antagonist": "悟空's investigation",
        "dynamic_antagonist": ["哪吒's betrayal", "神秘仓库 exposure"]
      }
    },
    "b_lines": [...],
    "c_lines": [...]
  },
  "metrics": {
    "total_scenes": 50,
    "a_line_coverage": 0.30,
    "b_line_coverage": 0.18,
    "c_line_coverage": 0.12
  }
}
```

### Stage 3: Modifier (`stage3_modifier.md`)

**Purpose**: Fix structural issues identified in audit report

**Key Features**:
- **Surgical fixes**: Minimal modifications, no creative additions
- **Modification log**: Tracks every change made
- **Validation**: Ensures no new issues introduced

**Usage**:
```python
from schemas import ModifierOutput, AuditReport

# Load prompt
with open("prompts/stage3_modifier.md") as f:
    prompt_template = f.read()

# Prepare input (script + audit report)
audit_report = AuditReport(issues=[...])
input_data = {
    "script": script.model_dump(),
    "audit_report": audit_report.model_dump()
}

# Call LLM
response = llm.invoke([
    {"role": "system", "content": prompt_template},
    {"role": "user", "content": json.dumps(input_data)}
])

# Validate output
output = ModifierOutput.model_validate_json(response.content)
```

**Output Example**:
```json
{
  "modified_script": {
    "scenes": [...]
  },
  "modification_log": [
    {
      "issue_id": "ISS_001",
      "applied": true,
      "scene_id": "S20",
      "field": "setup_payoff.payoff_from",
      "change_type": "add",
      "old_value": [],
      "new_value": ["S10"]
    }
  ],
  "validation": {
    "total_issues": 15,
    "fixed": 14,
    "skipped": 1,
    "new_issues_introduced": 0
  }
}
```

## Validation Pipeline

### 1. Schema Validation (Pydantic)
```python
from schemas import DiscovererOutput

try:
    output = DiscovererOutput.model_validate_json(llm_response)
    print("✅ Schema valid")
except ValidationError as e:
    print(f"❌ Schema invalid: {e}")
```

### 2. Business Logic Validation
```python
from schemas import validate_setup_payoff_integrity

# Check setup-payoff chain integrity
errors = validate_setup_payoff_integrity(script)
if errors:
    print(f"❌ Integrity issues: {errors}")
else:
    print("✅ Setup-payoff chains intact")
```

### 3. Output Quality Checks
```python
# Check Stage 1 output
assert len(output.tccs) >= 1, "Must identify at least 1 TCC"
assert all(tcc.confidence > 0.5 for tcc in output.tccs), "Low confidence TCCs"

# Check Stage 2 output
assert output.rankings.a_line is not None, "Must have exactly 1 A-line"
assert len(output.rankings.b_lines) <= 2, "Too many B-lines"
```

## Error Handling

### Retry Strategy
If LLM output is invalid:
1. **Parse error**: Retry with clearer format instructions (max 3 times)
2. **Validation error**: Include validation error in retry prompt
3. **Persistent failure**: Log error and request human review

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def call_discoverer(script: Script) -> DiscovererOutput:
    response = llm.invoke(...)
    return DiscovererOutput.model_validate_json(response.content)
```

### Fallback Modes
Each stage has degraded-but-functional fallback modes:
- **Stage 1**: If `setup_payoff` missing, use `scene_mission` + `key_events`
- **Stage 2**: If can't rank B/C-lines, return only A-line
- **Stage 3**: If fix fails, log and continue with next fix

## Testing

### Unit Tests for Schemas
```bash
python prompts/schemas.py
```

### Integration Tests for Prompts
```python
import pytest
from schemas import *

def test_discoverer_with_complete_data():
    script = Script(scenes=[...])  # Full data
    output = call_discoverer_actor(script)
    assert len(output.tccs) >= 1
    assert output.metadata.fallback_mode == False

def test_discoverer_with_missing_setup_payoff():
    script = Script(scenes=[...])  # Missing setup_payoff
    output = call_discoverer_actor(script)
    assert output.metadata.fallback_mode == True
    assert len(output.tccs) >= 1  # Still works!
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0-Engineering | 2025-11-12 | Initial engineered prompts with schemas |
| 1.0-Original | 2025-11-XX | Original non-technical prompts |

## Migration Guide

### From Original Prompts to Engineered Prompts

**Before** (Step1-prompt.md):
- Mixed instructions with data
- Subjective evaluation criteria
- Text-based output
- No validation

**After** (stage1_discoverer.md):
- Separated instructions from data
- Quantitative criteria with formulas
- Structured JSON output
- Pydantic validation

**Migration Checklist**:
- [ ] Replace prompt file paths
- [ ] Add Pydantic schema validation
- [ ] Implement retry logic
- [ ] Add unit tests
- [ ] Update documentation

## Best Practices

### 1. Always Validate
```python
# ❌ Don't use raw LLM output
result = json.loads(llm_response)

# ✅ Always validate with schema
result = DiscovererOutput.model_validate_json(llm_response)
```

### 2. Log Everything
```python
import logging

logging.info(f"Stage 1 input: {len(script.scenes)} scenes")
logging.info(f"Stage 1 output: {len(output.tccs)} TCCs identified")
logging.info(f"Fallback mode: {output.metadata.fallback_mode}")
```

### 3. Monitor Confidence Scores
```python
low_confidence_tccs = [
    tcc for tcc in output.tccs
    if tcc.confidence < 0.7
]
if low_confidence_tccs:
    logging.warning(f"Low confidence TCCs: {low_confidence_tccs}")
```

### 4. Track Metrics
```python
metrics = {
    "stage1_tcc_count": len(output.tccs),
    "stage1_confidence_avg": sum(t.confidence for t in output.tccs) / len(output.tccs),
    "stage2_a_line_coverage": auditor_output.metrics.a_line_coverage,
    "stage3_fix_rate": modifier_output.validation.fixed / modifier_output.validation.total_issues
}
```

## FAQ

**Q: Why not use the original prompts?**
A: Original prompts are great for human understanding but lack structure needed for engineering (validation, testing, error handling).

**Q: Can I modify the prompts?**
A: Yes! Just ensure:
- Output schema remains compatible
- Version number is updated
- Unit tests pass

**Q: What if LLM output doesn't match schema?**
A: The system will retry with validation errors included in the prompt. After 3 failures, it logs for human review.

**Q: How do I add a new stage?**
A:
1. Create `stageN_name.md` with prompt
2. Define schemas in `schemas.py`
3. Add validation functions
4. Write unit tests
5. Update this README

## Support

- **Documentation**: See main README.md
- **Issues**: Create issue in GitHub repo
- **Examples**: See `examples/` directory

---
**Maintained by**: AI Engineering Team
**Last Updated**: 2025-11-12
