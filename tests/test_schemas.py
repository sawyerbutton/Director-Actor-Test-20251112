"""
Unit tests for schemas.py validation functions and utilities.
"""

import pytest
from prompts.schemas import (
    TCC, Script, Scene, SetupPayoff, InfoChange, RelationChange, KeyObject,
    DiscovererOutput, DiscovererMetadata,
    AuditorOutput, Rankings, ALineRanking, BLineRanking, CLineRanking,
    RankingReasoning, BLineReasoning, CLineReasoning, Forces, AuditorMetrics,
    ModifierOutput, ModificationLogEntry, ModificationValidation,
    validate_setup_payoff_integrity,
    calculate_setup_payoff_density,
    calculate_spine_score,
    calculate_heart_score,
    calculate_a_line_interaction,
    validate_tcc_independence,
)
from pydantic import ValidationError


class TestTCCValidation:
    """Test TCC model validation."""

    def test_valid_tcc(self):
        """Test creating a valid TCC."""
        tcc = TCC(
            tcc_id="TCC_01",
            super_objective="玉鼠精的电商平台融资计划",
            core_conflict_type="interpersonal",
            evidence_scenes=["S03", "S05"],
            confidence=0.95
        )
        assert tcc.tcc_id == "TCC_01"
        assert tcc.confidence == 0.95

    def test_tcc_id_pattern(self):
        """Test TCC ID pattern validation."""
        with pytest.raises(ValidationError):
            TCC(
                tcc_id="INVALID",  # Wrong pattern
                super_objective="Test objective",
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "S02"],
                confidence=0.8
            )

    def test_confidence_minimum(self):
        """Test confidence score minimum validation."""
        with pytest.raises(ValidationError, match="too low"):
            TCC(
                tcc_id="TCC_01",
                super_objective="Test objective",
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "S02"],
                confidence=0.3  # Below 0.5 minimum
            )

    def test_super_objective_length(self):
        """Test super objective length constraints."""
        # Too short
        with pytest.raises(ValidationError):
            TCC(
                tcc_id="TCC_01",
                super_objective="Short",  # < 10 chars
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "S02"],
                confidence=0.8
            )

        # Too long
        with pytest.raises(ValidationError):
            TCC(
                tcc_id="TCC_01",
                super_objective="x" * 201,  # > 200 chars
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "S02"],
                confidence=0.8
            )

    def test_invalid_scene_id_format(self):
        """Test scene ID format validation."""
        with pytest.raises(ValidationError, match="Invalid scene ID format"):
            TCC(
                tcc_id="TCC_01",
                super_objective="Test objective",
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "INVALID"],  # Invalid format
                confidence=0.8
            )

    def test_minimum_evidence_scenes(self):
        """Test minimum evidence scenes requirement."""
        with pytest.raises(ValidationError):
            TCC(
                tcc_id="TCC_01",
                super_objective="Test objective",
                core_conflict_type="interpersonal",
                evidence_scenes=["S01"],  # Only 1 scene (need at least 2)
                confidence=0.8
            )


