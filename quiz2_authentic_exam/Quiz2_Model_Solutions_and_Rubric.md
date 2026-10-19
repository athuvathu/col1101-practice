# COL1101 Quiz 2: Official Model Solutions & Grading Rubric

> **Course Reference:** COL1101 (Data Structures and Algorithms) — Diwali 2026  
> **Grading Policy:** Strictly patterned after the official Quiz 1 grading rubric (`slides/submission_420680294.pdf`).

---

## Question 1: Binary Min-Heap Permutations & Ancestor Properties [6 points]

### 1(a) (2 points) Permutation $A = [0, 2, 1, 5, 4, 6, 3]$
- **Official Answer**: **Valid Binary Min-Heap (YES)**.
- **Model Justification**:
  In an ACBT of size $n = 7$, there are 3 internal nodes (indices 0, 1, 2) and 4 leaf nodes (indices 3, 4, 5, 6).
  We verify the min-heap order property ($A[\text{parent}] < A[\text{child}]$) for all 6 edges:
  1. For parent index 0 (val 0):
     - Left child index 1 has val 2: $0 < 2$ (Holds).
     - Right child index 2 has val 1: $0 < 1$ (Holds).
  2. For parent index 1 (val 2):
     - Left child index 3 has val 5: $2 < 5$ (Holds).
     - Right child index 4 has val 4: $2 < 4$ (Holds).
  3. For parent index 2 (val 1):
     - Left child index 5 has val 6: $1 < 6$ (Holds).
     - Right child index 6 has val 3: $1 < 3$ (Holds).
  Since every child is strictly greater than its parent, the array satisfies the min-heap property.
