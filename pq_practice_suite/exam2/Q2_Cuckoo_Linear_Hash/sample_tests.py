"""
sample_tests.py - Visible Sample Test Cases & Debug Runner
Exam 2 - Problem 2: Longest Divisible Subarray
"""

import sys
import traceback


def run_samples(target_module_name="student_code"):
    print("=" * 60)
    print("RUNNING VISIBLE SAMPLE CASES & DEBUG LOGS")
    print(f"Target Module: {target_module_name}")
    print("=" * 60)

    try:
        if target_module_name == "student_code":
            import student_code
            func = getattr(student_code, "longest_divisible_subarray", None)
        else:
            import solution
            func = getattr(solution, "longest_divisible_subarray", None)
    except Exception:
        print(f"IMPORT / SYNTAX ERROR:\n{traceback.format_exc()}")
        return 0, 1

    if not func:
        print("ERROR: longest_divisible_subarray() function not found!")
        return 0, 1

    cases = [
        ("Sample 1: Handout Example", [2, 7, 6, 1, 4, 5], 3, (4, 1, 4)),
        ("Sample 2: Negative Numbers", [-2, 2, -8, 1], 5, (3, 1, 3)),
        ("Sample 3: Entire Array Divisible", [3, 6, 9, 12], 3, (4, 0, 3)),
        ("Sample 4: No Divisible Subarray", [1, 1], 3, (0, -1, -1)),
        ("Sample 5: Minimal Single Element Divisible", [5], 5, (1, 0, 0)),
    ]

    passed = 0
    for name, arr, k, expected in cases:
        print(f"\n--- {name} ---")
        print(f"Input: arr={arr}, k={k}")
        print(">>> Student Output / Debug Prints:")
        try:
            actual = func(arr, k)
            print(f">>> Function Returned: {actual}")
            print(f"Expected:              {expected}")
            if actual == expected:
                print("Status: [PASS]")
                passed += 1
            else:
                print(f"Status: [FAIL - Output mismatch: expected {expected}, got {actual}]")
        except Exception:
            print("Status: [EXCEPTION]")
            print(traceback.format_exc())

    print("\n" + "=" * 60)
    print(f"SAMPLE RUN COMPLETE: {passed}/{len(cases)} Cases Passed")
    print("=" * 60)
    return passed, len(cases)


if __name__ == "__main__":
    mod = sys.argv[1] if len(sys.argv) > 1 else "student_code"
    passed, total = run_samples(mod)
    sys.exit(0 if passed == total else 1)
