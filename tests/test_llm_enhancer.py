"""
Unit tests for LLM Enhanced Parser
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from langchain_core.messages import AIMessage

from src.parser.llm_enhancer import LLMEnhancedParser
from prompts.schemas import Script, Scene, SetupPayoff, RelationChange, InfoChange


class TestLLMEnhancedParser:
    """Test LLM Enhanced Parser functionality."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        llm = Mock()
        return llm

    @pytest.fixture
    def parser(self, mock_llm):
        """Create an LLM Enhanced Parser instance."""
        return LLMEnhancedParser(llm=mock_llm)

    @pytest.fixture
    def simple_script_path(self):
        """Path to simple test script."""
        return "examples/test_scripts/simple_script.txt"

    def test_parser_initialization(self, parser):
        """Test that parser initializes correctly."""
        assert parser is not None
        assert parser.llm is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'validate')

    def test_prompts_loaded(self, parser):
        """Test that all prompts are loaded."""
        assert "scene_mission" in parser.prompts
        assert "setup_payoff" in parser.prompts
        assert "relation_change" in parser.prompts
        assert "info_change" in parser.prompts
        assert "key_events" in parser.prompts

        # Check prompts are not empty
        assert len(parser.prompts["scene_mission"]) > 0

    def test_parse_json_response_direct(self, parser):
        """Test parsing clean JSON response."""
        response = '{"scene_mission": "Test mission"}'
        result = parser._parse_json_response(response)

        assert result["scene_mission"] == "Test mission"

    def test_parse_json_response_with_markdown(self, parser):
        """Test parsing JSON wrapped in markdown code fence."""
        response = '''Here is the result:
```json
{
  "scene_mission": "Test mission"
}
```
That's the analysis.'''

        result = parser._parse_json_response(response)
        assert result["scene_mission"] == "Test mission"

    def test_parse_json_response_with_text(self, parser):
        """Test parsing JSON with surrounding text."""
        response = 'Some intro text {"scene_mission": "Test mission"} some outro text'
        result = parser._parse_json_response(response)

        assert result["scene_mission"] == "Test mission"

    def test_parse_json_response_invalid(self, parser):
        """Test handling invalid JSON."""
        response = 'This is not JSON at all'
        result = parser._parse_json_response(response)

        assert result == {}

    def test_extract_scene_mission(self, parser, mock_llm):
        """Test scene mission extraction."""
        # Mock LLM response
        mock_response = AIMessage(content='{"scene_mission": "悟空决定接受委托"}')
        mock_llm.invoke.return_value = mock_response

        scene_id = "S01"
        setting = "酒吧 - 夜"
        scene_text = "悟空和玉鼠精对话..."

        result = parser._extract_scene_mission(scene_id, setting, scene_text)

        assert result == "悟空决定接受委托"
        assert mock_llm.invoke.called

    def test_extract_setup_payoff(self, parser, mock_llm):
        """Test setup-payoff extraction."""
        # Mock LLM response
        mock_response = AIMessage(content='{"setup_for": ["S03"], "payoff_from": ["S01"]}')
        mock_llm.invoke.return_value = mock_response

        scene_id = "S02"
        scene_text = "..."
        all_scenes = [
            Scene(scene_id="S01", setting="酒吧", characters=["悟空"], scene_mission="待LLM提取场景目标"),
            Scene(scene_id="S02", setting="办公室", characters=["悟空"], scene_mission="待LLM提取场景目标"),
            Scene(scene_id="S03", setting="仓库", characters=["悟空"], scene_mission="待LLM提取场景目标")
        ]

        result = parser._extract_setup_payoff(scene_id, scene_text, all_scenes)

        assert isinstance(result, SetupPayoff)
        assert "S03" in result.setup_for
        assert "S01" in result.payoff_from

    def test_extract_relation_changes(self, parser, mock_llm):
        """Test relation changes extraction."""
        # Mock LLM response
        mock_response = AIMessage(content='''{
            "relation_changes": [
                {
                    "chars": ["悟空", "玉鼠精"],
                    "from": "陌生冷淡",
                    "to": "合作关系"
                }
            ]
        }''')
        mock_llm.invoke.return_value = mock_response

        scene_id = "S01"
        scene_text = "..."
        characters = ["悟空", "玉鼠精"]

        result = parser._extract_relation_changes(scene_id, scene_text, characters)

        assert len(result) == 1
        assert isinstance(result[0], RelationChange)
        assert result[0].chars == ["悟空", "玉鼠精"]

    def test_extract_info_changes(self, parser, mock_llm):
        """Test info changes extraction."""
        # Mock LLM response
        mock_response = AIMessage(content='''{
            "info_changes": [
                {
                    "character": "悟空",
                    "learned": "发现箱子里的商品都是假货"
                }
            ]
        }''')
        mock_llm.invoke.return_value = mock_response

        scene_id = "S03"
        scene_text = "..."
        characters = ["悟空"]

        result = parser._extract_info_changes(scene_id, scene_text, characters)

        assert len(result) == 1
        assert isinstance(result[0], InfoChange)
        assert result[0].character == "悟空"
        assert result[0].learned == "发现箱子里的商品都是假货"

    def test_extract_key_events(self, parser, mock_llm):
        """Test key events extraction."""
        # Mock LLM response
        mock_response = AIMessage(content='''{
            "key_events": [
                "玉鼠精提出委托",
                "悟空同意调查",
                "哪吒提供线索"
            ]
        }''')
        mock_llm.invoke.return_value = mock_response

        scene_id = "S01"
        scene_text = "..."
        characters = ["悟空", "玉鼠精"]

        result = parser._extract_key_events(scene_id, scene_text, characters)

        assert len(result) == 3
        assert "玉鼠精提出委托" in result

    @pytest.mark.integration
    def test_enhance_scene(self, parser, mock_llm):
        """Test full scene enhancement."""
        # Mock all LLM responses
        mock_llm.invoke.side_effect = [
            AIMessage(content='{"scene_mission": "测试场景的主要戏剧目标"}'),
            AIMessage(content='{"setup_for": [], "payoff_from": []}'),
            AIMessage(content='{"relation_changes": []}'),
            AIMessage(content='{"info_changes": []}'),
            AIMessage(content='{"key_events": ["事件1", "事件2"]}')
        ]

        basic_scene = Scene(
            scene_id="S01",
            setting="酒吧",
            characters=["悟空"],
            scene_mission="待LLM提取场景目标",
            key_events=[],
            setup_payoff=SetupPayoff()
        )

        scene_text = "测试场景内容"
        all_scenes = [basic_scene]

        result = parser._enhance_scene(basic_scene, scene_text, all_scenes)

        assert result.scene_id == "S01"
        assert result.scene_mission == "测试场景的主要戏剧目标"
        assert len(result.key_events) == 2
        assert mock_llm.invoke.call_count == 5

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual LLM and API key")
    def test_parse_real_script(self, simple_script_path):
        """
        Integration test with real LLM.

        NOTE: This test is skipped by default as it requires:
        - Valid API key in environment
        - Network connection
        - LLM API availability

        To run: pytest tests/test_llm_enhancer.py::TestLLMEnhancedParser::test_parse_real_script -v
        """
        from src.pipeline import create_llm

        # Create real LLM
        llm = create_llm(provider="deepseek", model_name="deepseek-chat")

        # Create parser
        parser = LLMEnhancedParser(llm=llm)

        # Parse script
        script = parser.parse(simple_script_path)

        # Assertions
        assert isinstance(script, Script)
        assert len(script.scenes) == 3

        # Check first scene is enhanced
        first_scene = script.scenes[0]
        assert first_scene.scene_mission != "待LLM提取场景目标"
        assert len(first_scene.key_events) > 0

        # Validate script
        warnings = parser.validate(script)
        print(f"\nValidation warnings: {warnings}")

    def test_llm_error_handling(self, parser, mock_llm):
        """Test error handling when LLM fails."""
        # Mock LLM to raise exception
        mock_llm.invoke.side_effect = Exception("LLM API Error")

        scene_id = "S01"
        setting = "test"
        scene_text = "test"

        # Should not raise, but return default value
        result = parser._extract_scene_mission(scene_id, setting, scene_text)

        assert result == "待LLM提取场景目标"

    def test_empty_response_handling(self, parser, mock_llm):
        """Test handling of empty LLM responses."""
        # Mock empty response
        mock_response = AIMessage(content='{}')
        mock_llm.invoke.return_value = mock_response

        scene_id = "S01"
        scene_text = "..."
        characters = []

        # Should return empty lists
        key_events = parser._extract_key_events(scene_id, scene_text, characters)
        assert key_events == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
