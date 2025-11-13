# API Reference

## Core Modules

### `src.pipeline`

#### `run_pipeline(script, provider=None, model=None, llm=None)`
Run the complete three-stage analysis pipeline.

**Parameters:**
- `script` (Script): Script object to analyze
- `provider` (str, optional): LLM provider ("deepseek", "anthropic", "openai")
- `model` (str, optional): Model name for the provider
- `llm` (BaseChatModel, optional): Custom LLM instance

**Returns:**
- `dict`: Final state containing all outputs

**Example:**
```python
from prompts.schemas import Script
from src.pipeline import run_pipeline

script = Script(**script_data)
result = run_pipeline(script, provider="deepseek")

print(result["discoverer_output"])
print(result["auditor_output"])
print(result["modifier_output"])
```

---

#### `create_pipeline(provider=None, model=None, llm=None)`
Create a LangGraph pipeline instance.

**Parameters:**
- `provider` (str, optional): LLM provider name
- `model` (str, optional): Model name
- `llm` (BaseChatModel, optional): Custom LLM instance

**Returns:**
- `StateGraph`: Compiled LangGraph pipeline

**Example:**
```python
from src.pipeline import create_pipeline

pipeline = create_pipeline(provider="deepseek", model="deepseek-chat")

initial_state = {
    "script": script,
    "discoverer_output": None,
    "auditor_output": None,
    "modifier_output": None,
    "current_stage": "initialized",
    "errors": [],
    "retry_count": 0,
    "messages": []
}

final_state = pipeline.invoke(initial_state)
```

---

#### `create_llm(provider, model=None, **kwargs)`
Create an LLM instance for the specified provider.

**Parameters:**
- `provider` (str): Provider name ("deepseek", "anthropic", "openai")
- `model` (str, optional): Model name (uses default if not specified)
- `**kwargs`: Additional arguments for the LLM

**Returns:**
- `BaseChatModel`: LLM instance

**Supported Providers & Models:**

| Provider | Default Model | API Key Variable |
|----------|--------------|------------------|
| deepseek | deepseek-chat | DEEPSEEK_API_KEY |
| anthropic | claude-sonnet-4-5 | ANTHROPIC_API_KEY |
| openai | gpt-4-turbo-preview | OPENAI_API_KEY |

**Example:**
```python
from src.pipeline import create_llm

# DeepSeek
llm = create_llm("deepseek")

# Claude with custom model
llm = create_llm("anthropic", model="claude-sonnet-3-5")

# OpenAI with temperature
llm = create_llm("openai", model="gpt-4-turbo", temperature=0.3)
```

---

#### `DiscovererActor(state)`
Stage 1: Identify TCCs from script.

**Parameters:**
- `state` (dict): Pipeline state with "script" key

**Returns:**
- `dict`: Updated state with "discoverer_output"

**Example:**
```python
from src.pipeline import DiscovererActor

state = {"script": script, "messages": []}
result = DiscovererActor(state)
print(result["discoverer_output"].tccs)
```

---

#### `AuditorActor(state)`
Stage 2: Rank TCCs as A/B/C-lines.

**Parameters:**
- `state` (dict): Pipeline state with "script" and "discoverer_output"

**Returns:**
- `dict`: Updated state with "auditor_output"

**Example:**
```python
from src.pipeline import AuditorActor

state = {
    "script": script,
    "discoverer_output": discoverer_result,
    "messages": []
}
result = AuditorActor(state)
print(result["auditor_output"].rankings)
```

---

#### `ModifierActor(state)`
Stage 3: Fix structural issues.

**Parameters:**
- `state` (dict): Pipeline state with "script" and "auditor_output"

**Returns:**
- `dict`: Updated state with "modifier_output"

**Example:**
```python
from src.pipeline import ModifierActor

state = {
    "script": script,
    "auditor_output": auditor_result,
    "messages": []
}
result = ModifierActor(state)
print(result["modifier_output"].modification_log)
```

