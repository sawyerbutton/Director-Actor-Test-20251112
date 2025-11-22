# Gemini 3 Pro Integration Guide

## Overview

This guide covers the integration of Google Gemini 3 Pro into the screenplay analysis system. Gemini was integrated to solve token limit issues when analyzing large scripts (12+ scenes).

**Version**: 2.7.0
**Added**: 2025-11-19 (Session 9), **Upgraded**: 2025-11-22 (Session 11)
**Status**: ✅ Production Ready

### Upgrade History
- **v2.5.0** (2025-11-19): Initial Gemini 2.5 Flash integration
- **v2.7.0** (2025-11-22): Upgraded to Gemini 3 Pro for improved reasoning

---

## Why Gemini?

### Token Limit Comparison

| Provider | Context Window | Max Output | Stage 3 Status |
|----------|---------------|------------|----------------|
| **DeepSeek** | 64K tokens | 16K tokens | ❌ Fails on large scripts (JSON truncation) |
| **Gemini 3 Pro** ✅ | 1M tokens | 64K tokens | ✅ Handles large scripts + advanced reasoning |
| Gemini 2.5 Flash | 1M tokens | 65K tokens | ✅ Good, but less capable reasoning |
| Anthropic Claude | 200K tokens | 4K tokens | ⚠️ Small output limit |
| OpenAI GPT-4 | 128K tokens | 4K tokens | ⚠️ Small output limit |

### Problem Solved

**Issue**: When analyzing large scripts (12+ scenes), DeepSeek's 16K max_tokens limit caused Stage 3 (Modifier) to produce truncated JSON output, resulting in parsing errors.

**Solution**: Gemini 3 Pro's 64K output capacity completely eliminates this issue, plus provides significantly improved reasoning capabilities.

### Gemini 3 Pro Advantages

- **Built-in Reasoning**: Reduces need for chain-of-thought prompt engineering
- **Better Accuracy**: Significant performance improvement over 2.5 in complex reasoning
- **Multimodal Excellence**: Improved handling of visual and text content
- **Reference**: https://ai.google.dev/gemini-api/docs/gemini-3

---

## Quick Start

### 1. Get API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (format: `AIzaSy...`)

### 2. Configure Environment

Add to `.env`:
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy...your_key_here
```

### 3. Test API Connectivity

**IMPORTANT**: Always test API before running business logic!

```bash
python test_gemini_api.py
```

Expected output:
```
============================================================
Gemini API 连通性测试
============================================================
✅ API Key 已找到: AIzaSy...Frc
📡 测试模型: gemini-3-pro-preview
   (Gemini 3 Pro: 1M 上下文, 64K 输出, 高级推理能力)
✅ LLM 实例创建成功
📤 发送测试请求...
✅ API 调用成功!
💬 响应内容:
我是 Gemini，一个由 Google DeepMind 开发的大型语言模型。
============================================================
✅ 测试通过! Gemini API 工作正常
============================================================
```

### 4. Run Analysis

Via Web UI:
1. Open http://localhost:8000
2. UI automatically selects configured provider (Gemini)
3. Upload script and analyze

Via CLI:
```bash
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json --provider gemini
```

---

## Implementation Details

### Code Changes

#### 1. Dependencies (`requirements.txt`)

Added:
```python
langchain-google-genai>=2.0.0  # For Google Gemini 3 Pro
```

Install:
```bash
pip install langchain-google-genai
```

#### 2. LLM Factory (`src/pipeline.py:288-303`)

```python
from langchain_google_genai import ChatGoogleGenerativeAI

def create_llm(provider: str = "deepseek", model: str = None, ...):
    """Create LLM instance with provider selection."""

    # ... existing providers (deepseek, anthropic, openai) ...

    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        # Use Gemini 3 Pro as default (1M tokens context + 64K output)
        # Gemini 3 Pro provides significant performance improvement over 2.5
        model = model or "gemini-3-pro-preview"

        logger.info(f"Creating Gemini LLM: {model} (max_tokens: {max_tokens})")

        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
