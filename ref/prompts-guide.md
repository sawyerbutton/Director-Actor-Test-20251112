# Prompts Guide

## Overview

This guide covers the engineered prompt system, including design principles, usage patterns, and customization strategies.

## Prompt Architecture

### Two Versions

#### 1. Original Prompts (Business-Oriented)
**Location**: Root directory
- `Step1-prompt.md` - Discoverer (original)
- `Step2-prompt.md` - Auditor (original)
- `Step3-prompt.md` - Modifier (original)

**Characteristics**:
- Written for human understanding
- Detailed narrative theory explanations
- Rich business context
- Mixed text and JSON output
- Difficult to validate programmatically

**Use Cases**:
- Understanding business requirements
- Discussing with non-technical stakeholders
- Learning narrative theory concepts

#### 2. Engineered Prompts (Production-Ready)
**Location**: `prompts/` directory
- `stage1_discoverer.md` - Stage 1 (engineered)
- `stage2_auditor.md` - Stage 2 (engineered)
- `stage3_modifier.md` - Stage 3 (engineered)
- `schemas.py` - Pydantic validation schemas

**Characteristics**:
- Structured JSON input/output
- Pydantic schema validation
- Quantitative evaluation criteria
- Explicit edge case handling
- Testable and maintainable

**Use Cases**:
- Production deployment
- Automated testing
- Integration with other systems
- API development

---

## Stage 1: Discoverer

### Purpose
Identify all independent Theatrical Conflict Chains (TCCs) from script data.

### Key Concepts

#### What is a TCC?
A **Theatrical Conflict Chain** is an independent narrative thread with:
- **Super Objective**: Character's ultimate goal
- **Protagonist Force**: What drives the story forward
- **Antagonist Force**: What opposes the goal
- **Evidence**: Specific scenes supporting this conflict

#### Example TCC
```json
{
  "tcc_id": "TCC_01",
  "super_objective": "Character A wants to achieve business success",
  "core_conflict_type": "interpersonal",
  "evidence_scenes": ["S03", "S05", "S10", "S12"],
  "confidence": 0.95
}
```

### Core Logic

#### Evidence Priority
1. **Primary Evidence** (most reliable):
   - `setup_payoff` chains
   - `relation_change` patterns

2. **Secondary Evidence** (fallback):
   - `scene_mission` descriptions
   - `key_events` content
   - `characters` presence

#### Anti-Mirror Pattern
**Problem**: LLM might identify the same conflict twice
- "Character A wants X" (protagonist view)
- "Character B opposes X" (antagonist view)

**Solution**: Check for mirror patterns
- Same scenes (>60% overlap)
- Complementary objectives
- Mark lower-confidence TCC as mirror

**Example**:
```python
# Potential mirror TCCs
TCC_01: "玉鼠精 wants funding" (scenes: S03, S05, S10)
TCC_02: "悟空 investigates fraud" (scenes: S03, S05, S10)

# Detection: 100% scene overlap, complementary goals
# Action: Merge or keep only TCC_01
```

### Prompt Structure

```markdown
# Stage 1: TCC Discovery

## Task
Identify all independent TCCs from the provided script.

## Input Format
[JSON schema for Script]

## Output Format
[JSON schema for DiscovererOutput]

## Analysis Steps
1. Scan all scenes
2. Identify super objectives
3. Group related scenes
4. Check for mirrors
5. Assign confidence scores

## Edge Cases
- Missing setup_payoff → use fallback
- Insufficient data → lower confidence
- Ambiguous conflicts → mark with reasoning

## Examples
[Concrete examples with expected outputs]
```

### Usage

```python
from langchain_anthropic import ChatAnthropic
from prompts.schemas import Script, DiscovererOutput

# Load prompt
with open("prompts/stage1_discoverer.md") as f:
    prompt = f.read()

# Prepare input
script = Script(**script_data)
input_text = script.model_dump_json(indent=2)

# Call LLM
llm = ChatAnthropic(model="claude-sonnet-4-5")
response = llm.invoke([
    {"role": "system", "content": prompt},
    {"role": "user", "content": input_text}
])

# Validate output
output = DiscovererOutput.model_validate_json(response.content)
```

