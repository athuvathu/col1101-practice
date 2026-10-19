"""
sample_tests.py - Visible Sample Test Cases & Debug Runner
Exam 1 - Problem 2: Running Quantile Monitor
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
            cls = getattr(student_code, "RunningQuantile", None)
        else:
            import solution
            cls = getattr(solution, "RunningQuantile", None)
    except Exception:
        print(f"IMPORT / SYNTAX ERROR:\n{traceback.format_exc()}")
        return 0, 1

    if not cls:
        print("ERROR: RunningQuantile class not found!")
        return 0, 1

    passed = 0
    total = 3

    # Sample 1: Handout Trace (Median p=0.5)
    print("\n--- Sample 1: Handout Trace (p = 0.50 Median) ---")
    print("Operations: add(10), add(20), add(5), add(1), add(15)")
    print(">>> Student Output / Debug Prints:")
    try:
        rq = cls(p=0.5)
        step_outputs = []
        for val in [10, 20, 5, 1, 15]:
            rq.add(val)
            step_outputs.append(rq.get_quantile())

        expected = [10, 10, 10, 5, 10]
        print(f">>> Quantiles after each step: {step_outputs}")
        print(f"Expected:                     {expected}")
        if step_outputs == expected and len(rq) == 5:
            print("Status: [PASS]")
            passed += 1
        else:
            print(f"Status: [FAIL - Mismatch]")
    except Exception:
        print("Status: [EXCEPTION]")
        print(traceback.format_exc())

    # Sample 2: 75th Percentile
    print("\n--- Sample 2: 75th Percentile (p = 0.75) ---")
    print("Operations: add(1), add(2), add(3), add(4)")
    print(">>> Student Output / Debug Prints:")
    try:
        rq75 = cls(p=0.75)
        for v in [1, 2, 3, 4]:
            rq75.add(v)
        actual = rq75.get_quantile()
        print(f">>> Function Returned: {actual}")
        print(f"Expected:              3")
        if actual == 3:
            print("Status: [PASS]")
            passed += 1
        else:
            print(f"Status: [FAIL - expected 3, got {actual}]")
    except Exception:
        print("Status: [EXCEPTION]")
        print(traceback.format_exc())

    # Sample 3: Empty State
    print("\n--- Sample 3: Empty State Handling ---")
    print(">>> Student Output / Debug Prints:")
    try:
        rq_empty = cls(p=0.5)
        q = rq_empty.get_quantile()
        print(f">>> get_quantile() on empty monitor: {q}")
        print(f"Expected:                           None")
        if q is None and len(rq_empty) == 0:
            print("Status: [PASS]")
            passed += 1
        else:
            print("Status: [FAIL]")
    except Exception:
        print("Status: [EXCEPTION]")
        print(traceback.format_exc())

    print("\n" + "=" * 60)
    print(f"SAMPLE RUN COMPLETE: {passed}/{total} Cases Passed")
    print("=" * 60)
    return passed, total


if __name__ == "__main__":
    mod = sys.argv[1] if len(sys.argv) > 1 else "student_code"
    passed, total = run_samples(mod)
    sys.exit(0 if passed == total else 1)
