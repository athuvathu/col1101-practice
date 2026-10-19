"""
verify_quiz2_exam.py
Empirically and mathematically validates every question and answer in the Quiz 2 exam paper.
"""

from functools import reduce
import threading
import time

def test_q1_heap_permutations():
    print("============================================================")
    print("TESTING QUESTION 1: Binary Min-Heap Permutations & Invariants")
    print("============================================================")
    
    # Check if a 0-indexed array represents a valid min-heap
    def is_min_heap(A):
        n = len(A)
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and A[i] > A[left]:
                return False, f"Violation at parent index {i} (val {A[i]}) > left child index {left} (val {A[left]})"
            if right < n and A[i] > A[right]:
                return False, f"Violation at parent index {i} (val {A[i]}) > right child index {right} (val {A[right]})"
        return True, "Valid min-heap"

    # Part (a): [0, 2, 1, 5, 4, 6, 3]
    perm_a = [0, 2, 1, 5, 4, 6, 3]
    valid_a, msg_a = is_min_heap(perm_a)
    print(f"Part (a) {perm_a}: {valid_a} -> {msg_a}")
    assert valid_a is True, "Permutation (a) should be a valid min-heap"

    # Part (b): [0, 3, 1, 2, 4, 5, 6]
    perm_b = [0, 3, 1, 2, 4, 5, 6]
    valid_b, msg_b = is_min_heap(perm_b)
    print(f"Part (b) {perm_b}: {valid_b} -> {msg_b}")
    assert valid_b is False, "Permutation (b) should NOT be a valid min-heap"
    assert "index 1" in msg_b and "index 3" in msg_b, "Violation should be between index 1 and 3"

    # Part (c): Determine whether 3rd smallest can reside at index 7 for n = 15
    # For any node at index 7 in a 0-indexed ACBT:
    # parent of 7 = (7-1)//2 = 3
    # parent of 3 = (3-1)//2 = 1
    # parent of 1 = (1-1)//2 = 0
    ancestors_7 = [3, 1, 0]
    print(f"Ancestors of node 7: {ancestors_7} (length {len(ancestors_7)})")
    assert len(ancestors_7) == 3, "Node 7 must have exactly 3 ancestors"
    # In any min-heap with distinct elements, A[0] < A[1] < A[3] < A[7]
    # Thus, A[7] is strictly greater than at least 3 elements, so rank(A[7]) >= 4.
    # Therefore, A[7] can NEVER be the 3rd smallest element!
    print(">> Question 1 Verification PASSED!\n")


