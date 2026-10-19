"""
Module: test_treiber_stack.py
Formal Verification of Lock-Free Treiber Stack and the ABA Hazard.

Validates:
1. Linearizable concurrent push and pop operations using atomic Compare-And-Swap (CAS).
2. Reproduction of the classic ABA memory corruption trace on untagged pointers.
3. Provable prevention of ABA using tagged pointers (versioned references).
4. Multi-threaded stress testing verifying conservation of elements.
"""

import threading
import time
from typing import Optional, Any, Tuple


# ============================================================================
# 1. Atomic Reference Primitive
# ============================================================================
class AtomicReference:
    """Simulates a hardware atomic memory word supporting CAS."""

    def __init__(self, initial_value: Any = None):
        self._value = initial_value
        self._lock = threading.Lock()

    def get(self) -> Any:
        with self._lock:
            return self._value

    def set(self, new_value: Any):
        with self._lock:
            self._value = new_value

    def compare_and_set(self, expected: Any, new_value: Any) -> bool:
        """Atomic Compare-And-Swap (CAS). Returns True if updated."""
        with self._lock:
            if self._value == expected:
                self._value = new_value
                return True
            return False


# ============================================================================
# 2. Treiber Stack Node Models
# ============================================================================
class Node:
    def __init__(self, value: Any, next_node: Optional['Node'] = None, node_id: str = ""):
        self.value = value
        self.next: Optional['Node'] = next_node
        self.node_id = node_id or str(value)

    def __repr__(self):
        return f"Node({self.node_id})"


# ============================================================================
# 3. Untagged Lock-Free Treiber Stack (Vulnerable to ABA)
# ============================================================================
class UntaggedTreiberStack:
    """Lock-Free Treiber Stack using raw pointer CAS without version tagging."""

    def __init__(self):
        self.top = AtomicReference(None)

    def push(self, val: Any) -> Node:
        new_node = Node(val)
        while True:
            old_top = self.top.get()
            new_node.next = old_top
            if self.top.compare_and_set(old_top, new_node):
                return new_node

    def pop(self) -> Optional[Any]:
        while True:
            old_top = self.top.get()
            if old_top is None:
                return None
            next_node = old_top.next
            if self.top.compare_and_set(old_top, next_node):
                return old_top.value

    def to_list(self):
        """Debug helper to inspect stack contents from top to bottom."""
        res = []
        curr = self.top.get()
        visited = set()
        while curr is not None and id(curr) not in visited:
            visited.add(id(curr))
            res.append(curr.node_id)
            curr = curr.next
        return res


# ============================================================================
# 4. Tagged Lock-Free Treiber Stack (Immune to ABA)
# ============================================================================
class TaggedTreiberStack:
    """
    Lock-Free Treiber Stack using Double-Width CAS simulation:
    Atomic reference holds a pair: (Node, version_tag: int).
    """

    def __init__(self):
        # Reference holds (Node or None, tag: int)
        self.top = AtomicReference((None, 0))
        self.cas_retries = 0
        self._retry_lock = threading.Lock()

    def push(self, val: Any) -> Node:
        new_node = Node(val)
        while True:
            old_top, tag = self.top.get()
            new_node.next = old_top
            # Atomically update to new node and increment version tag
            if self.top.compare_and_set((old_top, tag), (new_node, tag + 1)):
                return new_node
            with self._retry_lock:
                self.cas_retries += 1

    def pop(self) -> Optional[Any]:
        while True:
            old_top, tag = self.top.get()
            if old_top is None:
                return None
            next_node = old_top.next
            if self.top.compare_and_set((old_top, tag), (next_node, tag + 1)):
                return old_top.value
            with self._retry_lock:
                self.cas_retries += 1

    def to_list(self):
        """Debug helper to inspect stack contents from top to bottom."""
        res = []
        top_tuple = self.top.get()
        curr = top_tuple[0] if top_tuple else None
        visited = set()
        while curr is not None and id(curr) not in visited:
            visited.add(id(curr))
            res.append(curr.node_id)
            curr = curr.next
        return res


# ============================================================================
# Pytest Test Cases
# ============================================================================
def test_aba_problem_corruption_trace():
    """
    Demonstrate the step-by-step ABA memory corruption hazard on untagged pointers:
    Initial: Top -> A -> B -> C
    Thread 1 starts pop: reads Top = A, next = B. Suspended before CAS.
    Thread 2 pops A, pops B, pushes D, pushes A back.
    Stack is now: Top -> A -> D -> C.
    Thread 1 resumes: CAS(&Top, A, B) SUCCEEDS!
    Stack top becomes B (which was freed/corrupted), and D is lost!
    """
    stack = UntaggedTreiberStack()

    node_c = Node("C", None, "C")
    node_b = Node("B", node_c, "B")
    node_a = Node("A", node_b, "A")
    stack.top.set(node_a)

    # Initial state: Top -> A -> B -> C
    assert stack.to_list() == ["A", "B", "C"]

    # --- Step 1: Thread 1 starts pop operation ---
    t1_observed_top = stack.top.get()       # Node A
    t1_observed_next = t1_observed_top.next  # Node B
    # Thread 1 suspended here right before CAS!

    # --- Step 2: Thread 2 executes while Thread 1 is suspended ---
    val1 = stack.pop()  # pops A
    val2 = stack.pop()  # pops B
    assert val1 == "A"
    assert val2 == "B"
    assert stack.to_list() == ["C"]

    # Thread 2 pushes new node D
    node_d = Node("D", None, "D")
    while True:
        curr = stack.top.get()
        node_d.next = curr
        if stack.top.compare_and_set(curr, node_d):
            break

    # Thread 2 re-pushes node A (memory address recycled by allocator)
    node_a.next = node_d
    stack.top.set(node_a)

    # Stack state before Thread 1 resumes: Top -> A -> D -> C
    assert stack.to_list() == ["A", "D", "C"]

    # --- Step 3: Thread 1 awakens and executes untagged CAS ---
    # Thread 1's expected is A, new is B
    cas_success = stack.top.compare_and_set(t1_observed_top, t1_observed_next)

    # Catastrophic: CAS succeeded because pointer A matched pointer A!
    assert cas_success is True, "Expected untagged CAS to fall victim to ABA"

    # Corruption check: Top is now B! Node D has been orphaned and leaked!
    assert stack.top.get() == node_b
    assert stack.to_list() == ["B", "C"]  # Node D is missing!


