"""
Database module for analysis result caching and persistence.

This module provides SQLite-based caching for script analysis results,
enabling fast retrieval of previously analyzed scripts without redundant LLM calls.

Session 16 Feature: Analysis Result Persistence
"""

from .models import AnalysisCache, CacheStats
from .cache import CacheManager

__all__ = ["AnalysisCache", "CacheStats", "CacheManager"]
