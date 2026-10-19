#!/usr/bin/env python3
"""
Master Test Suite for COL1101 Quiz 2 Master Preparation
========================================================
Comprehensive automated validation covering:
- Tree height formalisms (h = number of levels) and CBT/ACBT node count bounds
- Binary min-heap array topology, leaf/internal bounds, and heap_down correctness
- Fast Build Heap invariant induction, well-founded termination, and AGP convergence
- k-th smallest element search space and depth rank inequalities
- Min-Max Heap duality rank intersection at index 1
- CPython closure mechanics (late-binding cell dereferencing vs eager default parameters)
- Concurrency race condition simulation, Lost Update verification, and Mutex fixes
- In-place HeapSort correctness
"""

import math
import itertools
import threading
import time
from functools import reduce
from typing import List, Tuple, Optional
import pytest


# ======================================================================
# 1. Tree Height Formalism & Node Count Bounds
# ======================================================================
def height_of_acbt(n: int) -> int:
    """In COL1101, height is the number of levels.
    For an empty tree: h = 0.
    For n >= 1: h = floor(log2(n)) + 1.
    """
    if n == 0:
        return 0
    return math.floor(math.log2(n)) + 1


def test_tree_height_formalism():
    assert height_of_acbt(0) == 0
    assert height_of_acbt(1) == 1  # Single node is level 1
    assert height_of_acbt(2) == 2
    assert height_of_acbt(3) == 2  # Complete 2-level tree (2^2 - 1 = 3)
    assert height_of_acbt(4) == 3
    assert height_of_acbt(7) == 3  # Complete 3-level tree (2^3 - 1 = 7)
    assert height_of_acbt(8) == 4
    assert height_of_acbt(15) == 4 # Complete 4-level tree (2^4 - 1 = 15)
    assert height_of_acbt(31) == 5

    # Test the ACBT node count theorem: 2^(h-1) <= n <= 2^h - 1
    for n in range(1, 1000):
        h = height_of_acbt(n)
        assert (1 << (h - 1)) <= n <= (1 << h) - 1


def test_leaf_and_internal_node_bounds():
    """In 0-indexed ACBT of size n:
    - Internal nodes: 0 to floor(n/2) - 1 (total floor(n/2) internal nodes)
    - Leaf nodes: floor(n/2) to n - 1 (total ceil(n/2) leaf nodes)
    - Last non-leaf node: floor(n/2) - 1
    """
    for n in range(1, 200):
        last_internal = (n // 2) - 1
        num_internal = n // 2
        first_leaf = n // 2
        num_leaves = n - num_internal

        assert num_internal + num_leaves == n
        if n == 1:
            assert last_internal == -1 # No internal nodes in 1-node tree
            assert first_leaf == 0
            assert num_leaves == 1
        else:
            # Check left child of last internal node is within bounds
            left_child = 2 * last_internal + 1
            assert 0 <= left_child < n
            # Check left child of first leaf is strictly out of bounds
            leaf_left_child = 2 * first_leaf + 1
            assert leaf_left_child >= n


# ======================================================================
# 2. Binary Heap Topology & Fast Build Heap Implementation
# ======================================================================
def is_min_heap(A: List[int]) -> Tuple[bool, Optional[str]]:
    n = len(A)
    for i in range(n):
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and A[i] > A[l]:
            return False, f"Violation: parent A[{i}]={A[i]} > left A[{l}]={A[l]}"
        if r < n and A[i] > A[r]:
            return False, f"Violation: parent A[{i}]={A[i]} > right A[{r}]={A[r]}"
    return True, None


def is_max_heap(A: List[int]) -> Tuple[bool, Optional[str]]:
    n = len(A)
    for i in range(n):
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and A[i] < A[l]:
            return False, f"Violation: parent A[{i}]={A[i]} < left A[{l}]={A[l]}"
        if r < n and A[i] < A[r]:
            return False, f"Violation: parent A[{i}]={A[i]} < right A[{r}]={A[r]}"
    return True, None


def heap_down(A: List[int], i: int, n: int):
    """0-indexed sift-down for min-heap."""
    while 2 * i + 1 < n:
        left = 2 * i + 1
        right = 2 * i + 2
        smallest = left
        if right < n and A[right] < A[left]:
            smallest = right
        if A[i] <= A[smallest]:
            break
        A[i], A[smallest] = A[smallest], A[i]
        i = smallest


def max_heap_down(A: List[int], i: int, n: int):
    """0-indexed sift-down for max-heap."""
    while 2 * i + 1 < n:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = left
        if right < n and A[right] > A[left]:
            largest = right
        if A[i] >= A[largest]:
            break
        A[i], A[largest] = A[largest], A[i]
        i = largest


def fast_build_min_heap(A: List[int]):
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        heap_down(A, i, n)


def fast_build_max_heap(A: List[int]):
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        max_heap_down(A, i, n)


def test_fast_build_heap_correctness():
    # Test random, sorted, reverse sorted, identical
    test_cases = [
        [40, 10, 20, 15, 12, 25, 30],
        [1, 2, 3, 4, 5, 6, 7],
        [7, 6, 5, 4, 3, 2, 1],
        [42],
        [5, 5, 5, 5, 5],
        [100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3]
    ]
    for orig in test_cases:
        arr = list(orig)
        fast_build_min_heap(arr)
        valid, msg = is_min_heap(arr)
        assert valid, f"Failed on {orig}: {msg}"

        arr_max = list(orig)
        fast_build_max_heap(arr_max)
        valid_max, msg_max = is_max_heap(arr_max)
        assert valid_max, f"Failed max heap on {orig}: {msg_max}"


def test_heapsort_in_place():
    """Verify in-place heapsort sorts array in ascending order."""
    def heapsort(A: List[int]):
        n = len(A)
        fast_build_max_heap(A)
        for i in range(n - 1, 0, -1):
            A[0], A[i] = A[i], A[0]
            max_heap_down(A, 0, i)

    test_arrays = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 4, 3, 2, 1],
        [1, 2, 3, 4, 5],
        [10],
        [9, 9, 9, 9],
        [15, 3, 2, 1, 9, 8, 7, 6, 12, 10, 14, 11, 4, 5, 13]
    ]
    for arr in test_arrays:
        expected = sorted(arr)
        heapsort(arr)
        assert arr == expected


