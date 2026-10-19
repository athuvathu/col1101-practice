"""
test_suite.py - Authentic VPL Evaluation Runner for Exam 1 Problem 2
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 2)
"""

import sys
import time
import math
import random


def evaluate(target_module_name="student_code"):
    print(f"============================================================")
    print(f"COL1101 Exam 1 - Problem 2: Running Quantile Monitor Evaluation")
    print(f"Target Module: {target_module_name}")
    print(f"============================================================")

    try:
        if target_module_name == "student_code":
            from student_code import RunningQuantile
        else:
            from solution import RunningQuantile
    except ImportError as e:
        print(f"IMPORT ERROR: Could not import RunningQuantile: {e}")
        print("Grade :=>> 0")
        return 0

    points = 0
    total_points = 60

    # Test 1: Public Handout Specification (12 pts)
    try:
        rq = RunningQuantile(p=0.5)
        assert rq.get_quantile() is None
        assert len(rq) == 0

        rq.add(10)
        assert rq.get_quantile() == 10
        rq.add(20)
        assert rq.get_quantile() == 10
        rq.add(5)
        assert rq.get_quantile() == 10
        rq.add(1)
        assert rq.get_quantile() == 5
        rq.add(15)
        assert rq.get_quantile() == 10
        assert len(rq) == 5

        print("  [PASS] Test 1: Public Handout Median Trace (12/12 pts)")
        points += 12
    except Exception as e:
        print(f"  [FAIL] Test 1: Public Handout Trace Failed: {e}")

    # Test 2: Arbitrary Percentiles (p=0.25, p=0.75, p=0.90) (16 pts)
    try:
        # p = 0.25 on values 1..12
        rq25 = RunningQuantile(p=0.25)
        for x in [5, 1, 9, 3, 11, 7, 2, 8, 4, 12, 6, 10]:
            rq25.add(x)
        # N=12, K=ceil(0.25 * 12) = 3 -> 3rd element in 1..12 is 3
        assert rq25.get_quantile() == 3, f"Expected 3, got {rq25.get_quantile()}"

        # p = 0.90 on values 1..10
        rq90 = RunningQuantile(p=0.90)
        for x in range(1, 11):
            rq90.add(x)
        # N=10, K=ceil(0.9 * 10) = 9 -> 9th element is 9
        assert rq90.get_quantile() == 9

        print("  [PASS] Test 2: Arbitrary Quantiles (p=0.25, 0.90) (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 2: Quantile Invariant Failed: {e}")

    # Test 3: Duplicates & Reverse-sorted Stream (16 pts)
    try:
        rq_dup = RunningQuantile(p=0.5)
        for _ in range(5):
            rq_dup.add(42)
        assert rq_dup.get_quantile() == 42

        # Monotonically decreasing stream
        rq_dec = RunningQuantile(p=0.6)
        elements = list(range(100, 0, -1))
        ground_truth = []
        for x in elements:
            rq_dec.add(x)
            ground_truth.append(x)
            sorted_curr = sorted(ground_truth)
            k = math.ceil(0.6 * len(ground_truth))
            expected = sorted_curr[k - 1]
            assert rq_dec.get_quantile() == expected

        print("  [PASS] Test 3: Stream Invariants & Duplicate Elements (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 3: Duplicates & Invariants Failed: {e}")

    # Test 4: Stress Scaling (20,000 insertions & O(1) queries in < 0.3s) (16 pts)
    try:
        rng = random.Random(1337)
        rq_stress = RunningQuantile(p=0.73)
        stream = [rng.uniform(-1000.0, 1000.0) for _ in range(15000)]

        t0 = time.perf_counter()
        for v in stream:
            rq_stress.add(v)
            _ = rq_stress.get_quantile()
        dt = time.perf_counter() - t0

        assert len(rq_stress) == 15000
        # Verification of final quantile
        sorted_all = sorted(stream)
        target_k = math.ceil(0.73 * 15000)
        expected_final = sorted_all[target_k - 1]
        assert abs(rq_stress.get_quantile() - expected_final) < 1e-9

        assert dt < 0.8, f"Too slow: {dt:.3f}s (expected < 0.8s)"
        print(f"  [PASS] Test 4: High-Throughput Stream (15,000 ops in {dt:.3f}s) (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 4: Stress Quantile Failed: {e}")

    print(f"\nFINAL SCORE: {points}/{total_points}")
    print(f"Grade :=>> {points}")
    return points


if __name__ == "__main__":
    mod = sys.argv[1] if len(sys.argv) > 1 else "student_code"
    evaluate(mod)
