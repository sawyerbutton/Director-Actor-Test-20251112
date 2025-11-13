"""
LangSmith Observability and Monitoring Utilities

This module provides utilities for enhanced observability and monitoring
of the screenplay analysis pipeline using LangSmith.

Features:
- Custom metrics export
- Performance analysis
- Cost tracking
- Error rate monitoring
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class RunMetrics:
    """Metrics for a single pipeline run."""

    run_id: str
    script_name: str
    timestamp: datetime
    total_duration: float
    stage_durations: Dict[str, float]
    llm_calls: Dict[str, int]
    retries: Dict[str, int]
    token_usage: Dict[str, int]
    errors: List[str] = field(default_factory=list)
    success: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "run_id": self.run_id,
            "script_name": self.script_name,
            "timestamp": self.timestamp.isoformat(),
            "total_duration": self.total_duration,
            "stage_durations": self.stage_durations,
            "llm_calls": self.llm_calls,
            "retries": self.retries,
            "token_usage": self.token_usage,
            "errors": self.errors,
            "success": self.success
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunMetrics":
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class MetricsStore:
    """Store and analyze metrics across multiple runs."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize metrics store.

        Args:
            storage_path: Path to store metrics JSON file.
                         Defaults to .langsmith_metrics.json
        """
        self.storage_path = storage_path or Path(".langsmith_metrics.json")
        self.runs: List[RunMetrics] = []
        self._load()

    def _load(self):
        """Load metrics from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.runs = [RunMetrics.from_dict(r) for r in data]
            except Exception as e:
                print(f"Warning: Failed to load metrics: {e}")

    def _save(self):
        """Save metrics to storage."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                data = [r.to_dict() for r in self.runs]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save metrics: {e}")

    def record_run(self, metrics: RunMetrics):
        """Record a new run."""
        self.runs.append(metrics)
        self._save()

    def get_stats(self, last_n: Optional[int] = None) -> Dict[str, Any]:
        """
        Get statistics across runs.

        Args:
            last_n: Only analyze last N runs. None means all runs.

        Returns:
            Dictionary with statistics
        """
        runs = self.runs[-last_n:] if last_n else self.runs

        if not runs:
            return {"error": "No runs recorded"}

        total_runs = len(runs)
        successful_runs = sum(1 for r in runs if r.success)
        failed_runs = total_runs - successful_runs

        # Average durations
        avg_duration = sum(r.total_duration for r in runs) / total_runs

        # Stage-wise averages
        stage_stats = {}
        for stage in ["discoverer", "auditor", "modifier"]:
            durations = [r.stage_durations.get(stage, 0) for r in runs]
            calls = [r.llm_calls.get(stage, 0) for r in runs]
            retries = [r.retries.get(stage, 0) for r in runs]

            stage_stats[stage] = {
                "avg_duration": sum(durations) / total_runs if durations else 0,
                "avg_calls": sum(calls) / total_runs if calls else 0,
                "avg_retries": sum(retries) / total_runs if retries else 0
            }

        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": successful_runs / total_runs * 100,
            "avg_duration": avg_duration,
            "stage_stats": stage_stats
        }

    def print_report(self, last_n: Optional[int] = None):
        """Print formatted statistics report."""
        stats = self.get_stats(last_n)

        if "error" in stats:
            print(stats["error"])
            return

        print("\n" + "=" * 60)
        print("📊 PERFORMANCE ANALYTICS REPORT")
        print("=" * 60)
        print(f"Total Runs: {stats['total_runs']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Average Duration: {stats['avg_duration']:.2f}s")
        print("\nStage-wise Performance:")

        for stage, data in stats['stage_stats'].items():
            print(f"\n  {stage.upper()}:")
            print(f"    Avg Duration: {data['avg_duration']:.2f}s")
            print(f"    Avg LLM Calls: {data['avg_calls']:.1f}")
            print(f"    Avg Retries: {data['avg_retries']:.1f}")

        print("=" * 60 + "\n")


class CostEstimator:
    """Estimate costs based on token usage and provider pricing."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "deepseek": {
            "input": 0.14,   # $0.14 per 1M input tokens
            "output": 0.28   # $0.28 per 1M output tokens
        },
        "anthropic": {
            "input": 3.00,   # Claude Sonnet pricing
            "output": 15.00
        },
        "openai": {
            "input": 10.00,  # GPT-4 Turbo pricing
            "output": 30.00
        }
    }

    @classmethod
    def estimate_cost(
        cls,
        provider: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate cost for a run.

        Args:
            provider: LLM provider name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pricing = cls.PRICING.get(provider.lower(), cls.PRICING["deepseek"])

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    @classmethod
    def print_cost_breakdown(
        cls,
        provider: str,
        input_tokens: int,
        output_tokens: int
    ):
        """Print detailed cost breakdown."""
        total_cost = cls.estimate_cost(provider, input_tokens, output_tokens)
        pricing = cls.PRICING.get(provider.lower(), cls.PRICING["deepseek"])

        print("\n" + "=" * 60)
        print("💰 COST ESTIMATE")
        print("=" * 60)
        print(f"Provider: {provider.upper()}")
        print(f"Input Tokens: {input_tokens:,}")
        print(f"Output Tokens: {output_tokens:,}")
        print(f"Total Tokens: {input_tokens + output_tokens:,}")
        print(f"\nPricing (per 1M tokens):")
        print(f"  Input: ${pricing['input']:.2f}")
        print(f"  Output: ${pricing['output']:.2f}")
        print(f"\n💵 Estimated Cost: ${total_cost:.4f}")
        print("=" * 60 + "\n")


def export_metrics_for_dashboard(
    metrics_store: MetricsStore,
    output_path: Path
):
    """
    Export metrics in format suitable for visualization dashboards.

    Args:
        metrics_store: MetricsStore instance
        output_path: Path to save exported data
    """
    data = {
        "runs": [r.to_dict() for r in metrics_store.runs],
        "stats": metrics_store.get_stats(),
        "generated_at": datetime.now().isoformat()
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Metrics exported to {output_path}")


# Example usage
if __name__ == "__main__":
    # Create sample metrics
    sample_run = RunMetrics(
        run_id="test-001",
        script_name="test_script.json",
        timestamp=datetime.now(),
        total_duration=120.5,
        stage_durations={"discoverer": 45.2, "auditor": 35.1, "modifier": 40.2},
        llm_calls={"discoverer": 1, "auditor": 1, "modifier": 1},
        retries={"discoverer": 0, "auditor": 0, "modifier": 0},
        token_usage={"discoverer": 5000, "auditor": 4500, "modifier": 6000}
    )

    # Store and analyze
    store = MetricsStore()
    store.record_run(sample_run)
    store.print_report()

    # Estimate costs
    total_tokens = sum(sample_run.token_usage.values())
    CostEstimator.print_cost_breakdown(
        provider="deepseek",
        input_tokens=total_tokens,
        output_tokens=total_tokens // 2
    )
