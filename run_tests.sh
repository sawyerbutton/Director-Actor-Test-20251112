#!/bin/bash
#
# Test runner script for Script Analysis System
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh schemas      # Run only schema tests
#   ./run_tests.sh golden       # Run only golden dataset tests
#

set -e

echo "Script Analysis System - Test Runner"
echo "===================================="

# Check if pytest is installed
if ! python -m pytest --version > /dev/null 2>&1; then
    echo "Error: pytest not installed"
    echo "Please install test dependencies first:"
    echo "  pip install -r requirements-test.txt"
    exit 1
fi

# Parse arguments
TEST_TARGET="${1:-tests/}"

case "$TEST_TARGET" in
    schemas)
        echo "Running schema unit tests..."
        python -m pytest tests/test_schemas.py -v
        ;;
    golden)
        echo "Running golden dataset integration tests..."
        python -m pytest tests/test_golden_dataset.py -v -m "not llm"
        ;;
    all|tests/)
        echo "Running all tests..."
        python -m pytest tests/ -v -m "not llm"
        ;;
    *)
        echo "Running tests matching: $TEST_TARGET"
        python -m pytest "$TEST_TARGET" -v
        ;;
esac

echo ""
echo "Tests completed!"
