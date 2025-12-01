"""
Cache manager for analysis results.

Provides methods for storing, retrieving, and managing cached analysis results.
"""

import sqlite3
import hashlib
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from pathlib import Path

from .models import (
    AnalysisCache,
    CacheStats,
    DEFAULT_CACHE_EXPIRY_DAYS,
    DEFAULT_DB_PATH,
    init_database,
)

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages analysis result caching with SQLite backend.

    Usage:
        cache = CacheManager()

        # Check for cached result
        result = cache.get(content_hash, provider, model)
        if result:
            print("Cache hit!")
        else:
            # Run analysis...
            cache.set(content_hash, script_name, provider, model, results)
    """

    def __init__(self, db_path: str = None):
        """
        Initialize the cache manager.

        Args:
            db_path: Path to SQLite database. Defaults to DATABASE_PATH env var
                    or 'data/analysis_cache.db'
        """
        self.db_path = db_path or os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_connection()

    def _ensure_connection(self) -> sqlite3.Connection:
        """Ensure database connection is established."""
        if self._conn is None:
            self._conn = init_database(self.db_path)
            logger.info(f"Database initialized at {self.db_path}")
        return self._conn

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection."""
        return self._ensure_connection()

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @staticmethod
    def compute_hash(content: str) -> str:
        """
        Compute SHA256 hash of content.

        Args:
            content: The script content to hash

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get(
        self, content_hash: str, provider: str, model: str
    ) -> Optional[AnalysisCache]:
        """
        Retrieve cached analysis result.

        Args:
            content_hash: SHA256 hash of script content
            provider: LLM provider name
            model: Model name

        Returns:
            AnalysisCache if found and not expired, None otherwise
        """
        cursor = self.conn.cursor()

        # Query for matching cache entry
        cursor.execute(
            """
            SELECT * FROM analysis_cache
            WHERE content_hash = ?
              AND provider = ?
              AND model = ?
              AND (expires_at IS NULL OR expires_at > datetime('now'))
            """,
            (content_hash, provider, model),
        )

        row = cursor.fetchone()

        if row:
            entry = AnalysisCache.from_row(row)
            # Check if all stages are complete
            all_stages_complete = (
                entry.stage1_result is not None and
                entry.stage2_result is not None and
                entry.stage3_result is not None
            )
            if all_stages_complete:
                # Update hit counter only for complete entries
                self._increment_hits()
                logger.info(
                    f"Cache HIT (complete): {content_hash[:8]}... provider={provider} model={model}"
                )
            else:
                # Incomplete entry - count as miss
                self._increment_misses()
                logger.info(
                    f"Cache HIT (incomplete, ignoring): {content_hash[:8]}... provider={provider} model={model} "
                    f"(Stage 1: {entry.stage1_result is not None}, Stage 2: {entry.stage2_result is not None}, Stage 3: {entry.stage3_result is not None})"
                )
            return entry
        else:
            # Update miss counter
            self._increment_misses()
            logger.info(
                f"Cache MISS: {content_hash[:8]}... provider={provider} model={model}"
            )
            return None

    def get_by_id(self, cache_id: int) -> Optional[AnalysisCache]:
        """
        Retrieve cached analysis result by ID.

        Args:
            cache_id: Cache entry ID

        Returns:
            AnalysisCache if found, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM analysis_cache WHERE id = ?", (cache_id,))
        row = cursor.fetchone()
        return AnalysisCache.from_row(row) if row else None

    def set(
        self,
        content_hash: str,
        script_name: str,
        provider: str,
        model: str,
        parsed_script: Optional[dict] = None,
        stage1_result: Optional[dict] = None,
        stage2_result: Optional[dict] = None,
        stage3_result: Optional[dict] = None,
        scene_count: Optional[int] = None,
        tcc_count: Optional[int] = None,
        processing_time: Optional[float] = None,
        api_calls: Optional[int] = None,
        expiry_days: int = DEFAULT_CACHE_EXPIRY_DAYS,
    ) -> int:
        """
        Store analysis result in cache.

        Args:
            content_hash: SHA256 hash of script content
            script_name: Original script filename
            provider: LLM provider name
            model: Model name
            parsed_script: Parsed script data (dict)
            stage1_result: Stage 1 analysis result (dict)
            stage2_result: Stage 2 analysis result (dict)
            stage3_result: Stage 3 analysis result (dict)
            scene_count: Number of scenes
            tcc_count: Number of TCCs identified
            processing_time: Total processing time in seconds
            api_calls: Number of API calls made
            expiry_days: Days until cache expires

        Returns:
            ID of the inserted/updated cache entry
        """
        cursor = self.conn.cursor()

        # Calculate expiry time
        expires_at = datetime.now() + timedelta(days=expiry_days)

        # Serialize dict fields to JSON
        parsed_json = json.dumps(parsed_script, ensure_ascii=False) if parsed_script else None
        stage1_json = json.dumps(stage1_result, ensure_ascii=False) if stage1_result else None
        stage2_json = json.dumps(stage2_result, ensure_ascii=False) if stage2_result else None
        stage3_json = json.dumps(stage3_result, ensure_ascii=False) if stage3_result else None

        # Insert or replace (upsert)
        cursor.execute(
            """
            INSERT INTO analysis_cache (
                content_hash, script_name, provider, model,
                parsed_script, stage1_result, stage2_result, stage3_result,
                scene_count, tcc_count, processing_time, api_calls,
                created_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
            ON CONFLICT(content_hash, provider, model) DO UPDATE SET
                script_name = excluded.script_name,
                parsed_script = excluded.parsed_script,
                stage1_result = excluded.stage1_result,
                stage2_result = excluded.stage2_result,
                stage3_result = excluded.stage3_result,
                scene_count = excluded.scene_count,
                tcc_count = excluded.tcc_count,
                processing_time = excluded.processing_time,
                api_calls = excluded.api_calls,
                created_at = datetime('now'),
                expires_at = excluded.expires_at
            """,
            (
                content_hash,
                script_name,
                provider,
                model,
                parsed_json,
                stage1_json,
                stage2_json,
                stage3_json,
                scene_count,
                tcc_count,
                processing_time,
                api_calls,
                expires_at.isoformat(),
            ),
        )

        self.conn.commit()

        # Get the ID of inserted/updated row
        cursor.execute(
            """
            SELECT id FROM analysis_cache
            WHERE content_hash = ? AND provider = ? AND model = ?
            """,
            (content_hash, provider, model),
        )
        row = cursor.fetchone()
        cache_id = row["id"] if row else cursor.lastrowid

        logger.info(
            f"Cache SET: id={cache_id} hash={content_hash[:8]}... "
            f"provider={provider} model={model} expires={expires_at.date()}"
        )

        return cache_id

    def delete(self, cache_id: int) -> bool:
        """
        Delete a cache entry by ID.

        Args:
            cache_id: Cache entry ID

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM analysis_cache WHERE id = ?", (cache_id,))
        self.conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Cache DELETE: id={cache_id}")
        return deleted

    def delete_by_hash(self, content_hash: str) -> int:
        """
        Delete all cache entries for a content hash.

        Args:
            content_hash: SHA256 hash of script content

        Returns:
            Number of entries deleted
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM analysis_cache WHERE content_hash = ?", (content_hash,)
        )
        self.conn.commit()
        count = cursor.rowcount
        if count > 0:
            logger.info(f"Cache DELETE: {count} entries for hash={content_hash[:8]}...")
        return count

    def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Tuple[List[AnalysisCache], int]:
        """
        List cached entries with pagination and filtering.

        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            search: Search term for script_name
            provider: Filter by provider
            model: Filter by model

        Returns:
            Tuple of (list of cache entries, total count)
        """
        cursor = self.conn.cursor()

        # Build WHERE clause
        conditions = []
        params = []

        if search:
            conditions.append("script_name LIKE ?")
            params.append(f"%{search}%")

        if provider:
            conditions.append("provider = ?")
            params.append(provider)

        if model:
            conditions.append("model = ?")
            params.append(model)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Get total count
        cursor.execute(
            f"SELECT COUNT(*) FROM analysis_cache WHERE {where_clause}", params
        )
        total = cursor.fetchone()[0]

        # Get paginated results
        cursor.execute(
            f"""
            SELECT * FROM analysis_cache
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset],
        )

        entries = [AnalysisCache.from_row(row) for row in cursor.fetchall()]

        return entries, total

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            DELETE FROM analysis_cache
            WHERE expires_at IS NOT NULL AND expires_at < datetime('now')
            """
        )
        self.conn.commit()
        count = cursor.rowcount
        if count > 0:
            logger.info(f"Cache CLEANUP: removed {count} expired entries")
        return count

    def clear_all(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries removed
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM analysis_cache")
        self.conn.commit()
        count = cursor.rowcount
        logger.warning(f"Cache CLEAR: removed all {count} entries")

        # Reset stats
        cursor.execute("UPDATE cache_stats SET hits = 0, misses = 0")
        self.conn.commit()

        return count

    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.

        Returns:
            CacheStats with hit rate, entry counts, etc.
        """
        cursor = self.conn.cursor()

        # Get hit/miss counts
        cursor.execute("SELECT hits, misses FROM cache_stats LIMIT 1")
        stats_row = cursor.fetchone()
        hits = stats_row["hits"] if stats_row else 0
        misses = stats_row["misses"] if stats_row else 0

        # Get total entries
        cursor.execute("SELECT COUNT(*) FROM analysis_cache")
        total_entries = cursor.fetchone()[0]

        # Get oldest and newest entries
        cursor.execute(
            "SELECT MIN(created_at), MAX(created_at) FROM analysis_cache"
        )
        date_row = cursor.fetchone()
        oldest = datetime.fromisoformat(date_row[0]) if date_row[0] else None
        newest = datetime.fromisoformat(date_row[1]) if date_row[1] else None

        # Get entries by provider
        cursor.execute(
            "SELECT provider, COUNT(*) FROM analysis_cache GROUP BY provider"
        )
        by_provider = {row[0]: row[1] for row in cursor.fetchall()}

        # Get entries by model
        cursor.execute(
            "SELECT model, COUNT(*) FROM analysis_cache GROUP BY model"
        )
        by_model = {row[0]: row[1] for row in cursor.fetchall()}

        # Calculate database file size
        db_size = 0
        if os.path.exists(self.db_path):
            db_size = os.path.getsize(self.db_path)

        # Calculate hit rate
        total_requests = hits + misses
        hit_rate = hits / total_requests if total_requests > 0 else 0.0

        return CacheStats(
            total_entries=total_entries,
            total_hits=hits,
            total_misses=misses,
            hit_rate=hit_rate,
            cache_size_bytes=db_size,
            oldest_entry=oldest,
            newest_entry=newest,
            entries_by_provider=by_provider,
            entries_by_model=by_model,
        )

    def _increment_hits(self):
        """Increment hit counter."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE cache_stats SET hits = hits + 1, updated_at = datetime('now')"
        )
        self.conn.commit()

    def _increment_misses(self):
        """Increment miss counter."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE cache_stats SET misses = misses + 1, updated_at = datetime('now')"
        )
        self.conn.commit()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
