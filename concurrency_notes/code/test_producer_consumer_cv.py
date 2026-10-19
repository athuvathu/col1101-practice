"""
Module: test_producer_consumer_cv.py
Formal Verification of Mesa Condition Variable Semantics in Bounded Buffers.

Demonstrates:
1. Mesa predicate re-evaluation requirement: Why `while (!predicate) wait()` is mandatory.
2. Failure mode of `if (!predicate) wait()` under injected spurious wakeups,
   causing invariant violations (buffer underflow/overflow).
3. Concurrent correctness: Multi-threaded producer-consumer with dual condition
   variables (`not_full`, `not_empty`) under heavy spurious wakeups.
"""

import threading
import time
import random
import pytest
from typing import List, Optional


# ============================================================================
# 1. Mesa Bounded Buffer with Correct `while` Loop
# ============================================================================
class MesaBoundedBuffer:
    """Bounded buffer correctly implementing Mesa condition variable wait loops."""

    def __init__(self, capacity: int, inject_spurious_wakeups: bool = True):
        self.capacity = capacity
        self.buffer: List[int] = []
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        self.inject_spurious = inject_spurious_wakeups
        self.max_observed_size = 0
        self.spurious_wakeup_count = 0

    def put(self, item: int):
        with self.lock:
            # Mesa mandate: re-check condition in a while loop
            while len(self.buffer) >= self.capacity:
                self.not_full.wait()

            self.buffer.append(item)
            if len(self.buffer) > self.max_observed_size:
                self.max_observed_size = len(self.buffer)

            # Signal consumer
            self.not_empty.notify()

    def get(self) -> int:
        with self.lock:
            # Mesa mandate: re-check condition in a while loop
            while len(self.buffer) == 0:
                self.not_empty.wait()

            item = self.buffer.pop(0)
            # Signal producer
            self.not_full.notify()
            return item

    def trigger_spurious_wakeup(self):
        """Simulates kernel/spurious signal waking waiting threads."""
        with self.lock:
            self.spurious_wakeup_count += 1
            self.not_empty.notify_all()
            self.not_full.notify_all()


