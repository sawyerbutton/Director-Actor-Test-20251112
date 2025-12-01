"""
Database models for analysis cache.

Defines the SQLite table schema and Pydantic models for cache entries.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import os

# Default cache expiration: 90 days
DEFAULT_CACHE_EXPIRY_DAYS = 90

# Default database path
DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "data/analysis_cache.db")


@dataclass
class AnalysisCache:
    """Represents a cached analysis result."""

    id: Optional[int] = None
    content_hash: str = ""
    script_name: str = ""
    provider: str = ""
    model: str = ""

    # Parse results (JSON strings)
    parsed_script: Optional[str] = None

    # Three-stage analysis results (JSON strings)
    stage1_result: Optional[str] = None
    stage2_result: Optional[str] = None
    stage3_result: Optional[str] = None

    # Metadata
    scene_count: Optional[int] = None
    tcc_count: Optional[int] = None
    processing_time: Optional[float] = None
    api_calls: Optional[int] = None

    # Timestamps
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "content_hash": self.content_hash,
            "script_name": self.script_name,
            "provider": self.provider,
            "model": self.model,
            "parsed_script": self.parsed_script,
            "stage1_result": self.stage1_result,
            "stage2_result": self.stage2_result,
            "stage3_result": self.stage3_result,
            "scene_count": self.scene_count,
            "tcc_count": self.tcc_count,
            "processing_time": self.processing_time,
            "api_calls": self.api_calls,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "AnalysisCache":
        """Create from SQLite row."""
        return cls(
            id=row["id"],
            content_hash=row["content_hash"],
            script_name=row["script_name"],
            provider=row["provider"],
            model=row["model"],
            parsed_script=row["parsed_script"],
            stage1_result=row["stage1_result"],
            stage2_result=row["stage2_result"],
            stage3_result=row["stage3_result"],
            scene_count=row["scene_count"],
            tcc_count=row["tcc_count"],
            processing_time=row["processing_time"],
            api_calls=row["api_calls"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
        )


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    hit_rate: float = 0.0
    cache_size_bytes: int = 0
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
    entries_by_provider: dict = field(default_factory=dict)
    entries_by_model: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_entries": self.total_entries,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "hit_rate": round(self.hit_rate, 4),
            "cache_size_bytes": self.cache_size_bytes,
            "oldest_entry": self.oldest_entry.isoformat() if self.oldest_entry else None,
            "newest_entry": self.newest_entry.isoformat() if self.newest_entry else None,
            "entries_by_provider": self.entries_by_provider,
            "entries_by_model": self.entries_by_model,
        }


# SQL Schema
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS analysis_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash    TEXT NOT NULL,
    script_name     TEXT NOT NULL,
    provider        TEXT NOT NULL,
    model           TEXT NOT NULL,

    -- Parse results
    parsed_script   TEXT,

    -- Three-stage analysis results
    stage1_result   TEXT,
    stage2_result   TEXT,
    stage3_result   TEXT,

    -- Metadata
    scene_count     INTEGER,
    tcc_count       INTEGER,
    processing_time REAL,
    api_calls       INTEGER,

    -- Timestamps
    created_at      TEXT DEFAULT (datetime('now')),
    expires_at      TEXT,

    -- Unique constraint: same content + provider + model = unique record
    UNIQUE(content_hash, provider, model)
);
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_content_hash ON analysis_cache(content_hash);",
    "CREATE INDEX IF NOT EXISTS idx_expires_at ON analysis_cache(expires_at);",
    "CREATE INDEX IF NOT EXISTS idx_script_name ON analysis_cache(script_name);",
    "CREATE INDEX IF NOT EXISTS idx_provider_model ON analysis_cache(provider, model);",
]

# Cache stats table for tracking hits/misses
CREATE_STATS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cache_stats (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    hits        INTEGER DEFAULT 0,
    misses      INTEGER DEFAULT 0,
    updated_at  TEXT DEFAULT (datetime('now'))
);
"""


def init_database(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Initialize the database with required tables and indexes.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        SQLite connection with row_factory set
    """
    # Ensure directory exists
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    # Connect and create tables
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Create main cache table
    cursor.execute(CREATE_TABLE_SQL)

    # Create indexes
    for index_sql in CREATE_INDEXES_SQL:
        cursor.execute(index_sql)

    # Create stats table
    cursor.execute(CREATE_STATS_TABLE_SQL)

    # Initialize stats row if not exists
    cursor.execute("SELECT COUNT(*) FROM cache_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO cache_stats (hits, misses) VALUES (0, 0)")

    conn.commit()

    return conn
