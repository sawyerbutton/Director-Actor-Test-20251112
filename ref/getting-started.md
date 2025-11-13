# Getting Started

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
```bash
# Copy example configuration
cp .env.example .env

# Edit .env and add your DeepSeek API key
# Get it from: https://platform.deepseek.com/
nano .env
```

Add to `.env`:
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. Run Example Analysis
```bash
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json
```

You should see output like:
```
✅ Stage 1 complete: 3 TCCs identified
✅ Stage 2 complete: Ranked as 1 A-line, 2 B-lines
✅ Stage 3 complete: 12 issues fixed
📊 Analysis complete!
```

## Installation Options

### Option 1: Core Only (Recommended)
```bash
pip install -r requirements.txt
```

This includes:
- langchain
- langchain-openai (for DeepSeek)
- langgraph
- pydantic
- python-dotenv
- tenacity

### Option 2: With Testing Tools
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

Adds:
- pytest
- pytest-cov (coverage)
- pytest-mock

### Option 3: Development Mode
```bash
# Install in editable mode
pip install -e .

# Install all dependencies
pip install -r requirements.txt -r requirements-test.txt
```

## API Key Setup

### DeepSeek (Default, Recommended)
1. Visit: https://platform.deepseek.com/
2. Sign up and get API key
3. Add to `.env`:
```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

**Cost**: ~$0.14 per 1M input tokens, $0.28 per 1M output tokens

### Anthropic Claude (Optional)
1. Visit: https://console.anthropic.com/
2. Get API key
3. Add to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Cost**: ~$3 per 1M input tokens, $15 per 1M output tokens

### OpenAI (Optional)
1. Visit: https://platform.openai.com/
2. Get API key
3. Add to `.env`:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

**Cost**: Variable by model

## Basic Usage

### Python API
```python
from prompts.schemas import Script
from src.pipeline import run_pipeline
import json

# Load your script
with open("examples/golden/百妖_ep09_s01-s05.json") as f:
    script_data = json.load(f)
script = Script(**script_data)

# Run analysis (uses DeepSeek by default)
final_state = run_pipeline(script)

# Access results
discoverer_output = final_state["discoverer_output"]
auditor_output = final_state["auditor_output"]
modifier_output = final_state["modifier_output"]

print(f"Found {len(discoverer_output.tccs)} TCCs")
print(f"A-line: {auditor_output.rankings.a_line.super_objective}")
print(f"Fixed {len(modifier_output.modification_log)} issues")
```

### Command Line
```bash
# Analyze a script
python -m src.cli analyze path/to/script.json

# Save results to file
python -m src.cli analyze script.json --output results.json

# Use different LLM provider
python -m src.cli analyze script.json --provider anthropic

# Validate script structure
python -m src.cli validate script.json

# Run benchmark
python -m src.cli benchmark script.json
```

## Configuration

### Environment Variables
Create `.env` file with:
```bash
# LLM Provider (default: deepseek)
LLM_PROVIDER=deepseek

# API Keys (set the one you'll use)
DEEPSEEK_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# DeepSeek Configuration
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Logging
LOG_LEVEL=INFO
```

### Provider Selection Priority
1. CLI argument: `--provider deepseek`
2. Function parameter: `run_pipeline(script, provider="deepseek")`
3. Environment variable: `LLM_PROVIDER=deepseek`
4. Default: `deepseek`

## Running Tests

### Quick Test
```bash
./run_tests.sh
```

### Specific Tests
```bash
# Schema tests only
./run_tests.sh schemas

# Golden dataset tests
./run_tests.sh golden

# All tests with coverage
pytest tests/ --cov=prompts --cov=src --cov-report=html
```

### Skip LLM Tests (Save API costs)
```bash
pytest tests/ -m "not llm"
```

## Project Structure Tour

```
.
├── README.md              # Main documentation (Chinese)
├── USAGE.md              # Detailed usage guide
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
│
├── src/                 # Core implementation
│   ├── pipeline.py      # LangGraph pipeline
│   └── cli.py          # Command-line interface
│
├── prompts/            # LLM prompts + schemas
│   ├── stage1_discoverer.md
│   ├── stage2_auditor.md
│   ├── stage3_modifier.md
│   ├── schemas.py      # Pydantic models
│   └── README.md       # Prompt documentation
│
├── tests/              # Test suites
│   ├── test_schemas.py
│   └── test_golden_dataset.py
│
├── benchmarks/         # Performance tests
│   └── run_benchmark.py
│
└── examples/           # Sample data
    └── golden/         # Test datasets
```

## Common Workflows

### Workflow 1: Analyze a New Script
```bash
# 1. Prepare your script JSON
# (See examples/golden/*.json for format)

