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


class PerformanceNote(BaseModel):
    """表演提示 - 角色名后括号内的表演指示。"""
    character: str = Field(..., min_length=1, description="角色名")
    note: str = Field(..., min_length=1, description="表演提示内容，如'呢喃'、'颤抖'")
    line_context: Optional[str] = Field(None, description="关联的台词片段")


class Scene(BaseModel):
    """A single scene in the script."""
    scene_id: str = Field(..., pattern=r"^S\d{2,3}[a-z]?$")  # Allow optional lowercase letter suffix for duplicate IDs
    setting: str = Field(..., min_length=1)
    characters: List[str] = Field(..., min_length=1)
    scene_mission: str = Field(..., min_length=10)
    key_events: List[str] = Field(default_factory=list)
    info_change: List[InfoChange] = Field(default_factory=list)
    relation_change: List[RelationChange] = Field(default_factory=list)
    key_object: List[KeyObject] = Field(default_factory=list)
    setup_payoff: SetupPayoff = Field(default_factory=SetupPayoff)
    # 新增字段：表演提示和视觉动作 (v2.6.0)
    performance_notes: List[PerformanceNote] = Field(
        default_factory=list,
        description="表演提示列表，如'呢喃'、'颤抖'等情绪指示"
    )
    visual_actions: List[str] = Field(
        default_factory=list,
        description="视觉动作描述，如'她扶在丈夫肩头的手滑落'"
    )


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
        """Ensure all scene IDs follow the pattern (supports optional lowercase suffix like S05b)."""
        pattern = re.compile(r"^S\d{2,3}[a-z]?$")
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

    @field_validator('dynamic_antagonist', mode='before')
    @classmethod
    def coerce_dynamic_antagonist_to_list(cls, v):
        """Convert string to list if needed (LLM sometimes returns string instead of array)."""
        if v is None:
            return None
        if isinstance(v, str):
            # Convert single string to list
            return [v]
        return v


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
    change_type: Optional[Literal["add", "append", "update", "remove", "delete"]] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reason: Optional[str] = None

    @field_validator('issue_id', mode='before')
    @classmethod
    def normalize_issue_id(cls, v):
        """Normalize issue_id values (LLM sometimes returns ISS_001_corrected, ISS_001_fixed, etc.)."""
        if v is None:
            return None
        if isinstance(v, str):
            # Extract ISS_XXX pattern from strings like "ISS_001_corrected", "ISS_002_fixed"
            import re
            match = re.match(r'^(ISS_\d{3})', v)
            if match:
                return match.group(1)
            # If no match, return as-is and let pattern validation catch it
        return v

    @field_validator('change_type', mode='before')
    @classmethod
    def normalize_change_type(cls, v):
        """Normalize change_type values (LLM sometimes returns descriptive strings)."""
        if v is None:
            return None
        if isinstance(v, str):
            v_lower = v.lower().strip()
            # Handle 'none', 'N/A', etc. as no change - convert to 'update' (no-op)
            if v_lower in ['none', 'skip', 'no_change', 'n/a', 'na', 'null', '']:
                return 'update'  # Treat as update with no actual change
            # Map various removal-related strings to 'remove'
            if 'remove' in v_lower or 'delete' in v_lower or 'clear' in v_lower:
                return 'remove'
            # Map other common variants
            if v_lower in ['add', 'append', 'update', 'remove', 'delete']:
                return v_lower
        return v


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