# ============================================================================
# 2. Flawed Bounded Buffer with Buggy `if` Statement
# ============================================================================
class FlawedIfBoundedBuffer:
    """
    Bounded buffer using `if` instead of `while`.
    Vulnerable to spurious wakeups and interloper preemption.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer: List[int] = []
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def put(self, item: int):
        with self.lock:
            # BUG: using `if` instead of `while`
            if len(self.buffer) >= self.capacity:
                self.not_full.wait()

            # If woken spuriously while buffer is still full, this causes overflow!
            if len(self.buffer) >= self.capacity:
                raise OverflowError(
                    f"Buffer Overflow Invariant Violated! size={len(self.buffer) + 1} > capacity={self.capacity}"
                )
            self.buffer.append(item)
            self.not_empty.notify()

    def get(self) -> int:
        with self.lock:
            # BUG: using `if` instead of `while`
            if len(self.buffer) == 0:
                self.not_empty.wait()

            # If woken spuriously while buffer is still empty, this causes underflow!
            if len(self.buffer) == 0:
                raise IndexError(
                    "Buffer Underflow Invariant Violated! Attempted pop from empty buffer."
                )
            item = self.buffer.pop(0)
            self.not_full.notify()
            return item


# ============================================================================
# 3. Flawed Single Condition Variable Buffer (Vulnerable to Lost Wakeups)
# ============================================================================
class FlawedSingleCVBoundedBuffer:
    """
    Bounded buffer that mistakenly shares a single condition variable
    and uses notify() (waking only 1 thread) instead of separate condition variables.
    Causes lost wakeups when a producer wakes another producer instead of a consumer.
    """

    def __init__(self, capacity: int = 1):
        self.capacity = capacity
        self.buffer: List[int] = []
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)

    def put(self, item: int, timeout: float = 0.2) -> bool:
        with self.lock:
            start = time.time()
            while len(self.buffer) >= self.capacity:
                remaining = timeout - (time.time() - start)
                if remaining <= 0 or not self.cv.wait(timeout=remaining):
                    return False  # Timed out due to lost wakeup
            self.buffer.append(item)
            self.cv.notify()  # Bug: wakes only 1 thread, which might be another producer!
            return True

    def get(self, timeout: float = 0.2) -> Optional[int]:
        with self.lock:
            start = time.time()
            while len(self.buffer) == 0:
                remaining = timeout - (time.time() - start)
                if remaining <= 0 or not self.cv.wait(timeout=remaining):
                    return None  # Timed out due to lost wakeup
            item = self.buffer.pop(0)
            self.cv.notify()  # Bug: wakes only 1 thread, which might be another consumer!
            return item


# ============================================================================
# Pytest Test Cases
# ============================================================================
def test_mesa_cv_with_while_loop_handles_spurious_wakeups():
    """
    Verify that a Mesa bounded buffer using `while` loop maintains all safety
    invariants (0 <= size <= capacity) even under continuous injected spurious wakeups.
    """
    capacity = 5
    buffer = MesaBoundedBuffer(capacity=capacity, inject_spurious_wakeups=True)
    num_producers = 4
    num_consumers = 4
    items_per_thread = 75
    total_items = num_producers * items_per_thread

    consumed_items: List[int] = []
    consumed_lock = threading.Lock()
    stop_spurious_thread = threading.Event()

    def producer(pid: int):
        for i in range(items_per_thread):
            val = pid * 10000 + i
            buffer.put(val)

    def consumer():
        for _ in range(items_per_thread):
            val = buffer.get()
            with consumed_lock:
                consumed_items.append(val)

    def spurious_injector():
        while not stop_spurious_thread.is_set():
            time.sleep(0.0005)
            buffer.trigger_spurious_wakeup()

    # Start spurious wakeup generator
    injector = threading.Thread(target=spurious_injector)
    injector.daemon = True
    injector.start()

    # Start producers and consumers
    threads = []
    for pid in range(num_producers):
        t = threading.Thread(target=producer, args=(pid,))
        threads.append(t)
        t.start()

    for _ in range(num_consumers):
        t = threading.Thread(target=consumer)
        threads.append(t)
        t.start()

    # Join all threads
    for t in threads:
        t.join(timeout=5.0)
        assert not t.is_alive(), "Worker thread deadlocked during execution!"

    stop_spurious_thread.set()
    injector.join(timeout=0.2)

    # Invariant assertions:
    # 1. Total items consumed matches total produced
    assert len(consumed_items) == total_items, (
        f"Consumed count mismatch: {len(consumed_items)} vs {total_items}"
    )
    # 2. Buffer capacity invariant was never violated
    assert buffer.max_observed_size <= capacity, (
        f"Max buffer size {buffer.max_observed_size} exceeded capacity {capacity}"
    )
    assert len(buffer.buffer) == 0, "Buffer not drained"
    assert buffer.spurious_wakeup_count > 0, "Spurious wakeups were not generated"


def test_buggy_cv_with_if_statement_fails_on_spurious_wakeup():
    """
    Demonstrate that replacing `while` with `if` directly causes an invariant violation
    (IndexError / Buffer Underflow) when a spurious wakeup occurs.
    """
    buffer = FlawedIfBoundedBuffer(capacity=3)
    error_caught = []

    def consumer_thread():
        try:
            # Buffer is initially empty. Thread will execute `if len == 0: wait()`
            buffer.get()
        except (IndexError, OverflowError) as e:
            error_caught.append(e)

    t = threading.Thread(target=consumer_thread)
    t.start()

    # Give thread time to enter wait state
    time.sleep(0.02)

    # Inject spurious wakeup WITHOUT producing any item!
    with buffer.lock:
        buffer.not_empty.notify_all()

    t.join(timeout=1.0)

    # Verify that the flawed `if` design allowed consumer to pop from empty buffer
    assert len(error_caught) == 1, "Expected invariant violation was not triggered!"
    assert isinstance(error_caught[0], IndexError), (
        f"Expected IndexError from empty buffer pop, got {type(error_caught[0])}"
    )


def test_dual_condition_variable_liveness():
    """
    Verify that separating `not_full` and `not_empty` conditions avoids lost wakeups
    and ensures liveness under rapid alternating producer-consumer cycles.
    """
    buffer = MesaBoundedBuffer(capacity=1)
    results = []

    def producer():
        for i in range(50):
            buffer.put(i)

    def consumer():
        for _ in range(50):
            results.append(buffer.get())

    tp = threading.Thread(target=producer)
    tc = threading.Thread(target=consumer)

    tp.start()
    tc.start()
    tp.join(timeout=2.0)
    tc.join(timeout=2.0)

    assert not tp.is_alive(), "Producer deadlocked!"
    assert not tc.is_alive(), "Consumer deadlocked!"
    assert results == list(range(50)), "Items received out of FIFO order"


def test_single_cv_lost_wakeup_deadlock():
    """
    Demonstrate that sharing a single condition variable with notify() (notify_one)
    causes lost wakeups and thread timeouts under multi-producer multi-consumer workloads.
    """
    buffer = FlawedSingleCVBoundedBuffer(capacity=1)
    producer_timeouts = []
    consumer_timeouts = []

    def producer(pid: int):
        for i in range(25):
            if not buffer.put(pid * 100 + i, timeout=0.06):
                producer_timeouts.append(pid)
                break

    def consumer(cid: int):
        for _ in range(25):
            val = buffer.get(timeout=0.06)
            if val is None:
                consumer_timeouts.append(cid)
                break

    threads = [
        threading.Thread(target=producer, args=(0,)),
        threading.Thread(target=producer, args=(1,)),
        threading.Thread(target=consumer, args=(0,)),
        threading.Thread(target=consumer, args=(1,)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=3.0)

    # In single-CV design with notify(), lost wakeups guarantee that threads time out
    assert len(producer_timeouts) > 0 or len(consumer_timeouts) > 0, (
        "Expected lost wakeups in flawed single-CV buffer to cause thread timeouts"
    )

