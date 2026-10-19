"""
sample_tests.py - Visible Sample Test Cases & Debug Runner
Exam 1 - Problem 1: Sliding Window Max XOR Pair
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
            func = getattr(student_code, "max_xor_in_window", None)
        else:
            import solution
            func = getattr(solution, "max_xor_in_window", None)
    except Exception as e:
        print(f"IMPORT / SYNTAX ERROR:\n{traceback.format_exc()}")
        return 0, 1

    if not func:
        print("ERROR: max_xor_in_window() function not found!")
        return 0, 1

    cases = [
        ("Sample 1 (Handout Example)", [3, 10, 5, 25, 2, 8], 3, 28),
        ("Sample 2 (Window = 2)", [1, 2, 4, 8, 16], 2, 24),
        ("Sample 3 (Small Window = 1)", [10, 20, 30], 1, 0),
        ("Sample 4 (Minimal Pair)", [1, 2], 2, 3),
        ("Sample 5 (Uniform Values)", [7, 7, 7, 7], 3, 0),
    ]

    passed = 0
    for name, stream, w, expected in cases:
        print(f"\n--- {name} ---")
        print(f"Input: stream={stream}, window_size={w}")
        print(">>> Student Output / Debug Prints:")
        try:
            actual = func(stream, w)
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