# 2. Validate structure first
python -m src.cli validate my_script.json

# 3. Run analysis
python -m src.cli analyze my_script.json --output results.json

# 4. Review results
cat results.json | jq .
```

### Workflow 2: Batch Processing
```python
from src.pipeline import run_pipeline
from prompts.schemas import Script
import json
from pathlib import Path

script_dir = Path("scripts/")
results = []

for script_file in script_dir.glob("*.json"):
    with open(script_file) as f:
        script = Script(**json.load(f))

    final_state = run_pipeline(script)
    results.append({
        "file": script_file.name,
        "tccs": len(final_state["discoverer_output"].tccs),
        "a_line": final_state["auditor_output"].rankings.a_line.super_objective
    })

# Save batch results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

### Workflow 3: Custom Provider
```python
from langchain_anthropic import ChatAnthropic
from src.pipeline import create_pipeline

# Create custom LLM
llm = ChatAnthropic(
    model="claude-sonnet-4-5",
    temperature=0,
    max_tokens=4096
)

# Create pipeline with custom LLM
pipeline = create_pipeline(llm=llm)

# Run
final_state = pipeline.invoke({
    "script": your_script,
    "discoverer_output": None,
    "auditor_output": None,
    "modifier_output": None,
    "current_stage": "initialized",
    "errors": [],
    "retry_count": 0,
    "messages": []
})
```

## Next Steps

### Learn the Concepts
1. Read: `README.md` - Understand TCCs, A/B/C-lines
2. Read: `prompts/README.md` - Understand prompt engineering
3. Read: `USAGE.md` - Detailed API reference

### Explore Examples
```bash
# List example scripts
ls -lh examples/golden/

# View example structure
cat examples/golden/百妖_ep09_s01-s05.json | jq .

# Run example analysis
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json
```

### Customize for Your Needs
1. Modify prompts in `prompts/` directory
2. Add custom validation rules in `prompts/schemas.py`
3. Extend pipeline in `src/pipeline.py`

### Run Benchmarks
```bash
# Performance benchmark
python benchmarks/run_benchmark.py examples/golden

# Multiple runs for consistency
python benchmarks/run_benchmark.py examples/golden 5
```

## Troubleshooting

### Issue: Module not found
```bash
# Make sure you're in project root
cd /path/to/Director-Actor-Test-20251112

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API key error
```bash
# Check .env file exists
ls -la .env

# Check API key is set
grep DEEPSEEK_API_KEY .env

# Test API connection
python -c "from src.pipeline import create_llm; llm = create_llm('deepseek'); print('✅ Connection OK')"
```

### Issue: Validation errors
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run analysis
final_state = run_pipeline(script)
```

### Issue: Slow execution
```bash
# Use faster provider
python -m src.cli analyze script.json --provider deepseek

# Or skip validation (not recommended)
# Edit pytest.ini to reduce test time
```

## Getting Help

### Documentation
- Main README: `README.md`
- Usage guide: `USAGE.md`
- Prompt guide: `prompts/README.md`
- Reference docs: `ref/` directory

### Examples
- Sample scripts: `examples/golden/`
- Test cases: `tests/`
- Benchmark scripts: `benchmarks/`

### Common Issues
See `USAGE.md` → Troubleshooting section

### Project Resources
- Repository: Check git remote for URL
- Issues: Report bugs in GitHub issues
- Version: Check `README.md` for current version

## Development Setup

### For Contributors
```bash
# Clone repository
git clone <repo-url>
cd Director-Actor-Test-20251112

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt -r requirements-test.txt

# Run tests
./run_tests.sh

# Make changes and test
pytest tests/ -v

# Check coverage
pytest tests/ --cov=prompts --cov=src --cov-report=html
open htmlcov/index.html
```

### Code Quality
```bash
# Format code (if you have black)
black src/ prompts/ tests/

# Type checking (if you have mypy)
mypy src/ prompts/

# Linting (if you have ruff)
ruff check src/ prompts/ tests/
```

## Resources

### Documentation Files
- Project overview: `ref/project-overview.md`
- Architecture: `ref/architecture.md`
- API reference: `ref/api-reference.md`
- Testing guide: `ref/testing.md`

### Key Concepts
- **TCC**: Theatrical Conflict Chain - independent story thread
- **A-line**: Main plot (spine)
- **B-line**: Subplot (heart)
- **C-line**: Minor thread (flavor)
- **Setup-Payoff**: Cause-effect relationship between scenes

### External Resources
- LangChain docs: https://python.langchain.com/
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- Pydantic docs: https://docs.pydantic.dev/
- DeepSeek API: https://platform.deepseek.com/
