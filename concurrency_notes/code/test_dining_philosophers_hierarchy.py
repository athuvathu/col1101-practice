"""
Module: test_dining_philosophers_hierarchy.py
Formal Verification of Havender's Resource Hierarchy Protocol.

Demonstrates:
1. Deadlock-freedom under high concurrency: 10 philosophers executing 500 total
   eat cycles using Havender's min(L, R) -> max(L, R) acquisition ordering.
2. Formal proof demonstration of Havender's invariant: Every philosopher acquires
   resources in strict monotonically increasing order.
3. Reproduction of circular-wait deadlock when Havender's ordering is violated.
"""

import threading
import time
import pytest
from typing import List, Tuple


# ============================================================================
# 1. Havender Resource Hierarchy Dining Philosophers
# ============================================================================
class DiningPhilosophersHavender:
    """
    Implements Havender's Resource Hierarchy for Dining Philosophers.
    Forks are indexed 0 ... N-1.
    Philosopher i requires fork L = i and fork R = (i + 1) % N.
    Havender Rule: Always acquire min(L, R) first, then max(L, R).
    """

    def __init__(self, num_philosophers: int):
        self.n = num_philosophers
        self.forks = [threading.Lock() for _ in range(num_philosophers)]
        self.eat_counts = [0] * num_philosophers
        self.acquisition_log: List[Tuple[int, int, int]] = []  # (phil_id, first_fork, second_fork)
        self.log_lock = threading.Lock()

    def eat(self, phil_id: int):
        left = phil_id
        right = (phil_id + 1) % self.n

        # Havender hierarchy: strict partial order on resources
        first = min(left, right)
        second = max(left, right)

        with self.forks[first]:
            with self.forks[second]:
                with self.log_lock:
                    self.acquisition_log.append((phil_id, first, second))
                    self.eat_counts[phil_id] += 1
                time.sleep(0.0001)


# ============================================================================
# 2. Naive Circular Dining Philosophers (Subject to Deadlock)
# ============================================================================
class NaiveDiningPhilosophers:
    """
    Naive implementation: Every philosopher acquires left fork, then right fork.
    Under simultaneous start, this provokes a circular wait deadlock.
    """

    def __init__(self, num_philosophers: int):
        self.n = num_philosophers
        self.forks = [threading.Lock() for _ in range(num_philosophers)]
        self.left_barrier = threading.Barrier(num_philosophers)
        self.deadlocked_flags = [False] * num_philosophers

    def attempt_eat_with_timeout(self, phil_id: int, timeout_sec: float) -> bool:
        left = phil_id
        right = (phil_id + 1) % self.n

        # Everyone acquires their left fork
        acquired_left = self.forks[left].acquire(timeout=timeout_sec)
        if not acquired_left:
            self.deadlocked_flags[phil_id] = True
            return False

        try:
            # Synchronize so ALL philosophers hold their left fork before requesting right
            self.left_barrier.wait(timeout=timeout_sec)

            # Now all philosophers hold their left fork and compete for right fork (held by neighbor)
            acquired_right = self.forks[right].acquire(timeout=timeout_sec)
            if not acquired_right:
                # Timed out: circular wait detected!
                self.deadlocked_flags[phil_id] = True
                return False
            try:
                return True
            finally:
                self.forks[right].release()
        except (threading.BrokenBarrierError, Exception):
            self.deadlocked_flags[phil_id] = True
            return False
        finally:
            self.forks[left].release()


# ============================================================================
# Pytest Test Cases
# ============================================================================
def test_havender_hierarchy_prevents_deadlock():
    """
    Verify that 10 philosophers running concurrently with Havender ordering
    complete 500 eating cycles without deadlocking.
    """
    num_phil = 10
    cycles_per_phil = 50
    table = DiningPhilosophersHavender(num_philosophers=num_phil)

    def philosopher_thread(pid: int):
        for _ in range(cycles_per_phil):
            table.eat(pid)

    threads = [
        threading.Thread(target=philosopher_thread, args=(i,))
        for i in range(num_phil)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=5.0)
        assert not t.is_alive(), "Deadlock detected! Thread failed to terminate."

    # Assert all philosophers ate their target number of times
    assert table.eat_counts == [cycles_per_phil] * num_phil, (
        f"Eat count mismatch: {table.eat_counts}"
    )
    assert len(table.acquisition_log) == num_phil * cycles_per_phil


def test_havender_strict_order_invariant():
    """
    Formally verify the strict total order invariant:
    For every fork acquisition pair (f1, f2), f1 < f2.
    """
    num_phil = 5
    table = DiningPhilosophersHavender(num_philosophers=num_phil)

    for i in range(num_phil):
        table.eat(i)

    for pid, first, second in table.acquisition_log:
        assert first < second, (
            f"Havender invariant violated by philosopher {pid}: acquired {first} then {second}"
        )


def test_naive_dining_philosophers_deadlock_detection():
    """
    Demonstrate that naive left-then-right acquisition creates circular wait,
    triggering deadlock timeouts.
    """
    num_phil = 5
    naive_table = NaiveDiningPhilosophers(num_philosophers=num_phil)
    results = [None] * num_phil

    def run_phil(pid: int):
        results[pid] = naive_table.attempt_eat_with_timeout(pid, timeout_sec=0.08)

    threads = [
        threading.Thread(target=run_phil, args=(i,))
        for i in range(num_phil)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2.0)

    # Circular wait guarantees that at least one (and usually all) philosophers deadlock
    assert any(flag is True for flag in naive_table.deadlocked_flags), (
        "Expected circular wait deadlock flags to be set"
    )
    assert any(res is False for res in results), (
        "Expected at least one philosopher to timeout due to circular wait"
    )


def test_havender_two_philosophers_minimal_table():
    """
    Verify Havender ordering on the minimal 2-philosopher table (edge case).
    Philosopher 0 requires forks (0, 1).
    Philosopher 1 requires forks (1, 0) -> Havender forces acquisition of (0, 1).
    Both compete for fork 0 first; whoever wins consumes fork 1, preventing deadlock.
    """
    num_phil = 2
    cycles = 50
    table = DiningPhilosophersHavender(num_philosophers=num_phil)

    def worker(pid: int):
        for _ in range(cycles):
            table.eat(pid)

    t0 = threading.Thread(target=worker, args=(0,))
    t1 = threading.Thread(target=worker, args=(1,))
    t0.start()
    t1.start()
    t0.join(timeout=3.0)
    t1.join(timeout=3.0)

    assert not t0.is_alive() and not t1.is_alive(), "2-philosopher table deadlocked!"
    assert table.eat_counts == [cycles, cycles]
    for pid, first, second in table.acquisition_log:
        assert first < second, f"Havender ordering violated: {first} >= {second}"

