"""
Version information for Script Analysis System.

This module provides centralized version information that can be used
across the application for health checks, UI display, and deployment tracking.
"""

import subprocess
from functools import lru_cache

# Application version - update this when releasing new versions
__version__ = "2.8.1"

# Version name for display
VERSION_NAME = "Session 13: TXT Parser Enhancement + Gemini 3 API Key"

# Build info
BUILD_DATE = "2025-11-24"


@lru_cache(maxsize=1)
def get_git_info() -> dict:
    """
    Get git commit information for deployment tracking.

    Returns:
        dict with commit_hash, commit_short, branch, and commit_message
    """
    try:
        # Get short commit hash
        commit_short = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Get full commit hash
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Get current branch
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Get commit message (first line)
        commit_message = subprocess.check_output(
            ["git", "log", "-1", "--format=%s"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        return {
            "commit_hash": commit_hash,
            "commit_short": commit_short,
            "branch": branch,
            "commit_message": commit_message
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            "commit_hash": "unknown",
            "commit_short": "unknown",
            "branch": "unknown",
            "commit_message": "unknown"
        }


def get_version_info() -> dict:
    """
    Get complete version information.

    Returns:
        dict with version, name, build_date, and git info
    """
    git_info = get_git_info()
    return {
        "version": __version__,
        "name": VERSION_NAME,
        "build_date": BUILD_DATE,
        "git": git_info,
        "display": f"v{__version__} ({git_info['commit_short']})"
    }
