"""
Command-line interface for the Script Analysis System.

Usage:
    python -m src.cli analyze <script.json> [--output results.json]
    python -m src.cli validate <script.json>
    python -m src.cli benchmark examples/golden/百妖_ep09_s01-s05.json
    python -m src.cli ab-test <script.json> --variants baseline,optimized
"""

import argparse
import json
import sys
import os
from pathlib import Path
from prompts.schemas import Script, validate_setup_payoff_integrity
from src.pipeline import run_pipeline
from src.ab_testing import ABTestRunner, PromptVariant
from src.exporters import MarkdownExporter
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_script(script_path: str) -> Script:
    """Load and validate a script from JSON file."""
    path = Path(script_path)

    if not path.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return Script(**data)


def export_markdown(final_state: dict, output_path: str, script_path: str):
    """Export analysis results to Markdown report."""
    try:
        exporter = MarkdownExporter()

        # Prepare result data for exporter
        result = {
            "tccs": final_state["discoverer_output"].tccs if final_state["discoverer_output"] else [],
            "rankings": final_state["auditor_output"].rankings if final_state["auditor_output"] else None,
            "modifications": {
                "modifications": final_state["modifier_output"].modification_log if final_state["modifier_output"] else [],
                "total_issues": final_state["modifier_output"].validation.total_issues if final_state["modifier_output"] else 0,
            },
            "_metrics": final_state.get("_metrics", {}),
            "script_json": final_state.get("script_json", {}),
        }

        # Extract script name from path
        script_name = Path(script_path).stem

        # Export to Markdown
        output = exporter.export(result, Path(output_path), script_name=script_name)
        logger.info(f"✅ Markdown report exported to: {output}")
        print(f"\n📄 Markdown报告已导出: {output}")

    except Exception as e:
        logger.error(f"Failed to export Markdown report: {e}")
        print(f"\n⚠️  Markdown导出失败: {e}")


def save_results(output_path: str, final_state: dict):
    """Save pipeline results to JSON file."""
    # Convert Pydantic models to dicts
    output_data = {
        "discoverer_output": final_state["discoverer_output"].model_dump() if final_state["discoverer_output"] else None,
        "auditor_output": final_state["auditor_output"].model_dump() if final_state["auditor_output"] else None,
        "modifier_output": final_state["modifier_output"].model_dump() if final_state["modifier_output"] else None,
        "errors": final_state["errors"],
        "retry_count": final_state["retry_count"]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to: {output_path}")


def cmd_analyze(args):
    """Analyze a script using the full pipeline."""
    logger.info(f"Analyzing script: {args.script}")

    try:
        # Load script
        script = load_script(args.script)
        logger.info(f"Loaded script with {len(script.scenes)} scenes")

        # Get provider from args or environment
        provider = args.provider or os.getenv("LLM_PROVIDER", "deepseek")
        model = args.model

        logger.info(f"Using LLM provider: {provider}" + (f", model: {model}" if model else ""))

        # Run pipeline
        final_state = run_pipeline(script, provider=provider, model=model)

        # Save results
        if args.output:
            save_results(args.output, final_state)

        # Export to Markdown if requested
        if hasattr(args, 'export') and args.export:
            export_markdown(final_state, args.export, args.script)

        # Print summary
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)

        if final_state["discoverer_output"]:
            print(f"\n📋 Stage 1 (Discoverer):")
            print(f"  TCCs identified: {len(final_state['discoverer_output'].tccs)}")
            for tcc in final_state["discoverer_output"].tccs:
                print(f"    - {tcc.tcc_id}: {tcc.super_objective[:50]}... (conf: {tcc.confidence:.2f})")

        if final_state["auditor_output"]:
            print(f"\n📊 Stage 2 (Auditor):")
            rankings = final_state["auditor_output"].rankings
            print(f"  A-line: {rankings.a_line.tcc_id} (spine: {rankings.a_line.spine_score:.1f})")
            print(f"  B-lines: {len(rankings.b_lines)}")
            print(f"  C-lines: {len(rankings.c_lines)}")

        if final_state["modifier_output"]:
            print(f"\n🔧 Stage 3 (Modifier):")
            validation = final_state["modifier_output"].validation
            print(f"  Issues found: {validation.total_issues}")
            print(f"  Fixed: {validation.fixed}")
            print(f"  Skipped: {validation.skipped}")

        if final_state["errors"]:
            print(f"\n⚠️  Warnings/Errors: {len(final_state['errors'])}")
            for error in final_state["errors"]:
                print(f"    - {error}")

        print()

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


def cmd_validate(args):
    """Validate a script's structure without running full analysis."""
    logger.info(f"Validating script: {args.script}")

    try:
        # Load script
        script = load_script(args.script)
        logger.info(f"✅ Script loaded successfully ({len(script.scenes)} scenes)")

        # Run validations
        errors = validate_setup_payoff_integrity(script)

        if errors:
            print(f"\n❌ Validation failed with {len(errors)} errors:")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
            sys.exit(1)
        else:
            print("\n✅ Script validation passed!")
            print(f"  - {len(script.scenes)} scenes")
            print(f"  - All setup-payoff chains are valid")

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


