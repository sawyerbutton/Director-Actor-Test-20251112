"""
Performance benchmark script for comparing v2.0 vs v2.1 prompts.

This script measures:
1. Accuracy: How well does the system identify expected TCCs?
2. Precision: Are the identified TCCs correct (no false positives)?
3. Recall: Are all expected TCCs found (no false negatives)?
4. Consistency: Do multiple runs produce the same results?
"""

import json
import time
from pathlib import Path
from typing import Dict, List
from collections import Counter
from prompts.schemas import Script, DiscovererOutput
import sys

# Mock implementation - replace with actual LLM calls when ready
class BenchmarkRunner:
    """Run performance benchmarks on the script analysis system."""

    def __init__(self, golden_dataset_path: str):
        """Initialize with golden dataset."""
        self.dataset_path = Path(golden_dataset_path)
        self.script_path = self.dataset_path / "百妖_ep09_s01-s05.json"
        self.expected_path = self.dataset_path / "百妖_ep09_expected.json"

        # Load data
        with open(self.script_path, 'r', encoding='utf-8') as f:
            self.script = Script(**json.load(f))

        with open(self.expected_path, 'r', encoding='utf-8') as f:
            self.expected = json.load(f)

    def run_stage1_benchmark(self, num_runs: int = 3) -> Dict:
        """
        Run Stage 1 (Discoverer) benchmark.

        Args:
            num_runs: Number of times to run (for consistency testing)

        Returns:
            Benchmark results dictionary
        """
        print(f"\n{'='*60}")
        print("Stage 1 (Discoverer) Benchmark")
        print(f"{'='*60}")

        results = {
            "accuracy": [],
            "precision": [],
            "recall": [],
            "execution_times": [],
            "tcc_counts": [],
            "confidence_scores": []
        }

        expected_tccs = {t["tcc_id"]: t for t in self.expected["expected_stage1_output"]["tccs"]}
        expected_tcc_ids = set(expected_tccs.keys())

        for run in range(1, num_runs + 1):
            print(f"\nRun {run}/{num_runs}...")
            start_time = time.time()

            # TODO: Replace with actual LLM call
            # For now, use mock data
            actual_output = self._mock_discoverer_output()

            execution_time = time.time() - start_time
            results["execution_times"].append(execution_time)

            # Extract actual TCC IDs
            actual_tcc_ids = {tcc.tcc_id for tcc in actual_output.tccs}
            results["tcc_counts"].append(len(actual_tcc_ids))

            # Calculate metrics
            true_positives = len(expected_tcc_ids & actual_tcc_ids)
            false_positives = len(actual_tcc_ids - expected_tcc_ids)
            false_negatives = len(expected_tcc_ids - actual_tcc_ids)

            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            accuracy = true_positives / len(expected_tcc_ids) if expected_tcc_ids else 0

            results["accuracy"].append(accuracy)
            results["precision"].append(precision)
            results["recall"].append(recall)

            # Store confidence scores
            avg_confidence = sum(tcc.confidence for tcc in actual_output.tccs) / len(actual_output.tccs)
            results["confidence_scores"].append(avg_confidence)

            print(f"  ✅ Execution time: {execution_time:.2f}s")
            print(f"  📊 TCCs identified: {len(actual_tcc_ids)}")
            print(f"  🎯 Accuracy: {accuracy:.2%}")
            print(f"  ⚖️  Precision: {precision:.2%}")
            print(f"  📈 Recall: {recall:.2%}")

        # Calculate summary statistics
        summary = self._calculate_summary(results)
        self._print_summary(summary, "Stage 1")

        return {**results, "summary": summary}

    def run_stage2_benchmark(self, num_runs: int = 3) -> Dict:
        """Run Stage 2 (Auditor) benchmark."""
        print(f"\n{'='*60}")
        print("Stage 2 (Auditor) Benchmark")
        print(f"{'='*60}")

        results = {
            "a_line_correct": [],
            "b_line_count_correct": [],
            "execution_times": []
        }

        expected_a_line = self.expected["expected_stage2_output"]["rankings"]["a_line"]["tcc_id"]
        expected_b_count = len(self.expected["expected_stage2_output"]["rankings"]["b_lines"])

        for run in range(1, num_runs + 1):
            print(f"\nRun {run}/{num_runs}...")
            start_time = time.time()

            # TODO: Replace with actual LLM call
            actual_a_line = "TCC_01"  # Mock
            actual_b_count = 1  # Mock

            execution_time = time.time() - start_time
            results["execution_times"].append(execution_time)

            a_line_correct = (actual_a_line == expected_a_line)
            b_count_correct = (actual_b_count == expected_b_count)

            results["a_line_correct"].append(a_line_correct)
            results["b_line_count_correct"].append(b_count_correct)

            print(f"  ✅ Execution time: {execution_time:.2f}s")
            print(f"  🎯 A-line correct: {'✅' if a_line_correct else '❌'}")
            print(f"  📊 B-line count correct: {'✅' if b_count_correct else '❌'}")

        # Calculate summary
        summary = {
            "a_line_accuracy": sum(results["a_line_correct"]) / num_runs,
            "b_line_count_accuracy": sum(results["b_line_count_correct"]) / num_runs,
            "avg_execution_time": sum(results["execution_times"]) / num_runs
        }

        self._print_summary(summary, "Stage 2")

        return {**results, "summary": summary}

    def _mock_discoverer_output(self) -> DiscovererOutput:
        """Mock discoverer output for testing (remove when LLM is integrated)."""
        from prompts.schemas import TCC, DiscovererMetadata

        # Return expected TCCs for now
        tccs = [
            TCC(
                tcc_id="TCC_01",
                super_objective="玉鼠精的电商平台融资计划",
                core_conflict_type="interpersonal",
                evidence_scenes=["S03", "S04", "S05"],
                confidence=0.95
            ),
            TCC(
                tcc_id="TCC_02",
                super_objective="悟空因外表被误解的身份认同困境",
                core_conflict_type="internal",
                evidence_scenes=["S02"],
                confidence=0.75
            ),
            TCC(
                tcc_id="TCC_03",
                super_objective="阿蠢的偶像崇拜幻灭",
                core_conflict_type="internal",
                evidence_scenes=["S03"],
                confidence=0.85
            )
        ]

        return DiscovererOutput(
            tccs=tccs,
            metadata=DiscovererMetadata(
                total_scenes_analyzed=5,
                primary_evidence_available=True,
                fallback_mode=False
            )
        )

    def _calculate_summary(self, results: Dict) -> Dict:
        """Calculate summary statistics from results."""
        return {
            "avg_accuracy": sum(results["accuracy"]) / len(results["accuracy"]),
            "avg_precision": sum(results["precision"]) / len(results["precision"]),
            "avg_recall": sum(results["recall"]) / len(results["recall"]),
            "avg_execution_time": sum(results["execution_times"]) / len(results["execution_times"]),
            "consistency_score": self._calculate_consistency(results["tcc_counts"])
        }

    def _calculate_consistency(self, values: List) -> float:
        """Calculate consistency score (0-1, where 1 is perfectly consistent)."""
        if len(values) <= 1:
            return 1.0

        # Check if all values are the same
        counts = Counter(values)
        most_common_count = counts.most_common(1)[0][1]
        return most_common_count / len(values)

    def _print_summary(self, summary: Dict, stage_name: str):
        """Print formatted summary statistics."""
        print(f"\n{'─'*60}")
        print(f"{stage_name} Summary Statistics")
        print(f"{'─'*60}")

        for key, value in summary.items():
            if isinstance(value, float):
                if "time" in key.lower():
                    print(f"  {key:25s}: {value:.2f}s")
                else:
                    print(f"  {key:25s}: {value:.2%}")
            else:
                print(f"  {key:25s}: {value}")

    def run_full_benchmark(self, num_runs: int = 3) -> Dict:
        """Run complete benchmark across all stages."""
        print(f"\n{'#'*60}")
        print("# FULL PIPELINE BENCHMARK")
        print(f"{'#'*60}")
        print(f"\nDataset: {self.script_path.name}")
        print(f"Scenes: {len(self.script.scenes)}")
        print(f"Runs per stage: {num_runs}")

        results = {}

        try:
            results["stage1"] = self.run_stage1_benchmark(num_runs)
        except Exception as e:
            print(f"\n❌ Stage 1 benchmark failed: {e}")

        try:
            results["stage2"] = self.run_stage2_benchmark(num_runs)
        except Exception as e:
            print(f"\n❌ Stage 2 benchmark failed: {e}")

        # Final summary
        print(f"\n{'#'*60}")
        print("# BENCHMARK COMPLETE")
        print(f"{'#'*60}")

        return results


def main():
    """Run benchmark from command line."""
    if len(sys.argv) < 2:
        print("Usage: python run_benchmark.py <golden_dataset_dir>")
        print("Example: python run_benchmark.py examples/golden")
        sys.exit(1)

    dataset_dir = sys.argv[1]
    num_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    benchmark = BenchmarkRunner(dataset_dir)
    results = benchmark.run_full_benchmark(num_runs)

    # Save results
    output_file = Path("benchmarks") / "latest_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