---

### `src.cli`

#### Command: `analyze`
Analyze a script and output results.

**Usage:**
```bash
python -m src.cli analyze <script_path> [options]
```

**Options:**
- `--output`, `-o`: Output file path
- `--provider`, `-p`: LLM provider (deepseek, anthropic, openai)
- `--model`, `-m`: Model name

**Examples:**
```bash
# Basic analysis
python -m src.cli analyze script.json

# With output file
python -m src.cli analyze script.json --output results.json

# Different provider
python -m src.cli analyze script.json --provider anthropic

# Custom model
python -m src.cli analyze script.json --provider deepseek --model deepseek-chat
```

---

#### Command: `validate`
Validate script structure without LLM analysis.

**Usage:**
```bash
python -m src.cli validate <script_path>
```

**Example:**
```bash
python -m src.cli validate examples/golden/百妖_ep09_s01-s05.json
```

**Checks:**
- JSON schema validity
- Setup-payoff chain integrity
- Scene ID references
- Required fields presence

---

#### Command: `benchmark`
Compare analysis output against expected results.

**Usage:**
```bash
python -m src.cli benchmark <script_path> [options]
```

**Options:**
- `--provider`, `-p`: LLM provider
- `--model`, `-m`: Model name

**Example:**
```bash
python -m src.cli benchmark examples/golden/百妖_ep09_s01-s05.json
```

---

### `prompts.schemas`

#### Data Models

##### `Script`
Represents a screenplay with scenes.

**Fields:**
- `scenes` (List[Scene]): List of scene cards

**Methods:**
- `model_validate(data)`: Validate and parse from dict
- `model_dump()`: Convert to dict
- `model_dump_json()`: Convert to JSON string

**Example:**
```python
from prompts.schemas import Script
import json

with open("script.json") as f:
    script = Script(**json.load(f))

print(f"Total scenes: {len(script.scenes)}")
```

---

##### `Scene`
Represents a single scene card.

**Key Fields:**
- `scene_id` (str): Unique identifier (e.g., "S01")
- `scene_mission` (str, optional): Scene purpose
- `key_events` (List[str]): Important events
- `setup_payoff` (SetupPayoff, optional): Cause-effect data
- `relation_change` (List[RelationChange], optional): Character relationship changes
- `info_change` (List[InfoChange], optional): Information revelation
- `characters` (List[str], optional): Characters present

**Example:**
```python
scene = script.scenes[0]
print(f"Scene: {scene.scene_id}")
print(f"Mission: {scene.scene_mission}")
print(f"Events: {scene.key_events}")
```

---

##### `TCC`
Theatrical Conflict Chain.

**Fields:**
- `tcc_id` (str): Unique ID (pattern: "TCC_\d{2}")
- `super_objective` (str): Character's ultimate goal
- `core_conflict_type` (str): "interpersonal", "internal", or "ideological"
- `evidence_scenes` (List[str]): Scene IDs supporting this TCC
- `confidence` (float): Confidence score (0.0-1.0)

**Example:**
```python
from prompts.schemas import TCC

tcc = TCC(
    tcc_id="TCC_01",
    super_objective="Character wants to achieve goal X",
    core_conflict_type="interpersonal",
    evidence_scenes=["S01", "S05", "S10"],
    confidence=0.95
)
```

---

##### `DiscovererOutput`
Output from Stage 1.

**Fields:**
- `tccs` (List[TCC]): Identified TCCs
- `metadata` (dict): Metadata about analysis

**Example:**
```python
output = discoverer_output
print(f"Found {len(output.tccs)} TCCs")
for tcc in output.tccs:
    print(f"  {tcc.tcc_id}: {tcc.super_objective}")
```

---

##### `AuditorOutput`
Output from Stage 2.

**Fields:**
- `rankings` (Rankings): A/B/C-line classifications
- `metrics` (dict, optional): Coverage metrics