# ======================================================================
# 3. Mathematical Rigor: Invariant Induction Strict Inequalities
# ======================================================================
def test_strict_inequalities_invariant():
    """Quiz 1 graders deduct marks if weak inequalities (2i+1 >= i) are written.
    We verify strictly that for all i >= 0:
      2i + 1 > i
      2i + 2 > i
    """
    for i in range(0, 1000):
        left_child = 2 * i + 1
        right_child = 2 * i + 2
        assert left_child > i, f"Violation for i={i}: 2i+1 <= i"
        assert right_child > i, f"Violation for i={i}: 2i+2 <= i"


# ======================================================================
# 4. Rank Bounds & Min-Max Heap Duality at Index 1
# ======================================================================
def test_kth_smallest_rank_bounds():
    """In a binary min-heap with distinct keys:
    A node at depth d has d ancestors strictly smaller than itself.
    Therefore, rank >= d + 1.
    For rank k, depth d <= k - 1.
    """
    # Verify depth and index range for 3rd smallest (rank 3)
    # d <= 2 -> depths 1 and 2 -> indices 1 to 6 (for n >= 7)
    # Let's generate all 7! = 5040 permutations of {1, 2, 3, 4, 5, 6, 7}
    # and find all valid min-heaps, checking where the 3rd smallest (value 3) can be!
    elements = [1, 2, 3, 4, 5, 6, 7]
    valid_3rd_smallest_indices = set()

    for perm in itertools.permutations(elements):
        arr = list(perm)
        valid, _ = is_min_heap(arr)
        if valid:
            idx_of_3 = arr.index(3)
            valid_3rd_smallest_indices.add(idx_of_3)

    # In a valid min-heap of size 7, value 3 must be at depth 1 or depth 2
    # Depth 0: index 0 (value must be 1)
    # Depth 1: indices 1, 2
    # Depth 2: indices 3, 4, 5, 6
    assert 0 not in valid_3rd_smallest_indices, "Value 3 cannot be at root!"
    assert valid_3rd_smallest_indices.issubset({1, 2, 3, 4, 5, 6})
    # Verify that value 3 can indeed appear at both depth 1 and depth 2
    assert len(valid_3rd_smallest_indices.intersection({1, 2})) > 0
    assert len(valid_3rd_smallest_indices.intersection({3, 4, 5, 6})) > 0


def test_min_max_heap_duality_intersection():
    """For unique set {1, 2, 3, 4, 5, 6, 7}:
    In min-heap H1:
      index 1 has 1 ancestor (0) -> H1[1] > H1[0] -> rank >= 2
      index 1 has 2 children (3, 4) -> H1[1] < H1[3], H1[4] -> rank <= 7 - 2 = 5
      Feasible values: {2, 3, 4, 5}
    In max-heap H2:
      index 1 has 1 ancestor (0) -> H2[1] < H2[0] -> rank <= 6
      index 1 has 2 children (3, 4) -> H2[1] > H2[3], H2[4] -> rank >= 3
      Feasible values: {3, 4, 5, 6}
    Intersection: {3, 4, 5}.
    """
    elements = [1, 2, 3, 4, 5, 6, 7]
    min_heap_idx1_vals = set()
    max_heap_idx1_vals = set()

    for perm in itertools.permutations(elements):
        arr = list(perm)
        if is_min_heap(arr)[0]:
            min_heap_idx1_vals.add(arr[1])
        if is_max_heap(arr)[0]:
            max_heap_idx1_vals.add(arr[1])

    assert min_heap_idx1_vals == {2, 3, 4, 5}
    assert max_heap_idx1_vals == {3, 4, 5, 6}
    intersection = min_heap_idx1_vals.intersection(max_heap_idx1_vals)
    assert intersection == {3, 4, 5}

    # Verify that roots and extremums cannot be shared across internal nodes
    # e.g., H1[0] == 1, but H2[2] has children (5, 6), so H2[2] >= 2 > 1
    for perm in itertools.permutations(elements):
        arr = list(perm)
        if is_max_heap(arr)[0]:
            assert arr[2] > 1, "In a size 7 max-heap, node 2 has children and cannot equal 1!"


