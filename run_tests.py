#!/usr/bin/env python3
"""
Comprehensive test runner for Biomedical Assistant
"""
import os
import sys
import subprocess
import argparse


def run_pytest_tests(test_type="all",
                     coverage=True,
                     verbose=True,
                     html_report=True):
    """Run pytest tests with specified options."""

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test selection
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "stress":
        cmd.extend(["-m", "stress"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])

    # Add coverage options
    if coverage:
        cmd.extend(["--cov=knowledge_graph", "--cov=rag", "--cov=app"])
        if html_report:
            cmd.extend(["--cov-report=html:htmlcov"])
        cmd.extend(["--cov-report=term-missing"])

    # Add verbosity
    if verbose:
        cmd.extend(["-v"])

    # Add test discovery
    cmd.append("tests/")

    print(f"Running tests with command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        return False


def run_specific_test_file(test_file):
    """Run a specific test file."""
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False

    cmd = ["python", "-m", "pytest", test_file, "-v"]
    print(f"Running specific test: {test_file}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Test failed with exit code: {e.returncode}")
        return False


def run_coverage_report():
    """Generate and display coverage report."""
    print("Generating coverage report...")
    print("=" * 60)

    try:
        # Generate HTML coverage report
        subprocess.run(["python", "-m", "coverage", "html"], check=True)
        print("✅ HTML coverage report generated in htmlcov/ directory")

        # Display terminal coverage report
        subprocess.run(["python", "-m", "coverage", "report"], check=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Coverage report generation failed: {e}")
        return False


def install_test_dependencies():
    """Install test dependencies if not already installed."""
    print("Checking test dependencies...")

    try:
        import pytest
        import pytest_cov
        print("✅ Test dependencies already installed")
        return True
    except ImportError:
        print("Installing test dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r",
                "requirements.txt"
            ],
                           check=True)
            print("✅ Test dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install test dependencies: {e}")
            return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Biomedical Assistant Test Runner")
    parser.add_argument("--type",
                        choices=[
                            "all", "unit", "integration", "performance",
                            "stress", "fast"
                        ],
                        default="all",
                        help="Type of tests to run")
    parser.add_argument("--no-coverage",
                        action="store_true",
                        help="Disable coverage reporting")
    parser.add_argument("--no-html",
                        action="store_true",
                        help="Disable HTML coverage report")
    parser.add_argument("--quiet",
                        action="store_true",
                        help="Reduce verbosity")
    parser.add_argument("--file", type=str, help="Run specific test file")
    parser.add_argument("--coverage-only",
                        action="store_true",
                        help="Only generate coverage report")

    args = parser.parse_args()

    print("🏥 Biomedical Assistant - Test Runner")
    print("=" * 60)

    # Install dependencies if needed
    if not install_test_dependencies():
        print("❌ Cannot proceed without test dependencies")
        return 1

    # Run specific test file if requested
    if args.file:
        success = run_specific_test_file(args.file)
        return 0 if success else 1

    # Generate coverage report only if requested
    if args.coverage_only:
        success = run_coverage_report()
        return 0 if success else 1

    # Run tests
    success = run_pytest_tests(test_type=args.type,
                               coverage=not args.no_coverage,
                               verbose=not args.quiet,
                               html_report=not args.no_html)

    if success:
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")

        # Generate coverage report if enabled
        if not args.no_coverage:
            print("\nGenerating coverage report...")
            run_coverage_report()

        print("\n📊 Test Summary:")
        print(f"   Test Type: {args.type}")
        print(
            f"   Coverage: {'Enabled' if not args.no_coverage else 'Disabled'}"
        )
        print(
            f"   HTML Report: {'Enabled' if not args.no_html else 'Disabled'}")

        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