**Example:**
```python
output = auditor_output
a_line = output.rankings.a_line
print(f"A-line: {a_line.super_objective}")
print(f"Spine score: {a_line.spine_score}")
```

---

##### `ModifierOutput`
Output from Stage 3.

**Fields:**
- `modified_script` (Script): Fixed script
- `modification_log` (List[Modification]): Changes made
- `validation` (dict): Validation summary

**Example:**
```python
output = modifier_output
print(f"Fixed {len(output.modification_log)} issues")
for mod in output.modification_log:
    print(f"  {mod.scene_id}.{mod.field}: {mod.change_type}")
```

---

#### Validation Functions

##### `validate_setup_payoff_integrity(script)`
Check setup-payoff chain integrity.

**Parameters:**
- `script` (Script): Script to validate

**Returns:**
- `List[str]`: List of error messages (empty if valid)

**Example:**
```python
from prompts.schemas import validate_setup_payoff_integrity

errors = validate_setup_payoff_integrity(script)
if errors:
    print("Integrity issues:")
    for error in errors:
        print(f"  - {error}")
```

---

##### `validate_tcc_independence(tccs)`
Check for mirror TCCs (duplicate conflicts).

**Parameters:**
- `tccs` (List[TCC]): TCCs to validate

**Returns:**
- `List[str]`: List of warnings

**Example:**
```python
from prompts.schemas import validate_tcc_independence

warnings = validate_tcc_independence(discoverer_output.tccs)
if warnings:
    print("Potential duplicates:")
    for warning in warnings:
        print(f"  - {warning}")
```

---

##### `validate_scene_references(script)`
Check if all scene references are valid.

**Parameters:**
- `script` (Script): Script to validate

**Returns:**
- `List[str]`: List of invalid references

**Example:**
```python
from prompts.schemas import validate_scene_references

errors = validate_scene_references(script)
if errors:
    print("Invalid scene references:")
    for error in errors:
        print(f"  - {error}")
```

---

#### Calculation Functions

##### `calculate_spine_score(scene_count, setup_payoff_density, drives_climax)`
Calculate spine score for A-line ranking.

**Parameters:**
- `scene_count` (int): Number of scenes in TCC
- `setup_payoff_density` (float): Ratio of setup-payoff events (0.0-1.0)
- `drives_climax` (bool): Whether this TCC drives the climax

**Returns:**
- `float`: Spine score

**Formula:**
```
spine_score = (scene_count × 2) + (setup_payoff_density × 1.5) + (10 if drives_climax else 0)
```

**Example:**
```python
from prompts.schemas import calculate_spine_score

score = calculate_spine_score(
    scene_count=15,
    setup_payoff_density=0.80,
    drives_climax=True
)
print(f"Spine score: {score}")  # 41.2
```

---

##### `calculate_heart_score(relation_changes, a_line_interaction, theme_depth)`
Calculate heart score for B-line ranking.

**Parameters:**
- `relation_changes` (int): Number of relationship changes
- `a_line_interaction` (float): Degree of A-line interaction (0.0-1.0)
- `theme_depth` (float): Thematic depth score (0.0-1.0)

**Returns:**
- `float`: Heart score

**Formula:**
```
heart_score = (relation_changes × 1.5) + (a_line_interaction × 2.0) + (theme_depth × 1.0)
```

**Example:**
```python
from prompts.schemas import calculate_heart_score

score = calculate_heart_score(
    relation_changes=8,
    a_line_interaction=0.75,
    theme_depth=0.90
)
print(f"Heart score: {score}")  # 14.4
```

---

##### `calculate_setup_payoff_density(tcc, script)`
Calculate setup-payoff density for a TCC.

**Parameters:**
- `tcc` (TCC): TCC to analyze
- `script` (Script): Full script

**Returns:**
- `float`: Density ratio (0.0-1.0)

