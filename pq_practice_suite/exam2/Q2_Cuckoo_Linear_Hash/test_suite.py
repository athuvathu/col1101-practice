"""
test_suite.py - Authentic VPL Evaluation Runner for Exam 2 Problem 2
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 2)
"""

import sys
import time
import random


def evaluate(target_module_name="student_code"):
    print(f"============================================================")
    print(f"COL1101 Exam 2 - Problem 2: Longest Divisible Subarray")
    print(f"Target Module: {target_module_name}")
    print(f"============================================================")

    try:
        if target_module_name == "student_code":
            from student_code import longest_divisible_subarray
        else:
            from solution import longest_divisible_subarray
    except ImportError as e:
        print(f"IMPORT ERROR: Could not import longest_divisible_subarray: {e}")
        print("Grade :=>> 0")
        return 0

    points = 0
    total_points = 60

    # Test 1: Public Handout Trace (12 pts)
    try:
        arr = [2, 7, 6, 1, 4, 5]
        res = longest_divisible_subarray(arr, 3)
        assert res == (4, 1, 4), f"Expected (4, 1, 4), got {res}"
        # Verification: sum(arr[1..4]) = 7+6+1+4 = 18 % 3 == 0
        assert sum(arr[1:5]) % 3 == 0
        print("  [PASS] Test 1: Public Handout Specification Trace (12/12 pts)")
        points += 12
    except Exception as e:
        print(f"  [FAIL] Test 1: Public Handout Trace Failed: {e}")

    # Test 2: Negative Numbers & Entire Array Divisible (16 pts)
    try:
        # Negative numbers handling in modular arithmetic
        arr_neg = [-2, 2, -8, 1]
        # sum([-2, 2]) = 0 % 5 == 0 -> len 2 [0..1]
        # sum([2, -8, 1]) = -5 % 5 == 0 -> len 3 [1..3] (longer!)
        res_neg = longest_divisible_subarray(arr_neg, 5)
        assert res_neg == (3, 1, 3), f"Expected (3, 1, 3), got {res_neg}"

        # Entire array is divisible
        arr_all = [3, 6, 9, 12]
        assert longest_divisible_subarray(arr_all, 3) == (4, 0, 3)

        # No divisible non-empty subarray
        arr_none = [1, 1]
        assert longest_divisible_subarray(arr_none, 3) == (0, -1, -1)

        print("  [PASS] Test 2: Negative Numbers & Full Array Cases (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 2: Negative Numbers Failed: {e}")

    # Test 3: Large Modulus & Earliest Tie-breaking (16 pts)
    try:
        # Two equal length divisible subarrays: [0..1] (sum 6) and [2..3] (sum 6)
        arr_tie = [2, 4, 1, 5]
        res_tie = longest_divisible_subarray(arr_tie, 6)
        assert res_tie == (4, 0, 3) # sum 12 % 6 == 0, full array len 4!

        # Two disjoint len 2 subarrays:
        arr_tie2 = [1, 2, 9, 4, 5]
        # [1, 2] sum 3 % 3 == 0 (start 0, end 1, len 2)
        # [4, 5] sum 9 % 3 == 0 (start 3, end 4, len 2)
        # Full [1, 2, 9, 4, 5] sum 21 % 3 == 0 (len 5, start 0, end 4)
        assert longest_divisible_subarray(arr_tie2, 3) == (5, 0, 4)

        # Large K > N
        arr_large_k = [1000000000, 2000000000]
        assert longest_divisible_subarray(arr_large_k, 3000000000) == (2, 0, 1)

        print("  [PASS] Test 3: Large Modulus & Tie-Breaking (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 3: Large Modulus Failed: {e}")

    # Test 4: Stress Scaling (20,000 items in < 0.2s) (16 pts)
    try:
        rng = random.Random(999)
        large_arr = [rng.randint(-10000, 10000) for _ in range(20000)]
        k = 179

        t0 = time.perf_counter()
        length, s, e = longest_divisible_subarray(large_arr, k)
        dt = time.perf_counter() - t0

        if length > 0:
            assert sum(large_arr[s:e+1]) % k == 0
        assert dt < 0.5, f"Execution too slow: {dt:.3f}s"
        print(f"  [PASS] Test 4: High-Throughput Stream (20,000 items in {dt:.3f}s) (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 4: Stress Scaling Failed: {e}")

    print(f"\nFINAL SCORE: {points}/{total_points}")
    print(f"Grade :=>> {points}")
    return points


if __name__ == "__main__":
    mod = sys.argv[1] if len(sys.argv) > 1 else "student_code"
    evaluate(mod)
