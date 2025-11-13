"""
A/B Testing Framework for Prompt and Model Comparison

This module provides tools to compare different:
- Prompt versions
- LLM providers (DeepSeek, Claude, OpenAI)
- Model parameters (temperature, max_tokens)

Usage:
    from src.ab_testing import ABTestRunner, PromptVariant

    # Define variants
    variants = [
        PromptVariant(name="v2.1", prompt_version="2.1"),
        PromptVariant(name="v2.2", prompt_version="2.2")
    ]

    # Run A/B test
    runner = ABTestRunner()
    results = runner.compare_variants(script, variants)
    runner.print_comparison(results)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Literal
from pathlib import Path
import json
import time
from datetime import datetime
import statistics

from prompts.schemas import Script
from src.pipeline import run_pipeline
from src.monitoring import CostEstimator


@dataclass
class PromptVariant:
    """
    Represents a variant in A/B testing.

    You can vary:
    - prompt_version: Different prompt files (requires custom implementation)
    - provider: LLM provider (deepseek, anthropic, openai)
    - model: Specific model name
    - temperature: Sampling temperature
    - max_tokens: Maximum tokens to generate
    """
    name: str
    prompt_version: Optional[str] = None
    provider: str = "deepseek"
    model: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "prompt_version": self.prompt_version,
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "metadata": self.metadata
        }


@dataclass
class ABTestResult:
    """Results from a single variant test run."""
    variant: PromptVariant
    success: bool
    duration: float
    metrics: Dict[str, Any]
    errors: List[str]
    tcc_count: int
    tcc_confidence_avg: float
    stage_durations: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "variant": self.variant.to_dict(),
            "success": self.success,
            "duration": self.duration,
            "metrics": self.metrics,
            "errors": self.errors,
            "tcc_count": self.tcc_count,
            "tcc_confidence_avg": self.tcc_confidence_avg,
            "stage_durations": self.stage_durations,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ABTestComparison:
    """Comparison results across multiple variants."""
    test_id: str
    script_name: str
    variants: List[PromptVariant]
    results: List[ABTestResult]
    winner: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "script_name": self.script_name,
            "variants": [v.to_dict() for v in self.variants],
            "results": [r.to_dict() for r in self.results],
            "winner": self.winner,
            "timestamp": self.timestamp.isoformat()
        }


class ABTestRunner:
    """
    A/B testing runner for comparing prompt variants.

    Features:
    - Run multiple variants against the same script
    - Collect and compare metrics
    - Determine statistical winner
    - Generate comparison reports
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize A/B test runner.

        Args:
            output_dir: Directory to save test results (default: ./ab_tests/)
        """
        self.output_dir = output_dir or Path("./ab_tests")
        self.output_dir.mkdir(exist_ok=True)

    def run_variant(
        self,
        script: Script,
        variant: PromptVariant,
        run_name: Optional[str] = None
    ) -> ABTestResult:
        """
        Run a single variant test.

        Args:
            script: Script to analyze
            variant: Variant configuration
            run_name: Optional custom run name

        Returns:
            ABTestResult with metrics
        """
        print(f"\n{'='*60}")
        print(f"🧪 Testing Variant: {variant.name}")
        print(f"   Provider: {variant.provider}")
        print(f"   Model: {variant.model or 'default'}")
        print(f"   Temperature: {variant.temperature}")
        print(f"{'='*60}\n")

        start_time = time.time()

        try:
            # Run pipeline with variant configuration
            result = run_pipeline(
                script=script,
                provider=variant.provider,
                model=variant.model,
                run_name=run_name or f"ab-test-{variant.name}"
            )

            duration = time.time() - start_time

            # Extract metrics
            metrics = result.get("_metrics", {})
            errors = result.get("errors", [])

            # Calculate TCC metrics
            tcc_count = 0
            tcc_confidence_avg = 0.0

            if result.get("discoverer_output"):
                tccs = result["discoverer_output"].tccs
                tcc_count = len(tccs)
                if tccs:
                    tcc_confidence_avg = sum(t.confidence for t in tccs) / len(tccs)

            return ABTestResult(
                variant=variant,
                success=len(errors) == 0,
                duration=duration,
                metrics=metrics,
                errors=errors,
                tcc_count=tcc_count,
                tcc_confidence_avg=tcc_confidence_avg,
                stage_durations=metrics.get("stages", {})
            )

        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ Variant {variant.name} failed: {e}")

            return ABTestResult(
                variant=variant,
                success=False,
                duration=duration,
                metrics={},
                errors=[str(e)],
                tcc_count=0,
                tcc_confidence_avg=0.0,
                stage_durations={}
            )

    def compare_variants(
        self,
        script: Script,
        variants: List[PromptVariant],
        script_name: str = "test_script",
        runs_per_variant: int = 1
    ) -> ABTestComparison:
        """
        Compare multiple variants.

        Args:
            script: Script to test on
            variants: List of variants to compare
            script_name: Name for reporting
            runs_per_variant: Number of runs per variant (for averaging)

        Returns:
            ABTestComparison with results
        """
        test_id = f"ab-test-{datetime.now():%Y%m%d-%H%M%S}"
        all_results = []

        print(f"\n{'='*60}")
        print(f"🚀 Starting A/B Test: {test_id}")
        print(f"📄 Script: {script_name}")
        print(f"🔬 Variants: {len(variants)}")
        print(f"🔁 Runs per variant: {runs_per_variant}")
        print(f"{'='*60}\n")

        for variant in variants:
            variant_results = []

            for run_num in range(runs_per_variant):
                run_name = f"{test_id}-{variant.name}-run{run_num+1}"
                result = self.run_variant(script, variant, run_name)
                variant_results.append(result)

            # Average results if multiple runs
            if runs_per_variant > 1:
                averaged_result = self._average_results(variant_results)
                all_results.append(averaged_result)
            else:
                all_results.append(variant_results[0])

        # Determine winner
        winner = self._determine_winner(all_results)

        comparison = ABTestComparison(
            test_id=test_id,
            script_name=script_name,
            variants=variants,
            results=all_results,
            winner=winner
        )

        # Save results
        self._save_results(comparison)

        return comparison

    def _average_results(self, results: List[ABTestResult]) -> ABTestResult:
        """Average multiple results for the same variant."""
        if not results:
            raise ValueError("No results to average")

        variant = results[0].variant

        return ABTestResult(
            variant=variant,
            success=all(r.success for r in results),
            duration=statistics.mean(r.duration for r in results),
            metrics={
                "total_duration": statistics.mean(
                    r.metrics.get("total_duration", 0) for r in results
                ),
                "total_llm_calls": statistics.mean(
                    r.metrics.get("total_llm_calls", 0) for r in results
                ),
            },
            errors=[e for r in results for e in r.errors],
            tcc_count=int(statistics.mean(r.tcc_count for r in results)),
            tcc_confidence_avg=statistics.mean(r.tcc_confidence_avg for r in results),
            stage_durations={
                stage: statistics.mean(
                    r.stage_durations.get(stage, 0) for r in results
                )
                for stage in ["discoverer", "auditor", "modifier"]
            }
        )

    def _determine_winner(self, results: List[ABTestResult]) -> Optional[str]:
        """
        Determine the winner based on multiple criteria.

        Priority:
        1. Success (no errors)
        2. TCC confidence (higher is better)
        3. Duration (faster is better)
        """
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return None

        # Sort by: confidence (desc), then duration (asc)
        sorted_results = sorted(
            successful_results,
            key=lambda r: (-r.tcc_confidence_avg, r.duration)
        )

        return sorted_results[0].variant.name

    def _save_results(self, comparison: ABTestComparison):
        """Save comparison results to JSON file."""
        output_file = self.output_dir / f"{comparison.test_id}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {output_file}")

    def print_comparison(self, comparison: ABTestComparison):
        """
        Print formatted comparison report.

        Args:
            comparison: ABTestComparison to display
        """
        print("\n" + "="*80)
        print("📊 A/B TEST COMPARISON REPORT")
        print("="*80)
        print(f"Test ID: {comparison.test_id}")
        print(f"Script: {comparison.script_name}")
        print(f"Timestamp: {comparison.timestamp:%Y-%m-%d %H:%M:%S}")
        print(f"\n🏆 Winner: {comparison.winner or 'No clear winner'}")
        print("\n" + "-"*80)

        # Build comparison table
        print(f"\n{'Variant':<15} {'Success':<10} {'Duration':<12} {'TCCs':<8} "
              f"{'Confidence':<12} {'Errors':<8}")
        print("-"*80)

        for result in comparison.results:
            success_icon = "✅" if result.success else "❌"
            print(
                f"{result.variant.name:<15} "
                f"{success_icon:<10} "
                f"{result.duration:>10.2f}s  "
                f"{result.tcc_count:>6}  "
                f"{result.tcc_confidence_avg:>10.2%}  "
                f"{len(result.errors):>6}"
            )

        # Stage-wise breakdown
        print("\n" + "-"*80)
        print("📈 STAGE-WISE PERFORMANCE")
        print("-"*80)

        for stage in ["discoverer", "auditor", "modifier"]:
            print(f"\n{stage.upper()}:")
            for result in comparison.results:
                duration = result.stage_durations.get(stage, 0)
                print(f"  {result.variant.name:<15}: {duration:>8.2f}s")

        # Winner analysis
        if comparison.winner:
            winner_result = next(
                r for r in comparison.results if r.variant.name == comparison.winner
            )
            print("\n" + "-"*80)
            print(f"🎯 WINNER ANALYSIS: {comparison.winner}")
            print("-"*80)
            print(f"Provider: {winner_result.variant.provider}")
            print(f"Model: {winner_result.variant.model or 'default'}")
            print(f"Success: {winner_result.success}")
            print(f"Duration: {winner_result.duration:.2f}s")
            print(f"TCCs: {winner_result.tcc_count}")
            print(f"Avg Confidence: {winner_result.tcc_confidence_avg:.2%}")

        print("\n" + "="*80 + "\n")

    def compare_providers(
        self,
        script: Script,
        providers: List[str] = ["deepseek", "anthropic", "openai"],
        script_name: str = "test_script"
    ) -> ABTestComparison:
        """
        Convenience method to compare different LLM providers.

        Args:
            script: Script to test
            providers: List of provider names
            script_name: Name for reporting

        Returns:
            ABTestComparison results
        """
        variants = [
            PromptVariant(name=f"{provider}", provider=provider)
            for provider in providers
        ]

        return self.compare_variants(script, variants, script_name)

    def load_results(self, test_id: str) -> Optional[ABTestComparison]:
        """
        Load saved test results.

        Args:
            test_id: Test ID to load

        Returns:
            ABTestComparison or None if not found
        """
        result_file = self.output_dir / f"{test_id}.json"

        if not result_file.exists():
            print(f"❌ Test results not found: {test_id}")
            return None

        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Reconstruct objects (simplified - you may want full reconstruction)
        return data

    def list_tests(self) -> List[str]:
        """List all saved test IDs."""
        json_files = list(self.output_dir.glob("ab-test-*.json"))
        return [f.stem for f in sorted(json_files, reverse=True)]


# Convenience functions
def quick_compare(
    script: Script,
    variant_names: List[str],
    provider: str = "deepseek"
) -> ABTestComparison:
    """
    Quick comparison of named variants (useful for prompt versions).

    Args:
        script: Script to test
        variant_names: Names for variants (e.g., ["baseline", "optimized"])
        provider: LLM provider to use

    Returns:
        ABTestComparison results
    """
    variants = [
        PromptVariant(name=name, provider=provider)
        for name in variant_names
    ]

    runner = ABTestRunner()
    results = runner.compare_variants(script, variants)
    runner.print_comparison(results)

    return results


# Example usage
if __name__ == "__main__":
    from prompts.schemas import Scene, SetupPayoff

    # Create test script
    test_script = Script(scenes=[
        Scene(
            scene_id="S01",
            setting="测试场景",
            characters=["角色A", "角色B"],
            scene_mission="测试任务",
            key_events=["事件1"],
            setup_payoff=SetupPayoff(setup_for=[], payoff_from=[])
        )
    ])

    # Define variants
    variants = [
        PromptVariant(name="baseline", provider="deepseek", temperature=0.0),
        PromptVariant(name="creative", provider="deepseek", temperature=0.7),
    ]

    # Run comparison
    runner = ABTestRunner()
    results = runner.compare_variants(test_script, variants)
    runner.print_comparison(results)
