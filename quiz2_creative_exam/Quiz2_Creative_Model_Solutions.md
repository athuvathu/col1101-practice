# COL1101 Quiz 2 (Creative Exam): Official Model Solutions & Grading Rubric

> **Course Reference:** COL1101 (Data Structures and Algorithms) — Diwali 2026  
> **Grading Policy:** Patterned strictly on the official Quiz 1 grading rubric (`slides/submission_420680294.pdf`).

---

## Question 1: Min-Max Heap Duality & Ancestor Rank Bounds [6 points]

### 1(a) (2 points) Can $H_1[1] = H_2[1]$ for min-heap $H_1$ and max-heap $H_2$ on $\{1, 2, 3, 4, 5, 6, 7\}$?
- **Official Answer**: **YES (It is possible)**.
- **Model Justification**:
  In a 0-indexed ACBT of size $n = 7$:
  - Node 1 has parent 0 and two children: left child 3 and right child 4.
  - In a min-heap $H_1$: $H_1[0] < H_1[1]$, $H_1[1] < H_1[3]$, and $H_1[1] < H_1[4]$.
    Therefore, $H_1[1]$ is strictly greater than at least 1 element ($H_1[0]$) and strictly less than at least 2 elements ($H_1[3], H_1[4]$). This requires $\text{rank}(H_1[1]) \in \{2, 3, 4, 5\}$.
  - In a max-heap $H_2$: $H_2[0] > H_2[1]$, $H_2[1] > H_2[3]$, and $H_2[1] > H_2[4]$.
    Therefore, $H_2[1]$ is strictly less than at least 1 element ($H_2[0]$) and strictly greater than at least 2 elements ($H_2[3], H_2[4]$). This requires $\text{rank}(H_2[1]) \in \{3, 4, 5, 6\}$.
  - The intersection of permissible ranks is $\{3, 4, 5\}$. Choosing the value $4$ allows both heaps to share index 1.
  
  **Explicit Valid Arrays**:
  - Valid Min-Heap $H_1$:
    $$H_1 = [1, \mathbf{4}, 2, 6, 7, 3, 5]$$
    *Verification*: $1 < 4, 2$; $4 < 6, 7$; $2 < 3, 5$. (All min-heap edges hold).
  - Valid Max-Heap $H_2$:
    $$H_2 = [7, \mathbf{4}, 6, 2, 1, 5, 3]$$
    *Verification*: $7 > 4, 6$; $4 > 2, 1$; $6 > 5, 3$. (All max-heap edges hold).
  Both arrays contain $\{1, 2, 3, 4, 5, 6, 7\}$, and $H_1[1] = H_2[1] = 4$.
- **Grading Rubric**:
  - `+ 1 pt`: Correct answer ("YES" / "Possible").
  - `+ 1 pt`: Providing explicit valid arrays for both $H_1$ and $H_2$ showing $H_1[1] = H_2[1]$ (or rigorous rank intersection argument $\text{rank} \in \{3, 4, 5\}$ with a valid example).
  - `+ 0 pts`: Wrong / missing answer (explanation does not matter).

---

### 1(b) (2 points) Can $H_1[0] = H_2[2]$ for heaps on $\{1, 2, 3, 4, 5, 6, 7\}$?
- **Official Answer**: **NO (Impossible)**.
- **Model Justification**:
  1. In any binary min-heap $H_1$ containing distinct integers $\{1, 2, 3, 4, 5, 6, 7\}$, the root $H_1[0]$ must be the unique minimum element of the set:
     $$H_1[0] = 1$$
  2. Now consider index 2 in an ACBT of size $n = 7$. Node 2 is an internal node with two children:
     - Left child at index $2 \times 2 + 1 = 5$
     - Right child at index $2 \times 2 + 2 = 6$
  3. By the max-heap order property, every parent must be strictly greater than its children:
     $$H_2[2] > H_2[5] \quad \text{and} \quad H_2[2] > H_2[6]$$
  4. Because the set contains only positive integers $\ge 1$, the children $H_2[5]$ and $H_2[6]$ must be at least 1. Therefore:
     $$H_2[2] > H_2[5] \ge 1 \implies H_2[2] \ge 2$$
  5. Thus, $H_2[2]$ can never equal 1. But $H_1[0] = 1$. Hence, $H_1[0] = H_2[2]$ is mathematically impossible.
- **Grading Rubric**:
  - `+ 1 pt`: Correct answer ("NO" / "Impossible").
  - `+ 1 pt`: Correct explanation (stating $H_1[0] = 1$ is the minimum, and in $H_2$, node 2 has children at indices 5 and 6, forcing $H_2[2] > H_2[5] \ge 1$).
  - `+ 0 pts`: Wrong / missing answer.