---

## Stage 2: Auditor

### Purpose
Rank TCCs by dramatic importance as A/B/C-lines.

### Line Classifications

#### A-Line (Spine)
The main plot - without it, the story doesn't exist.

**Criteria**:
- Highest stakes (failure = story ends)
- Most scenes (highest coverage)
- Drives climax (it IS the climax)

**Quantitative Score**:
```python
spine_score = (scene_count × 2) + (setup_payoff_density × 1.5) + (10 if drives_climax else 0)
```

**Example**:
```
A-Line: 玉鼠精's e-commerce funding plan
- Scenes: 15 (30 points)
- Setup-payoff density: 0.80 (1.2 points)
- Drives climax: Yes (10 points)
- Total spine_score: 41.2
```

#### B-Lines (Heart)
Subplots that provide emotional depth and must interact with A-line.

**Criteria**:
- Emotional core (internal conflicts)
- Affects A-line (crossover required)
- Character development

**Quantitative Score**:
```python
heart_score = (relation_changes × 1.5) + (a_line_interaction × 2.0) + (theme_depth × 1.0)
```

**Example**:
```
B-Line: 悟空's self-identity struggle
- Relation changes: 8 (12 points)
- A-line interaction: 0.75 (1.5 points)
- Theme depth: 0.90 (0.9 points)
- Total heart_score: 14.4
```

#### C-Lines (Flavor)
Minor threads that add richness but are removable.

**Criteria**:
- Theme reflection (mirrors A/B-lines)
- Removable (story works without it)
- Limited coverage

**Example**:
```
C-Line: 哪吒's workplace politics
- Scenes: 5
- Independent story
- Adds flavor but not essential
```

### Force Analysis

For each line, identify:
- **Protagonist Force**: What drives it forward
- **Primary Antagonist**: Main opposing force
- **Dynamic Antagonist**: Evolving obstacles

**Example**:
```json
{
  "forces": {
    "protagonist": "玉鼠精's business ambition",
    "primary_antagonist": "悟空's investigation",
    "dynamic_antagonist": [
      "哪吒's betrayal",
      "神秘仓库 exposure"
    ]
  }
}
```

### Prompt Structure

```markdown
# Stage 2: TCC Ranking

## Task
Rank TCCs as A/B/C-lines based on dramatic importance.

## Input Format
- Script JSON
- TCC list from Stage 1

## Output Format
[JSON schema for AuditorOutput]

## Ranking Criteria
### A-Line (exactly 1)
- Formula: spine_score = ...
- Must drive climax

### B-Lines (0-2)
- Formula: heart_score = ...
- Must interact with A-line

### C-Lines (0-N)
- Flavor, removable
- Limited coverage

## Examples
[Concrete ranking examples]
```

---

## Stage 3: Modifier

### Purpose
Fix structural issues identified in audit report.

### Modification Types

#### 1. Add Missing Setup-Payoff
**Issue**: Scene S20 lacks setup reference
**Fix**: Add `"S10"` to `setup_payoff.payoff_from`

```json
{
  "scene_id": "S20",
  "setup_payoff": {
    "payoff_from": ["S10"]  // Added
  }
}
```

#### 2. Complete Key Events
**Issue**: Scene S15 missing critical event
**Fix**: Add event to `key_events` list

```json
{
  "scene_id": "S15",
  "key_events": [
    "Character A discovers truth"  // Added
  ]
}
```

#### 3. Repair Relation Changes
**Issue**: Character relationship change not recorded
**Fix**: Add entry to `relation_change`

```json
{
  "scene_id": "S18",
  "relation_change": [
    {
      "characters": ["A", "B"],
      "before": "allies",
      "after": "enemies",
      "cause": "betrayal revealed"
    }  // Added
  ]
}
```

### Modification Principles

#### 1. Surgical Fixes Only
- ✅ Fix identified issues
- ❌ Don't add creative content
- ❌ Don't change core plot

#### 2. Minimal Changes
- Change smallest unit possible
- Preserve existing structure
- Document all changes

