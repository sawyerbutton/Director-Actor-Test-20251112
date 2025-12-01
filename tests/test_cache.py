"""
Unit tests for the database cache module.

Tests cover:
- CacheManager CRUD operations
- Cache statistics
- Hash computation
- Expiration handling
- Pagination and filtering
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from src.db import CacheManager, AnalysisCache, CacheStats
from src.db.models import init_database, DEFAULT_CACHE_EXPIRY_DAYS


class TestCacheManager:
    """Tests for CacheManager class."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    def cache_manager(self, temp_db):
        """Create a CacheManager with temporary database."""
        manager = CacheManager(db_path=temp_db)
        yield manager
        manager.close()

    def test_init_creates_database(self, temp_db):
        """Test that initialization creates the database file."""
        manager = CacheManager(db_path=temp_db)
        assert os.path.exists(temp_db)
        manager.close()

    def test_compute_hash_consistent(self):
        """Test that hash computation is consistent."""
        content = "测试剧本内容"
        hash1 = CacheManager.compute_hash(content)
        hash2 = CacheManager.compute_hash(content)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64 hex characters

    def test_compute_hash_different_content(self):
        """Test that different content produces different hashes."""
        hash1 = CacheManager.compute_hash("内容A")
        hash2 = CacheManager.compute_hash("内容B")
        assert hash1 != hash2

    def test_set_and_get(self, cache_manager):
        """Test basic set and get operations."""
        content_hash = CacheManager.compute_hash("测试剧本")
        script_name = "test_script.json"
        provider = "deepseek"
        model = "deepseek-chat"

        # Set cache entry
        cache_id = cache_manager.set(
            content_hash=content_hash,
            script_name=script_name,
            provider=provider,
            model=model,
            stage1_result={"tccs": [{"id": "TCC_01"}]},
            stage2_result={"rankings": ["A", "B", "C"]},
            stage3_result={"modifications": []},
            scene_count=5,
            tcc_count=3,
            processing_time=10.5,
            api_calls=15,
        )

        assert cache_id is not None
        assert cache_id > 0

        # Get cache entry
        result = cache_manager.get(content_hash, provider, model)
        assert result is not None
        assert result.script_name == script_name
        assert result.scene_count == 5
        assert result.tcc_count == 3
        assert result.processing_time == 10.5

    def test_get_by_id(self, cache_manager):
        """Test get_by_id operation."""
        content_hash = CacheManager.compute_hash("测试剧本2")
        cache_id = cache_manager.set(
            content_hash=content_hash,
            script_name="test2.json",
            provider="gemini",
            model="gemini-2.5-flash",
        )

        result = cache_manager.get_by_id(cache_id)
        assert result is not None
        assert result.id == cache_id
        assert result.provider == "gemini"

    def test_get_nonexistent(self, cache_manager):
        """Test get returns None for nonexistent entry."""
        result = cache_manager.get("nonexistent_hash", "provider", "model")
        assert result is None

    def test_get_by_id_nonexistent(self, cache_manager):
        """Test get_by_id returns None for nonexistent entry."""
        result = cache_manager.get_by_id(99999)
        assert result is None

    def test_delete(self, cache_manager):
        """Test delete operation."""
        content_hash = CacheManager.compute_hash("删除测试")
        cache_id = cache_manager.set(
            content_hash=content_hash,
            script_name="delete_test.json",
            provider="deepseek",
            model="default",
        )

        # Verify entry exists
        assert cache_manager.get_by_id(cache_id) is not None

        # Delete entry
        result = cache_manager.delete(cache_id)
        assert result is True

        # Verify entry is gone
        assert cache_manager.get_by_id(cache_id) is None

    def test_delete_nonexistent(self, cache_manager):
        """Test delete returns False for nonexistent entry."""
        result = cache_manager.delete(99999)
        assert result is False

    def test_delete_by_hash(self, cache_manager):
        """Test delete_by_hash operation."""
        content_hash = CacheManager.compute_hash("哈希删除测试")

        # Create multiple entries with same hash but different providers
        cache_manager.set(
            content_hash=content_hash,
            script_name="test.json",
            provider="deepseek",
            model="default",
        )
        cache_manager.set(
            content_hash=content_hash,
            script_name="test.json",
            provider="gemini",
            model="gemini-2.5-flash",
        )

        # Delete all entries for this hash
        count = cache_manager.delete_by_hash(content_hash)
        assert count == 2

        # Verify both are gone
        assert cache_manager.get(content_hash, "deepseek", "default") is None
        assert cache_manager.get(content_hash, "gemini", "gemini-2.5-flash") is None

    def test_upsert_behavior(self, cache_manager):
        """Test that set updates existing entry instead of creating duplicate."""
        content_hash = CacheManager.compute_hash("更新测试")
        provider = "deepseek"
        model = "default"

        # First insert
        id1 = cache_manager.set(
            content_hash=content_hash,
            script_name="original.json",
            provider=provider,
            model=model,
            scene_count=5,
        )

        # Second insert with same key (should update)
        id2 = cache_manager.set(
            content_hash=content_hash,
            script_name="updated.json",
            provider=provider,
            model=model,
            scene_count=10,
        )

        # Same ID means it was updated, not duplicated
        assert id1 == id2

        # Verify updated values
        result = cache_manager.get(content_hash, provider, model)
        assert result.script_name == "updated.json"
        assert result.scene_count == 10

    def test_list_all_empty(self, cache_manager):
        """Test list_all on empty database."""
        entries, total = cache_manager.list_all()
        assert entries == []
        assert total == 0

    def test_list_all_with_entries(self, cache_manager):
        """Test list_all returns all entries."""
        # Create multiple entries
        for i in range(5):
            cache_manager.set(
                content_hash=CacheManager.compute_hash(f"剧本{i}"),
                script_name=f"script_{i}.json",
                provider="deepseek",
                model="default",
            )

        entries, total = cache_manager.list_all()
        assert len(entries) == 5
        assert total == 5

    def test_list_all_pagination(self, cache_manager):
        """Test list_all pagination."""
        # Create 10 entries
        for i in range(10):
            cache_manager.set(
                content_hash=CacheManager.compute_hash(f"分页测试{i}"),
                script_name=f"script_{i}.json",
                provider="deepseek",
                model="default",
            )

        # First page
        entries, total = cache_manager.list_all(limit=3, offset=0)
        assert len(entries) == 3
        assert total == 10

        # Second page
        entries, total = cache_manager.list_all(limit=3, offset=3)
        assert len(entries) == 3
        assert total == 10

        # Last page (partial)
        entries, total = cache_manager.list_all(limit=3, offset=9)
        assert len(entries) == 1
        assert total == 10

    def test_list_all_search(self, cache_manager):
        """Test list_all with search filter."""
        cache_manager.set(
            content_hash=CacheManager.compute_hash("西游记剧本"),
            script_name="西游记_ep01.json",
            provider="deepseek",
            model="default",
        )
        cache_manager.set(
            content_hash=CacheManager.compute_hash("百妖剧本"),
            script_name="百妖_ep01.json",
            provider="deepseek",
            model="default",
        )

        # Search for 西游记
        entries, total = cache_manager.list_all(search="西游记")
        assert len(entries) == 1
        assert entries[0].script_name == "西游记_ep01.json"

    def test_list_all_provider_filter(self, cache_manager):
        """Test list_all with provider filter."""
        cache_manager.set(
            content_hash=CacheManager.compute_hash("测试1"),
            script_name="test1.json",
            provider="deepseek",
            model="default",
        )
        cache_manager.set(
            content_hash=CacheManager.compute_hash("测试2"),
            script_name="test2.json",
            provider="gemini",
            model="gemini-2.5-flash",
        )

        # Filter by provider
        entries, total = cache_manager.list_all(provider="gemini")
        assert len(entries) == 1
        assert entries[0].provider == "gemini"

    def test_list_all_model_filter(self, cache_manager):
        """Test list_all with model filter."""
        cache_manager.set(
            content_hash=CacheManager.compute_hash("测试3"),
            script_name="test3.json",
            provider="gemini",
            model="gemini-2.5-flash",
        )
        cache_manager.set(
            content_hash=CacheManager.compute_hash("测试4"),
            script_name="test4.json",
            provider="gemini",
            model="gemini-2.5-pro",
        )

        # Filter by model
        entries, total = cache_manager.list_all(model="gemini-2.5-pro")
        assert len(entries) == 1
        assert entries[0].model == "gemini-2.5-pro"

    def test_cleanup_expired(self, cache_manager):
        """Test cleanup_expired removes expired entries."""
        # Create an entry with short expiry (already expired)
        content_hash = CacheManager.compute_hash("过期测试")
        cursor = cache_manager.conn.cursor()
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute(
            """
            INSERT INTO analysis_cache
            (content_hash, script_name, provider, model, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (content_hash, "expired.json", "deepseek", "default", yesterday),
        )
        cache_manager.conn.commit()

        # Create a non-expired entry
        cache_manager.set(
            content_hash=CacheManager.compute_hash("有效测试"),
            script_name="valid.json",
            provider="deepseek",
            model="default",
        )

        # Cleanup
        removed = cache_manager.cleanup_expired()
        assert removed == 1

        # Verify expired entry is gone
        assert cache_manager.get(content_hash, "deepseek", "default") is None

    def test_clear_all(self, cache_manager):
        """Test clear_all removes all entries."""
        # Create multiple entries
        for i in range(5):
            cache_manager.set(
                content_hash=CacheManager.compute_hash(f"清空测试{i}"),
                script_name=f"clear_{i}.json",
                provider="deepseek",
                model="default",
            )

        # Clear all
        removed = cache_manager.clear_all()
        assert removed == 5

        # Verify all entries are gone
        entries, total = cache_manager.list_all()
        assert total == 0

    def test_get_stats_empty(self, cache_manager):
        """Test get_stats on empty database."""
        stats = cache_manager.get_stats()
        assert stats.total_entries == 0
        assert stats.total_hits == 0
        assert stats.total_misses == 0
        assert stats.hit_rate == 0.0

    def test_get_stats_with_entries(self, cache_manager):
        """Test get_stats with entries."""
        # Create entries with different providers/models
        cache_manager.set(
            content_hash=CacheManager.compute_hash("统计测试1"),
            script_name="stats1.json",
            provider="deepseek",
            model="default",
        )
        cache_manager.set(
            content_hash=CacheManager.compute_hash("统计测试2"),
            script_name="stats2.json",
            provider="gemini",
            model="gemini-2.5-flash",
        )

        stats = cache_manager.get_stats()
        assert stats.total_entries == 2
        assert "deepseek" in stats.entries_by_provider
        assert "gemini" in stats.entries_by_provider
        assert stats.entries_by_provider["deepseek"] == 1
        assert stats.entries_by_provider["gemini"] == 1

    def test_hit_miss_tracking(self, cache_manager):
        """Test that hits and misses are tracked correctly."""
        content_hash = CacheManager.compute_hash("命中测试")

        # Miss (entry doesn't exist)
        cache_manager.get(content_hash, "deepseek", "default")

        stats = cache_manager.get_stats()
        assert stats.total_misses == 1
        assert stats.total_hits == 0

        # Create entry
        cache_manager.set(
            content_hash=content_hash,
            script_name="hit_test.json",
            provider="deepseek",
            model="default",
        )

        # Hit (entry exists)
        cache_manager.get(content_hash, "deepseek", "default")

        stats = cache_manager.get_stats()
        assert stats.total_hits == 1
        assert stats.total_misses == 1
        assert stats.hit_rate == 0.5

    def test_context_manager(self, temp_db):
        """Test CacheManager as context manager."""
        with CacheManager(db_path=temp_db) as manager:
            manager.set(
                content_hash=CacheManager.compute_hash("上下文测试"),
                script_name="context.json",
                provider="deepseek",
                model="default",
            )
            entries, _ = manager.list_all()
            assert len(entries) == 1
        # Connection should be closed after context exit

    def test_json_serialization(self, cache_manager):
        """Test that JSON data is correctly serialized and deserialized."""
        content_hash = CacheManager.compute_hash("JSON测试")
        stage1_data = {
            "tccs": [
                {
                    "id": "TCC_01",
                    "super_objective": "测试超级目标",
                    "chinese_text": "中文测试",
                }
            ]
        }

        cache_manager.set(
            content_hash=content_hash,
            script_name="json_test.json",
            provider="deepseek",
            model="default",
            stage1_result=stage1_data,
        )

        result = cache_manager.get(content_hash, "deepseek", "default")
        assert result is not None

        # Parse the stored JSON
        stored_data = json.loads(result.stage1_result)
        assert stored_data["tccs"][0]["id"] == "TCC_01"
        assert stored_data["tccs"][0]["chinese_text"] == "中文测试"


class TestAnalysisCache:
    """Tests for AnalysisCache model."""

    def test_to_dict(self):
        """Test to_dict conversion."""
        cache = AnalysisCache(
            id=1,
            content_hash="abc123",
            script_name="test.json",
            provider="deepseek",
            model="default",
            scene_count=5,
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        d = cache.to_dict()
        assert d["id"] == 1
        assert d["content_hash"] == "abc123"
        assert d["script_name"] == "test.json"
        assert d["scene_count"] == 5
        assert d["created_at"] == "2025-01-01T12:00:00"


class TestCacheStats:
    """Tests for CacheStats model."""

    def test_to_dict(self):
        """Test to_dict conversion."""
        stats = CacheStats(
            total_entries=10,
            total_hits=80,
            total_misses=20,
            hit_rate=0.8,
            cache_size_bytes=1024,
            entries_by_provider={"deepseek": 5, "gemini": 5},
        )

        d = stats.to_dict()
        assert d["total_entries"] == 10
        assert d["total_hits"] == 80
        assert d["total_misses"] == 20
        assert d["hit_rate"] == 0.8
        assert d["entries_by_provider"]["deepseek"] == 5

    def test_hit_rate_rounding(self):
        """Test that hit_rate is properly rounded."""
        stats = CacheStats(
            hit_rate=0.33333333,
        )

        d = stats.to_dict()
        assert d["hit_rate"] == 0.3333


class TestInitDatabase:
    """Tests for database initialization."""

    def test_init_creates_tables(self):
        """Test that init_database creates required tables."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            conn = init_database(db_path)

            # Check tables exist
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            assert "analysis_cache" in tables
            assert "cache_stats" in tables

            conn.close()
        finally:
            os.unlink(db_path)

    def test_init_creates_indexes(self):
        """Test that init_database creates indexes."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            conn = init_database(db_path)

            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            indexes = [row[0] for row in cursor.fetchall()]

            assert "idx_content_hash" in indexes
            assert "idx_expires_at" in indexes
            assert "idx_script_name" in indexes
            assert "idx_provider_model" in indexes

            conn.close()
        finally:
            os.unlink(db_path)

    def test_init_creates_directory(self):
        """Test that init_database creates parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "subdir", "nested", "cache.db")

            conn = init_database(db_path)
            assert os.path.exists(db_path)
            conn.close()

    def test_init_initializes_stats(self):
        """Test that init_database creates initial stats row."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            conn = init_database(db_path)

            cursor = conn.cursor()
            cursor.execute("SELECT hits, misses FROM cache_stats")
            row = cursor.fetchone()

            assert row is not None
            assert row["hits"] == 0
            assert row["misses"] == 0

            conn.close()
        finally:
            os.unlink(db_path)