def cmd_benchmark(args):
    """Run benchmark on a script (requires expected output)."""
    logger.info(f"Running benchmark on: {args.script}")

    # Check if expected output exists
    expected_path = Path(args.script).parent / "百妖_ep09_expected.json"
    if not expected_path.exists():
        logger.error(f"Expected output not found: {expected_path}")
        sys.exit(1)

    try:
        # Load script and expected output
        script = load_script(args.script)
        with open(expected_path, 'r', encoding='utf-8') as f:
            expected = json.load(f)

        # Run pipeline
        final_state = run_pipeline(script)

        # Compare results
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)

        # Stage 1 comparison
        if final_state["discoverer_output"]:
            actual_tccs = len(final_state["discoverer_output"].tccs)
            expected_tccs = len(expected["expected_stage1_output"]["tccs"])
            print(f"\n📋 Stage 1:")
            print(f"  Expected TCCs: {expected_tccs}")
            print(f"  Actual TCCs: {actual_tccs}")
            print(f"  Match: {'✅' if actual_tccs == expected_tccs else '❌'}")

        # Stage 2 comparison
        if final_state["auditor_output"]:
            actual_a_line = final_state["auditor_output"].rankings.a_line.tcc_id
            expected_a_line = expected["expected_stage2_output"]["rankings"]["a_line"]["tcc_id"]
            print(f"\n📊 Stage 2:")
            print(f"  Expected A-line: {expected_a_line}")
            print(f"  Actual A-line: {actual_a_line}")
            print(f"  Match: {'✅' if actual_a_line == expected_a_line else '❌'}")

        print()

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        sys.exit(1)


def cmd_ab_test(args):
    """Run A/B test comparing multiple variants."""
    logger.info(f"Running A/B test on: {args.script}")

    try:
        # Load script
        script = load_script(args.script)
        script_name = Path(args.script).stem

        # Create runner
        runner = ABTestRunner()

        # Mode 1: Compare providers
        if args.providers:
            providers = args.providers.split(',')
            logger.info(f"Comparing providers: {providers}")

            comparison = runner.compare_providers(
                script=script,
                providers=providers,
                script_name=script_name
            )

        # Mode 2: Compare named variants
        elif args.variants:
            variant_names = args.variants.split(',')
            provider = args.provider or os.getenv("LLM_PROVIDER", "deepseek")

            logger.info(f"Comparing variants: {variant_names}")

            variants = [
                PromptVariant(name=name, provider=provider)
                for name in variant_names
            ]

            comparison = runner.compare_variants(
                script=script,
                variants=variants,
                script_name=script_name,
                runs_per_variant=args.runs
            )

        # Mode 3: Custom temperature comparison
        elif args.temperatures:
            temps = [float(t) for t in args.temperatures.split(',')]
            provider = args.provider or os.getenv("LLM_PROVIDER", "deepseek")

            logger.info(f"Comparing temperatures: {temps}")

            variants = [
                PromptVariant(
                    name=f"temp-{temp}",
                    provider=provider,
                    temperature=temp
                )
                for temp in temps
            ]

            comparison = runner.compare_variants(
                script=script,
                variants=variants,
                script_name=script_name,
                runs_per_variant=args.runs
            )

        else:
            logger.error("Please specify --variants, --providers, or --temperatures")
            sys.exit(1)

        # Print comparison
        runner.print_comparison(comparison)

        # Save detailed results if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(comparison.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Detailed results saved to: {output_path}")

        # Print conclusion
        print("\n💡 RECOMMENDATION")
        print("="*80)
        if comparison.winner:
            print(f"Based on the test results, '{comparison.winner}' is recommended.")
            winner_result = next(
                r for r in comparison.results
                if r.variant.name == comparison.winner
            )
            print(f"✅ Success rate: 100%")
            print(f"⏱️  Average duration: {winner_result.duration:.2f}s")
            print(f"🎯 TCC confidence: {winner_result.tcc_confidence_avg:.2%}")
        else:
            print("No clear winner. Please review the comparison table above.")
        print("="*80 + "\n")

    except Exception as e:
        logger.error(f"A/B test failed: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Script Analysis System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Analyze a script')
    parser_analyze.add_argument('script', help='Path to script JSON file')
    parser_analyze.add_argument('--output', '-o', help='Output file for results (JSON)')
    parser_analyze.add_argument('--export', '-e', help='Export Markdown report to specified path')
    parser_analyze.add_argument('--provider', '-p',
                                choices=['deepseek', 'anthropic', 'openai'],
                                help='LLM provider (default: from .env or deepseek)')
    parser_analyze.add_argument('--model', '-m', help='Model name (optional)')
    parser_analyze.set_defaults(func=cmd_analyze)

    # Validate command
    parser_validate = subparsers.add_parser('validate', help='Validate a script structure')
    parser_validate.add_argument('script', help='Path to script JSON file')
    parser_validate.set_defaults(func=cmd_validate)

    # Benchmark command
    parser_benchmark = subparsers.add_parser('benchmark', help='Run benchmark test')
    parser_benchmark.add_argument('script', help='Path to golden dataset script')
    parser_benchmark.set_defaults(func=cmd_benchmark)

    # A/B test command
    parser_abtest = subparsers.add_parser('ab-test', help='Run A/B test comparing variants')
    parser_abtest.add_argument('script', help='Path to script JSON file')
    parser_abtest.add_argument('--variants', help='Comma-separated variant names (e.g., baseline,optimized)')
    parser_abtest.add_argument('--providers', help='Comma-separated provider names (e.g., deepseek,anthropic)')
    parser_abtest.add_argument('--temperatures', help='Comma-separated temperatures (e.g., 0.0,0.5,0.7)')
    parser_abtest.add_argument('--provider', '-p',
                               choices=['deepseek', 'anthropic', 'openai'],
                               help='Base provider for variant/temperature comparison')
    parser_abtest.add_argument('--runs', '-r', type=int, default=1,
                               help='Number of runs per variant (for averaging)')
    parser_abtest.add_argument('--output', '-o', help='Output file for detailed results')
    parser_abtest.set_defaults(func=cmd_ab_test)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
