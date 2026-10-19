"""
sample_tests.py - Visible Sample Test Cases & Debug Runner
Exam 2 - Problem 1: Limit Order Book Matching Engine
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
            func = getattr(student_code, "simulate_order_book", None)
        else:
            import solution
            func = getattr(solution, "simulate_order_book", None)
    except Exception:
        print(f"IMPORT / SYNTAX ERROR:\n{traceback.format_exc()}")
        return 0, 1

    if not func:
        print("ERROR: simulate_order_book() function not found!")
        return 0, 1

    passed = 0
    total = 2

    # Sample 1: Handout Trace
    print("\n--- Sample 1: Handout Example (Single Crossing Trade) ---")
    orders1 = [
        {"id": "S1", "type": "SELL", "price": 105, "qty": 10},
        {"id": "S2", "type": "SELL", "price": 100, "qty": 5},
        {"id": "B1", "type": "BUY",  "price": 102, "qty": 8}
    ]
    print(f"Orders: {orders1}")
    print(">>> Student Output / Debug Prints:")
    try:
        vol, trades = func(orders1)
        print(f">>> Traded Volume: {vol}")
        print(f">>> Trades Log:    {trades}")
        expected_vol = 5
        expected_trades = [("B1", "S2", 100, 5)]
        print(f"Expected Volume:   {expected_vol}")
        print(f"Expected Trades:   {expected_trades}")
        if vol == expected_vol and trades == expected_trades:
            print("Status: [PASS]")
            passed += 1
        else:
            print("Status: [FAIL - Output mismatch]")
    except Exception:
        print("Status: [EXCEPTION]")
        print(traceback.format_exc())

    # Sample 2: Multi-level Sweeping & Residual Book Resting
    print("\n--- Sample 2: Multi-Level Order Sweep ---")
    orders2 = [
        {"id": "S1", "type": "SELL", "price": 100, "qty": 10},
        {"id": "S2", "type": "SELL", "price": 102, "qty": 10},
        {"id": "B1", "type": "BUY",  "price": 103, "qty": 15}
    ]
    print(f"Orders: {orders2}")
    print(">>> Student Output / Debug Prints:")
    try:
        vol2, trades2 = func(orders2)
        print(f">>> Traded Volume: {vol2}")
        print(f">>> Trades Log:    {trades2}")
        expected_vol2 = 15
        expected_trades2 = [("B1", "S1", 100, 10), ("B1", "S2", 102, 5)]
        print(f"Expected Volume:   {expected_vol2}")
        print(f"Expected Trades:   {expected_trades2}")
        if vol2 == expected_vol2 and trades2 == expected_trades2:
            print("Status: [PASS]")
            passed += 1
        else:
            print("Status: [FAIL - Output mismatch]")
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
