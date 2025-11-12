"""
Command-line interface for the Script Analysis System.

Usage:
    python -m src.cli analyze <script.json> [--output results.json]
    python -m src.cli validate <script.json>
    python -m src.cli benchmark examples/golden/百妖_ep09_s01-s05.json
"""

import argparse
import json
import sys
import os
from pathlib import Path
from prompts.schemas import Script, validate_setup_payoff_integrity
from src.pipeline import run_pipeline
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
    parser_analyze.add_argument('--output', '-o', help='Output file for results')
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

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
