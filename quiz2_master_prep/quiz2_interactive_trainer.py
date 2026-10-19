#!/usr/bin/env python3
"""
COL1101 Quiz 2 Interactive Trainer & Exam Simulator
----------------------------------------------------
An authentic, terminal-based interactive study engine and exam simulator
designed specifically for IIT Delhi COL1101 Quiz 2 preparation.

Covers:
- Complete & Almost Complete Binary Trees (CBT/ACBT) & LOT Queue Invariant
- Binary Min-Heaps: 0-Indexed Array Mapping, Sift-Down, Ancestor Ranks
- Fast Build Heap: Invariant Induction & AGP Summation Analysis
- Functional Programming: Immutability, Currying, Pipelines, Closures & Late Binding
- Concurrency from Slides: Threads vs Processes, Race Conditions, Locks, Deadlocks
"""

import sys
import time
import dis
import threading
from functools import reduce
from typing import List, Tuple, Optional

# ANSI Color codes for clean terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    banner = f"""
{CYAN}{BOLD}================================================================================
     COL1101 (Data Structures and Algorithms) — Quiz 2 Exam Trainer
          Interactive Diagnostic Engine & Authentic Mock Simulator
================================================================================{RESET}
"""
    print(banner)


# ----------------------------------------------------------------------
# Visual Heap ASCII Formatter
# ----------------------------------------------------------------------
def print_ascii_heap(arr: List[int], max_nodes: int = 15):
    """Prints a clear ASCII representation of a binary heap stored in arr."""
    n = min(len(arr), max_nodes)
    if n == 0:
        print("  (Empty heap)")
        return

    print(f"\n{BOLD}Array representation:{RESET} {arr[:n]} (showing {n} nodes)")
    print(f"{BOLD}ASCII Tree Visualization:{RESET}")
    
    # Levels up to 4 (15 nodes)
    if n >= 1:
        print(f"               [{arr[0]:02d}] (idx 0)")
    if n >= 2:
        l1_str = f"       [{arr[1]:02d}] (idx 1)"
        if n >= 3:
            l1_str += f"              [{arr[2]:02d}] (idx 2)"
        print("              /        \\")
        print(l1_str)
    if n >= 4:
        print("          /      \\            /      \\")
        l2_parts = []
        for i in range(3, min(7, n)):
            l2_parts.append(f"[{arr[i]:02d}]({i})")
        print("     " + "     ".join(l2_parts))
    if n >= 8:
        print("      /  \\   /  \\      /  \\   /  \\")
        l3_parts = []
        for i in range(7, n):
            l3_parts.append(f"[{arr[i]:02d}]({i})")
        print("   " + " ".join(l3_parts))
    print()


# ----------------------------------------------------------------------
# Heap Operations with Detailed Tracing
# ----------------------------------------------------------------------
def heap_down_trace(A: List[int], i: int, n: int) -> List[str]:
    """Performs heap_down and returns step-by-step swap traces."""
    trace = []
    step = 1
    while 2 * i + 1 < n:
        left = 2 * i + 1
        right = 2 * i + 2
        smallest = left
        if right < n and A[right] < A[left]:
            smallest = right
        if A[i] <= A[smallest]:
            trace.append(f"Step {step}: Node {i} ({A[i]}) <= smallest child {smallest} ({A[smallest]}). Heap property satisfied. Terminating.")
            break
        trace.append(f"Step {step}: Sift down: swap parent idx {i} (val {A[i]}) with child idx {smallest} (val {A[smallest]}). Array: {list(A)}")
        A[i], A[smallest] = A[smallest], A[i]
        i = smallest
        step += 1
    return trace


def is_min_heap(A: List[int]) -> Tuple[bool, Optional[str]]:
    n = len(A)
    for i in range(n):
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and A[i] > A[l]:
            return False, f"Violation at parent index {i} (val {A[i]}) > left child index {l} (val {A[l]})"
        if r < n and A[i] > A[r]:
            return False, f"Violation at parent index {i} (val {A[i]}) > right child index {r} (val {A[r]})"
    return True, "Valid min-heap"


# ----------------------------------------------------------------------
# Interactive Closures & Concurrency Demonstrators
# ----------------------------------------------------------------------
def inspect_closure_mechanics():
    """Live demonstration of eager parameter defaults vs late binding."""
    print(f"\n{BOLD}{CYAN}=== INTERACTIVE CLOSURE MECHANICS DEMONSTRATOR ==={RESET}")
    print("Consider the classic loop with lambdas:")
    print("  eager = [lambda x, s=step: x + s for step in [1, 2, 3]]")
    print("  late  = [lambda x: x + step for step in [1, 2, 3]]\n")

    step = 0
    eager = []
    for step in [1, 2, 3]:
        eager.append(lambda x, s=step: x + s)

    late = []
    for step in [1, 2, 3]:
        late.append(lambda x: x + step)

    print(f"{BOLD}1. Eager Functions with Default Arguments (`s=step`):{RESET}")
    for idx, fn in enumerate(eager):
        print(f"   fn[{idx}].__defaults__ = {fn.__defaults__} -> calls with x=10: {fn(10)}")

    print(f"\n{BOLD}2. Late-Binding Functions with Enclosing Scope (`step`):{RESET}")
    for idx, fn in enumerate(late):
        cell_val = fn.__closure__[0].cell_contents if fn.__closure__ else "None"
        print(f"   fn[{idx}].__closure__[0].cell_contents = {cell_val} -> calls with x=10: {fn(10)}")

    print(f"\n{GREEN}Key Takeaway:{RESET} Eager binding evaluates parameter defaults at DEFINITION TIME.")
    print("Late binding captures a shared Cell Object pointer that dereferences the variable at CALL TIME!\n")


def simulate_bank_race_condition():
    """Live demonstration of thread interleaving and lost updates."""
    print(f"\n{BOLD}{CYAN}=== INTERACTIVE CONCURRENCY LOST-UPDATE SIMULATOR ==={RESET}")
    print("Simulating two threads depositing $10 and $20 to an account with initial balance $100 without locks...\n")

    class UnsafeAccount:
        def __init__(self):
            self.balance = 100
        def deposit(self, amt):
            curr = self.balance
            time.sleep(0.0001) # forces thread preemption
            self.balance = curr + amt

    trials = 10
    lost_updates = 0
    for t_idx in range(trials):
        acc = UnsafeAccount()
        t1 = threading.Thread(target=acc.deposit, args=(10,))
        t2 = threading.Thread(target=acc.deposit, args=(20,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        if acc.balance != 130:
            lost_updates += 1
            print(f"  Trial {t_idx+1}: Balance = ${acc.balance} {RED}(LOST UPDATE OCCURRED! Expected $130){RESET}")
        else:
            print(f"  Trial {t_idx+1}: Balance = ${acc.balance} {GREEN}(No context switch during write){RESET}")

    print(f"\nResult: {lost_updates}/{trials} trials experienced data loss due to unsynchronized race conditions.")


# ----------------------------------------------------------------------
# Interactive Mock Exam Engine
# ----------------------------------------------------------------------
class QuizEngine:
    def __init__(self):
        self.score = 0.0
        self.total_points = 20.0

    def ask_mcq(self, q_num: str, points: float, question: str, options: List[str], correct_idx: int, explanation: str) -> bool:
        print(f"\n{BOLD}{MAGENTA}[Question {q_num}] ({points} points){RESET}")
        print(question)
        for i, opt in enumerate(options):
            print(f"  ({chr(97+i)}) {opt}")
        
        while True:
            try:
                choice = input(f"\n{BOLD}Your Choice (a-{chr(97+len(options)-1)}): {RESET}").strip().lower()
                if choice and ord('a') <= ord(choice[0]) < ord('a') + len(options):
                    user_idx = ord(choice[0]) - ord('a')
                    break
                print(f"{RED}Invalid input. Please enter a letter from a to {chr(97+len(options)-1)}.{RESET}")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting quiz.")
                sys.exit(0)

        if user_idx == correct_idx:
            print(f"{GREEN}{BOLD}CORRECT! (+{points} pts){RESET}")
            self.score += points
            print(f"{CYAN}Explanation:{RESET} {explanation}")
            return True
        else:
            print(f"{RED}{BOLD}INCORRECT. (+0.0 pts){RESET}")
            print(f"Correct answer was: ({chr(97+correct_idx)}) {options[correct_idx]}")
            print(f"{CYAN}Explanation:{RESET} {explanation}")
            return False

    def run_full_mock_quiz(self):
        print(f"\n{BOLD}{YELLOW}Starting Authentic COL1101 Quiz 2 Mock Exam (20 Points Total){RESET}")
        print("Patterned strictly on the IIT Delhi format, syllabus, and grading criteria.")
        self.score = 0.0

        # Q1.1 (2 pts)
        self.ask_mcq(
            "1.1", 2.0,
            "Consider a binary min-heap H1 and a binary max-heap H2, both containing the exact same set {1, 2, 3, 4, 5, 6, 7}.\nIs it possible for H1 and H2 to share the exact same value at array index 1 (i.e., H1[1] == H2[1])?",
            [
                "No, because the root must be unique and index 1 must be strictly smaller in min-heap than max-heap.",
                "Yes, any value in {3, 4, 5} can sit at index 1 in both heaps (e.g. H1[1] = H2[1] = 4).",
                "Yes, but only the median value 4 is possible.",
                "No, because in a size 7 max-heap, index 1 must be either 6 or 7."
            ],
            1,
            "In min-heap H1, index 1 is > root (1 element) and < its 2 children (nodes 3, 4), bounding rank to {2, 3, 4, 5}. In max-heap H2, index 1 is < root and > its 2 children, bounding rank to {3, 4, 5, 6}. The intersection is {3, 4, 5}. Valid heaps exist for values 3, 4, and 5!"
        )

        # Q1.2 (2 pts)
        self.ask_mcq(
            "1.2", 2.0,
            "In a binary min-heap H1 and binary max-heap H2 on {1, 2, 3, 4, 5, 6, 7}, is it possible that H1[0] == H2[2]?",
            [
                "Yes, by setting H2[2] to 1.",
                "No, because H1[0] is the global minimum 1, while in H2, node 2 has children at indices 5 and 6, forcing H2[2] > H2[5] >= 1.",
                "Yes, because node 2 is a leaf in a size 7 ACBT.",
                "No, because roots of min-heaps and max-heaps can never equal each other."
            ],
            1,
            "In H1, root H1[0] = 1 (unique minimum). In H2, node 2 is an internal node with children 5 and 6. Max-heap property dictates H2[2] > H2[5] >= 1, so H2[2] >= 2. Hence H1[0] == H2[2] is strictly impossible!"
        )

        # Q1.3 (2 pts)
        self.ask_mcq(
            "1.3", 2.0,
            "In a binary min-heap of size n = 30 containing distinct elements, what is the exact array index range [i_min, i_max] where the 4th smallest element can possibly reside?",
            [
                "[1, 6] (depths 1 and 2 only)",
                "[1, 14] (depths 1, 2, and 3)",
                "[0, 14] (depths 0 through 3)",
                "[3, 29] (all nodes except depth 0 and 1)"
            ],
            1,
            "A node at depth d has d strictly smaller ancestors, so its rank is >= d + 1. For rank = 4, depth <= 3. Depth 0 has rank 1. Thus candidate depths are 1, 2, and 3, which span array indices [1, 14]!"
        )

        # Q2.1 (3 pts)
        self.ask_mcq(
            "2.1", 3.0,
            "Consider the Python code:\n"
            "  ops = [lambda x, s=step: x + s * 2 for step in [1, 2, 3]]\n"
            "  late_ops = [lambda x: x + step * 2 for step in [1, 2, 3]]\n"
            "  pipe_a = lambda x: reduce(lambda acc, f: f(acc), ops, x)\n"
            "  pipe_b = lambda x: reduce(lambda acc, f: f(acc), late_ops, x)\n"
            "What are the exact integer outputs of print(pipe_a(10)) and print(pipe_b(10))?",
            [
                "pipe_a(10) = 22, pipe_b(10) = 22",
                "pipe_a(10) = 22, pipe_b(10) = 28",
                "pipe_a(10) = 16, pipe_b(10) = 19",
                "pipe_a(10) = 28, pipe_b(10) = 28"
            ],
            1,
            "In ops, s=step binds eagerly: 10 + 2 -> 12 + 4 -> 16 + 6 = 22. In late_ops, all lambdas look up step dynamically from enclosing scope, where loop ended with step=3! Thus each lambda adds 3*2 = 6, yielding 10 + 6 + 6 + 6 = 28!"
        )

        # Q2.2 (3 pts)
        self.ask_mcq(
            "2.2", 3.0,
            "Thread 1 executes: with lockA: with lockB: work()\n"
            "Thread 2 executes: with lockB: with lockA: work()\n"
            "What happens and what is the standard algorithmic prevention?",
            [
                "Race condition occurs; prevent using time.sleep().",
                "Deadlock occurs due to circular wait; prevent by enforcing a strict global lock acquisition order (e.g. acquire min(id(A), id(B)) first).",
                "Starvation occurs; prevent by using FIFO process queues.",
                "Live-lock occurs; prevent using threading.Event()."
            ],
            1,
            "Reverse lock acquisition leads to circular wait (T1 holds lockA waiting for lockB; T2 holds lockB waiting for lockA). The definitive fix is Global Lock Ordering (Havender's principle), forcing all threads to acquire locks in monotonically increasing order!"
        )

        # Q3.1 (3 pts)
        self.ask_mcq(
            "3.1", 3.0,
            "In the Fast Build Heap algorithm (for i from n//2 - 1 down to 0: heap_down(A, i, n)), why does the inductive step P(i) => P(i-1) hold?",
            [
                "Because children 2i+1 and 2i+2 are strictly greater than i (for i >= 0), ensuring their subtrees are already valid min-heaps by P(i), satisfying the precondition of heap_down.",
                "Because array elements are already sorted.",
                "Because heap_down runs in O(1) time.",
                "Because n is always odd."
            ],
            0,
            "For index i >= 0, child indices satisfy 2i+1 > i and 2i+2 > i. Invariant P(i) guarantees all subtrees with root index > i are already valid heaps, which directly satisfies the precondition of heap_down(A, i, n)!"
        )

        # Q3.2 (2 pts)
        self.ask_mcq(
            "3.2", 2.0,
            "Why does a call to heap_down(A, i, n) on a binary min-heap necessarily terminate?",
            [
                "Because it uses an infinite loop with a break statement.",
                "Because each swap strictly increases the current node's depth and strictly decreases the remaining subtree height, which is a well-founded metric bounded by tree height <= floor(log2 n).",
                "Because array length n decreases at each step.",
                "Because the CPU clock interrupts the thread."
            ],
            1,
            "At each swap step, the node index moves from k to at least 2k + 1. The remaining height of the subtree strictly decreases towards 0. Since the ACBT has finite height <= floor(log2 n) + 1, it must terminate in finite steps!"
        )

        # Q3.3 (3 pts)
        self.ask_mcq(
            "3.3", 3.0,
            "Why does Fast Build Heap achieve Theta(n) linear time, while naive top-down insertion requires Theta(n log n)?",
            [
                "Because bottom-up uses faster memory caches.",
                "Because in bottom-up, ~n/2 leaves have height 0 (doing 0 comparisons) and only 1 root has height log2 n; the AGP sum sum_{h=1}^infty (h / 2^h) evaluates to 2.",
                "Because Python's list implementation has O(1) swaps.",
                "Because top-down insertion creates an ACBT while bottom-up creates a CBT."
            ],
            1,
            "Bottom-up does work proportional to node height (distance to leaf). The vast majority of nodes are leaves (height 0) doing zero work! In contrast, top-down does work proportional to depth, where ~n/2 leaves do the maximum O(log n) work. The AGP sum S = sum h/2^h = 2 proves T(n) <= 2n = Theta(n)!"
        )

        print(f"\n{BOLD}================================================================================{RESET}")
        print(f"{BOLD}FINAL EXAM SCORE: {self.score:.1f} / {self.total_points:.1f} points ({self.score/self.total_points*100:.1f}%){RESET}")
        if self.score >= 18.0:
            print(f"{GREEN}{BOLD}GRADE: A+ (Outstanding Mastery of COL1101 Concurrency & Heaps!){RESET}")
        elif self.score >= 14.0:
            print(f"{YELLOW}{BOLD}GRADE: A / B+ (Solid Understanding; review closure scoping & loop invariants){RESET}")
        else:
            print(f"{RED}{BOLD}GRADE: Needs Revision (Review 15_Minute_Quick_Revision_Notes.md){RESET}")
        print(f"{BOLD}================================================================================{RESET}\n")


# ----------------------------------------------------------------------
# Interactive Terminal Main Menu
# ----------------------------------------------------------------------
def main():
    print_banner()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running non-interactive self-test...")
        inspect_closure_mechanics()
        simulate_bank_race_condition()
        sample_heap = [10, 40, 20, 15, 12, 25, 30]
        print_ascii_heap(sample_heap)
        trace = heap_down_trace(sample_heap, 0, len(sample_heap))
        for t in trace:
            print(" ", t)
        print("\nAll self-test routines executed successfully!")
        return

    engine = QuizEngine()

    while True:
        print(f"{BOLD}Select an Activity:{RESET}")
        print("  1. Take Full Timed 20-Point Mock Exam (Authentic Quiz 2)")
        print("  2. Run Interactive Binary Heap Sift-Down Visualizer")
        print("  3. Run Interactive Python Closure Scoping Demonstrator")
        print("  4. Run Live Multi-Threaded Lost-Update Concurrency Simulator")
        print("  5. Exit")

        try:
            choice = input(f"\n{BOLD}Enter choice (1-5): {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if choice == "1":
            engine.run_full_mock_quiz()
        elif choice == "2":
            user_arr_str = input("\nEnter space-separated integers for heap (or press Enter for default [40 10 20 15 12 25 30]): ").strip()
            if not user_arr_str:
                arr = [40, 10, 20, 15, 12, 25, 30]
            else:
                try:
                    arr = [int(x) for x in user_arr_str.split()]
                except ValueError:
                    print(f"{RED}Invalid input. Using default.{RESET}")
                    arr = [40, 10, 20, 15, 12, 25, 30]
            print_ascii_heap(arr)
            traces = heap_down_trace(arr, 0, len(arr))
            print(f"\n{BOLD}Sift-Down Trace on Root (index 0):{RESET}")
            for t in traces:
                print(" ", t)
            print(f"\n{BOLD}Final Array:{RESET} {arr}")
            print_ascii_heap(arr)
        elif choice == "3":
            inspect_closure_mechanics()
        elif choice == "4":
            simulate_bank_race_condition()
        elif choice == "5":
            print("Good luck on your exam! Exiting.")
            break
        else:
            print(f"{RED}Invalid option. Please enter 1-5.{RESET}")


if __name__ == "__main__":
    main()