---

### 1(c) (2 points) Candidate array index range for 4th smallest element in min-heap of size $n = 30$
- **Official Answer**: **Index range $[1, 14]$** (indices $1 \le i \le 14$).
- **Model Justification**:
  1. **Ancestor Rank Theorem**: In a binary min-heap of distinct elements, every node at depth $d$ has exactly $d$ ancestors on its path to the root. Since every ancestor is strictly smaller, any node at depth $d$ is strictly greater than at least $d$ elements, which implies its rank is at least $d + 1$:
     $$\text{rank}(v) \ge \text{depth}(v) + 1$$
  2. **Upper Bound on Depth**:
     For a node to hold the 4th smallest element ($\text{rank} = 4$), we must have:
     $$\text{depth}(v) + 1 \le 4 \implies \text{depth}(v) \le 3$$
     - Any node at depth $\ge 4$ has at least 4 ancestors, so its rank is $\ge 5$, meaning it can NEVER hold the 4th smallest element.
  3. **Lower Bound on Depth**:
     - Depth 0 (the root, index 0) has 0 ancestors and must hold the 1st smallest element ($\text{rank} = 1$). It can never hold the 4th smallest element.
     - Therefore, the 4th smallest element must reside at **depth 1, depth 2, or depth 3**.
  4. **Mapping Depths to 0-Indexed Array Ranges**:
     - Depth 1: indices $2^1 - 1$ to $2^2 - 2 \implies [1, 2]$.
     - Depth 2: indices $2^2 - 1$ to $2^3 - 2 \implies [3, 6]$.
     - Depth 3: indices $2^3 - 1$ to $2^4 - 2 \implies [7, 14]$.
     - In an ACBT of size $n = 30$, all nodes up to index 14 exist (since $14 < 30$).
  5. Thus, the exact candidate index range is:
     $$[i_{\min}, i_{\max}] = [1, 14]$$
- **Grading Rubric**:
  - `+ 1 pt`: Correct index range $[1, 14]$ (or stating depths 1, 2, and 3).
  - `+ 1 pt`: Rigorous justification (proving depth 0 has rank 1, depth $\ge 4$ has rank $\ge 5$ due to having $\ge 4$ smaller ancestors).
  - `+ 0 pts`: Guessing an incorrect range.

---

## Question 2: Python Semantics: Discount Pipeline & Concurrent Ledger [6 points]

### 2(a) Closures, Pipelines & Scoping (3 points)

1. **Output of `print(apply_eager(1000))`**: `360` (1 point)
   - *Intermediate Accumulator Trace*:
     - Initial value: $acc = 1000$
     - Stage 1 ($rate = 10$): $1000 - \frac{1000 \times 10}{100} = 1000 - 100 = \mathbf{900}$
     - Stage 2 ($rate = 20$): $900 - \frac{900 \times 20}{100} = 900 - 180 = \mathbf{720}$
     - Stage 3 ($rate = 50$): $720 - \frac{720 \times 50}{100} = 720 - 360 = \mathbf{360}$
   - *Rubric*: `+ 1 pt` for correct output `360` with intermediate stage values shown.

2. **Output of `print(apply_late(1000))`**: `125` (1 point)
   - *Intermediate Accumulator Trace*:
     - `late_rules` closures do not use default arguments; they reference the variable `r` in the enclosing scope `make_discount_pipeline`.
     - When the `for` loop completes, `r` remains at its terminal value `50`.
     - When `apply_late` executes, all three closures dynamically read $r = 50$. Each stage applies a 50% discount:
       - Stage 1: $1000 - 500 = \mathbf{500}$
       - Stage 2: $500 - 250 = \mathbf{250}$
       - Stage 3: $250 - 125 = \mathbf{125}$
   - *Rubric*: `+ 1 pt` for correct output `125`.

3. **Explanation of Scoping & CPython Mechanism** (1 point)
   - *Explanation*:
     - In `rules_eager`, `rate=r` is evaluated at **function definition time** when the `def/lambda` line executes. CPython stores these evaluated values in the function object's `__defaults__` tuple. Each function gets its own snapshot of `r`.
     - In `rules_late`, `r` is a free variable captured from the enclosing scope. CPython stores a reference to a shared **cell object** (`__closure__[0]`). At **call time**, the closure dereferences this cell, which contains the final loop value ($r = 50$) for all three functions.
   - *Rubric*: `+ 1 pt` for clearly explaining definition-time default argument evaluation vs call-time cell object lookup.

---

### 2(b) Concurrency, Race Conditions & Deadlocks (3 points)