- **Grading Rubric**:
  - `+ 1 pt`: Correct answer ("Valid" / "YES").
  - `+ 1 pt`: Correct explanation (verifying all parent-child pairs or demonstrating that no edge violates heap order).
  - `+ 0 pts`: Wrong / missing answer (explanation doesn't matter, as per Quiz 1 rubric).

---

### 1(b) (2 points) Permutation $A = [0, 3, 1, 2, 4, 5, 6]$
- **Official Answer**: **Not a Valid Binary Min-Heap (NO)**.
- **Model Justification**:
  Consider node at index 1 with value $A[1] = 3$.
  Its left child in a 0-indexed array is at index $2 \times 1 + 1 = 3$, with value $A[3] = 2$.
  The min-heap property requires $A[1] < A[3]$, but here:
  $$A[1] = 3 > 2 = A[3]$$
  Because parent value 3 is strictly greater than child value 2, the min-heap order property is violated.
- **Grading Rubric**:
  - `+ 1 pt`: Correct answer ("Not valid" / "NO").
  - `+ 1 pt`: Correct explanation (identifying the specific parent-child violation between index 1 and index 3: $A[1] = 3 > 2 = A[3]$).
  - `+ 0 pts`: Wrong / missing answer (explanation doesn't matter).

---

### 1(c) (2 points) Can the 3rd smallest element reside at index 7 for $n = 15$?
- **Official Answer**: **NO (Impossible)**.
- **Model Justification**:
  In a 0-indexed ACBT, the path of ancestors from node 7 to the root is:
  1. Parent of node 7: $\lfloor (7 - 1) / 2 \rfloor = 3$.
  2. Grandparent of node 7: $\lfloor (3 - 1) / 2 \rfloor = 1$.
  3. Great-grandparent (root): $\lfloor (1 - 1) / 2 \rfloor = 0$.
  
  Thus, node 7 has strictly **3 distinct ancestors**: nodes 3, 1, and 0.
  By the min-heap order property on distinct elements:
  $$A[0] < A[1] < A[3] < A[7]$$
  This chain establishes that $A[7]$ is strictly greater than at least 3 distinct elements in the heap ($A[0], A[1],$ and $A[3]$).
  Therefore, $A[7]$ can at best be the 4th smallest element (its rank is at least 4), and it can **never** be the 3rd smallest element.
- **Grading Rubric**:
  - `+ 1 pt`: Correct answer ("NO" / "Impossible").
  - `+ 1 pt`: Correct explanation (identifying that node 7 has 3 distinct ancestors: 3, 1, and 0, each strictly smaller than node 7, forcing its rank to be $\ge 4$).
  - `+ 0 pts`: Wrong / missing answer (explanation doesn't matter).

---

## Question 2: Python Semantics: Closures & Concurrency [6 points]

### 2(a) Closures, Pipelines & Scoping (3 points)
1. **Output of `print(pipe_a(10))`**: `22` (1 point)
   - *Intermediate Trace*:
     - `ops` contains closures created with default argument binding `s=step` where `step` was 1, 2, 3:
       - $f_0(x) = x + 1 \times 2 = x + 2$
       - $f_1(x) = x + 2 \times 2 = x + 4$
       - $f_2(x) = x + 3 \times 2 = x + 6$
     - `reduce` applies these sequentially starting with $acc = 10$:
       - After $f_0$: $10 + 2 = 12$
       - After $f_1$: $12 + 4 = 16$
       - After $f_2$: $16 + 6 = \mathbf{22}$
   - *Rubric*: `+ 1 pt` for correct output `22` with intermediate accumulator trace.

2. **Output of `print(pipe_b(10))`**: `28` (1 point)
   - *Intermediate Trace*:
     - `late_ops` closures do not use default arguments. Each lambda references the variable `step` in the enclosing scope `make_pipeline`.
     - When the `for` loop finishes, the variable `step` in `make_pipeline` has the terminal value `3`.
     - When `pipe_b(10)` runs, all three closures look up `step` dynamically, and all three see `step = 3`.
     - Each function computes: $x + 3 \times 2 = x + 6$.
     - `reduce` computes: $10 + 6 + 6 + 6 = \mathbf{28}$.
   - *Rubric*: `+ 1 pt` for correct output `28`.

3. **Explanation of Scoping Difference** (1 point)
   - *Explanation*:
     - In `ops`, `s=step` binds the parameter $s$ at **function definition time** (eager binding); each closure receives a snapshot of the current value of `step`.
     - In `late_ops`, `step` is looked up at **call time** via a closure cell object in the enclosing lexical scope (late binding). Because all three lambdas share the same lexical cell, they all read the final value of `step` ($3$) when called.
   - *Rubric*: `+ 1 pt` for clearly contrasting definition-time binding vs call-time / late-binding cell lookup.

---

### 2(b) Concurrency, Race Conditions & Deadlocks (3 points)

1. **Lost Update Trace (1.5 points)**:
   - Initial balance = $100$.
   - **Interleaving Trace**:
     ```text
     Time  Thread T1                     Thread T2                     acc.balance
     -----------------------------------------------------------------------------
     t0    Reads t1 = 100                (idle)                        100
     t1    [Context switch to T2]
     t2    (idle)                        Reads t2 = 100                100
     t3    (idle)                        Writes balance = 100+20=120   120
     t4    [Context switch to T1]
     t5    Writes balance = 100+10=110   (idle)                        110
     ```
   - **Final Balance**: `110` (or `120` if $T_2$ writes last).
   - **Explanation**: $T_1$ read a stale value of `balance` ($100$) before $T_2$ made its deposit. When $T_1$ writes back, it silently overwrites $T_2$'s deposit of 20.
   - *Rubric*: `+ 1 pt` for correct trace showing concurrent read of stale balance followed by overwrite; `+ 0.5 pt` for stating correct final balance (`110` or `120`).

2. **Deadlock Trace & Prevention (1.5 points)**:
   - **Deadlock Trace**:
     ```text
     Time  Thread T1                     Thread T2                     Lock States
     -----------------------------------------------------------------------------------------
     t0    Acquires acc1.lock            (idle)                        acc1.lock held by T1
     t1    [Context switch to T2]
     t2    (idle)                        Acquires acc2.lock            acc2.lock held by T2
     t3    (idle)                        Attempts acquire acc1.lock    T2 BLOCKS (waits for T1)
     t4    [Context switch to T1]
     t5    Attempts acquire acc2.lock    (blocked)                     T1 BLOCKS (waits for T2)
     ```
     Both threads are blocked forever waiting for each other (Circular Wait).
   - **Prevention**: Enforce a **global lock hierarchy / acquisition order**. Assign each account a unique identifier (e.g. account ID or `id(acc)`), and mandate that all threads must always acquire locks in strictly increasing order:
     $$\min(\text{acc1}, \text{acc2}).\text{lock} \quad \text{acquired before} \quad \max(\text{acc1}, \text{acc2}).\text{lock}$$
     Because all threads acquire locks in the identical order, circular waiting is mathematically impossible.
   - *Rubric*: `+ 1 pt` for valid interleaving trace showing deadlock; `+ 0.5 pt` for explaining lock ordering prevention.

---

## Question 3: Formal Correctness & Complexity of Fast Build Heap [8 points]

### 3(a) Inductive Step for Loop Invariant $\mathcal{P}(i)$ (3 points)
- **Model Proof**:
  1. By the induction hypothesis, $\mathcal{P}(i)$ holds immediately before executing the loop for index $i$, meaning every subtree rooted at index $j \in \{i+1, \dots, n-1\}$ is a valid min-heap.
  2. For index $i \ge 0$, its left child $2i + 1$ and right child $2i + 2$ satisfy $2i + 1 > i$ and $2i + 2 > i$. Therefore, both subtrees rooted at $2i + 1$ and $2i + 2$ are already valid min-heaps, which directly satisfies the precondition of `heap_down(A, i, n)`.
  3. By the proven correctness of `heap_down`, sifting $A[i]$ down ensures that the subtree $T_i$ rooted at index $i$ becomes a valid binary min-heap.
  4. Furthermore, `heap_down(A, i, n)` only modifies nodes within the subtree $T_i$ and leaves all other disjoint subtrees rooted at $j > i$ completely unaffected. Hence, every node $j \in \{i, i+1, \dots, n-1\}$ roots a valid min-heap, establishing $\mathcal{P}(i-1)$. $\blacksquare$
- **Grading Rubric**:
  - `+ 1 pt`: Stating that child indices $2i+1 > i$ and $2i+2 > i$ ensure the precondition of `heap_down` is satisfied by $\mathcal{P}(i)$.
  - `+ 1 pt`: Citing correctness of `heap_down` to conclude subtree $T_i$ becomes a valid min-heap.
  - `+ 1 pt`: Explicitly noting that subtrees rooted at $j > i$ remain valid min-heaps (no interference).
  - *Grading Feedback Note from Quiz 1*: Deductions applied if the proof fails to show why the precondition holds or claims $2i+1 \ge i$ rather than strict inequality $2i+1 > i$.

---

### 3(b) Correctness at Termination (1 point)
- **Model Proof**:
  When the `for` loop terminates, the loop counter decrements to $i = -1$.
  By the invariant, $\mathcal{P}(-1)$ holds, which asserts that for every $j \in \{0, 1, \dots, n-1\}$, the subtree $T_j$ is a valid binary min-heap.
  Node $0$ is the root of the entire ACBT containing all $n$ elements; since $T_0$ is a valid min-heap, the entire array $A$ satisfies the min-heap property. $\blacksquare$
- **Grading Rubric**:
  - `+ 1 pt`: Correct deduction that $i = -1 \implies \mathcal{P}(-1)$ holds $\implies T_0$ is a valid min-heap containing all $n$ elements.
  - `+ 0 pts`: Incomplete or hand-wavy assertion.

---

### 3(c) Termination Argument (1 point)
- **Model Proof**:
  The outer `for` loop executes a fixed, finite number of iterations ($\lfloor n/2 \rfloor$). In each iteration, `heap_down(A, i, n)` starts at index $i$ and in each step moves to a child with index $\ge 2k + 1$, strictly increasing the depth and strictly decreasing the remaining height of the subtree.
  Because the height of an ACBT of size $n$ is finite ($\lfloor \log_2 n \rfloor + 1$), the sift-down path cannot exceed $\lfloor \log_2 n \rfloor$ steps.
  Thus, each call to `heap_down` terminates in finite steps, and the entire algorithm terminates. $\blacksquare$
- **Grading Rubric**:
  - `+ 1 pt`: Identifying well-founded decreasing metric (strictly decreasing subtree height / strictly increasing index bounded by $n$) and finite outer loop iterations.
  - `+ 0 pts`: Missing termination metric.

---

### 3(d) Worst-Case Time Complexity Analysis (3 points)

1. **Summation Formulation (1 point)**:
   - A node at height $h$ can sift down at most $h$ levels, performing at most $2h$ comparisons.
   - An ACBT of size $n$ has at most $\lceil \frac{n}{2^{h+1}} \rceil$ nodes at height $h$.
   - Total comparisons $T(n)$:
     $$T(n) \le \sum_{h=1}^{\lfloor \log_2 n \rfloor} \left\lceil \frac{n}{2^{h+1}} \right\rceil \cdot 2h \le \sum_{h=1}^{\infty} \frac{n}{2^h} \cdot h = n \sum_{h=1}^{\infty} \frac{h}{2^h}$$
   - *Rubric*: `+ 1 pt` for correct height-node summation setup.

2. **Evaluating the AGP Summation (1 point)**:
   - Let $S = \sum_{h=1}^{\infty} \frac{h}{2^h} = \frac{1}{2^1} + \frac{2}{2^2} + \frac{3}{2^3} + \frac{4}{2^4} + \dots$
   - Multiply by $\frac{1}{2}$:
     $$\frac{1}{2}S = \frac{1}{2^2} + \frac{2}{2^3} + \frac{3}{2^4} + \dots$$
   - Subtracting the second equation from the first:
     $$S - \frac{1}{2}S = \frac{1}{2^1} + \frac{1}{2^2} + \frac{1}{2^3} + \frac{1}{2^4} + \dots = \sum_{k=1}^{\infty} \left(\frac{1}{2}\right)^k$$
   - Evaluating the infinite geometric series:
     $$\frac{1}{2}S = \frac{1/2}{1 - 1/2} = 1 \implies \mathbf{S = 2}$$
   - *Rubric*: `+ 1 pt` for showing unrolling, subtraction $S - \frac{1}{2}S$, and concluding $S = 2$.

3. **Tight $\Theta(n)$ Bound (1 point)**:
   - Substituting $S = 2$ back into the summation:
     $$T(n) \le n \cdot S = 2n \implies T(n) = O(n)$$
   - Furthermore, `fast_build_min_heap` must inspect each of the $\lfloor n/2 \rfloor$ internal nodes at least once (doing $\ge 1$ comparison per internal node), so $T(n) = \Omega(n)$.
   - Since $T(n) = O(n)$ and $T(n) = \Omega(n)$, we have:
     $$\mathbf{T(n) = \Theta(n)}$$
   - *Rubric*: `+ 1 pt` for establishing both $O(n)$ and $\Omega(n)$ to conclude $\Theta(n)$.