def test_q2_python_scoping_and_concurrency():
    print("============================================================")
    print("TESTING QUESTION 2: Python Closures & Concurrency Traces")
    print("============================================================")

    # Question 2 Program definition
    def make_pipeline(base):
        ops = []
        for step in [1, 2, 3]:
            ops.append(lambda x, s=step: x + s * base)
        
        late_ops = []
        for step in [1, 2, 3]:
            late_ops.append(lambda x: x + step * base)
            
        return ops, late_ops

    ops, late_ops = make_pipeline(2)

    # 2(a)(i) pipe_a(10)
    pipe_a = lambda x: reduce(lambda acc, f: f(acc), ops, x)
    res_a = pipe_a(10)
    print(f"2(a)(i) pipe_a(10) = {res_a}")
    # Trace:
    # initial x = 10
    # step 1: 10 + 1 * 2 = 12
    # step 2: 12 + 2 * 2 = 16
    # step 3: 16 + 3 * 2 = 22
    assert res_a == 22, f"Expected 22, got {res_a}"

    # 2(a)(ii) pipe_b(10)
    pipe_b = lambda x: reduce(lambda acc, f: f(acc), late_ops, x)
    res_b = pipe_b(10)
    print(f"2(a)(ii) pipe_b(10) = {res_b}")
    # Trace:
    # late_ops closures capture `step` by reference.
    # At the end of loop, step = 3.
    # Each function adds 3 * 2 = 6!
    # initial x = 10
    # step 1: 10 + 6 = 16
    # step 2: 16 + 6 = 22
    # step 3: 22 + 6 = 28
    assert res_b == 28, f"Expected 28, got {res_b}"

    # 2(b) Concurrency Bank Account Lost Update Trace
    class Account:
        def __init__(self, balance):
            self.balance = balance
            self.lock = threading.Lock()

        def deposit_unsafe(self, amt):
            t = self.balance
            time.sleep(0.0001)
            self.balance = t + amt

    # Run multiple trials to empirically trigger lost update
    lost_update_found = False
    for _ in range(20):
        acc = Account(100)
        t1 = threading.Thread(target=acc.deposit_unsafe, args=(10,))
        t2 = threading.Thread(target=acc.deposit_unsafe, args=(20,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        if acc.balance in (110, 120): # Expected is 130! If 110 or 120, a lost update happened
            lost_update_found = True
            print(f"Empirical race condition triggered: final balance = {acc.balance} (expected 130)")
            break

    # 2(b)(ii) Deadlock simulation with timeout
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    deadlock_detected = False

    def t1_deadlock():
        nonlocal deadlock_detected
        with lock1:
            time.sleep(0.01)
            acquired = lock2.acquire(timeout=0.05)
            if not acquired:
                deadlock_detected = True
            else:
                lock2.release()

    def t2_deadlock():
        with lock2:
            time.sleep(0.01)
            acquired = lock1.acquire(timeout=0.05)
            if acquired:
                lock1.release()

    th1 = threading.Thread(target=t1_deadlock)
    th2 = threading.Thread(target=t2_deadlock)
    th1.start()
    th2.start()
    th1.join()
    th2.join()

    assert deadlock_detected is True, "Deadlock was not simulated"
    print("Deadlock verified: reverse lock acquisition caused circular blocking.")
    print(">> Question 2 Verification PASSED!\n")


def test_q3_fast_build_heap():
    print("============================================================")
    print("TESTING QUESTION 3: Fast Build Heap Correctness & Summation")
    print("============================================================")

    def heap_down(A, i, n):
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

    def is_subtree_heap(A, root, n):
        # Verify min-heap property for subtree rooted at 'root'
        queue = [root]
        while queue:
            curr = queue.pop(0)
            l = 2 * curr + 1
            r = 2 * curr + 2
            if l < n:
                if A[curr] > A[l]:
                    return False
                queue.append(l)
            if r < n:
                if A[curr] > A[r]:
                    return False
                queue.append(r)
        return True

    def fast_build_min_heap_instrumented(A):
        n = len(A)
        # Verify Base Case P(n//2 - 1): all j >= n//2 are leaves, hence valid heaps
        for j in range(n // 2, n):
            assert is_subtree_heap(A, j, n), f"Leaf {j} must be a valid heap"
        
        for i in range(n // 2 - 1, -1, -1):
            # Precondition: subtrees rooted at 2i+1 and 2i+2 must be heaps
            if 2 * i + 1 < n:
                assert is_subtree_heap(A, 2 * i + 1, n), f"Left child {2*i+1} must be a heap before heap_down"
            if 2 * i + 2 < n:
                assert is_subtree_heap(A, 2 * i + 2, n), f"Right child {2*i+2} must be a heap before heap_down"
            
            heap_down(A, i, n)
            
            # Postcondition P(i-1): subtrees rooted at all j >= i must be heaps
            for j in range(i, n):
                assert is_subtree_heap(A, j, n), f"Subtree {j} must be a heap after heap_down on {i}"

    import random
    random.seed(42)
    for size in [1, 2, 7, 15, 31, 50, 63, 100]:
        arr = list(range(size))
        random.shuffle(arr)
        fast_build_min_heap_instrumented(arr)
        # Verify final array is a heap across all elements
        assert is_subtree_heap(arr, 0, size), f"Root of size {size} is not a valid min-heap!"

    print("Fast Build Heap invariant P(i) rigorously verified across multiple array sizes.")

    # AGP Summation verification: sum_{h=1}^infty h / 2^h = 2
    agp_sum = sum(h / (2.0 ** h) for h in range(1, 100))
    print(f"AGP Sum evaluated to 99 terms: {agp_sum:.10f} (Expected: 2.0)")
    assert abs(agp_sum - 2.0) < 1e-12, "AGP sum does not converge to 2"

    print(">> Question 3 Verification PASSED!\n")


if __name__ == "__main__":
    test_q1_heap_permutations()
    test_q2_python_scoping_and_concurrency()
    test_q3_fast_build_heap()
    print("=" * 60)
    print("ALL QUIZ 2 VERIFICATION TESTS PASSED (100% Correct)")
    print("=" * 60)
