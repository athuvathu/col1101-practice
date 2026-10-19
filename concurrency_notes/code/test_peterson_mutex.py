"""
Module: test_peterson_mutex.py
Formal Verification of Peterson's Mutual Exclusion Algorithm.

Validates:
1. Safety invariant under Sequential Consistency (SC): At most one thread in Critical Section.
2. Failure under Total Store Order (TSO): Demonstrates how Store-Load (W -> R) reordering
   violates mutual exclusion when store buffers delay visibility.
3. Restoration under TSO with Memory Fence (MFENCE): Flushing the store buffer before reading
   re-establishes the strict mutual exclusion invariant.
"""

import threading
import time
from collections import deque
from typing import Dict, Any


# ============================================================================
# 1. Sequentially Consistent Peterson's Mutex
# ============================================================================
class PetersonMutexSC:
    """Peterson's 2-thread mutual exclusion algorithm under Sequential Consistency."""

    def __init__(self):
        self.flag = [False, False]
        self.turn = 0
        self.in_cs = [0, 0]
        self.max_concurrent_in_cs = 0
        self._monitor_lock = threading.Lock()

    def lock(self, thread_id: int):
        other = 1 - thread_id
        self.flag[thread_id] = True
        self.turn = other
        # Under SC, stores are immediately visible in program order.
        # time.sleep(0) yields the GIL, acting like a pause/yield in user-space spinlock.
        while self.flag[other] and self.turn == other:
            time.sleep(0)

        # Invariant check instrumentation
        with self._monitor_lock:
            self.in_cs[thread_id] = 1
            concurrent = sum(self.in_cs)
            if concurrent > self.max_concurrent_in_cs:
                self.max_concurrent_in_cs = concurrent

    def unlock(self, thread_id: int):
        with self._monitor_lock:
            self.in_cs[thread_id] = 0
        self.flag[thread_id] = False


# ============================================================================
# 2. Hardware TSO Memory Subsystem Simulator
# ============================================================================
class TSOMemory:
    """
    Simulates an x86 Total Store Order (TSO) memory architecture.
    Each core possesses a private FIFO Store Buffer with Store Forwarding.
    Writes are queued locally; Loads bypass pending writes to OTHER addresses,
    exposing the canonical Store-Load reordering hazard.
    """

    def __init__(self, initial_memory: Dict[str, Any]):
        self.main_memory = dict(initial_memory)
        self.store_buffers = {0: deque(), 1: deque()}
        self._lock = threading.Lock()

    def write(self, core_id: int, address: str, value: Any):
        """Buffer store into private FIFO store buffer."""
        with self._lock:
            self.store_buffers[core_id].append((address, value))

    def read(self, core_id: int, address: str) -> Any:
        """
        Read with Store Forwarding:
        Check local store buffer from newest to oldest; if not present,
        read from main memory.
        """
        with self._lock:
            # Inspect local store buffer in reverse (store forwarding)
            for addr, val in reversed(self.store_buffers[core_id]):
                if addr == address:
                    return val
            # Not in local buffer: read from shared memory
            return self.main_memory[address]

    def mfence(self, core_id: int):
        """MFENCE / Store barrier: drains this core's store buffer to main memory."""
        with self._lock:
            while self.store_buffers[core_id]:
                addr, val = self.store_buffers[core_id].popleft()
                self.main_memory[addr] = val

    def drain_one(self, core_id: int) -> bool:
        """Drains a single pending store from core's buffer to main memory."""
        with self._lock:
            if self.store_buffers[core_id]:
                addr, val = self.store_buffers[core_id].popleft()
                self.main_memory[addr] = val
                return True
            return False


# ============================================================================
# 3. Peterson Mutex under TSO
# ============================================================================
class PetersonMutexTSO:
    """
    Peterson mutex executing over TSOMemory.
    Allows toggling use_mfence to prove failure without fence and safety with fence.
    """

    def __init__(self, use_fence: bool = False):
        self.use_fence = use_fence
        self.mem = TSOMemory({
            "flag_0": False,
            "flag_1": False,
            "turn": 0
        })

    def enter_critical_section(self, core_id: int) -> bool:
        """
        Executes Peterson's entry protocol under TSO.
        Returns True if the thread enters CS.
        """
        other = 1 - core_id
        # W1: flag[i] = True
        self.mem.write(core_id, f"flag_{core_id}", True)
        # W2: turn = other
        self.mem.write(core_id, "turn", other)

        if self.use_fence:
            # Full memory fence: drains store buffer before proceeding to load flag[other]
            self.mem.mfence(core_id)

        # R1: Read flag[other] and turn
        # Under TSO without fence, flag[other] may be read from main memory before
        # the peer's store buffer has drained!
        flag_other = self.mem.read(core_id, f"flag_{other}")
        turn = self.mem.read(core_id, "turn")

        # Spin condition: while (flag[other] && turn == other)
        # If condition evaluates to False, thread enters CS
        can_enter = not (flag_other and turn == other)
        return can_enter

    def exit_critical_section(self, core_id: int):
        """
        Executes Peterson's exit protocol under TSO.
        Resets flag[core_id] = False and flushes store buffer if fenced.
        """
        self.mem.write(core_id, f"flag_{core_id}", False)
        if self.use_fence:
            self.mem.mfence(core_id)