def merge_mirror_tccs(tccs: List[TCC], threshold: float = 0.9) -> tuple[List[TCC], List[str]]:
    """
    Automatically merge TCCs that have very high scene overlap (>threshold).

    Args:
        tccs: List of TCCs to check
        threshold: Overlap ratio threshold for merging (default: 0.9 = 90%)

    Returns:
        Tuple of (merged_tccs, merge_logs)
    """
    if len(tccs) <= 1:
        return tccs, []

    merged = []
    skip_indices = set()
    merge_logs = []

    for i, tcc1 in enumerate(tccs):
        if i in skip_indices:
            continue

        # Find TCCs that should be merged with tcc1
        to_merge = [tcc1]

        for j, tcc2 in enumerate(tccs[i+1:], start=i+1):
            if j in skip_indices:
                continue

            overlap = len(set(tcc1.evidence_scenes) & set(tcc2.evidence_scenes))
            overlap_ratio = overlap / min(len(tcc1.evidence_scenes), len(tcc2.evidence_scenes))

            if overlap_ratio >= threshold:
                to_merge.append(tcc2)
                skip_indices.add(j)
                merge_logs.append(
                    f"Merged {tcc2.tcc_id} into {tcc1.tcc_id} (overlap: {overlap_ratio:.1%})"
                )

        # If multiple TCCs were merged, keep the one with highest confidence
        if len(to_merge) > 1:
            best_tcc = max(to_merge, key=lambda t: t.confidence)
            merged.append(best_tcc)
            merge_logs.append(
                f"Kept {best_tcc.tcc_id} as representative (confidence: {best_tcc.confidence:.2f})"
            )
        else:
            merged.append(tcc1)

    return merged, merge_logs


def filter_low_coverage_tccs(
    tccs: List[TCC],
    total_scenes: int,
    coverage_threshold: float = 0.15
) -> tuple[List[TCC], List[str]]:
    """
    Filter out TCCs with coverage below threshold.

    Coverage formula: (Last_Scene - First_Scene + 1) / Total_Scenes

    A TCC appearing only in S01 and S12 in a 50-scene script has coverage
    of (12-1+1)/50 = 0.24, which is above the 0.15 threshold.

    Args:
        tccs: List of TCCs to filter
        total_scenes: Total number of scenes in the script
        coverage_threshold: Minimum coverage ratio (default: 0.15 = 15%)

    Returns:
        Tuple of (filtered_tccs, filter_logs)
    """
    if total_scenes <= 0:
        return tccs, ["Warning: total_scenes is 0, skipping coverage filter"]

    filtered = []
    filter_logs = []

    for tcc in tccs:
        if not tcc.evidence_scenes:
            filter_logs.append(f"⚠️ {tcc.tcc_id} has no evidence_scenes, filtered out")
            continue

        # Extract scene numbers from scene IDs (e.g., "S01" -> 1, "S12" -> 12)
        scene_numbers = []
        for scene_id in tcc.evidence_scenes:
            try:
                # Handle formats like "S01", "S1", "Scene1"
                import re
                match = re.search(r'\d+', scene_id)
                if match:
                    scene_numbers.append(int(match.group()))
            except (ValueError, AttributeError):
                continue

        if len(scene_numbers) < 2:
            filter_logs.append(f"⚠️ {tcc.tcc_id} has <2 parseable scenes, filtered out")
            continue

        first_scene = min(scene_numbers)
        last_scene = max(scene_numbers)
        span = last_scene - first_scene + 1
        coverage = span / total_scenes

        if coverage >= coverage_threshold:
            filtered.append(tcc)
            filter_logs.append(
                f"✅ {tcc.tcc_id} coverage: {coverage:.1%} (S{first_scene:02d}-S{last_scene:02d})"
            )
        else:
            filter_logs.append(
                f"❌ {tcc.tcc_id} filtered: coverage {coverage:.1%} < {coverage_threshold:.1%} threshold"
            )

    return filtered, filter_logs