#### 3. Validation
- Check no new issues introduced
- Verify JSON integrity
- Ensure setup-payoff chains valid

### Modification Log

Every change is logged:
```json
{
  "issue_id": "ISS_001",
  "applied": true,
  "scene_id": "S20",
  "field": "setup_payoff.payoff_from",
  "change_type": "add",
  "old_value": [],
  "new_value": ["S10"],
  "reasoning": "Missing setup reference for character revelation"
}
```

---

## Prompt Engineering Best Practices

### 1. Clear Structure
```markdown
# Task Definition
[What needs to be done]

# Input Format
[Exact schema]

# Output Format
[Exact schema with examples]

# Step-by-Step Process
[Explicit algorithm]

# Edge Cases
[How to handle problems]

# Examples
[Concrete examples]
```

### 2. Quantitative Criteria
```markdown
# Bad
"Choose the most important conflict"

# Good
"Calculate spine_score for each TCC using:
spine_score = (scene_count × 2) + (setup_payoff_density × 1.5) + (10 if drives_climax else 0)
Select the TCC with highest spine_score as A-line"
```

### 3. Explicit Edge Cases
```markdown
## Edge Case: Missing Setup-Payoff Data

**Condition**: `setup_payoff` field is null/empty for >50% of scenes

**Action**:
1. Set `fallback_mode = true` in metadata
2. Use secondary evidence (scene_mission, key_events)
3. Lower confidence scores by 0.2

**Example**:
[Show concrete example]
```

### 4. Examples with Context
```markdown
## Example 1: Single-Line Script

**Input**:
```json
{
  "scenes": [
    {"scene_id": "S01", "scene_mission": "Introduce hero", ...},
    {"scene_id": "S02", "scene_mission": "Hero faces challenge", ...}
  ]
}
```

**Expected Output**:
```json
{
  "tccs": [
    {
      "tcc_id": "TCC_01",
      "super_objective": "Hero wants to overcome challenge",
      ...
    }
  ]
}
```

**Reasoning**: Only one conflict thread detected.
```

---

## Customizing Prompts

### Adding New Criteria

#### 1. Define in Prompt
```markdown
## New Criterion: Character Arc Depth

**Definition**: Measure how much characters change

**Calculation**:
arc_depth = relation_changes + internal_conflicts

**Usage**: Factor into B-line heart_score
```

#### 2. Update Schema
```python
class LineRanking(BaseModel):
    arc_depth: float = Field(ge=0.0)  # Add new field
```

#### 3. Update Calculation
```python
def calculate_heart_score(
    relation_changes: int,
    a_line_interaction: float,
    theme_depth: float,
    arc_depth: float  # New parameter
) -> float:
    return (
        (relation_changes * 1.5) +
        (a_line_interaction * 2.0) +
        (theme_depth * 1.0) +
        (arc_depth * 0.5)  # New factor
    )
```

#### 4. Test
```python
def test_heart_score_with_arc_depth():
    score = calculate_heart_score(
        relation_changes=8,
        a_line_interaction=0.75,
        theme_depth=0.90,
        arc_depth=5.0
    )
    assert score == 16.9  # 12 + 1.5 + 0.9 + 2.5
```

### Adding New Stage

#### 1. Create Prompt File
```markdown
# prompts/stage4_analyzer.md

# Stage 4: Theme Analysis

## Task
Identify thematic elements in the script.

## Input Format
- Script JSON
- Previous stage outputs

## Output Format
{
  "themes": [...],
  "evidence": [...]
}
```

#### 2. Define Schema
```python
# prompts/schemas.py

class Theme(BaseModel):
    theme_id: str
    description: str
    evidence_scenes: List[str]

class AnalyzerOutput(BaseModel):
    themes: List[Theme]
    metadata: dict
```

#### 3. Add Actor Node
```python
# src/pipeline.py

def AnalyzerActor(state: PipelineState) -> PipelineState:
    """Stage 4: Analyze themes"""
    with open("prompts/stage4_analyzer.md") as f:
        prompt = f.read()

    # ... implementation
    return state
```

#### 4. Update Pipeline
```python
pipeline.add_node("analyzer", AnalyzerActor)
pipeline.add_edge("modifier", "analyzer")
```

