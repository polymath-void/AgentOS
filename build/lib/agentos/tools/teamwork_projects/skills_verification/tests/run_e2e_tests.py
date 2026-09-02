#!/usr/bin/env python3
"""
E2E Test Runner Harness for AI Agent Skills Workspace Verification.

Discovers and executes all `test_tier*.py` modules in the tests directory
using Python standard library unittest, printing progress and detailed test
count summaries (passed, failed, total) grouped by Tier.
"""

import sys
import os
import re
import time
import argparse
import unittest
from pathlib import Path

# Ensure project root and tests directory are in sys.path
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


class TierTestResult(unittest.TestResult):
    """
    Custom TestResult listener that tracks test outcomes (pass, fail, skip, error)
    grouped by test Tier (e.g. Tier 1, Tier 2, etc.).
    """

    def __init__(self, stream=sys.stdout, verbosity=1):
        super().__init__(stream, verbosity)
        self.stream = stream
        self.verbosity = verbosity
        self.tier_stats = {}
        self.failures_details = []
        self.errors_details = []

    def _get_tier_name(self, test) -> str:
        """Extract Tier label from test module or test ID."""
        test_id = test.id()
        # Look for test_tierN or TierN pattern
        match = re.search(r'tier[_\s]*(\d+)', test_id, re.IGNORECASE)
        if match:
            return f"Tier {match.group(1)}"
        return "Other Tiers"

    def _init_tier(self, tier_name: str):
        if tier_name not in self.tier_stats:
            self.tier_stats[tier_name] = {
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'total': 0
            }

    def startTest(self, test):
        super().startTest(test)
        tier_name = self._get_tier_name(test)
        self._init_tier(tier_name)
        if self.verbosity > 1:
            self.stream.write(f"[{tier_name}] {test.id()} ... ")
            self.stream.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        tier_name = self._get_tier_name(test)
        self._init_tier(tier_name)
        self.tier_stats[tier_name]['passed'] += 1
        self.tier_stats[tier_name]['total'] += 1
        if self.verbosity > 1:
            self.stream.write("OK\n")
        elif self.verbosity == 1:
            self.stream.write(".")
            self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        tier_name = self._get_tier_name(test)
        self._init_tier(tier_name)
        self.tier_stats[tier_name]['failed'] += 1
        self.tier_stats[tier_name]['total'] += 1
        self.failures_details.append((test, self._exc_info_to_string(err, test)))
        if self.verbosity > 1:
            self.stream.write("FAIL\n")
        elif self.verbosity == 1:
            self.stream.write("F")
            self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        tier_name = self._get_tier_name(test)
        self._init_tier(tier_name)
        self.tier_stats[tier_name]['failed'] += 1
        self.tier_stats[tier_name]['total'] += 1
        self.errors_details.append((test, self._exc_info_to_string(err, test)))
        if self.verbosity > 1:
            self.stream.write("ERROR\n")
        elif self.verbosity == 1:
            self.stream.write("E")
            self.stream.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        tier_name = self._get_tier_name(test)
        self._init_tier(tier_name)
        self.tier_stats[tier_name]['skipped'] += 1
        self.tier_stats[tier_name]['total'] += 1
        if self.verbosity > 1:
            self.stream.write(f"SKIPPED ({reason})\n")
        elif self.verbosity == 1:
            self.stream.write("S")
            self.stream.flush()


def natural_tier_sort_key(tier_name: str):
    """Sort key helper for tier names like 'Tier 1', 'Tier 2', 'Tier 10'."""
    match = re.search(r'(\d+)', tier_name)
    if match:
        return (0, int(match.group(1)))
    return (1, tier_name)