1. **Lost Update Trace (1.5 points)**:
   - Initial balance = $1000$.
   - **Interleaving Trace**:
     ```text
     Time  Thread T1 (withdraw 400)      Thread T2 (withdraw 700)      acc.balance
     -----------------------------------------------------------------------------
     t0    Reads current = 1000          (idle)                        1000
     t1    [Context switch to T2]
     t2    (idle)                        Reads current = 1000          1000
     t3    (idle)                        Writes balance = 1000-700=300 300
     t4    [Context switch to T1]
     t5    Writes balance = 1000-400=600 (idle)                        600
     ```
   - **Final Balance**: `600`.
   - **Explanation**: Both threads read `current = 1000` before either could write. Because $T_1$ writes last, its update ($600$) overwrites $T_2$'s withdrawal. The bank dispensed $400 + 700 = 1100$ in cash, but the account balance is still $600$ instead of being overdrawn to $-100$, causing the bank a direct loss of $700$.
   - *Rubric*: `+ 1 pt` for valid interleaving trace showing preemption between read and write; `+ 0.5 pt` for correct final balance $600$ and explanation of lost update.

2. **Deadlock Trace & Corrected Function (1.5 points)**:
   - **Deadlock Trace**:
     ```text
     Time  Thread 1 (Alice: A -> B)      Thread 2 (Bob: B -> A)        Lock States
     -------------------------------------------------------------------------------------
     t0    Acquires accA.lock            (idle)                        accA locked by T1
     t1    [Context switch to T2]
     t2    (idle)                        Acquires accB.lock            accB locked by T2
     t3    (idle)                        Attempts acquire accA.lock    T2 BLOCKS (waits for T1)
     t4    [Context switch to T1]
     t5    Attempts acquire accB.lock    (blocked)                     T1 BLOCKS (waits for T2)
     ```
     Both threads wait forever on locks held by each other (Circular Dependency).
   - **Corrected Function `transfer_correct`**:
     ```python
     def transfer_correct(acc1, acc2, amt):
         # Enforce a global lock acquisition hierarchy based on object identity
         first_lock, second_lock = (acc1.lock, acc2.lock) if id(acc1) < id(acc2) else (acc2.lock, acc1.lock)
         with first_lock:
             with second_lock:
                 acc1.balance -= amt
                 acc2.balance += amt
     ```
   - **Invariant**: All threads acquire shared locks in a **strict total order** (here defined by `id(acc)`). Because every thread requests locks in monotonically increasing order, circular waiting is mathematically impossible.
   - *Rubric*: `+ 0.5 pt` for deadlock trace; `+ 0.5 pt` for correct Python code with lock ordering; `+ 0.5 pt` for stating the strict order invariant eliminating circular wait.

---

## Question 3: Formal Invariant Induction & Complexity of Fast Build Heap [8 points]

### 3(a) Inductive Step for Loop Invariant $\mathcal{P}(i)$ (3 points)
- **Model Proof**:
  1. By the induction hypothesis, $\mathcal{P}(i)$ holds immediately before executing the loop iteration for index $i$, meaning every subtree rooted at index $j \in \{i+1, \dots, n-1\}$ is a valid binary min-heap.
  2. In an ACBT stored in a 0-indexed array, the left child of node $i$ is $2i + 1$ and the right child is $2i + 2$. Because $i \ge 0$, we have strictly $2i + 1 > i$ and $2i + 2 > i$. Therefore, any children that exist for node $i$ are rooted at indices $> i$, which guarantees that the left and right subtrees of node $i$ are already valid min-heaps by $\mathcal{P}(i)$.
  3. This directly satisfies the fundamental precondition of `heap_down(A, i, n)`. By the proven correctness of `heap_down`, sifting $A[i]$ down restores the min-heap property for the subtree $T_i$ rooted at index $i$.
  4. Furthermore, `heap_down(A, i, n)` only modifies elements within the subtree $T_i$ and does not touch any disjoint subtrees rooted at $j > i$. Thus, every subtree rooted at $j \in \{i, i+1, \dots, n-1\}$ is a valid min-heap, which establishes that $\mathcal{P}(i-1)$ holds after the iteration. $\blacksquare$
- **Grading Rubric**:
  - `+ 1 pt`: Proving strict inequality $2i+1 > i$ and $2i+2 > i$ to establish that child subtrees satisfy the precondition of `heap_down`.
  - `+ 1 pt`: Stating that `heap_down` correctness guarantees subtree $T_i$ becomes a valid min-heap.
  - `+ 1 pt`: Proving non-interference (subtrees $T_j$ for $j > i$ remain valid min-heaps).
  - *Quiz 1 Grader Deduction Note*: Deductions applied if bounds are weak (e.g. writing $2i+1 \ge i$ instead of strictly $> i$).

