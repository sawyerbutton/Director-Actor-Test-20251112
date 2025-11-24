# Version Tracking Guide

## Overview

This guide explains the version tracking system introduced in v2.7.0. The system provides multiple ways to identify which version is deployed, making it easy to verify deployments and debug issues.

**Version**: 2.7.0
**Added**: 2025-11-24 (Session 11)
**Status**: ✅ Production Ready

---

## Version Information Sources

### 1. Centralized Version File

**File**: `src/version.py`

```python
# Application version - update this when releasing new versions
__version__ = "2.7.0"

# Version name for display
VERSION_NAME = "Session 11: Gemini 3 Pro + Version Tracking"

# Build info
BUILD_DATE = "2025-11-24"
```

**Functions**:
- `get_version_info()` - Returns complete version dict
- `get_git_info()` - Returns git commit/branch info

**Usage in code**:
```python
from src.version import __version__, get_version_info

print(__version__)  # "2.7.0"
print(get_version_info())
# {
#   "version": "2.7.0",
#   "name": "Session 11: Gemini 3 Pro + Version Tracking",
#   "build_date": "2025-11-24",
#   "git": {"commit_short": "f5ec6dc", "branch": "main", ...},
#   "display": "v2.7.0 (f5ec6dc)"
# }
```

---

### 2. Health Endpoint (API)

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "screenplay-analysis",
  "version": "2.7.0",
  "version_name": "Session 11: Gemini 3 Pro + Version Tracking",
  "git_commit": "f5ec6dc",
  "git_branch": "main",
  "build_date": "2025-11-24",
  "timestamp": "2025-11-24T07:34:46.435804"
}
```

**Quick check**:
```bash
curl http://localhost:8014/health | jq '.version, .git_commit'
# "2.7.0"
# "f5ec6dc"
```

---

### 3. Web UI Footer

All pages display version info in the footer:

```
剧本叙事结构分析系统 v2.7.0 [f5ec6dc] | 文档 | 基于 LangChain + LangGraph
```

**Components**:
- Version number from `__version__`
- Git commit short hash in badge
- Hover shows full commit info

---

### 4. Deploy Script

**Command**: `./scripts/deploy.sh version`

**Output**:
```
============================================
  Version Information
============================================
  App Version:  2.7.0
  Git Commit:   f5ec6dc
  Git Branch:   main
  Image Tag:    screenplay-analysis:2.7.0
============================================
```

---

## Version Update Workflow

### When Releasing a New Version

1. **Update version file**:
   ```python
   # src/version.py
   __version__ = "2.8.0"
   VERSION_NAME = "Session 12: New Feature Name"
   BUILD_DATE = "2025-12-01"
   ```

2. **Commit changes**:
   ```bash
   git add src/version.py
   git commit -m "chore: bump version to 2.8.0"
   ```

3. **Deploy**:
   ```bash
   git push origin main
   # On ECS:
   git pull origin main
   ./scripts/deploy.sh deploy
   ```

4. **Verify**:
   ```bash
   curl http://your-server:8014/health | jq '.version'
   # "2.8.0"
   ```

---

## Docker Image Tagging

Docker images are tagged with the version:

```yaml
# docker-compose.yml
services:
  web:
    image: screenplay-analysis:${APP_VERSION:-2.7.0}
```

**Build with version**:
```bash
docker build -t screenplay-analysis:2.7.0 .
```

**Deploy script auto-tags**:
```bash
./scripts/deploy.sh deploy
# Builds: screenplay-analysis:2.7.0 AND screenplay-analysis:latest
```

---

## Troubleshooting

### Version Mismatch

**Symptom**: Health endpoint shows old version after deployment

**Cause**: Docker cache or container not restarted

**Solution**:
```bash
# Force rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Git Info Shows "unknown"

**Symptom**: `git_commit: "unknown"` in health response

**Cause**: `.git` directory not available in container

**Solution**: Ensure `.git` is not in `.dockerignore`, or build image with git info baked in.

---

## Files Changed (v2.7.0)

| File | Change |
|------|--------|
| `src/version.py` | NEW - Centralized version module |
| `src/web/app.py` | Import version, update health endpoint, pass to templates |
| `templates/base.html` | Display version in footer |
| `docker-compose.yml` | Support APP_VERSION variable |
| `scripts/deploy.sh` | Auto-read version, add `version` command |

---

## Related Documentation

- [`ref/gemini-integration.md`](gemini-integration.md) - Gemini 3 Pro setup
- [`ref/getting-started.md`](getting-started.md) - Installation and deployment
- [`docs/deployment/DEPLOYMENT.md`](../docs/deployment/DEPLOYMENT.md) - Full deployment guide