# ======================================================================
# 5. AGP Summation Proof Verification
# ======================================================================
def test_agp_summation_limit():
    """Verify S = sum_{h=1}^infty (h / 2^h) == 2."""
    partial_sum = 0.0
    for h in range(1, 100):
        partial_sum += h / (2 ** h)
    assert math.isclose(partial_sum, 2.0, rel_tol=1e-15)


# ======================================================================
# 6. Python Closure Scoping & Bytecode Execution Mechanics
# ======================================================================
def test_closure_late_vs_eager_binding():
    steps = [1, 2, 3]

    # Eager binding via default parameters
    eager_ops = [lambda x, s=s: x + s * 2 for s in steps]
    # Late binding via shared closure cell
    late_ops = [lambda x: x + s * 2 for s in steps]

    # Reduce pipeline starting with x = 10
    res_eager = reduce(lambda acc, f: f(acc), eager_ops, 10)
    res_late = reduce(lambda acc, f: f(acc), late_ops, 10)

    # Eager: 10 + 2 -> 12 + 4 -> 16 + 6 = 22
    assert res_eager == 22

    # Late: loop finishes with s = 3. Each f adds 3*2 = 6. 10 + 6 + 6 + 6 = 28
    assert res_late == 28

    # Verify closure cell mechanism
    for f in late_ops:
        assert f.__closure__ is not None
        assert f.__closure__[0].cell_contents == 3

    for idx, f in enumerate(eager_ops):
        # Default argument is stored in __defaults__ tuple
        assert f.__defaults__ == (idx + 1,)


def test_nested_nonlocal_closure():
    def outer():
        x = 20
        def inner():
            nonlocal x
            x += 5
            return lambda y: x + y
        fn = inner()
        x += 10
        return fn

    closure_fn = outer()
    assert closure_fn(100) == 135


# ======================================================================
# 7. Slide-Grounded Concurrency & Race Simulation
# ======================================================================
def test_unsynchronized_race_lost_update():
    """Demonstrate that unsynchronized concurrent increments cause lost updates."""
    class Counter:
        def __init__(self):
            self.val = 0
        def add(self):
            # Preemption simulation: read, pause, write
            curr = self.val
            time.sleep(0.00005)
            self.val = curr + 1

    # Run multiple trials to ensure preemption occurs
    lost_update_detected = False
    for _ in range(5):
        c = Counter()
        t1 = threading.Thread(target=c.add)
        t2 = threading.Thread(target=c.add)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        if c.val == 1:
            lost_update_detected = True
            break
    assert lost_update_detected, "Context switch lost update occurred as predicted!"


def test_synchronized_mutex_correctness():
    """Demonstrate that threading.Lock() completely prevents race conditions."""
    class SafeCounter:
        def __init__(self):
            self.val = 0
            self.lock = threading.Lock()
        def add(self):
            with self.lock:
                curr = self.val
                time.sleep(0.00005)
                self.val = curr + 1

    for _ in range(5):
        c = SafeCounter()
        threads = [threading.Thread(target=c.add) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert c.val == 4, "Mutex successfully serialized all 4 increments!"


def test_havender_lock_ordering_deadlock_freedom():
    """Havender's principle prevents circular waiting by acquiring locks in global order."""
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    finished = []

    def safe_transfer(lA, lB, thread_id):
        # Enforce global acquisition ordering by memory address id(lock)
        first, second = (lA, lB) if id(lA) < id(lB) else (lB, lA)
        with first:
            time.sleep(0.0001)
            with second:
                finished.append(thread_id)

    t1 = threading.Thread(target=safe_transfer, args=(lock1, lock2, 1))
    t2 = threading.Thread(target=safe_transfer, args=(lock2, lock1, 2))
    t1.start()
    t2.start()
    t1.join(timeout=2.0)
    t2.join(timeout=2.0)

    assert len(finished) == 2, "Both threads finished successfully without deadlock!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