```

**Key Points**:
- Default model: `gemini-3-pro-preview`
- Uses `max_output_tokens` parameter (not `max_tokens`)
- Recommended temperature: 1.0 (Gemini 3 default)
- Validates API key exists

#### 3. Environment Configuration (`.env.example`)

```bash
# Google Gemini (Optional)
# Get your API key from: https://aistudio.google.com/app/apikey
# GOOGLE_API_KEY=your_google_api_key_here

# Default LLM provider (deepseek, anthropic, openai, or gemini)
LLM_PROVIDER=gemini
```

#### 4. Docker Support (`docker-compose.yml:33`)

```yaml
environment:
  - GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

#### 5. Web UI Integration (`templates/index.html:94-110`)

Provider selection dropdown:
```html
<select class="form-select" id="provider">
    <option value="deepseek" {% if default_provider == 'deepseek' %}selected{% endif %}>
        DeepSeek (推荐)
    </option>
    <option value="anthropic" {% if default_provider == 'anthropic' %}selected{% endif %}>
        Anthropic Claude
    </option>
    <option value="openai" {% if default_provider == 'openai' %}selected{% endif %}>
        OpenAI
    </option>
    <option value="gemini" {% if default_provider == 'gemini' %}selected{% endif %}>
        Google Gemini 3 Pro (64K output)
    </option>
</select>
<div class="form-text">
    <i class="bi bi-lightbulb"></i>
    <span id="providerHint">
        {% if default_provider == 'gemini' %}
        Gemini 3 Pro 提供 64K 输出 + 1M 上下文 + 高级推理能力
        {% else %}
        DeepSeek 提供最佳性价比
        {% endif %}
    </span>
</div>
```

Backend route (`src/web/app.py:122-131`):
```python
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page with upload form."""
    # Get configured LLM provider from environment
    default_provider = os.getenv("LLM_PROVIDER", "deepseek")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": STATIC_VERSION,
        "default_provider": default_provider
    })
```

---

## Model Selection

### Available Models

Gemini 3 Pro is recommended for this project:

| Model | Context | Output | Best For |
|-------|---------|--------|----------|
| **gemini-3-pro-preview** ✅ | 1M tokens | 64K tokens | Screenplay analysis (recommended, best reasoning) |
| gemini-2.5-flash | 1M tokens | 65K tokens | Fallback if Gemini 3 unavailable |
| gemini-2.5-pro | 2M tokens | 65K tokens | Extra large context needs |
| gemini-1.5-flash | 1M tokens | 8K tokens | ⚠️ Output too small for Stage 3 |

### Model Selection Guide

Use **gemini-3-pro-preview** (default) for:
- Best reasoning accuracy and complex screenplay analysis
- Built-in reasoning capabilities (reduces prompt engineering)
- Significant performance improvement over Gemini 2.5

**Fallback options**:
- `gemini-2.5-flash`: If Gemini 3 is temporarily unavailable
- `deepseek`: For cost-sensitive small scripts (<5 scenes)

**Do NOT use**:
- `gemini-1.5-*` models (output limit too small)
- `gemini-2.0-*` experimental models (deprecated)

---

## API Key Management

### Getting Your API Key

1. **Sign Up**: https://aistudio.google.com/
2. **Create Key**: Click "Get API Key" → "Create API key"
3. **Free Tier**: Gemini offers generous free tier
4. **Quota**: Check quota at https://aistudio.google.com/app/apikey

### Quota Issues

If you see `429 Quota exceeded`:

**Common Causes**:
1. **Free tier limit reached**: Wait 24 hours or upgrade
2. **Region restrictions**: Some regions have quota=0
3. **Model not enabled**: Ensure Gemini API is enabled

