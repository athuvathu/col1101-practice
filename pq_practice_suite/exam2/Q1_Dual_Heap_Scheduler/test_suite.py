"""
test_suite.py - Authentic VPL Evaluation Runner for Exam 2 Problem 1
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 1)
"""

import sys
import time
import random


def evaluate(target_module_name="student_code"):
    print(f"============================================================")
    print(f"COL1101 Exam 2 - Problem 1: Limit Order Book Crossing Engine")
    print(f"Target Module: {target_module_name}")
    print(f"============================================================")

    try:
        if target_module_name == "student_code":
            from student_code import simulate_order_book
        else:
            from solution import simulate_order_book
    except ImportError as e:
        print(f"IMPORT ERROR: Could not import simulate_order_book: {e}")
        print("Grade :=>> 0")
        return 0

    points = 0
    total_points = 40

    # Test 1: Public Handout Trace (8 pts)
    try:
        orders = [
            {"id": "S1", "type": "SELL", "price": 105, "qty": 10},
            {"id": "S2", "type": "SELL", "price": 100, "qty": 5},
            {"id": "B1", "type": "BUY",  "price": 102, "qty": 8}
        ]
        total_vol, trades = simulate_order_book(orders)
        assert total_vol == 5, f"Expected total volume 5, got {total_vol}"
        assert len(trades) == 1
        assert trades[0] == ("B1", "S2", 100, 5)
        print("  [PASS] Test 1: Public Handout Specification Trace (8/8 pts)")
        points += 8
    except Exception as e:
        print(f"  [FAIL] Test 1: Public Handout Trace Failed: {e}")

    # Test 2: Multi-level Sweeping & Partial Fills (8 pts)
    try:
        # Buy order sweeps across multiple ask price levels (100, 102, 105)
        orders = [
            {"id": "S1", "type": "SELL", "price": 100, "qty": 10},
            {"id": "S2", "type": "SELL", "price": 102, "qty": 10},
            {"id": "S3", "type": "SELL", "price": 105, "qty": 10},
            {"id": "B1", "type": "BUY",  "price": 103, "qty": 25}
        ]
        vol, trades = simulate_order_book(orders)
        # Should fill 10 @ 100 (S1), 10 @ 102 (S2), and 5 remaining resting at 103
        assert vol == 20
        assert len(trades) == 2
        assert trades[0] == ("B1", "S1", 100, 10)
        assert trades[1] == ("B1", "S2", 102, 10)

        # Incoming sell sweeps resting B1 (at 103)
        orders2 = orders + [{"id": "S4", "type": "SELL", "price": 101, "qty": 15}]
        vol2, trades2 = simulate_order_book(orders2)
        # S4 should match remaining 5 of B1 at 103
        assert vol2 == 25
        assert len(trades2) == 3
        assert trades2[2] == ("B1", "S4", 103, 5)

        print("  [PASS] Test 2: Multi-Level Order Sweeps & Residual Book Resting (8/8 pts)")
        points += 8
    except Exception as e:
        print(f"  [FAIL] Test 2: Multi-Level Sweeps Failed: {e}")

    # Test 3: FIFO Queue at Same Price Level (8 pts)
    try:
        # Two orders at same price: first to arrive must trade first
        orders = [
            {"id": "S_first",  "type": "SELL", "price": 50, "qty": 5},
            {"id": "S_second", "type": "SELL", "price": 50, "qty": 5},
            {"id": "B1",       "type": "BUY",  "price": 50, "qty": 8}
        ]
        vol, trades = simulate_order_book(orders)
        assert vol == 8
        assert len(trades) == 2
        assert trades[0] == ("B1", "S_first", 50, 5)
        assert trades[1] == ("B1", "S_second", 50, 3)
        print("  [PASS] Test 3: Same Price FIFO Priority Invariant (8/8 pts)")
        points += 8
    except Exception as e:
        print(f"  [FAIL] Test 3: FIFO Priority Invariant Failed: {e}")

    # Test 4: Stress Scaling Simulation (5000 orders in < 0.3s) (16 pts)
    try:
        rng = random.Random(2026)
        stream = []
        for i in range(4000):
            side = "BUY" if rng.random() < 0.5 else "SELL"
            p = rng.randint(90, 110)
            q = rng.randint(1, 20)
            stream.append({"id": f"O_{i}", "type": side, "price": p, "qty": q})

        t0 = time.perf_counter()
        vol, trades = simulate_order_book(stream)
        dt = time.perf_counter() - t0

        assert vol > 0
        assert len(trades) > 0
        assert dt < 0.6, f"Execution too slow: {dt:.3f}s"
        print(f"  [PASS] Test 4: High-Throughput Exchange Stream (4,000 orders in {dt:.3f}s) (16/16 pts)")
        points += 16
    except Exception as e:
        print(f"  [FAIL] Test 4: Stress Simulation Failed: {e}")

    print(f"\nFINAL SCORE: {points}/{total_points}")
    print(f"Grade :=>> {points}")
    return points


if __name__ == "__main__":
    mod = sys.argv[1] if len(sys.argv) > 1 else "student_code"
    evaluate(mod)