---

### 3(b) Correctness at Termination (1 point)
- **Model Proof**:
  The `for` loop terminates when the loop counter reaches $i = -1$.
  By the invariant, $\mathcal{P}(-1)$ holds, which asserts that for every $j \in \{0, 1, \dots, n-1\}$, the subtree $T_j$ is a valid binary min-heap.
  Because node $0$ is the root of the entire ACBT, its subtree $T_0$ encompasses all $n$ elements; hence, the entire array $A$ is a valid binary min-heap. $\blacksquare$
- **Grading Rubric**:
  - `+ 1 pt`: Concluding that termination at $i = -1 \implies \mathcal{P}(-1) \implies T_0$ is a valid min-heap of all $n$ elements.
  - `+ 0 pts`: Incomplete reasoning.

---

### 3(c) Termination Argument (1 point)
- **Model Proof**:
  The outer `for` loop executes a fixed, finite number of iterations ($\lfloor n/2 \rfloor$). In each iteration, `heap_down(A, i, n)` operates on an index $k$: at each step, if a swap occurs, $k$ is updated to a child index ($k \ge 2k + 1$), which strictly increases the depth and strictly decreases the remaining subtree height.
  Because the tree has finite height $h = \lfloor \log_2 n \rfloor + 1$, the remaining height is a **well-founded metric** that strictly decreases to 0 in at most $\lfloor \log_2 n \rfloor$ steps. Thus, every call to `heap_down` terminates, and the overall algorithm must terminate. $\blacksquare$
- **Grading Rubric**:
  - `+ 1 pt`: Stating finite outer loop iterations and identifying strictly decreasing remaining subtree height as a well-founded metric bounded by tree height.
  - `+ 0 pts`: Missing termination metric.

---

### 3(d) Asymptotic Running Time Analysis (3 points)

1. **Summation Formulation (1 point)**:
   - In an ACBT of size $n$, the number of nodes at height $h$ (where leaves have $h = 0$) is at most $\lceil \frac{n}{2^{h+1}} \rceil$.
   - Sifting down a node at height $h$ takes at most $2h$ key comparisons.
   - The total number of key comparisons $T(n)$ is bounded by:
     $$T(n) \le \sum_{h=1}^{\lfloor \log_2 n \rfloor} \left\lceil \frac{n}{2^{h+1}} \right\rceil \cdot 2h \le \sum_{h=1}^{\infty} \frac{n}{2^h} \cdot h = n \sum_{h=1}^{\infty} \frac{h}{2^h}$$
   - *Rubric*: `+ 1 pt` for correct height-node summation setup.

2. **Evaluating the AGP Summation (1 point)**:
   - Let $S = \sum_{h=1}^{\infty} \frac{h}{2^h} = \frac{1}{2^1} + \frac{2}{2^2} + \frac{3}{2^3} + \frac{4}{2^4} + \dots$
   - Multiply by $\frac{1}{2}$:
     $$\frac{1}{2}S = \frac{1}{2^2} + \frac{2}{2^3} + \frac{3}{2^4} + \dots$$
   - Subtracting the second equation from the first:
     $$S - \frac{1}{2}S = \frac{1}{2^1} + \frac{1}{2^2} + \frac{1}{2^3} + \frac{1}{2^4} + \dots = \sum_{k=1}^{\infty} \left(\frac{1}{2}\right)^k$$
   - Evaluating the infinite geometric series ($\frac{a}{1 - r}$ with $a = 1/2, r = 1/2$):
     $$\frac{1}{2}S = \frac{1/2}{1 - 1/2} = 1 \implies \mathbf{S = 2}$$
   - *Rubric*: `+ 1 pt` for clear unrolling, subtraction $S - \frac{1}{2}S$, and concluding $S = 2$.

3. **Deducing $\Theta(n)$ Bound (1 point)**:
   - Substituting $S = 2$ into the upper bound:
     $$T(n) \le n \cdot S = 2n \implies T(n) = O(n)$$
   - Furthermore, `fast_build_min_heap` must inspect at least the $\lfloor n/2 \rfloor$ internal nodes, performing at least one comparison per internal node, so $T(n) = \Omega(n)$.
   - Since $T(n) = O(n)$ and $T(n) = \Omega(n)$, we conclude:
     $$\mathbf{T(n) = \Theta(n)}$$
   - *Rubric*: `+ 1 pt` for establishing both $O(n)$ and $\Omega(n)$ to conclude $\Theta(n)$.
