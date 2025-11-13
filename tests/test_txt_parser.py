"""
Unit tests for TXT Script Parser
"""

import pytest
from pathlib import Path
from src.parser.txt_parser import TXTScriptParser
from prompts.schemas import Script


class TestTXTScriptParser:
    """Test TXT script parser functionality."""

    @pytest.fixture
    def parser(self):
        """Create a TXT parser instance."""
        return TXTScriptParser()

    @pytest.fixture
    def simple_script_path(self):
        """Path to simple test script."""
        return "examples/test_scripts/simple_script.txt"

    def test_parser_initialization(self, parser):
        """Test that parser initializes correctly."""
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'validate')

    def test_parse_simple_script(self, parser, simple_script_path):
        """Test parsing a simple script."""
        script = parser.parse(simple_script_path)

        # Should be a Script object
        assert isinstance(script, Script)

        # Should have scenes
        assert len(script.scenes) > 0

        # First scene should have expected properties
        first_scene = script.scenes[0]
        assert first_scene.scene_id is not None
        assert first_scene.characters is not None

    def test_scene_count(self, parser, simple_script_path):
        """Test that correct number of scenes are identified."""
        script = parser.parse(simple_script_path)

        # Simple script has 3 scenes
        assert len(script.scenes) == 3

    def test_scene_ids(self, parser, simple_script_path):
        """Test that scene IDs are generated correctly."""
        script = parser.parse(simple_script_path)

        scene_ids = [scene.scene_id for scene in script.scenes]

        # Should have S01, S02, S03
        assert "S01" in scene_ids
        assert "S02" in scene_ids
        assert "S03" in scene_ids

    def test_character_extraction(self, parser, simple_script_path):
        """Test that characters are extracted from dialogue."""
        script = parser.parse(simple_script_path)

        # First scene should have 悟空 and 玉鼠精
        first_scene_characters = script.scenes[0].characters
        assert "悟空" in first_scene_characters
        assert "玉鼠精" in first_scene_characters

        # Second scene should have 悟空 and 哪吒
        second_scene_characters = script.scenes[1].characters
        assert "悟空" in second_scene_characters
        assert "哪吒" in second_scene_characters

    def test_validation_warnings(self, parser, simple_script_path):
        """Test validation of parsed script."""
        script = parser.parse(simple_script_path)
        warnings = parser.validate(script)

        # Should have some basic validation
        assert isinstance(warnings, list)

    def test_file_not_found(self, parser):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent_file.txt")

    def test_invalid_file_type(self, parser):
        """Test handling of wrong file type."""
        with pytest.raises(ValueError):
            parser.parse("script.json")  # Wrong extension

    def test_chinese_number_conversion(self, parser):
        """Test conversion of Chinese numbers to Arabic."""
        assert parser._chinese_to_number("一") == 1
        assert parser._chinese_to_number("五") == 5
        assert parser._chinese_to_number("十") == 10

    def test_scene_splitting_with_separators(self, parser):
        """Test scene splitting with different separators."""
        # Create a temporary test file
        test_content = """场景 1: 测试场景一

内容1

---

场景 2: 测试场景二

内容2

===

场景 3: 测试场景三

内容3
"""
        # Write to temp file
        temp_file = Path("tests/temp_test.txt")
        temp_file.write_text(test_content, encoding='utf-8')

        try:
            script = parser.parse(str(temp_file))
            assert len(script.scenes) == 3
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()

    def test_empty_scene_handling(self, parser):
        """Test handling of empty scenes."""
        test_content = """场景 1: 空场景

---

场景 2: 有内容的场景

悟空：测试台词
"""
        temp_file = Path("tests/temp_empty.txt")
        temp_file.write_text(test_content, encoding='utf-8')

        try:
            script = parser.parse(str(temp_file))
            # Should still parse scenes, even if empty
            assert len(script.scenes) >= 1
        finally:
            if temp_file.exists():
                temp_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