def check_antagonist_mutual_exclusion(tccs: List[TCC]) -> tuple[List[TCC], List[str]]:
    """
    Detect and handle antagonist/protagonist mirror TCCs.

    When two TCCs have:
    1. Opposite super_objectives (one is to achieve X, other is to block X)
    2. Very high scene overlap (>80%)

    They should be merged into one TCC where one party is the antagonist.

    Args:
        tccs: List of TCCs to check

    Returns:
        Tuple of (processed_tccs, check_logs)
    """
    if len(tccs) <= 1:
        return tccs, []

    # Keywords that indicate opposition/blocking
    OPPOSITION_MARKERS = [
        ("阻止", "寻求"), ("阻止", "获取"), ("阻止", "想要"),
        ("block", "get"), ("stop", "achieve"), ("prevent", "want"),
        ("反对", "支持"), ("破坏", "建立"), ("against", "for"),
    ]

    processed = []
    skip_indices = set()
    check_logs = []

    for i, tcc1 in enumerate(tccs):
        if i in skip_indices:
            continue

        antagonist_found = None

        for j, tcc2 in enumerate(tccs[i+1:], start=i+1):
            if j in skip_indices:
                continue

            # Check scene overlap
            overlap = len(set(tcc1.evidence_scenes) & set(tcc2.evidence_scenes))
            total = max(len(tcc1.evidence_scenes), len(tcc2.evidence_scenes))
            overlap_ratio = overlap / total if total > 0 else 0

            if overlap_ratio < 0.8:
                continue  # Not enough overlap to be mirror

            # Check for opposition in super_objectives
            obj1 = tcc1.super_objective.lower()
            obj2 = tcc2.super_objective.lower()

            is_opposition = False
            for block_word, achieve_word in OPPOSITION_MARKERS:
                if (block_word in obj1 and achieve_word in obj2) or \
                   (achieve_word in obj1 and block_word in obj2):
                    is_opposition = True
                    break

            if is_opposition:
                antagonist_found = (j, tcc2)
                skip_indices.add(j)
                check_logs.append(
                    f"🔀 {tcc1.tcc_id} & {tcc2.tcc_id} are antagonist mirrors "
                    f"(overlap: {overlap_ratio:.1%})"
                )
                check_logs.append(
                    f"   Merged: keeping {tcc1.tcc_id} (higher confidence wins)"
                )
                break

        # Keep the TCC with higher confidence if antagonist found
        if antagonist_found:
            _, tcc2 = antagonist_found
            winner = tcc1 if tcc1.confidence >= tcc2.confidence else tcc2
            # Merge evidence scenes
            merged_scenes = list(set(tcc1.evidence_scenes) | set(tcc2.evidence_scenes))
            winner.evidence_scenes = sorted(merged_scenes)
            processed.append(winner)
        else:
            processed.append(tcc1)

    return processed, check_logs