class TestDiscovererOutput:
    """Test Discoverer output validation."""

    def test_valid_discoverer_output(self):
        """Test creating valid discoverer output."""
        output = DiscovererOutput(
            tccs=[
                TCC(
                    tcc_id="TCC_01",
                    super_objective="Test objective 1",
                    core_conflict_type="interpersonal",
                    evidence_scenes=["S01", "S02"],
                    confidence=0.95
                )
            ],
            metadata=DiscovererMetadata(
                total_scenes_analyzed=50,
                primary_evidence_available=True,
                fallback_mode=False
            )
        )
        assert len(output.tccs) == 1
        assert output.metadata.fallback_mode is False

    def test_duplicate_tcc_ids(self):
        """Test duplicate TCC ID detection."""
        with pytest.raises(ValidationError, match="Duplicate TCC IDs"):
            DiscovererOutput(
                tccs=[
                    TCC(
                        tcc_id="TCC_01",
                        super_objective="Test objective 1",
                        core_conflict_type="interpersonal",
                        evidence_scenes=["S01", "S02"],
                        confidence=0.95
                    ),
                    TCC(
                        tcc_id="TCC_01",  # Duplicate!
                        super_objective="Test objective 2",
                        core_conflict_type="internal",
                        evidence_scenes=["S03", "S04"],
                        confidence=0.85
                    )
                ],
                metadata=DiscovererMetadata(
                    total_scenes_analyzed=50,
                    primary_evidence_available=True,
                    fallback_mode=False
                )
            )

    def test_max_tccs(self):
        """Test maximum TCC limit."""
        with pytest.raises(ValidationError):
            DiscovererOutput(
                tccs=[
                    TCC(
                        tcc_id=f"TCC_{i:02d}",
                        super_objective=f"Test objective {i}",
                        core_conflict_type="interpersonal",
                        evidence_scenes=["S01", "S02"],
                        confidence=0.8
                    )
                    for i in range(1, 7)  # 6 TCCs (max is 5)
                ],
                metadata=DiscovererMetadata(
                    total_scenes_analyzed=50,
                    primary_evidence_available=True,
                    fallback_mode=False
                )
            )


class TestCalculationFunctions:
    """Test calculation utility functions."""

    def test_calculate_setup_payoff_density(self):
        """Test setup-payoff density calculation."""
        script = Script(scenes=[
            Scene(
                scene_id="S01",
                setting="Test setting",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=["S02"], payoff_from=[])
            ),
            Scene(
                scene_id="S02",
                setting="Test setting",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=[], payoff_from=["S01"])
            ),
            Scene(
                scene_id="S03",
                setting="Test setting",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=[], payoff_from=[])  # Empty
            )
        ])

        # Test with all 3 scenes
        density = calculate_setup_payoff_density(script, ["S01", "S02", "S03"])
        assert density == pytest.approx(2/3, rel=0.01)  # 2 out of 3 have SP data

        # Test with only scenes that have SP data
        density = calculate_setup_payoff_density(script, ["S01", "S02"])
        assert density == 1.0

    def test_calculate_spine_score(self):
        """Test spine score calculation."""
        # Basic calculation
        score = calculate_spine_score(scene_count=5, setup_payoff_density=0.8)
        assert score == pytest.approx(5 * 2 + 0.8 * 1.5, rel=0.01)  # 10 + 1.2 = 11.2

        # With climax bonus
        score_with_climax = calculate_spine_score(
            scene_count=5, setup_payoff_density=0.8, drives_climax=True
        )
        assert score_with_climax == pytest.approx(11.2 + 2.0, rel=0.01)  # 13.2

    def test_calculate_heart_score(self):
        """Test heart score calculation."""
        score = calculate_heart_score(emotional_intensity=0.875, a_line_interaction=0.75)
        assert score == pytest.approx(0.875 * 10 + 0.75 * 5, rel=0.01)  # 8.75 + 3.75 = 12.5

    def test_calculate_a_line_interaction(self):
        """Test A-line interaction calculation."""
        tcc_scenes = ["S05", "S10", "S18", "S25"]
        a_line_scenes = ["S03", "S05", "S10", "S12", "S15", "S20", "S25"]

        interaction = calculate_a_line_interaction(tcc_scenes, a_line_scenes)
        # Intersection: S05, S10, S25 → 3 scenes
        # min(4, 7) = 4
        assert interaction == pytest.approx(3/4, rel=0.01)

    def test_a_line_interaction_empty(self):
        """Test A-line interaction with empty input."""
        assert calculate_a_line_interaction([], ["S01"]) == 0.0
        assert calculate_a_line_interaction(["S01"], []) == 0.0