def main():
    parser = argparse.ArgumentParser(
        description="Run E2E Test Suite for AI Agent Skills Workspace Verification."
    )
    parser.add_argument(
        "-v", "--verbosity", type=int, choices=[0, 1, 2], default=1,
        help="Verbosity level: 0 = quiet, 1 = dots (default), 2 = verbose"
    )
    parser.add_argument(
        "--pattern", type=str, default="test_tier*.py",
        help="Glob pattern for discovering test modules (default: test_tier*.py)"
    )
    parser.add_argument(
        "--tier", type=str, default=None,
        help="Filter tests by specific tier (e.g. tier1, tier2)"
    )
    args = parser.parse_args()

    print("======================================================================")
    print("AI AGENT SKILLS WORKSPACE — E2E TEST RUNNER")
    print("======================================================================")
    print(f"Test Directory : {TESTS_DIR}")
    print(f"Pattern        : {args.pattern}")
    if args.tier:
        print(f"Tier Filter    : {args.tier}")
    print("----------------------------------------------------------------------")

    start_time = time.time()

    # Discover tests
    loader = unittest.TestLoader()

    if not TESTS_DIR.exists():
        TESTS_DIR.mkdir(parents=True, exist_ok=True)

    suite = loader.discover(start_dir=str(TESTS_DIR), pattern=args.pattern)

    # Filter suite if tier filter is requested
    if args.tier:
        filtered_suite = unittest.TestSuite()
        tier_filter_pattern = args.tier.lower()
        def _filter_tests(test_item):
            if isinstance(test_item, unittest.TestSuite):
                for sub in test_item:
                    _filter_tests(sub)
            elif isinstance(test_item, unittest.TestCase):
                if tier_filter_pattern in test_item.id().lower():
                    filtered_suite.addTest(test_item)
        _filter_tests(suite)
        suite = filtered_suite

    total_discovered = suite.countTestCases()

    if total_discovered == 0:
        print("\n[WARNING] No test cases found matching pattern!")
        print("----------------------------------------------------------------------")
        print("Summary:")
        print("  Passed : 0")
        print("  Failed : 0")
        print("  Skipped: 0")
        print("  Total  : 0")
        print("======================================================================")
        print("Result: SUCCESS (0 tests executed)")
        sys.exit(0)

    # Run tests
    result = TierTestResult(sys.stdout, verbosity=args.verbosity)
    suite.run(result)

    elapsed_time = time.time() - start_time
    if args.verbosity == 1:
        print()  # New line after progress dots

    # Print failures and errors details
    if result.failures_details or result.errors_details:
        print("\n======================================================================")
        print("DETAILED TEST FAILURES / ERRORS")
        print("======================================================================")
        for test, trace in result.failures_details:
            print(f"\n--- FAILURE: {test.id()} ---")
            print(trace)
        for test, trace in result.errors_details:
            print(f"\n--- ERROR: {test.id()} ---")
            print(trace)

    # Print summary table
    print("\n======================================================================")
    print("E2E TEST SUMMARY BY TIER")
    print("======================================================================")
    header = f"{'Tier':<24} {'Passed':>10} {'Failed':>10} {'Skipped':>10} {'Total':>10}"
    print(header)
    print("-" * len(header))

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_count = 0

    sorted_tiers = sorted(result.tier_stats.keys(), key=natural_tier_sort_key)
    for tier in sorted_tiers:
        stats = result.tier_stats[tier]
        p = stats['passed']
        f = stats['failed']
        s = stats['skipped']
        t = stats['total']

        total_passed += p
        total_failed += f
        total_skipped += s
        total_count += t

        print(f"{tier:<24} {p:>10} {f:>10} {s:>10} {t:>10}")

    print("-" * len(header))
    summary_total = f"{'TOTAL':<24} {total_passed:>10} {total_failed:>10} {total_skipped:>10} {total_count:>10}"
    print(summary_total)
    print("======================================================================")
    print(f"Elapsed Time: {elapsed_time:.3f}s")

    if total_failed > 0 or len(result.errors) > 0 or len(result.failures) > 0:
        print("Result: FAILURE")
        sys.exit(1)
    else:
        print("Result: SUCCESS")
        sys.exit(0)


if __name__ == "__main__":
    main()
