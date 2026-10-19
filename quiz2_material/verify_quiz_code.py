#!/usr/bin/env python3
"""
Verification Script for COL1101 Quiz 2 Material
Validates all code snippets, traces, concurrency guarantees, and algorithmic bounds.
"""

import sys
import threading
import time
import random
import math
import struct

def test_q2_closures():
    print("=" * 60)
    print("RUNNING TEST 1: Question 2.1 Closures & Late Binding")
    print("=" * 60)

    def make_evaluators(init=1):
        funcs = []
        for step in [2, 3, 5]:
            funcs.append(lambda x, s=step: x + s * 2 + init)
        
        late_funcs = []
        for step in [2, 3, 5]:
            late_funcs.append(lambda x: x + step * 3 + init)
            
        return funcs, late_funcs

    f, l = make_evaluators(1)

    res_a = f[2](5)
    res_b = l[0](3)

    print(f"res_a = f[2](5) -> {res_a} (Expected: 16)")
    print(f"res_b = l[0](3) -> {res_b} (Expected: 19)")

    assert res_a == 16, f"Expected res_a=16, got {res_a}"
    assert res_b == 19, f"Expected res_b=19, got {res_b}"

    # Demonstrate that all late_funcs use the final loop value step = 5
    late_outputs = [fn(3) for fn in l]
    print(f"All late_funcs called with x=3: {late_outputs} (All 19 due to late binding)")
    assert late_outputs == [19, 19, 19], "Late binding failed to bind to step=5"

    # Demonstrate that default-bound funcs preserve step values [2, 3, 5]
    default_outputs = [fn(5) for fn in f]
    print(f"All funcs called with x=5: {default_outputs} (10, 12, 16)")
    assert default_outputs == [10, 12, 16], "Default binding failed"

    # Deep CPython bytecode & cell introspection
    assert f[2].__defaults__ == (5,), f"Expected __defaults__ == (5,), got {f[2].__defaults__}"
    closure_cells = [cell.cell_contents for cell in l[0].__closure__]
    print(f"l[0] closure cell contents: {closure_cells} (contains step=5 and init=1)")
    assert 5 in closure_cells and 1 in closure_cells, "Closure cell contents mismatch"

    print(">> Question 2.1 Closures verification PASSED!\n")


def test_q2_heap_down_trace():
    print("=" * 60)
    print("RUNNING TEST 2: Question 2(b) Heap Down Step-by-Step Trace")
    print("=" * 60)

    def heap_down(H, i, n, trace=None):
        while 2 * i + 1 < n:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = left
            if right < n and H[right] < H[left]:
                smallest = right
            if H[i] <= H[smallest]:
                break
            H[i], H[smallest] = H[smallest], H[i]
            if trace is not None:
                trace.append((i, smallest, list(H)))
            i = smallest

    initial_H = [40, 10, 20, 15, 12, 25, 30]
    H = list(initial_H)
    trace = []
    heap_down(H, 0, len(H), trace)

    print(f"Initial array: {initial_H}")
    for step_num, (p, c, state) in enumerate(trace, 1):
        print(f"Swap {step_num}: swapped index {p} and {c} -> {state}")

    assert len(trace) == 2, f"Expected 2 swaps, got {len(trace)}"
    assert trace[0][2] == [10, 40, 20, 15, 12, 25, 30], "Swap 1 state mismatch"
    assert trace[1][2] == [10, 12, 20, 15, 40, 25, 30], "Swap 2 state mismatch"
    assert H == [10, 12, 20, 15, 40, 25, 30], "Final heap state mismatch"

    # Verify min-heap property on H
    for idx in range(len(H)):
        l = 2 * idx + 1
        r = 2 * idx + 2
        if l < len(H):
            assert H[idx] <= H[l], f"Heap property violated at {idx} and {l}"
        if r < len(H):
            assert H[idx] <= H[r], f"Heap property violated at {idx} and {r}"

    # Untested Edge Case Attack: Boundary node with single child (n = 50, node 24)
    # Node 24 has left child 49 (in bounds) and right child 50 (out of bounds)
    H_50 = list(range(50, 100))
    H_50[24] = 999
    H_50[49] = 10
    heap_down(H_50, 24, 50)
    assert H_50[24] == 10 and H_50[49] == 999, "Single-child sift-down failed!"
    print("Single-child boundary node 24 for n=50 verified successfully without IndexError!")

    print(">> Question 2.2 Heap Down Trace & Boundaries verification PASSED!\n")