class TestTCCIndependence:
    """Test TCC independence validation."""

    def test_independent_tccs(self):
        """Test TCCs with low overlap (independent)."""
        tccs = [
            TCC(
                tcc_id="TCC_01",
                super_objective="Main business conflict",
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "S02", "S03", "S04", "S05"],
                confidence=0.95
            ),
            TCC(
                tcc_id="TCC_02",
                super_objective="Internal identity struggle",
                core_conflict_type="internal",
                evidence_scenes=["S10", "S20", "S30"],
                confidence=0.85
            )
        ]

        warnings = validate_tcc_independence(tccs)
        assert len(warnings) == 0  # No warnings for independent TCCs

    def test_mirror_tccs_detection(self):
        """Test detection of potential mirror TCCs (high overlap)."""
        tccs = [
            TCC(
                tcc_id="TCC_01",
                super_objective="Character A wants X",
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "S02", "S03", "S04", "S05"],
                confidence=0.95
            ),
            TCC(
                tcc_id="TCC_02",
                super_objective="Character B opposes X",
                core_conflict_type="interpersonal",
                evidence_scenes=["S01", "S02", "S03", "S04"],  # 4/5 overlap = 80%
                confidence=0.90
            )
        ]

        warnings = validate_tcc_independence(tccs)
        assert len(warnings) == 1
        assert "High overlap between TCC_01 and TCC_02" in warnings[0]
        assert "May be mirror conflicts" in warnings[0]


class TestSetupPayoffIntegrity:
    """Test setup-payoff chain integrity validation."""

    def test_valid_setup_payoff_chain(self):
        """Test valid bidirectional setup-payoff chain."""
        script = Script(scenes=[
            Scene(
                scene_id="S01",
                setting="Test",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=["S02"], payoff_from=[])
            ),
            Scene(
                scene_id="S02",
                setting="Test",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=[], payoff_from=["S01"])
            )
        ])

        errors = validate_setup_payoff_integrity(script)
        assert len(errors) == 0

    def test_broken_setup_payoff_chain(self):
        """Test broken setup-payoff chain detection."""
        script = Script(scenes=[
            Scene(
                scene_id="S01",
                setting="Test",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=["S02"], payoff_from=[])
            ),
            Scene(
                scene_id="S02",
                setting="Test",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=[], payoff_from=[])  # Missing S01!
            )
        ])

        errors = validate_setup_payoff_integrity(script)
        assert len(errors) == 1
        assert "doesn't have S01 in payoff_from" in errors[0]

    def test_nonexistent_scene_reference(self):
        """Test detection of references to non-existent scenes."""
        script = Script(scenes=[
            Scene(
                scene_id="S01",
                setting="Test",
                characters=["A"],
                scene_mission="Test mission",
                setup_payoff=SetupPayoff(setup_for=["S99"], payoff_from=[])  # S99 doesn't exist
            )
        ])

        errors = validate_setup_payoff_integrity(script)
        assert len(errors) == 1
        assert "non-existent scene S99" in errors[0]


class TestSceneValidation:
    """Test Scene model validation."""

    def test_valid_scene(self):
        """Test creating a valid scene."""
        scene = Scene(
            scene_id="S01",
            setting="日 内 办公室",
            characters=["悟空", "女娲"],
            scene_mission="Establish character dynamics",
            key_events=["悟空迟到", "女娲批评"],
            info_change=[
                InfoChange(character="悟空", learned="女娲很严格")
            ],
            relation_change=[
                RelationChange(chars=["悟空", "女娲"], from_="中立", to="紧张")
            ],
            key_object=[
                KeyObject(object="迟到记录", status="被记录")
            ],
            setup_payoff=SetupPayoff(setup_for=["S02"], payoff_from=[])
        )
        assert scene.scene_id == "S01"
        assert len(scene.characters) == 2

    def test_scene_id_pattern(self):
        """Test scene ID pattern validation."""
        # Valid patterns
        Scene(scene_id="S01", setting="Test", characters=["A"], scene_mission="Test mission description")
        Scene(scene_id="S99", setting="Test", characters=["A"], scene_mission="Test mission description")
        Scene(scene_id="S100", setting="Test", characters=["A"], scene_mission="Test mission description")

        # Invalid pattern
        with pytest.raises(ValidationError):
            Scene(scene_id="INVALID", setting="Test", characters=["A"], scene_mission="Test mission description")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
