"""
Mermaid diagram generator for TCC relationships visualization.
"""

from typing import Dict, List, Any, Optional
from prompts.schemas import TCC, Rankings


class MermaidGenerator:
    """Generate Mermaid flowchart for TCC relationships."""

    # Color schemes for A/B/C lines
    LINE_COLORS = {
        "A": "#ff6b6b",  # Red - Main storyline
        "B": "#4ecdc4",  # Teal - Subplot
        "C": "#95e1d3",  # Light green - Flavor
    }

    def __init__(self):
        """Initialize Mermaid generator."""
        pass

    def generate_tcc_diagram(
        self,
        tccs: List[TCC],
        rankings: Optional[Rankings] = None,
        script_scenes: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate Mermaid flowchart for TCC relationships.

        Args:
            tccs: List of TCCs identified
            rankings: Optional TCC rankings (A/B/C lines)
            script_scenes: Optional original script scenes for setup-payoff chains

        Returns:
            Mermaid flowchart syntax as string
        """
        lines = []

        # Header
        lines.append("```mermaid")
        lines.append("flowchart TD")
        lines.append("")

        # Add TCC nodes with line classification
        line_map = self._build_line_map(tccs, rankings)

        for tcc in tccs:
            node_id = tcc.tcc_id
            line_type = line_map.get(node_id, "")

            # Truncate long objectives for display
            objective = self._truncate_text(tcc.super_objective, 30)
            confidence = f"{tcc.confidence:.0%}"

            # Node label with line type and confidence
            label = f"{node_id}<br/>{objective}<br/>置信度: {confidence}"

            if line_type:
                label = f"[{line_type}线] " + label
                lines.append(f'    {node_id}["{label}"]')
            else:
                lines.append(f'    {node_id}["{label}"]')

        lines.append("")

        # Add setup-payoff relationships if available
        if script_scenes:
            payoff_links = self._extract_setup_payoff_links(tccs, script_scenes)
            if payoff_links:
                lines.append("    %% Setup-Payoff 关系")
                for source, target, label in payoff_links:
                    lines.append(f'    {source} -->|{label}| {target}')
                lines.append("")

        # Add styling for A/B/C lines
        if rankings:
            lines.append("    %% A/B/C线样式")

            if rankings.a_line:
                a_id = rankings.a_line.tcc_id
                lines.append(f"    style {a_id} fill:{self.LINE_COLORS['A']},stroke:#333,stroke-width:2px,color:#fff")

            for b_line in rankings.b_lines:
                b_id = b_line.tcc_id
                lines.append(f"    style {b_id} fill:{self.LINE_COLORS['B']},stroke:#333,stroke-width:2px,color:#fff")

            for c_line in rankings.c_lines:
                c_id = c_line.tcc_id
                lines.append(f"    style {c_id} fill:{self.LINE_COLORS['C']},stroke:#333,stroke-width:2px,color:#000")

        lines.append("```")

        return "\n".join(lines)

    def generate_legend(self) -> str:
        """Generate legend explaining the diagram."""
        legend = """
### 图例说明

- 🔴 **A线** (红色): 主线故事，剧本脊柱
- 🔵 **B线** (青色): 副线故事，情感核心
- 🟢 **C线** (绿色): 次线故事，主题映照
- ➡️ **箭头**: Setup-Payoff 因果关系
"""
        return legend.strip()

    def _build_line_map(self, tccs: List[TCC], rankings: Optional[Rankings]) -> Dict[str, str]:
        """Build mapping of TCC ID to line type (A/B/C)."""
        line_map = {}

        if not rankings:
            return line_map

        if rankings.a_line:
            line_map[rankings.a_line.tcc_id] = "A"

        for b_line in rankings.b_lines:
            line_map[b_line.tcc_id] = "B"

        for c_line in rankings.c_lines:
            line_map[c_line.tcc_id] = "C"

        return line_map

    def _extract_setup_payoff_links(
        self,
        tccs: List[TCC],
        script_scenes: List[Dict[str, Any]]
    ) -> List[tuple]:
        """
        Extract setup-payoff relationships between TCCs.

        Returns:
            List of (source_tcc, target_tcc, label) tuples
        """
        links = []

        # Build scene to TCC mapping
        scene_to_tcc = {}
        for tcc in tccs:
            for scene_id in tcc.evidence_scenes:
                if scene_id not in scene_to_tcc:
                    scene_to_tcc[scene_id] = []
                scene_to_tcc[scene_id].append(tcc.tcc_id)

        # Extract setup-payoff chains from scenes
        for scene in script_scenes:
            scene_id = scene.get("scene_id", "")
            setup_payoffs = scene.get("setup_payoff", [])

            if not setup_payoffs or scene_id not in scene_to_tcc:
                continue

            source_tccs = scene_to_tcc.get(scene_id, [])

            for sp in setup_payoffs:
                target_scene = sp.get("scene_id", "")
                if target_scene in scene_to_tcc:
                    target_tccs = scene_to_tcc[target_scene]

                    # Create links between TCCs
                    for source_tcc in source_tccs:
                        for target_tcc in target_tccs:
                            if source_tcc != target_tcc:
                                label = self._truncate_text(sp.get("type", "关联"), 15)
                                links.append((source_tcc, target_tcc, label))

        # Deduplicate links
        unique_links = list(set(links))

        return unique_links[:10]  # Limit to 10 links to avoid clutter

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