**Solutions**:
1. Check quota: https://aistudio.google.com/app/apikey
2. Try different API key
3. Use different model (e.g., switch to gemini-2.5-flash from gemini-2.5-pro)
4. Upgrade to paid tier

### Security Best Practices

1. **Never commit** `.env` to git
2. **Use environment variables** in production
3. **Rotate keys** periodically
4. **Monitor usage** to prevent unexpected costs

---

## Testing

### Pre-Business API Test

**File**: `test_gemini_api.py`

**Purpose**: Verify API connectivity BEFORE running full pipeline

```bash
python test_gemini_api.py
```

**What it tests**:
- API key is valid
- Model name is correct
- Network connectivity works
- Basic inference succeeds

**When to use**:
- After changing API key
- When switching models
- Before running expensive analysis
- When debugging quota issues

### Integration Test

Test full three-stage pipeline:
```bash
python -m src.cli analyze examples/golden/百妖_ep09_s01-s05.json --provider gemini
```

Expected result:
- Stage 1: ~20s, identifies 3 TCCs
- Stage 2: ~30s, ranks A/B/C lines
- Stage 3: ~60s, fixes issues
- Total: ~110s, 0 errors, 0 retries

### A/B Testing

Compare Gemini vs DeepSeek:
```bash
python -m src.cli ab-test examples/golden/百妖_ep09_s01-s05.json \
  --providers deepseek,gemini
```

Results show:
- Performance comparison
- Cost comparison
- Output quality comparison

---

## Troubleshooting

### Issue 1: Model Not Found (404)

**Error**: `404 models/gemini-3-pro-preview is not found`

**Cause**: Wrong model name or model not available in your region

**Solution**: Use exact model name: `gemini-3-pro-preview`

**Fallback**: If Gemini 3 is unavailable, use `gemini-2.5-flash` temporarily

**Reference**: https://ai.google.dev/gemini-api/docs/gemini-3

### Issue 2: Quota Exceeded (429)

**Error**: `429 Quota exceeded... quota_limit_value: "0"`

**Cause**: API key has no quota in current region

**Solutions**:
1. Try different API key
2. Check quota: https://aistudio.google.com/app/apikey
3. Wait 24 hours (daily reset)
4. Upgrade to paid tier

### Issue 3: Authentication Failed (401/403)

**Error**: `401 Unauthorized` or `403 Forbidden`

**Causes**:
1. Wrong API key
2. API key not enabled for Gemini
3. Project billing not enabled

**Solutions**:
1. Verify API key in .env matches https://aistudio.google.com/app/apikey
2. Ensure Gemini API is enabled
3. Check project billing settings

### Issue 4: Web UI Not Using Gemini

**Symptom**: UI shows DeepSeek despite .env set to gemini

**Cause**: Docker container not restarted after .env change

**Solution**:
```bash
docker-compose down
docker-compose up -d
```

**Verify**:
- Check logs: `docker-compose logs web | grep "provider"`
- UI should show "Gemini 3 Pro (64K output)" selected

---

## Performance Characteristics

### Speed

**Gemini 3 Pro vs DeepSeek** (百妖1.txt, 12 scenes):

| Stage | DeepSeek | Gemini 3 Pro | Change |
|-------|----------|--------------|--------|
| Stage 1 | ~15s | ~25s | +67% slower |
| Stage 2 | ~20s | ~30s | +50% slower |
| Stage 3 | ❌ Failed | ~65s | ✅ Works! |
| **Total** | ❌ Error | ~120s | ✅ Success |

**Verdict**: Gemini 3 Pro is slower but provides **best reasoning accuracy** for complex analysis.

### Cost

**Pricing** (as of 2025-11):
- Gemini 3 Pro: Check current pricing at https://ai.google.dev/pricing
- Gemini 2.5 Flash: $0.075 / 1M input, $0.30 / 1M output
- DeepSeek: $0.14 / 1M input, $0.28 / 1M output (cheapest)

**Recommendation**: Use Gemini 3 Pro for best quality, DeepSeek for cost-sensitive small scripts.