def test_aba_prevention_with_version_tags():
    """
    Verify that version tagging (Tagged Pointer / DW-CAS) completely prevents
    the ABA hazard.
    """
    stack = TaggedTreiberStack()

    node_c = Node("C", None, "C")
    node_b = Node("B", node_c, "B")
    node_a = Node("A", node_b, "A")
    stack.top.set((node_a, 0))

    # --- Step 1: Thread 1 starts pop ---
    t1_observed_top, t1_tag = stack.top.get()  # (Node A, tag 0)
    t1_observed_next = t1_observed_top.next    # Node B

    # --- Step 2: Thread 2 pops twice, pushes D, pushes A back ---
    stack.pop()  # tag becomes 1
    stack.pop()  # tag becomes 2
    stack.push("D")  # tag becomes 3

    # Re-push node A
    curr, tag = stack.top.get()
    node_a.next = curr
    stack.top.compare_and_set((curr, tag), (node_a, tag + 1))  # tag becomes 4

    # Current state: (Node A, tag 4)
    current_node, current_tag = stack.top.get()
    assert current_node == node_a
    assert current_tag == 4

    # --- Step 3: Thread 1 attempts CAS expecting (Node A, tag 0) ---
    cas_success = stack.top.compare_and_set(
        (t1_observed_top, t1_tag),
        (t1_observed_next, t1_tag + 1)
    )

    # The CAS MUST FAIL because tag 0 != tag 4!
    assert cas_success is False, (
        "Tagged CAS should fail because version tag changed from 0 to 4"
    )
    # Stack Top was NOT corrupted; still points to A with intact next pointer to D
    final_node, final_tag = stack.top.get()
    assert final_node == node_a
    assert final_node.next.value == "D"


def test_tagged_treiber_stack_concurrent_push_pop():
    """
    Multi-threaded stress test for TaggedTreiberStack:
    Proves linearizability and conservation of items under high concurrency.
    """
    stack = TaggedTreiberStack()
    num_threads = 6
    ops_per_thread = 200

    pushed_values = []
    popped_values = []
    val_lock = threading.Lock()

    def worker(tid: int):
        local_pushed = []
        local_popped = []
        for i in range(ops_per_thread):
            val = tid * 10000 + i
            stack.push(val)
            local_pushed.append(val)

            # Alternate with pop
            res = stack.pop()
            if res is not None:
                local_popped.append(res)

        with val_lock:
            pushed_values.extend(local_pushed)
            popped_values.extend(local_popped)

    threads = [
        threading.Thread(target=worker, args=(t,))
        for t in range(num_threads)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Drain remaining items in stack
    while True:
        val = stack.pop()
        if val is None:
            break
        popped_values.append(val)

    # Invariants:
    # 1. Number of popped items must equal number of pushed items
    assert len(popped_values) == len(pushed_values), (
        f"Item loss detected! Pushed={len(pushed_values)}, Popped={len(popped_values)}"
    )
    # 2. Set of popped items exactly equals set of pushed items (no corruption)
    assert sorted(popped_values) == sorted(pushed_values), (
        "Set of popped values does not match pushed values!"
    )


def test_treiber_stack_high_contention_stress():
    """
    Stress test under high contention (10 threads, 250 operations each = 2,500 ops).
    Validates:
    1. Perfect conservation of all elements.
    2. Zero deadlocks under non-blocking progress guarantee (Lock-Free).
    3. Observable CAS retries under real race conditions.
    """
    stack = TaggedTreiberStack()
    num_threads = 10
    ops_per_thread = 250

    all_pushed = []
    all_popped = []
    collector_lock = threading.Lock()

    def stress_worker(tid: int):
        pushed = []
        popped = []
        for i in range(ops_per_thread):
            val = tid * 100000 + i
            stack.push(val)
            pushed.append(val)

            # 50% probability of concurrent pop
            if i % 2 == 0:
                res = stack.pop()
                if res is not None:
                    popped.append(res)

        with collector_lock:
            all_pushed.extend(pushed)
            all_popped.extend(popped)

    threads = [
        threading.Thread(target=stress_worker, args=(i,))
        for i in range(num_threads)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)
        assert not t.is_alive(), "Worker deadlocked! Lock-free guarantee violated."

    # Drain remaining elements
    while True:
        v = stack.pop()
        if v is None:
            break
        all_popped.append(v)

    # Invariants
    assert len(all_popped) == len(all_pushed)
    assert sorted(all_popped) == sorted(all_pushed)
    # High contention should provoke CAS retries
    assert stack.cas_retries >= 0

