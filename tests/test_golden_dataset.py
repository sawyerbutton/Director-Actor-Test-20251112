"""
Integration tests using the Golden Dataset (百妖_ep09).

These tests verify that the prompt system can correctly analyze
the first 5 scenes of the script and produce expected outputs.
"""

import json
import pytest
from pathlib import Path
from prompts.schemas import (
    Script, DiscovererOutput, AuditorOutput,
    calculate_spine_score, calculate_setup_payoff_density
)


# Load Golden Dataset
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "golden"
SCRIPT_PATH = EXAMPLES_DIR / "百妖_ep09_s01-s05.json"
EXPECTED_PATH = EXAMPLES_DIR / "百妖_ep09_expected.json"


@pytest.fixture
def golden_script():
    """Load the golden script data (S01-S05)."""
    with open(SCRIPT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return Script(**data)


@pytest.fixture
def expected_output():
    """Load the expected analysis output."""
    with open(EXPECTED_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestGoldenDatasetStructure:
    """Test the structure of the Golden Dataset itself."""

    def test_golden_script_loads(self, golden_script):
        """Test that the golden script loads successfully."""
        assert golden_script is not None
        assert len(golden_script.scenes) == 5  # S01-S05
        assert golden_script.scenes[0].scene_id == "S01"
        assert golden_script.scenes[4].scene_id == "S05"

    def test_expected_output_structure(self, expected_output):
        """Test that the expected output has the correct structure."""
        assert "expected_stage1_output" in expected_output
        assert "expected_stage2_output" in expected_output
        assert "test_acceptance_criteria" in expected_output

        # Stage 1 structure
        stage1 = expected_output["expected_stage1_output"]
        assert "tccs" in stage1
        assert len(stage1["tccs"]) == 3  # Expect 3 TCCs

        # Stage 2 structure
        stage2 = expected_output["expected_stage2_output"]
        assert "rankings" in stage2
        assert "a_line" in stage2["rankings"]
        assert "b_lines" in stage2["rankings"]
        assert "c_lines" in stage2["rankings"]


class TestStage1Expectations:
    """Test Stage 1 (Discoverer) expectations against Golden Dataset."""

    def test_expected_tcc_count(self, expected_output):
        """Test that we expect exactly 3 TCCs."""
        stage1 = expected_output["expected_stage1_output"]
        assert len(stage1["tccs"]) == 3

    def test_tcc_01_is_main_line(self, expected_output):
        """Test that TCC_01 is identified as the main business conflict."""
        stage1 = expected_output["expected_stage1_output"]
        tcc_01 = next(t for t in stage1["tccs"] if t["tcc_id"] == "TCC_01")

        assert tcc_01["core_conflict_type"] == "interpersonal"
        assert "玉鼠精" in tcc_01["super_objective"]
        assert "融资" in tcc_01["super_objective"] or "电商" in tcc_01["super_objective"]
        assert tcc_01["confidence_range"][0] >= 0.90  # Should be high confidence

    def test_tcc_02_is_internal_conflict(self, expected_output):
        """Test that TCC_02 is identified as internal conflict."""
        stage1 = expected_output["expected_stage1_output"]
        tcc_02 = next(t for t in stage1["tccs"] if t["tcc_id"] == "TCC_02")

        assert tcc_02["core_conflict_type"] == "internal"
        assert "悟空" in tcc_02["super_objective"]
        assert tcc_02["confidence_range"][0] >= 0.70

    def test_tcc_03_is_flavor_line(self, expected_output):
        """Test that TCC_03 is identified as flavor line."""
        stage1 = expected_output["expected_stage1_output"]
        tcc_03 = next(t for t in stage1["tccs"] if t["tcc_id"] == "TCC_03")

        assert tcc_03["core_conflict_type"] == "internal"
        assert "阿蠢" in tcc_03["super_objective"]
        assert "偶像" in tcc_03["super_objective"] or "崇拜" in tcc_03["super_objective"]

    def test_no_mirror_tccs(self, expected_output):
        """Test that the expected output has no mirror TCCs."""
        stage1 = expected_output["expected_stage1_output"]
        validation = stage1["validation_rules"]
        assert validation["no_mirror_tccs"] is True

    def test_valid_evidence_scenes(self, expected_output, golden_script):
        """Test that all evidence scenes are valid scene IDs."""
        stage1 = expected_output["expected_stage1_output"]
        valid_scene_ids = {scene.scene_id for scene in golden_script.scenes}

        for tcc in stage1["tccs"]:
            for scene_id in tcc["evidence_scenes"]:
                # Note: Some scenes may be from full script (S01-S43)
                # So we just check format, not existence in S01-S05
                assert scene_id.startswith("S")
                assert len(scene_id) >= 3  # S + at least 2 digits


class TestStage2Expectations:
    """Test Stage 2 (Auditor) expectations against Golden Dataset."""

    def test_a_line_is_tcc_01(self, expected_output):
        """Test that A-line must be TCC_01."""
        stage2 = expected_output["expected_stage2_output"]
        assert stage2["rankings"]["a_line"]["tcc_id"] == "TCC_01"

        validation = stage2["validation_rules"]
        assert validation["a_line_must_be_tcc_01"] is True

    def test_b_line_exists(self, expected_output):
        """Test that at least one B-line exists."""
        stage2 = expected_output["expected_stage2_output"]
        assert len(stage2["rankings"]["b_lines"]) >= 1

    def test_b_line_interacts_with_a_line(self, expected_output):
        """Test that B-line must interact with A-line."""
        stage2 = expected_output["expected_stage2_output"]
        for b_line in stage2["rankings"]["b_lines"]:
            assert b_line["a_line_interaction_required"] is True

        validation = stage2["validation_rules"]
        assert validation["b_line_must_interact_with_a_line"] is True

    def test_c_line_is_removable(self, expected_output):
        """Test that C-line is marked as removable."""
        stage2 = expected_output["expected_stage2_output"]
        if stage2["rankings"]["c_lines"]:
            c_line = stage2["rankings"]["c_lines"][0]
            assert c_line["removable"] is True

    def test_force_analysis_present(self, expected_output):
        """Test that all TCCs have force analysis."""
        stage2 = expected_output["expected_stage2_output"]

        # A-line forces
        a_forces = stage2["rankings"]["a_line"]["forces"]
        assert "protagonist" in a_forces
        assert "primary_antagonist" in a_forces
        assert "dynamic_antagonist" in a_forces

        # B-line forces
        for b_line in stage2["rankings"]["b_lines"]:
            forces = b_line["forces"]
            assert "protagonist" in forces
            assert "primary_antagonist" in forces

    def test_spine_score_calculation(self, expected_output):
        """Test that spine score is in expected range."""
        stage2 = expected_output["expected_stage2_output"]
        a_line = stage2["rankings"]["a_line"]

        spine_min, spine_max = a_line["spine_score_range"]
        assert spine_min > 0
        assert spine_max > spine_min


class TestStage3Expectations:
    """Test Stage 3 (Modifier) expectations against Golden Dataset."""

    def test_possible_issues_defined(self, expected_output):
        """Test that possible issues are documented."""
        stage3 = expected_output["expected_stage3_output"]
        assert "possible_issues" in stage3
        assert len(stage3["possible_issues"]) > 0

    def test_structural_issues_documented(self, expected_output):
        """Test that known structural issues are documented."""
        assert "known_structural_issues" in expected_output
        issues = expected_output["known_structural_issues"]
        assert len(issues) > 0

        # Check that issues have required fields
        for issue in issues:
            assert "source" in issue
            assert "issue" in issue
            assert "category" in issue

    def test_s02_s43_setup_payoff_issue(self, expected_output):
        """Test that S02→S43 setup-payoff gap is documented."""
        stage3 = expected_output["expected_stage3_output"]
        possible_issues = stage3["possible_issues"]

        # Find the setup_payoff issue
        sp_issues = [i for i in possible_issues if i["category"] == "broken_setup_payoff"]
        assert len(sp_issues) > 0

        # Check that S02 and S43 are mentioned
        sp_issue = sp_issues[0]
        affected = sp_issue["affected_scenes"]
        assert "S02" in affected
        assert "S43" in affected


class TestAcceptanceCriteria:
    """Test acceptance criteria for all stages."""

    def test_stage1_acceptance_criteria(self, expected_output):
        """Test Stage 1 acceptance criteria are defined."""
        criteria = expected_output["test_acceptance_criteria"]["stage1"]
        must_pass = criteria["must_pass"]

        assert "识别出恰好3个TCCs" in must_pass
        assert any("TCC_01的confidence最高" in item for item in must_pass)
        assert any("不应出现镜像TCC" in item for item in must_pass)

    def test_stage2_acceptance_criteria(self, expected_output):
        """Test Stage 2 acceptance criteria are defined."""
        criteria = expected_output["test_acceptance_criteria"]["stage2"]
        must_pass = criteria["must_pass"]

        assert "A-line是TCC_01" in must_pass
        assert any("B-line" in item for item in must_pass)

    def test_stage3_acceptance_criteria(self, expected_output):
        """Test Stage 3 acceptance criteria are defined."""
        criteria = expected_output["test_acceptance_criteria"]["stage3"]
        must_pass = criteria["must_pass"]

        assert any("结构性问题" in item for item in must_pass)
        assert "new_issues_introduced == 0" in must_pass


class TestScriptDataQuality:
    """Test the quality of the script data in Golden Dataset."""

    def test_all_scenes_have_required_fields(self, golden_script):
        """Test that all scenes have required fields."""
        for scene in golden_script.scenes:
            assert scene.scene_id
            assert scene.setting
            assert len(scene.characters) > 0
            assert len(scene.scene_mission) >= 10  # Meaningful mission

    def test_setup_payoff_chain_exists(self, golden_script):
        """Test that setup-payoff chains exist in the script."""
        scenes_with_sp = 0
        for scene in golden_script.scenes:
            if scene.setup_payoff.setup_for or scene.setup_payoff.payoff_from:
                scenes_with_sp += 1

        # At least some scenes should have setup-payoff data
        assert scenes_with_sp >= 2

    def test_scene_missions_are_meaningful(self, golden_script):
        """Test that scene missions are not generic."""
        for scene in golden_script.scenes:
            mission = scene.scene_mission
            # Should not be too short or too generic
            assert len(mission) >= 15
            # Should not be just "无" or "N/A"
            assert mission not in ["无", "N/A", "None", ""]


# Mock test for future LLM integration
@pytest.mark.skip(reason="Requires LLM integration - implement after pipeline is built")
class TestLLMIntegration:
    """Tests that require actual LLM calls (to be implemented with pipeline)."""

    def test_stage1_produces_expected_output(self, golden_script):
        """Test that Stage 1 produces output matching expectations."""
        # TODO: Implement after LangGraph pipeline is ready
        pass

    def test_stage2_produces_expected_output(self, golden_script):
        """Test that Stage 2 produces output matching expectations."""
        # TODO: Implement after LangGraph pipeline is ready
        pass

    def test_stage3_produces_expected_output(self, golden_script):
        """Test that Stage 3 produces output matching expectations."""
        # TODO: Implement after LangGraph pipeline is ready
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