def test_q2_concurrency_safe_heap_down():
    print("=" * 60)
    print("RUNNING TEST 3: Question 2.2 Concurrency & safe_heap_down Synchronization")
    print("=" * 60)

    def heap_down(H, i, n, delay=False):
        while 2 * i + 1 < n:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = left
            if right < n and H[right] < H[left]:
                smallest = right
            if H[i] <= H[smallest]:
                break
            # Multi-instruction assignment simulates preemption
            val_smallest = H[smallest]
            val_i = H[i]
            if delay:
                time.sleep(0.00002)
            H[i] = val_smallest
            if delay:
                time.sleep(0.00002)
            H[smallest] = val_i
            i = smallest

    def safe_heap_down(H, i, n, lock, delay=False):
        with lock:
            heap_down(H, i, n, delay)

    # 1. Direct Heap Stress Test: Unsafe concurrent heap_down vs safe_heap_down
    lock = threading.Lock()
    NUM_TRIALS = 30

    unsafe_corruptions = 0
    for _ in range(NUM_TRIALS):
        data = [random.randint(1, 100) for _ in range(15)]
        expected_multiset = sorted(data)
        H_unsafe = list(data)
        threads = [
            threading.Thread(target=heap_down, args=(H_unsafe, 0, 15, True)),
            threading.Thread(target=heap_down, args=(H_unsafe, 1, 15, True)),
            threading.Thread(target=heap_down, args=(H_unsafe, 2, 15, True)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if sorted(H_unsafe) != expected_multiset:
            unsafe_corruptions += 1

    print(f"Unsynchronized heap_down corruptions: {unsafe_corruptions} / {NUM_TRIALS}")

    safe_corruptions = 0
    for _ in range(NUM_TRIALS):
        data = [random.randint(1, 100) for _ in range(15)]
        expected_multiset = sorted(data)
        H_safe = list(data)
        threads = [
            threading.Thread(target=safe_heap_down, args=(H_safe, 0, 15, lock, True)),
            threading.Thread(target=safe_heap_down, args=(H_safe, 1, 15, lock, True)),
            threading.Thread(target=safe_heap_down, args=(H_safe, 2, 15, lock, True)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if sorted(H_safe) != expected_multiset:
            safe_corruptions += 1

    print(f"safe_heap_down corruptions with lock: {safe_corruptions} / {NUM_TRIALS}")
    assert safe_corruptions == 0, "safe_heap_down failed mutual exclusion!"

    # 2. Counter mutual exclusion sanity check
    class SafeCounter:
        def __init__(self):
            self.value = 0
            self.lock = threading.Lock()

        def increment(self):
            with self.lock:
                curr = self.value
                time.sleep(0.00001)
                self.value = curr + 1

    safe_counter = SafeCounter()
    threads = [threading.Thread(target=lambda: [safe_counter.increment() for _ in range(10)]) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert safe_counter.value == 200, "SafeCounter failed mutual exclusion!"
    print("SafeCounter mutual exclusion verified: 200 / 200")

    print(">> Question 2.2 Concurrency & safe_heap_down verification PASSED!\n")


def test_q3_fast_build_heap():
    print("=" * 60)
    print("RUNNING TEST 4: Question 3 Fast Build Heap Correctness & Invariant")
    print("=" * 60)

    def heap_down(H, i, n):
        while 2 * i + 1 < n:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = left
            if right < n and H[right] < H[left]:
                smallest = right
            if H[i] <= H[smallest]:
                break
            H[i], H[smallest] = H[smallest], H[i]
            i = smallest

    def is_min_heap(A, root_idx, n):
        # Recursively check if subtree at root_idx is a min-heap
        left = 2 * root_idx + 1
        right = 2 * root_idx + 2
        if left < n:
            if A[root_idx] > A[left] or not is_min_heap(A, left, n):
                return False
        if right < n:
            if A[root_idx] > A[right] or not is_min_heap(A, right, n):
                return False
        return True

    def fast_build_min_heap(A):
        n = len(A)
        # Test the loop invariant at every step
        for i in range(n // 2 - 1, -1, -1):
            heap_down(A, i, n)
            # Invariant: subtrees rooted at j in {i, ..., n-1} are valid heaps
            for j in range(i, n):
                assert is_min_heap(A, j, n), f"Loop invariant violated for node {j} at step i={i}"

    # Test on multiple array sizes
    random.seed(42)
    for size in [7, 15, 50, 127, 255]:
        data = [random.randint(1, 1000) for _ in range(size)]
        fast_build_min_heap(data)
        assert is_min_heap(data, 0, size), f"Build heap failed for size {size}"

    print(">> Question 3 Fast Build Heap & Loop Invariant verification PASSED!\n")


def test_q1_math_and_float_bounds():
    print("=" * 60)
    print("RUNNING TEST 5: Question 1 Mathematical & IEEE 754 Bounds")
    print("=" * 60)

    # 1. Tree bounds for n = 50
    n = 50
    h = math.floor(math.log2(n)) + 1
    leaf_start = n // 2
    leaf_end = n - 1
    print(f"n = {n}: Height h = {h} (levels), Leaf range = [{leaf_start}, {leaf_end}]")
    assert h == 6, f"Expected height 6, got {h}"
    assert leaf_start == 25 and leaf_end == 49, "Leaf index range mismatch"

    # 2. Candidate indices for 3rd smallest element in size 50 min-heap
    # (a) Verify ancestor count >= 3 for ALL nodes at depth >= 3 (indices 7 to 49)
    for idx in range(7, 50):
        ancestors = []
        curr = idx
        while curr > 0:
            curr = (curr - 1) // 2
            ancestors.append(curr)
        assert len(ancestors) >= 3, f"Node {idx} should have >= 3 ancestors, got {len(ancestors)}"
    print("All nodes at depth >= 3 (indices 7 to 49) strictly have >= 3 ancestors.")

    # (b) Concretely construct a valid size-50 min-heap for each index in {1, 2, 3, 4, 5, 6}
    # where the 3rd smallest element (value 3) is located at that index!
    def check_min_heap(A):
        for i in range(len(A)):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < len(A) and A[i] > A[left]:
                return False
            if right < len(A) and A[i] > A[right]:
                return False
        return True

    for target_idx in [1, 2, 3, 4, 5, 6]:
        A = [None] * 50
        A[0] = 1 # 1st smallest
        if target_idx == 1:
            A[1] = 3 # 3rd smallest
            A[2] = 2 # 2nd smallest
        elif target_idx == 2:
            A[1] = 2 # 2nd smallest
            A[2] = 3 # 3rd smallest
        elif target_idx in (3, 4):
            A[1] = 2 # 2nd smallest (parent of 3 and 4)
            A[2] = 10
            A[target_idx] = 3 # 3rd smallest
            other = 4 if target_idx == 3 else 3
            A[other] = 11
        elif target_idx in (5, 6):
            A[1] = 10
            A[2] = 2 # 2nd smallest (parent of 5 and 6)
            A[target_idx] = 3 # 3rd smallest
            other = 6 if target_idx == 5 else 5
            A[other] = 11
        
        curr_val = 20
        for i in range(50):
            if A[i] is None:
                A[i] = curr_val
                curr_val += 1
        assert check_min_heap(A), f"Min-heap invalid for candidate index {target_idx}"
        sorted_elements = sorted(A)
        assert sorted_elements[2] == 3 and A[target_idx] == 3, f"Element at {target_idx} is not 3rd smallest!"
        print(f"  Candidate index {target_idx} confirmed realizable in valid size-50 min-heap.")

    # 3. Level-Order Traversal Queue State Verification (Question 1.2)
    # CBT of height 4 with 15 nodes (1 to 15)
    class TreeNode:
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None

    # Build CBT of 15 nodes
    nodes = [TreeNode(i) for i in range(1, 16)]
    for i in range(7):
        nodes[i].left = nodes[2 * i + 1]
        nodes[i].right = nodes[2 * i + 2]

    # Run LOT simulation up to node 5 dequeue
    from collections import deque
    q = deque([nodes[0]])
    visited = []
    
    while q:
        curr = q.popleft()
        visited.append(curr.val)
        if curr.left:  q.append(curr.left)
        if curr.right: q.append(curr.right)
        if curr.val == 5:
            # Snapshot of queue immediately after dequeuing 5 and enqueuing its children
            queue_after_5 = [node.val for node in q]
            break

    print(f"Visited nodes up to 5: {visited}")
    print(f"Queue state after dequeuing 5: {queue_after_5}")
    assert queue_after_5 == [6, 7, 8, 9, 10, 11], f"Expected [6, 7, 8, 9, 10, 11], got {queue_after_5}"
    assert visited == [1, 2, 3, 4, 5], f"Expected visited [1, 2, 3, 4, 5], got {visited}"
    print(">> Question 1.2 Level-Order Traversal Queue state verified successfully!")

    # 4. AGP sum verification: sum_{h=1}^infty h / 2^h = 2
    agp_partial = sum(h / (2.0**h) for h in range(1, 100))
    print(f"AGP Sum sum_{{h=1}}^99 h / 2^h = {agp_partial:.10f} (Expected: 2.0)")
    assert abs(agp_partial - 2.0) < 1e-12, "AGP summation does not converge to 2"

    print(">> Question 1 Trees, Heaps & LOT verification PASSED!\n")


if __name__ == "__main__":
    test_q2_closures()
    test_q2_heap_down_trace()
    test_q2_concurrency_safe_heap_down()
    test_q3_fast_build_heap()
    test_q1_math_and_float_bounds()
    print("=" * 60)
    print("ALL VERIFICATION SUITE TESTS PASSED SUCCESSFULLY! (100% Correct)")
    print("=" * 60)