### Reliability

**Gemini 3 Pro**:
- ✅ Best reasoning accuracy
- ✅ Built-in chain-of-thought capabilities
- ✅ Consistent JSON formatting
- ✅ Handles 12+ scene scripts
- ⚠️ Slower than DeepSeek and Gemini 2.5

**DeepSeek**:
- ✅ Fastest inference
- ✅ Best cost efficiency
- ❌ Fails on large scripts (JSON truncation)

---

## Best Practices

### 1. Choose Provider Based on Script Size

```python
# Rule of thumb:
if num_scenes <= 10:
    provider = "deepseek"  # Faster, cheaper
else:
    provider = "gemini"    # More reliable for large scripts
```

### 2. Always Test API First

Before running expensive analysis:
```bash
python test_gemini_api.py
```

### 3. Monitor Costs

- Check usage: https://aistudio.google.com/app/apikey
- Set up billing alerts
- Use A/B testing to compare costs

### 4. Fallback Strategy

Set up fallback in production:
```python
try:
    result = analyze_with_provider("gemini")
except QuotaExceeded:
    logger.warning("Gemini quota exceeded, falling back to DeepSeek")
    result = analyze_with_provider("deepseek")
```

---

## Migration Guide

### From DeepSeek to Gemini

**Step 1**: Get API key (see above)

**Step 2**: Update .env
```bash
# Change provider
LLM_PROVIDER=gemini

# Add API key
GOOGLE_API_KEY=your_key_here
```

**Step 3**: Restart Docker
```bash
docker-compose down
docker-compose up -d
```

**Step 4**: Verify
```bash
python test_gemini_api.py
```

**Step 5**: Test analysis
```bash
# Upload script via Web UI and check logs
docker-compose logs web | grep "Creating Gemini LLM"
```

### From Gemini to DeepSeek

Same steps, but set `LLM_PROVIDER=deepseek`

---

## References

### Official Documentation
- Gemini API: https://ai.google.dev/
- **Gemini 3 Pro Guide**: https://ai.google.dev/gemini-api/docs/gemini-3
- Model Documentation: https://ai.google.dev/gemini-api/docs/models
- Pricing: https://ai.google.dev/pricing
- API Key Management: https://aistudio.google.com/app/apikey

### Internal Documentation
- Architecture Guide: [`ref/architecture.md`](architecture.md)
- API Reference: [`ref/api-reference.md`](api-reference.md)
- Getting Started: [`ref/getting-started.md`](getting-started.md)
- A/B Testing: [`docs/ab-testing-guide.md`](../docs/ab-testing-guide.md)

### Related Files
- LLM Factory: `src/pipeline.py:211-303`
- Web UI: `src/web/app.py:122-131`, `templates/index.html:94-110`
- Environment: `.env.example`, `docker-compose.yml`
- Test Script: `test_gemini_api.py`

---

## Changelog

### v2.7.0 (2025-11-22) - Gemini 3 Pro Upgrade
- Upgraded from Gemini 2.5 Flash to Gemini 3 Pro Preview
- Model ID: `gemini-3-pro-preview`
- Improved reasoning capabilities with built-in chain-of-thought
- Updated all documentation, templates, and scripts
- Recommended temperature: 1.0 (Gemini 3 default)

### v2.5.0 (2025-11-19) - Initial Integration
- Added Gemini 2.5 Flash support
- Created API connectivity test script
- Updated Web UI with provider selection
- Added Docker environment variable
- Fixed token limit issues for large scripts
- Documentation: This guide created

### Future Improvements
- [ ] Auto-fallback when quota exceeded
- [ ] Cost estimation before analysis
- [ ] Batch processing optimization
- [x] ~~Gemini 2.5 Pro support for complex scripts~~ → Upgraded to Gemini 3 Pro

---

**Version**: 2.0
**Author**: AI Assistant
**Last Updated**: 2025-11-22
