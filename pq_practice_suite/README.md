# COL1101 Diwali 2026 — Programming Quiz Practice Suite (1.5 Hours)

Authentic, zero-slop examination preparation suite built specifically for **COL1101 (Programming with Data Structures)** at IIT Delhi.

All questions are calibrated to the exact post-Quiz 1 lab practicals (Weeks 6–9) and follow the **Virtual Programming Lab (VPL)** evaluation environment used on `exam.cse.iitd.ac.in`.

> [!IMPORTANT]
> **Strict Syllabus Constraint (Confirmed by TA):**
> **AVL Trees and self-balancing rotations are NOT in the programming quiz.** All tree problems focus on standard Binary Search Trees augmented with dynamic node attributes (subtree size, value sums, bounds), Tries, or Heaps.

---

## Suite Architecture

```
pq_practice_suite/
├── README.md                      # Complete guide and syllabus breakdown
├── vpl_runner.py                  # Unified CLI test runner & grading engine
├── portal/
│   └── index.html                 # Unixporn dark-themed 1.5-hour simulator portal
│
├── exam1/                         # Mock Exam 1 (Authentic 1.5-Hour Exam)
│   ├── Q1_Trie_Frequency_Filter/  # Problem 1: Trie with Top-K Branch & Bound (40 pts)
│   │   ├── README.md              # Detailed problem statement & sample traces
│   │   ├── common.py              # Abstract interface & TrieNode definitions
│   │   ├── student_code.py        # Code template for the student
│   │   ├── solution.py            # Master reference implementation
│   │   ├── test_suite.py          # VPL evaluation runner with stress tests
│   │   └── vpl_evaluate.sh        # Standard VPL execution shell script
│   │
│   └── Q2_Augmented_Order_BST/    # Problem 2: Augmented Order BST (60 pts)
│       ├── README.md              # Problem statement & deletion invariants
│       ├── common.py              # Node & BaseAugmentedBST definitions
│       ├── student_code.py        # Code template for the student
│       ├── solution.py            # Master reference implementation (No AVL)
│       ├── test_suite.py          # Differential fuzzing & stress test runner
│       └── vpl_evaluate.sh        # Standard VPL evaluation shell script
│
└── exam2/                         # Mock Exam 2 (Alternative 1.5-Hour Exam)
    ├── Q1_Dual_Heap_Scheduler/    # Problem 1: Dual-Priority Cross-Heap Scheduler (40 pts)
    │   ├── README.md              # Problem statement & pointer invariants
    │   ├── common.py              # Job & BaseDualScheduler definitions
    │   ├── student_code.py        # Code template for the student
    │   ├── solution.py            # Master reference implementation
    │   ├── test_suite.py          # Stress fuzzing runner
    │   └── vpl_evaluate.sh        # Standard VPL evaluation shell script
    │
    └── Q2_Cuckoo_Linear_Hash/     # Problem 2: Two-Table Cuckoo Dictionary (60 pts)
        ├── README.md              # Eviction chains & cycle rehash specification
        ├── common.py              # UniversalHasher & BaseCuckooDict
        ├── student_code.py        # Code template for the student
        ├── solution.py            # Master reference implementation
        ├── test_suite.py          # Displacement kick & rehash test runner
        └── vpl_evaluate.sh        # Standard VPL evaluation shell script
```

---

## 1. Quick Start Guide

### Launching the Interactive Portal
Open the Unixporn dark-themed exam portal directly in your browser:
```bash
xdg-open pq_practice_suite/portal/index.html
```
* **Timer:** 90-minute countdown with first-class `[Space]` or `[p]` to Pause/Resume.
* **State Persistence:** Preserves time and tab states across reloads and computer sleep via `localStorage`.

---

## 2. Running VPL Tests from the Command Line

You can test individual problems or run full 1.5-hour mock grading from your native terminal:

### Testing Individual Problems
```bash
# Test Mock Exam 1 Question 1 (Trie Top-K)
python3 pq_practice_suite/vpl_runner.py test exam1 q1

# Test Mock Exam 1 Question 2 (Augmented BST)
python3 pq_practice_suite/vpl_runner.py test exam1 q2

# Test Mock Exam 2 Question 1 (Dual Heap Scheduler)
python3 pq_practice_suite/vpl_runner.py test exam2 q1

# Test Mock Exam 2 Question 2 (Cuckoo Dictionary)
python3 pq_practice_suite/vpl_runner.py test exam2 q2
```

### Full Exam Grading
```bash
# Grade your student_code for Exam 1 (100 points total)
python3 pq_practice_suite/vpl_runner.py grade exam1

# Grade your student_code for Exam 2 (100 points total)
python3 pq_practice_suite/vpl_runner.py grade exam2

# Test against the master reference solutions
python3 pq_practice_suite/vpl_runner.py grade all solution
```

---

## 3. High-Yield Pitfalls for October 21

1. **BST Deletion (No AVL):**
   * When a node has 2 children, find its in-order successor (minimum in right subtree).
   * Splice out the successor, and bubble up subtree attribute updates (`size`, `sum_val`, `min_key`, `max_key`) starting from the successor's original parent up to the root.
2. **Order Statistics Indexing:**
   * In 1-indexed `kth_smallest`: if $k \le \text{left.size}$, go left; if $k == \text{left.size} + 1$, return current node; else decrement $k \leftarrow k - (\text{left.size} + 1)$ and go right.
3. **Cuckoo Hashing Kick Limits:**
   * Set `max_kicks = 2 * (len(T0) + len(T1))`. If a kick loop exceeds this threshold, a cycle is detected and the table must double in capacity and re-hash.
4. **Trie Branch-and-Bound Pruning:**
   * When finding top-$k$ words, store `subtree_max_freq` at every internal node. Terminate expansion of branches whose max frequency is strictly less than the $k$-th best candidate discovered so far.
