"""
TXT report exporter for screenplay analysis results.

Generates plain text reports without markdown formatting,
suitable for environments that don't support rich text.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from prompts.schemas import TCC, Rankings
from src.version import __version__


class TXTExporter:
    """Export analysis results as plain text report."""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize TXT exporter.

        Args:
            template_dir: Directory containing Jinja2 templates
        """
        if template_dir is None:
            # Default to templates/ directory in project root
            project_root = Path(__file__).parent.parent.parent
            template_dir = project_root / "templates"

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def export(
        self,
        result: Dict[str, Any],
        output_path: Path,
        script_name: Optional[str] = None
    ) -> Path:
        """
        Export analysis result to TXT report.

        Args:
            result: Pipeline execution result (from run_pipeline)
            output_path: Path to save the TXT report
            script_name: Optional script name for the report

        Returns:
            Path to the generated report
        """
        # Extract data from result
        tccs = result.get("tccs", [])
        rankings = result.get("rankings")
        modifications = result.get("modifications", {})
        metrics = result.get("_metrics", {})
        script_json = result.get("script_json", {})

        # Prepare template context
        context = self._prepare_context(
            tccs=tccs,
            rankings=rankings,
            modifications=modifications,
            metrics=metrics,
            script_json=script_json,
            script_name=script_name
        )

        # Render template
        template = self.env.get_template("report_template.txt.j2")
        txt_content = template.render(**context)

        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(txt_content, encoding="utf-8")

        return output_path

    def _prepare_context(
        self,
        tccs: List[Any],
        rankings: Optional[Any],
        modifications: Dict[str, Any],
        metrics: Dict[str, Any],
        script_json: Dict[str, Any],
        script_name: Optional[str]
    ) -> Dict[str, Any]:
        """Prepare template context from analysis results."""
        # Basic info
        if script_name is None:
            script_name = script_json.get("title", "未命名剧本")

        context = {
            "script_name": script_name,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_version": __version__,
            "llm_provider": "DeepSeek",
            "model_name": "deepseek-chat",
            "report_generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Execution metrics
        context.update({
            "total_duration": metrics.get("total_duration", 0),
            "total_llm_calls": sum(metrics.get("llm_calls", {}).values()),
            "total_retries": sum(metrics.get("retries", {}).values()),
            "success_rate": 100,  # Assume success if we got here
        })

        # Stage 1: TCCs
        context["tccs"] = tccs
        context["tcc_warnings"] = []  # TODO: Extract from validation

        # Stage 2: Rankings
        if rankings:
            context["a_line"] = rankings.a_line if hasattr(rankings, 'a_line') else None
            context["b_lines"] = rankings.b_lines if hasattr(rankings, 'b_lines') else []
            context["c_lines"] = rankings.c_lines if hasattr(rankings, 'c_lines') else []
        else:
            context["a_line"] = None
            context["b_lines"] = []
            context["c_lines"] = []

        # Stage 3: Modifications
        mod_list = modifications.get("modifications", [])
        context["modifications"] = mod_list
        context["total_issues"] = modifications.get("total_issues", len(mod_list))
        context["fixed_issues"] = len([m for m in mod_list if m.applied])
        context["skipped_issues"] = len([m for m in mod_list if not m.applied])

        # Stage metrics for table
        stage_metrics = {}
        for stage, duration in metrics.get("stage_durations", {}).items():
            stage_metrics[stage] = {
                "duration": duration,
                "llm_calls": metrics.get("llm_calls", {}).get(stage, 0),
                "retries": metrics.get("retries", {}).get(stage, 0),
            }
        context["stage_metrics"] = stage_metrics

        # Key findings and recommendations
        context["key_findings"] = self._generate_key_findings(tccs, rankings, modifications)
        context["recommendations"] = self._generate_recommendations(tccs, rankings, modifications)

        return context

    def _generate_key_findings(
        self,
        tccs: List[Any],
        rankings: Optional[Any],
        modifications: Dict[str, Any]
    ) -> List[str]:
        """Generate key findings from analysis results."""
        findings = []

        # TCC count
        tcc_count = len(tccs)
        if tcc_count == 1:
            findings.append("剧本为单线叙事，结构简洁清晰")
        elif tcc_count == 2:
            findings.append("剧本采用双线叙事，主副线并行发展")
        elif tcc_count >= 3:
            findings.append(f"剧本为多线叙事（{tcc_count}条线），结构复杂度较高")

        # Line distribution
        if rankings:
            if rankings.a_line:
                findings.append(f"主线（A线）明确：{rankings.a_line.super_objective[:30]}...")

            b_count = len(rankings.b_lines) if rankings.b_lines else 0
            if b_count > 0:
                findings.append(f"副线（B线）数量: {b_count}条，提供情感深度")

            c_count = len(rankings.c_lines) if rankings.c_lines else 0
            if c_count > 0:
                findings.append(f"次线（C线）数量: {c_count}条，增加叙事层次")

        # Modifications
        total_issues = modifications.get("total_issues", 0)
        if total_issues == 0:
            findings.append("剧本结构完整，未发现需修正的结构性问题")
        else:
            fixed = len([m for m in modifications.get("modifications", []) if m.applied])
            findings.append(f"发现{total_issues}个结构性问题，已修复{fixed}个")

        return findings

    def _generate_recommendations(
        self,
        tccs: List[Any],
        rankings: Optional[Any],
        modifications: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []

        # Check for B-line existence
        if rankings and rankings.a_line:
            b_count = len(rankings.b_lines) if rankings.b_lines else 0
            if b_count == 0:
                recommendations.append("考虑增加B线（副线），为主线提供情感深度和人物内部冲突")

        # Check TCC confidence
        low_confidence_tccs = [tcc for tcc in tccs if tcc.confidence < 0.7]
        if low_confidence_tccs:
            recommendations.append(
                f"部分TCC置信度较低（<70%），建议审核以下TCC的独立性: "
                f"{', '.join([tcc.tcc_id for tcc in low_confidence_tccs])}"
            )

        # Check for structural issues
        total_issues = modifications.get("total_issues", 0)
        if total_issues > 5:
            recommendations.append("结构性问题较多，建议重点检查场景的setup-payoff因果链完整性")

        # Default recommendation if none generated
        if not recommendations:
            recommendations.append("剧本结构良好，建议维持当前设计")
            recommendations.append("可考虑进一步深化角色冲突和情感弧线")

        return recommendations
