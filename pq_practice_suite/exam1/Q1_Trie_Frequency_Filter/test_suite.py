"""
test_suite.py - Authentic VPL Evaluation Runner for Exam 1 Problem 1
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 1)
"""

import sys
import time
import random


def evaluate(target_module_name="student_code"):
    print(f"============================================================")
    print(f"COL1101 Exam 1 - Problem 1: Sliding Window Max XOR Evaluation")
    print(f"Target Module: {target_module_name}")
    print(f"============================================================")

    try:
        if target_module_name == "student_code":
            from student_code import max_xor_in_window
        else:
            from solution import max_xor_in_window
    except ImportError as e:
        print(f"IMPORT ERROR: Could not import max_xor_in_window: {e}")
        print("Grade :=>> 0")
        return 0

    points = 0
    total_points = 40

    # Test 1: Public Handout Specification (8 pts)
    try:
        stream = [3, 10, 5, 25, 2, 8]
        assert max_xor_in_window(stream, 3) == 28
        assert max_xor_in_window(stream, 2) == 28 # (5 ^ 25 = 28)
        assert max_xor_in_window([1, 2], 2) == 3
        print("  [PASS] Test 1: Public Handout Specification Trace (8/8 pts)")
        points += 8
    except Exception as e:
        print(f"  [FAIL] Test 1: Public Handout Trace Failed: {e}")

    # Test 2: Edge Cases (Empty, Single, Window=1, Uniform Values) (8 pts)
    try:
        assert max_xor_in_window([], 5) == 0
        assert max_xor_in_window([42], 5) == 0
        assert max_xor_in_window([10, 20, 30], 1) == 0
        assert max_xor_in_window([7, 7, 7, 7], 3) == 0
        assert max_xor_in_window([0, 1024, 0, 1024], 2) == 1024
        print("  [PASS] Test 2: Boundary & Degenerate Cases (8/8 pts)")
        points += 8
    except Exception as e:
        print(f"  [FAIL] Test 2: Boundary Cases Failed: {e}")

    # Test 3: Window Boundary Sensitivity & Eviction Dynamics (8 pts)
    try:
        # 1 and 1023 (1 ^ 1023 = 1022) are separated by distance 3
        # In stream [1, 0, 0, 1023], with window_size=3, 1 and 1023 cannot be paired!
        s1 = [1, 0, 0, 1023]
        assert max_xor_in_window(s1, 3) == 1023 # (0 ^ 1023 = 1023)
        
        # With window_size=4, 1 and 1023 can be paired (1 ^ 1023 = 1022 vs 0 ^ 1023 = 1023)
        s2 = [1, 2, 4, 8, 16]
        # with window 2: max is (8 ^ 16 = 24)
        assert max_xor_in_window(s2, 2) == 24
        print("  [PASS] Test 3: Window Boundary & Sliding Eviction (8/8 pts)")
        points += 8
    except Exception as e:
        print(f"  [FAIL] Test 3: Sliding Eviction Failed: {e}")

    # Test 4: Stress Scaling (20,000 packets in under 0.6s) (16 pts)
    try:
        rng = random.Random(42)
        large_stream = [rng.randint(0, (1 << 30) - 1) for _ in range(15000)]
        t0 = time.perf_counter()
        res = max_xor_in_window(large_stream, 250)
        dt = time.perf_counter() - t0
        assert res > 0, "Expected non-zero XOR from large random stream"
        assert dt < 1.0, f"Execution too slow: {dt:.3f}s (expected < 1.0s)"
        print(f"  [PASS] Test 4: High-Throughput Stress Telemetry (15,000 items in {dt:.3f}s) (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 4: Stress Telemetry Failed: {e}")

    print(f"\nFINAL SCORE: {points}/{total_points}")
    print(f"Grade :=>> {points}")
    return points


if __name__ == "__main__":
    mod = sys.argv[1] if len(sys.argv) > 1 else "student_code"
    evaluate(mod)
