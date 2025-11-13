"""
Pydantic schemas for the Script Analysis System.

These schemas ensure type safety and validation across all stages
of the analysis pipeline.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re


# ============================================================================
# Script Input Schemas
# ============================================================================

class InfoChange(BaseModel):
    """Information change in a scene."""
    character: str = Field(..., min_length=1)
    learned: str = Field(..., min_length=5)


class RelationChange(BaseModel):
    """Relationship change between characters."""
    model_config = {"populate_by_name": True}

    chars: List[str] = Field(..., min_length=2, max_length=2)
    from_: str = Field(..., alias="from", min_length=2)
    to: str = Field(..., min_length=2)


class KeyObject(BaseModel):
    """Key object in a scene."""
    object: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)


class SetupPayoff(BaseModel):
    """Setup-payoff causal relationships."""
    setup_for: List[str] = Field(default_factory=list)
    payoff_from: List[str] = Field(default_factory=list)


class Scene(BaseModel):
    """A single scene in the script."""
    scene_id: str = Field(..., pattern=r"^S\d{2,3}$")
    setting: str = Field(..., min_length=1)
    characters: List[str] = Field(..., min_length=1)
    scene_mission: str = Field(..., min_length=10)
    key_events: List[str] = Field(default_factory=list)
    info_change: List[InfoChange] = Field(default_factory=list)
    relation_change: List[RelationChange] = Field(default_factory=list)
    key_object: List[KeyObject] = Field(default_factory=list)
    setup_payoff: SetupPayoff = Field(default_factory=SetupPayoff)


class Script(BaseModel):
    """Complete script data."""
    scenes: List[Scene] = Field(..., min_length=1)

    @field_validator("scenes")
    @classmethod
    def validate_unique_scene_ids(cls, scenes: List[Scene]) -> List[Scene]:
        """Ensure all scene IDs are unique."""
        scene_ids = [s.scene_id for s in scenes]
        if len(scene_ids) != len(set(scene_ids)):
            duplicates = [sid for sid in scene_ids if scene_ids.count(sid) > 1]
            raise ValueError(f"Duplicate scene IDs found: {duplicates}")
        return scenes


# ============================================================================
# Stage 1: Discoverer Output Schemas
# ============================================================================

class TCC(BaseModel):
    """Theatrical Conflict Chain."""
    tcc_id: str = Field(..., pattern=r"^TCC_\d{2}$")
    super_objective: str = Field(..., min_length=10, max_length=200,
                                 description="Brief description of the TCC's super-objective")
    core_conflict_type: Literal["interpersonal", "internal", "ideological"]
    evidence_scenes: List[str] = Field(..., min_length=2,
                                       description="Scene IDs where this TCC appears")
    confidence: float = Field(..., ge=0.0, le=1.0,
                              description="Confidence score (0.5-1.0 for output)")

    @field_validator("confidence")
    @classmethod
    def validate_confidence_minimum(cls, confidence: float) -> float:
        """Ensure confidence is at least 0.5 for valid TCCs."""
        if confidence < 0.5:
            raise ValueError(f"Confidence {confidence} is too low (minimum 0.5)")
        return confidence

    @field_validator("evidence_scenes")
    @classmethod
    def validate_scene_ids(cls, scene_ids: List[str]) -> List[str]:
        """Ensure all scene IDs follow the pattern."""
        pattern = re.compile(r"^S\d{2,3}$")
        for sid in scene_ids:
            if not pattern.match(sid):
                raise ValueError(f"Invalid scene ID format: {sid}")
        return scene_ids


class DiscovererMetadata(BaseModel):
    """Metadata from the Discoverer stage."""
    total_scenes_analyzed: int = Field(..., ge=1)
    primary_evidence_available: bool
    fallback_mode: bool
    fallback_reason: Optional[str] = None


class DiscovererOutput(BaseModel):
    """Output from Stage 1: Discoverer."""
    tccs: List[TCC] = Field(..., min_length=1, max_length=5)
    metadata: DiscovererMetadata

    @field_validator("tccs")
    @classmethod
    def validate_unique_tcc_ids(cls, tccs: List[TCC]) -> List[TCC]:
        """Ensure all TCC IDs are unique."""
        tcc_ids = [t.tcc_id for t in tccs]
        if len(tcc_ids) != len(set(tcc_ids)):
            duplicates = [tid for tid in tcc_ids if tcc_ids.count(tid) > 1]
            raise ValueError(f"Duplicate TCC IDs found: {duplicates}")
        return tccs


# ============================================================================
# Stage 2: Auditor Output Schemas
# ============================================================================

class Forces(BaseModel):
    """Force dynamics in a TCC."""
    protagonist: str = Field(..., min_length=5)
    primary_antagonist: str = Field(..., min_length=5)
    dynamic_antagonist: Optional[List[str]] = None


class RankingReasoning(BaseModel):
    """Reasoning for ranking decision."""
    scene_count: int = Field(..., ge=1)
    setup_payoff_density: float = Field(..., ge=0.0, le=1.0)
    drives_climax: bool


class ALineRanking(BaseModel):
    """A-line ranking details."""
    tcc_id: str = Field(..., pattern=r"^TCC_\d{2}$")
    super_objective: str = Field(..., min_length=10)
    spine_score: float = Field(..., gt=0.0)
    reasoning: RankingReasoning
    forces: Forces


class BLineReasoning(BaseModel):
    """Reasoning for B-line ranking."""
    emotional_intensity: float = Field(..., ge=0.0, le=1.0)
    a_line_interaction: float = Field(..., ge=0.3, le=1.0)
    internal_conflict: bool


class BLineRanking(BaseModel):
    """B-line ranking details."""
    tcc_id: str = Field(..., pattern=r"^TCC_\d{2}$")
    super_objective: str = Field(..., min_length=10)
    heart_score: float = Field(..., gt=0.0)
    reasoning: BLineReasoning
    forces: Forces


class CLineReasoning(BaseModel):
    """Reasoning for C-line ranking."""
    thematic_relevance: float = Field(..., ge=0.0, le=1.0)
    removable: bool


class CLineRanking(BaseModel):
    """C-line ranking details."""
    tcc_id: str = Field(..., pattern=r"^TCC_\d{2}$")
    super_objective: str = Field(..., min_length=10)
    flavor_score: float = Field(..., gt=0.0)
    reasoning: CLineReasoning
    forces: Forces


class Rankings(BaseModel):
    """All TCC rankings."""
    a_line: ALineRanking
    b_lines: List[BLineRanking] = Field(default_factory=list, max_length=2)
    c_lines: List[CLineRanking] = Field(default_factory=list)


class AuditorMetrics(BaseModel):
    """Metrics from auditor analysis."""
    total_scenes: int = Field(..., ge=1)
    a_line_coverage: float = Field(..., ge=0.0, le=1.0)
    b_line_coverage: float = Field(..., ge=0.0, le=1.0)
    c_line_coverage: float = Field(..., ge=0.0, le=1.0)


class AuditorOutput(BaseModel):
    """Output from Stage 2: Auditor."""
    rankings: Rankings
    metrics: AuditorMetrics


# ============================================================================
# Stage 3: Modifier Input/Output Schemas
# ============================================================================

class SuggestedFix(BaseModel):
    """Suggested fix for an issue."""
    action: Literal["add_payoff_reference", "add_info_change", "add_relation_change",
                    "add_key_object", "fix_consistency"]
    target_scene: str = Field(..., pattern=r"^S\d{2,3}$")
    field: str = Field(..., min_length=1)
    value: Any


class Issue(BaseModel):
    """An issue identified in the audit."""
    issue_id: str = Field(..., pattern=r"^ISS_\d{3}$")
    severity: Literal["high", "medium", "low"]
    category: Literal["broken_setup_payoff", "missing_info_change",
                      "incomplete_relation_change", "missing_key_object"]
    description: str = Field(..., min_length=10)
    affected_scenes: List[str] = Field(..., min_length=1)
    suggested_fix: SuggestedFix


class AuditReport(BaseModel):
    """Audit report with identified issues."""
    issues: List[Issue] = Field(default_factory=list)


class ModificationLogEntry(BaseModel):
    """Log entry for a modification."""
    issue_id: str = Field(..., pattern=r"^ISS_\d{3}$")
    applied: bool
    scene_id: Optional[str] = None
    field: Optional[str] = None
    change_type: Optional[Literal["add", "append", "update"]] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reason: Optional[str] = None


class ModificationValidation(BaseModel):
    """Validation results after modification."""
    total_issues: int = Field(..., ge=0)
    fixed: int = Field(..., ge=0)
    skipped: int = Field(..., ge=0)
    new_issues_introduced: int = Field(..., ge=0)


class ModifierOutput(BaseModel):
    """Output from Stage 3: Modifier."""
    modified_script: Script
    modification_log: List[ModificationLogEntry]
    validation: ModificationValidation

    @model_validator(mode='after')
    def validate_fix_counts(self) -> 'ModifierOutput':
        """Ensure fix counts are consistent."""
        total = self.validation.fixed + self.validation.skipped
        if total != self.validation.total_issues:
            raise ValueError(
                f"Fix counts don't match: {self.validation.fixed} fixed + "
                f"{self.validation.skipped} skipped != {self.validation.total_issues} total"
            )
        return self


# ============================================================================
# Complete Pipeline Output
# ============================================================================

class PipelineOutput(BaseModel):
    """Complete output from the entire pipeline."""
    discoverer_output: DiscovererOutput
    auditor_output: AuditorOutput
    modifier_output: ModifierOutput
    pipeline_metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_scene_references(script: Script, scene_ids: List[str]) -> bool:
    """Validate that all referenced scene IDs exist in the script."""
    valid_ids = {scene.scene_id for scene in script.scenes}
    for sid in scene_ids:
        if sid not in valid_ids:
            raise ValueError(f"Scene ID {sid} not found in script")
    return True


def validate_setup_payoff_integrity(script: Script) -> List[str]:
    """
    Validate setup-payoff chain integrity.

    Returns a list of error messages (empty if valid).
    """
    errors = []
    scene_map = {scene.scene_id: scene for scene in script.scenes}

    for scene in script.scenes:
        # Check that all setup_for references exist
        for setup_id in scene.setup_payoff.setup_for:
            if setup_id not in scene_map:
                errors.append(
                    f"Scene {scene.scene_id} references non-existent scene {setup_id} in setup_for"
                )
            else:
                # Check reciprocal payoff_from
                target_scene = scene_map[setup_id]
                if scene.scene_id not in target_scene.setup_payoff.payoff_from:
                    errors.append(
                        f"Scene {scene.scene_id} sets up for {setup_id}, "
                        f"but {setup_id} doesn't have {scene.scene_id} in payoff_from"
                    )

        # Check that all payoff_from references exist
        for payoff_id in scene.setup_payoff.payoff_from:
            if payoff_id not in scene_map:
                errors.append(
                    f"Scene {scene.scene_id} references non-existent scene {payoff_id} in payoff_from"
                )

    return errors


def calculate_setup_payoff_density(script: Script, scene_ids: List[str]) -> float:
    """
    Calculate setup-payoff density for a set of scenes.

    Args:
        script: The complete script
        scene_ids: List of scene IDs to calculate density for

    Returns:
        Float between 0.0 and 1.0 representing density
    """
    scene_map = {scene.scene_id: scene for scene in script.scenes}
    scenes_with_sp = 0

    for sid in scene_ids:
        if sid in scene_map:
            scene = scene_map[sid]
            if scene.setup_payoff.setup_for or scene.setup_payoff.payoff_from:
                scenes_with_sp += 1

    return scenes_with_sp / len(scene_ids) if scene_ids else 0.0


def calculate_spine_score(scene_count: int, setup_payoff_density: float,
                         drives_climax: bool = False) -> float:
    """
    Calculate spine score for A-line ranking.

    Formula: scene_count × 2 + setup_payoff_density × 1.5 + (2 if drives_climax else 0)

    Args:
        scene_count: Number of scenes the TCC appears in
        setup_payoff_density: Setup-payoff density (0.0-1.0)
        drives_climax: Whether this TCC drives the climax

    Returns:
        Spine score (higher = more likely to be A-line)
    """
    base_score = scene_count * 2 + setup_payoff_density * 1.5
    climax_bonus = 2.0 if drives_climax else 0.0
    return base_score + climax_bonus


def calculate_heart_score(emotional_intensity: float, a_line_interaction: float) -> float:
    """
    Calculate heart score for B-line ranking.

    Formula: emotional_intensity × 10 + a_line_interaction × 5

    Args:
        emotional_intensity: Emotional intensity score (0.0-1.0)
        a_line_interaction: Interaction with A-line score (0.0-1.0)

    Returns:
        Heart score (higher = more likely to be B-line)
    """
    return emotional_intensity * 10 + a_line_interaction * 5


def calculate_a_line_interaction(tcc_scenes: List[str], a_line_scenes: List[str]) -> float:
    """
    Calculate interaction score between a TCC and the A-line.

    Args:
        tcc_scenes: Scene IDs for the TCC being evaluated
        a_line_scenes: Scene IDs for the A-line

    Returns:
        Interaction score (0.0-1.0)
    """
    intersection = len(set(tcc_scenes) & set(a_line_scenes))
    min_count = min(len(tcc_scenes), len(a_line_scenes))
    return intersection / min_count if min_count > 0 else 0.0


def validate_tcc_independence(tccs: List[TCC]) -> List[str]:
    """
    Validate that TCCs are truly independent (not mirror conflicts).

    Returns a list of warnings about potential mirror TCCs.
    """
    warnings = []

    # Check for overlapping scenes that might indicate mirror conflicts
    for i, tcc1 in enumerate(tccs):
        for tcc2 in tccs[i+1:]:
            overlap = len(set(tcc1.evidence_scenes) & set(tcc2.evidence_scenes))
            overlap_ratio = overlap / min(len(tcc1.evidence_scenes), len(tcc2.evidence_scenes))

            if overlap_ratio > 0.8:
                warnings.append(
                    f"High overlap between {tcc1.tcc_id} and {tcc2.tcc_id} "
                    f"({overlap_ratio:.1%}). May be mirror conflicts. "
                    f"Check: '{tcc1.super_objective}' vs '{tcc2.super_objective}'"
                )

    return warnings


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Validate a TCC
    tcc = TCC(
        tcc_id="TCC_01",
        super_objective="玉鼠精's e-commerce funding plan",
        core_conflict_type="interpersonal",
        evidence_scenes=["S03", "S05", "S10"],
        confidence=0.95
    )
    print(f"Valid TCC: {tcc.tcc_id}")

    # Example: Validate Discoverer output
    output = DiscovererOutput(
        tccs=[tcc],
        metadata=DiscovererMetadata(
            total_scenes_analyzed=50,
            primary_evidence_available=True,
            fallback_mode=False
        )
    )
    print(f"Valid output with {len(output.tccs)} TCCs")