---

## Testing Prompts

### Unit Test Approach
```python
def test_stage1_with_complete_data():
    """Test Stage 1 with complete script data"""
    script = load_golden_script("complete.json")

    output = DiscovererActor({"script": script})

    assert len(output["discoverer_output"].tccs) >= 1
    assert output["discoverer_output"].metadata["fallback_mode"] == False
```

### Integration Test Approach
```python
@pytest.mark.llm
def test_full_pipeline():
    """Test all stages together"""
    script = load_golden_script("complete.json")

    final_state = run_pipeline(script)

    # Stage 1
    assert final_state["discoverer_output"] is not None

    # Stage 2
    assert final_state["auditor_output"].rankings.a_line is not None

    # Stage 3
    assert len(final_state["modifier_output"].modification_log) >= 0
```

### Golden Dataset Testing
```python
def test_against_golden_output():
    """Compare against expected output"""
    script = load_golden_script("complete.json")
    expected = load_golden_expected("complete_expected.json")

    final_state = run_pipeline(script)

    # Compare TCC IDs
    actual_ids = {t.tcc_id for t in final_state["discoverer_output"].tccs}
    expected_ids = set(expected["tcc_ids"])
    assert actual_ids == expected_ids
```

---

## Prompt Versioning

### Version Naming
```
v<major>.<minor>-<label>

Examples:
- v1.0-Original
- v2.0-Engineering
- v2.1-Refactored
```

### Changelog
```markdown
## prompts/stage1_discoverer.md

### Version 2.1-Refactored (2025-11-12)
- Added detailed mirror TCC detection patterns
- Improved fallback strategy documentation
- Added 5 concrete examples

### Version 2.0-Engineering (2025-11-11)
- Restructured for JSON I/O
- Added Pydantic schema validation
- Quantified evaluation criteria
```

### Migration Guide
```markdown
## Migrating from v2.0 to v2.1

### Changes
1. New field: `metadata.fallback_mode`
2. Enhanced mirror detection logic
3. Updated confidence scoring

### Action Required
- Update schema: Add `fallback_mode` field
- Review mirror detection logic
- Re-run tests with new version

### Backward Compatibility
- v2.1 outputs are compatible with v2.0 parsers
- Only `metadata` field additions (optional)
```

---

## Troubleshooting

### Issue: LLM Doesn't Follow Output Format

**Symptoms**: ValidationError when parsing output

**Solutions**:
1. Add more examples to prompt
2. Make format section more prominent
3. Include validation error in retry prompt

```python
try:
    output = DiscovererOutput.model_validate_json(response.content)
except ValidationError as e:
    # Retry with error message
    retry_prompt = f"""
Previous output had validation errors:
{e}

Please fix and return valid JSON matching the schema.
"""
```

### Issue: Low Confidence Scores

**Symptoms**: All TCCs have confidence < 0.7

**Diagnosis**: Likely using fallback mode (missing primary evidence)

**Solutions**:
1. Check `metadata.fallback_mode` flag
2. Review input data quality
3. Enhance setup_payoff data if possible

### Issue: Mirror TCCs Not Detected

**Symptoms**: Multiple TCCs with same scenes

**Solutions**:
1. Lower scene overlap threshold (60% → 50%)
2. Add more mirror pattern examples
3. Improve super_objective comparison logic

---

## References

### Internal Docs
- `prompts/README.md` - Detailed prompt documentation
- `ref/architecture.md` - System architecture
- `ref/testing.md` - Testing strategies

### Prompt Files
- `prompts/stage1_discoverer.md` - Stage 1 prompt
- `prompts/stage2_auditor.md` - Stage 2 prompt
- `prompts/stage3_modifier.md` - Stage 3 prompt
- `prompts/schemas.py` - Pydantic schemas

### External Resources
- Anthropic Prompt Engineering: https://docs.anthropic.com/claude/docs/prompt-engineering
- LangChain Prompts: https://python.langchain.com/docs/modules/model_io/prompts/
- Pydantic Validation: https://docs.pydantic.dev/latest/concepts/validation/