def validate_tcc_scene_evidence(
    tccs: List[TCC],
    script: "Script"
) -> tuple[List[TCC], List[str]]:
    """
    Atomic Scene Reverse Verification for TCCs.

    For each TCC's evidence_scenes, verify whether the scene's key_events
    can actually support the TCC's super_objective. This prevents
    "semantic hallucination" where LLM claims a scene supports a TCC
    without actual evidence.

    Args:
        tccs: List of TCCs to validate
        script: The Script object containing scene data

    Returns:
        Tuple of (validated_tccs, validation_logs)
    """
    validated_tccs = []
    validation_logs = []

    # Build scene lookup dict
    scene_dict = {scene.scene_id: scene for scene in script.scenes}

    for tcc in tccs:
        valid_scenes = []
        invalid_scenes = []

        for scene_id in tcc.evidence_scenes:
            scene = scene_dict.get(scene_id)

            if not scene:
                invalid_scenes.append(f"{scene_id} (not found)")
                continue

            # Check if scene has any key_events that could support the TCC
            has_relevant_event = False

            # Get keywords from super_objective for matching
            objective_lower = tcc.super_objective.lower()

            # Check key_events
            for event in (scene.key_events or []):
                event_lower = event.lower()
                # Basic keyword overlap check
                # In production, this could use embedding similarity
                if _has_keyword_overlap(objective_lower, event_lower):
                    has_relevant_event = True
                    break

            # Also check scene_mission
            if not has_relevant_event and scene.scene_mission:
                if _has_keyword_overlap(objective_lower, scene.scene_mission.lower()):
                    has_relevant_event = True

            # Also check relation_change for interpersonal conflicts
            if not has_relevant_event and scene.relation_change:
                for rel in scene.relation_change:
                    # Note: RelationChange uses from_ (aliased as "from") and to
                    rel_str = f"{rel.chars} {rel.from_} {rel.to}".lower()
                    if _has_keyword_overlap(objective_lower, rel_str):
                        has_relevant_event = True
                        break

            if has_relevant_event:
                valid_scenes.append(scene_id)
            else:
                invalid_scenes.append(f"{scene_id} (no supporting evidence)")

        # Log validation results
        if invalid_scenes:
            validation_logs.append(
                f"⚠️ {tcc.tcc_id}: {len(invalid_scenes)}/{len(tcc.evidence_scenes)} "
                f"scenes lack clear evidence: {', '.join(invalid_scenes)}"
            )

        # Keep TCC if at least 2 valid scenes remain
        if len(valid_scenes) >= 2:
            # Update evidence_scenes to only valid ones
            tcc.evidence_scenes = valid_scenes
            validated_tccs.append(tcc)
            validation_logs.append(
                f"✅ {tcc.tcc_id}: Validated with {len(valid_scenes)} evidence scenes"
            )
        elif len(valid_scenes) >= 1:
            # Keep TCC with reduced confidence if only 1 valid scene
            tcc.evidence_scenes = valid_scenes
            tcc.confidence = max(0.5, tcc.confidence - 0.2)  # Reduce confidence
            validated_tccs.append(tcc)
            validation_logs.append(
                f"⚠️ {tcc.tcc_id}: Kept with reduced confidence ({tcc.confidence:.2f}), only {len(valid_scenes)} valid scene"
            )
        else:
            # No valid scenes - keep original but mark as low confidence
            # Don't filter completely to avoid breaking downstream stages
            tcc.confidence = max(0.4, tcc.confidence - 0.3)
            validated_tccs.append(tcc)
            validation_logs.append(
                f"⚠️ {tcc.tcc_id}: No keyword evidence found, kept with low confidence ({tcc.confidence:.2f})"
            )

    return validated_tccs, validation_logs


def _has_keyword_overlap(text1: str, text2: str, min_overlap: int = 1) -> bool:
    """
    Check if two texts have meaningful keyword overlap.

    This is a simple heuristic. In production, you might use:
    - Word embeddings for semantic similarity
    - Named entity recognition
    - More sophisticated NLP

    Args:
        text1: First text (typically TCC objective)
        text2: Second text (typically scene event/mission)
        min_overlap: Minimum number of overlapping keywords required

    Returns:
        True if meaningful overlap found
    """
    # Common stop words to filter out
    STOP_WORDS = {
        '的', '了', '是', '在', '和', '与', '被', '把', '对', '到', '为',
        '着', '过', '不', '这', '那', '有', '要', '会', '能', '想',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of', 'and',
        'in', 'for', 'on', 'with', 'as', 'at', 'by', 'from'
    }

    # Extract words (Chinese characters are individual, English are space-separated)
    import re

    # For Chinese: extract all Chinese character sequences
    chinese_words1 = set(re.findall(r'[\u4e00-\u9fa5]+', text1))
    chinese_words2 = set(re.findall(r'[\u4e00-\u9fa5]+', text2))

    # For English: extract word tokens
    english_words1 = set(w.lower() for w in re.findall(r'[a-zA-Z]+', text1))
    english_words2 = set(w.lower() for w in re.findall(r'[a-zA-Z]+', text2))

    # Combine and filter stop words
    words1 = (chinese_words1 | english_words1) - STOP_WORDS
    words2 = (chinese_words2 | english_words2) - STOP_WORDS

    # Check for overlap
    overlap = words1 & words2

    # Also check if any word from text1 is a substring of text2 (or vice versa)
    # This handles cases like "投资" matching "创业投资"
    for w1 in words1:
        if len(w1) >= 2:
            for w2 in words2:
                if len(w2) >= 2 and (w1 in w2 or w2 in w1):
                    overlap.add(w1)

    return len(overlap) >= min_overlap


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