# ============================================================================
# Pytest Test Cases
# ============================================================================
def test_peterson_sc_mutual_exclusion():
    """Verify that Peterson's mutex guarantees mutual exclusion under SC."""
    mutex = PetersonMutexSC()
    shared_counter = 0
    iterations = 500

    def worker(tid: int):
        nonlocal shared_counter
        for _ in range(iterations):
            mutex.lock(tid)
            # In Critical Section
            current = shared_counter
            time.sleep(0.00001)  # Context switch opportunity
            shared_counter = current + 1
            mutex.unlock(tid)

    t0 = threading.Thread(target=worker, args=(0,))
    t1 = threading.Thread(target=worker, args=(1,))

    t0.start()
    t1.start()
    t0.join()
    t1.join()

    # Assert mutual exclusion invariant held: exactly 1 thread in CS at any time
    assert mutex.max_concurrent_in_cs == 1, (
        f"Mutual exclusion violated under SC! Max concurrent in CS: {mutex.max_concurrent_in_cs}"
    )
    assert shared_counter == 2 * iterations, (
        f"Data race detected! Counter={shared_counter}, expected {2 * iterations}"
    )


def test_peterson_tso_violation_without_fence():
    """
    Demonstrate Peterson's algorithm FAILURE under TSO without MFENCE.
    Due to Store-Load reordering, both cores execute stores to store buffers,
    and both read flag[other] == False from main memory, simultaneously entering CS.
    """
    mutex_unfenced = PetersonMutexTSO(use_fence=False)

    # Core 0 executes stores to its store buffer
    # Core 1 executes stores to its store buffer
    c0_enters = mutex_unfenced.enter_critical_section(core_id=0)
    c1_enters = mutex_unfenced.enter_critical_section(core_id=1)

    # Both cores observe the other's flag as False because writes are still in store buffers!
    assert c0_enters is True, "Core 0 failed to enter CS"
    assert c1_enters is True, "Core 1 failed to enter CS"

    # Invariant: Simultaneous entry constitutes a mutual exclusion violation
    simultaneous_cs_count = int(c0_enters) + int(c1_enters)
    assert simultaneous_cs_count == 2, (
        "Expected TSO Store-Load reordering to cause simultaneous CS entry"
    )


def test_peterson_tso_restored_with_fence():
    """
    Demonstrate that inserting MFENCE drains store buffers, restoring mutual exclusion
    under TSO.
    """
    mutex_fenced = PetersonMutexTSO(use_fence=True)

    # Core 0 enters first with MFENCE: stores are flushed to main memory
    c0_enters = mutex_fenced.enter_critical_section(core_id=0)
    assert c0_enters is True, "Core 0 should enter CS"

    # Now Core 1 executes entry protocol with MFENCE
    # Core 1 flushes its stores, reads flag_0 == True and turn == 0, so it CANNOT enter
    c1_enters = mutex_fenced.enter_critical_section(core_id=1)
    assert c1_enters is False, (
        "Core 1 must NOT enter CS while Core 0 holds lock with MFENCE"
    )


def test_peterson_tso_full_lifecycle_with_exit():
    """
    Verify complete lifecycle under TSO with fences:
    1. Core 0 enters CS successfully.
    2. Core 1 attempts entry and is blocked (mutual exclusion preserved).
    3. Core 0 exits CS, resetting flag_0 and flushing store buffer.
    4. Core 1 now re-checks and can safely enter CS.
    5. Core 1 exits CS.
    """
    mutex = PetersonMutexTSO(use_fence=True)

    # Core 0 enters
    assert mutex.enter_critical_section(core_id=0) is True

    # Core 1 attempts entry while Core 0 holds CS -> blocked!
    assert mutex.enter_critical_section(core_id=1) is False

    # Core 0 completes work and exits CS
    mutex.exit_critical_section(core_id=0)

    # Core 1 re-checks entry condition: flag_0 is now False in memory
    flag_0 = mutex.mem.read(1, "flag_0")
    turn = mutex.mem.read(1, "turn")
    assert flag_0 is False
    assert not (flag_0 and turn == 0)  # Core 1 can now enter!

    # Core 1 exits
    mutex.exit_critical_section(core_id=1)