**Example:**
```python
from prompts.schemas import calculate_setup_payoff_density

density = calculate_setup_payoff_density(tcc, script)
print(f"Setup-payoff density: {density:.2%}")
```

---

## Type Definitions

### PipelineState
```python
TypedDict('PipelineState', {
    'script': Script,
    'discoverer_output': Optional[DiscovererOutput],
    'auditor_output': Optional[AuditorOutput],
    'modifier_output': Optional[ModifierOutput],
    'current_stage': str,
    'errors': List[str],
    'retry_count': int,
    'messages': List[BaseMessage]
})
```

### ConflictType
```python
Literal["interpersonal", "internal", "ideological"]
```

### LineType
```python
Literal["A", "B", "C"]
```

### ChangeType
```python
Literal["add", "modify", "delete"]
```

---

## Environment Variables

### Required
- `DEEPSEEK_API_KEY`: DeepSeek API key (if using DeepSeek)
- `ANTHROPIC_API_KEY`: Anthropic API key (if using Claude)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)

### Optional
- `LLM_PROVIDER`: Default provider ("deepseek", "anthropic", "openai")
- `DEEPSEEK_BASE_URL`: DeepSeek API base URL
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

---

## Error Handling

### Exception Types

#### `ValidationError`
Raised when Pydantic validation fails.

**Example:**
```python
from pydantic import ValidationError
from prompts.schemas import Script

try:
    script = Script(**invalid_data)
except ValidationError as e:
    print(f"Validation error: {e}")
```

#### `ValueError`
Raised for invalid input parameters.

**Example:**
```python
try:
    llm = create_llm("invalid_provider")
except ValueError as e:
    print(f"Error: {e}")
```

### Retry Behavior

All actor functions automatically retry up to 3 times on failure:
- Retry 1: Wait 2s
- Retry 2: Wait 4s
- Retry 3: Wait 8s
- After 3 failures: Raise exception

**Configure in code:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10)
)
def custom_function():
    pass
```

---

## Performance

### Typical Execution Times (DeepSeek)
- Stage 1 (Discoverer): 3-5 seconds
- Stage 2 (Auditor): 4-6 seconds
- Stage 3 (Modifier): 5-8 seconds
- **Total**: ~12-19 seconds

### Typical Costs (DeepSeek)
- Per script analysis: ~$0.01-0.03 USD
- Per 100 scripts: ~$1-3 USD

### Optimization Tips
```python
# 1. Reuse LLM instance
llm = create_llm("deepseek")
pipeline = create_pipeline(llm=llm)

# 2. Batch processing
results = [run_pipeline(script, llm=llm) for script in scripts]

# 3. Use faster model for simple tasks
llm = create_llm("deepseek", model="deepseek-chat")
```

---

## Testing

### Run Unit Tests
```bash
pytest tests/test_schemas.py -v
```

### Run Integration Tests
```bash
pytest tests/test_golden_dataset.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=prompts --cov=src --cov-report=html
```

### Skip LLM Tests
```bash
pytest tests/ -m "not llm"
```

---

## Versioning

### Current Version
2.1.0 (2025-11-12)

### Version History
- **2.1.0**: Enhanced prompts, utility functions, comprehensive testing
- **2.0.0**: Engineering refactor, Pydantic schemas, LangGraph pipeline
- **1.0.0**: Initial prototype with basic prompts

### Compatibility
- Python: 3.8+
- LangChain: 0.1.0+
- LangGraph: 0.0.40+
- Pydantic: 2.0.0+

---

## References

### External Documentation
- LangChain: https://python.langchain.com/docs/
- LangGraph: https://langchain-ai.github.io/langgraph/
- Pydantic: https://docs.pydantic.dev/
- DeepSeek API: https://platform.deepseek.com/docs

### Internal Documentation
- Main README: `README.md`
- Usage Guide: `USAGE.md`
- Prompt Guide: `prompts/README.md`
- Architecture: `ref/architecture.md`
