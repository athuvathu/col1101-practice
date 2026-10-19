# COL1101-Diwali2026 Quiz 2: Model Solutions & Grading Rubric

**Course**: COL1101 (Data Structures and Algorithms)  
**Total Points**: 20 pts &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Duration**: 1 hour  
**Grading Philosophy**: Modeled directly on official IIT Delhi grading conventions (Quiz 1 submission format). Partial credit is awarded strictly for mathematically sound reasoning; incorrect answers with no valid justification receive 0 points.

---

## Question 1: Algorithmic Concepts & Architectural Foundations [6 points]

### 1.1 Tree & Min-Heap Structural Bounds (2 points)

#### (a) Exact Height of ACBT with $n = 50$ (0.5 points)
- **Model Solution**:
  In this course, the height $h$ of a binary tree is defined as the number of levels (empty tree $h = 0$, root only $h = 1$).
  In an ACBT of height $h$, the number of nodes $n$ satisfies:
  $$2^{h-1} \le n \le 2^h - 1 \quad \iff \quad 2^{h-1} \le n < 2^h$$
  Equivalently, $h = \lfloor \log_2 n \rfloor + 1$.
  For $n = 50$:
  $$2^5 = 32 \le 50 < 64 = 2^6 \implies h = 6$$
  The height of the tree is **$6$** (levels 0, 1, 2, 3, 4, 5).
- **Grading Rubric**:
  - `[+ 0.5 pt]` Correct height $h = 6$ with correct inequality $32 \le 50 < 64$ or logarithmic formula.
  - `[+ 0.25 pt]` Correct formula but arithmetic mistake; or stated $h = 5$ if edges convention was explicitly noted (with 0.25 penalty for ignoring exam prompt's definition).
  - `[+ 0.0 pt]` Incorrect answer with no valid justification.

---

#### (b) Range of Leaf Node Indices (0.5 points)
- **Model Solution**:
  In a 0-indexed array representation of an ACBT of size $n$, a node at index $i$ has its left child at $2i + 1$.
  A node is a leaf if and only if it has no left child within the array bounds:
  $$2i + 1 \ge n \iff 2i \ge n - 1 \iff i \ge \left\lceil \frac{n-1}{2} \right\rceil = \left\lfloor \frac{n}{2} \right\rfloor$$
  For $n = 50$:
  $$i_{\min} = \left\lfloor \frac{50}{2} \right\rfloor = 25, \quad i_{\max} = n - 1 = 49$$
  The exact range of leaf indices is **$[25, 49]$** (i.e. indices $25, 26, \dots, 49$).
- **Grading Rubric**:
  - `[+ 0.5 pt]` Correct range $[25, 49]$ (or indices 25 to 49) with justification $2i+1 \ge 50$.
  - `[+ 0.25 pt]` Correct boundary formula $\lfloor n/2 \rfloor$ but off-by-one arithmetic error (e.g. $[24, 49]$).
  - `[+ 0.0 pt]` Missing or incorrect answer.

---

#### (c) Position of 3rd Smallest Element in Min-Heap (1.0 point)
- **Model Solution**:
  1. **Ancestral Depth Property**: In a binary min-heap with distinct elements, for any node $v$ at depth $d$, every ancestor of $v$ on the path from the root has a key strictly smaller than $v$. A node at depth $d$ has exactly $d$ ancestors.
  2. **Maximum Depth**:
     - At depth 0: The root $A[0]$ has 0 ancestors and is the 1st smallest element.
     - At depth 1: Nodes $A[1]$ and $A[2]$ have 1 ancestor ($A[0]$). The 2nd smallest element MUST be at depth 1 (either index 1 or 2).
     - At depth 2: Nodes $A[3], A[4], A[5], A[6]$ have 2 ancestors (the root and their depth 1 parent). If the depth 1 parent is the 2nd smallest element, and the other depth 1 node has a value larger than this node, this node can be the 3rd smallest element in the entire heap.
     - At depth $d \ge 3$: Any node $u$ at depth $d \ge 3$ has at least 3 distinct ancestors (at depths 0, 1, and 2), all of which are strictly smaller than $u$. Thus, at least 3 elements in the heap are strictly smaller than $u$, which implies $u$ is at best the 4th smallest element ($u \ge 4\text{th}$ smallest).
     - Therefore, the **maximum depth** for the 3rd smallest element is **depth 2**.
  3. **Possible Indices**:
     - Depth 1 indices: **$1, 2$**
     - Depth 2 indices: **$3, 4, 5, 6$**
     - Hence, the complete set of candidate indices is **$\{1, 2, 3, 4, 5, 6\}$**.
- **Grading Rubric**:
  - `[+ 0.5 pt]` Correct maximum depth (2) and complete set of indices $\{1, 2, 3, 4, 5, 6\}$.
  - `[+ 0.5 pt]` Rigorous justification showing depth $\ge 3$ nodes have at least 3 strictly smaller ancestors.
  - `[- 0.25 pt]` Missing depth 1 indices (only listing $\{3, 4, 5, 6\}$) or missing depth 2 indices.
  - `[+ 0.0 pt]` Guessing without ancestor justification.

---

### 1.2 Level-Order Traversal & Queue Invariant (2 points)

#### (a) Formal Queue Loop Invariant (0.5 points)
- **Model Solution**:
  From Lecture 18 (Page 5), the formal loop invariant for the FIFO queue $Q$ in Level-Order Traversal states:
  - **Two-Depth Property**: At any iteration, every node currently in queue $Q$ resides at depth $d$ or depth $d + 1$ (where $d$ is the depth of the node currently at the front of the queue).
  - **Ordering Structure**: If node $x$ at depth $d$ is at the front of $Q$, $Q$ contains:
    1. Node $x$, followed by
    2. All unvisited nodes at depth $d$ to the right of $x$ (in left-to-right order), followed by
    3. The children of all already-visited nodes at depth $d$ (which reside at depth $d+1$, in left-to-right order).
- **Grading Rubric**:
  - `[+ 0.5 pt]` Explicitly stating that nodes in $Q$ belong to at most two consecutive depths ($d$ and $d+1$) in left-to-right order.
  - `[+ 0.25 pt]` Incomplete description of the queue state.

---

#### (b) Queue State When Node 5 is Dequeued (1.5 points)
- **Model Solution**:
  - In a CBT of height $h = 4$ with $n = 15$ nodes:
    - Level 0 (depth 0): Node `[1]`
    - Level 1 (depth 1): Nodes `[2, 3]`
    - Level 2 (depth 2): Nodes `[4, 5, 6, 7]`
    - Level 3 (depth 3): Nodes `[8, 9, 10, 11, 12, 13, 14, 15]`
  - **Step-by-Step Traversal State**:
    1. Initially: $Q = [1]$.
    2. Node 1 dequeued; children 2, 3 enqueued: $Q = [2, 3]$.
    3. Node 2 dequeued; children 4, 5 enqueued: $Q = [3, 4, 5]$.
    4. Node 3 dequeued; children 6, 7 enqueued: $Q = [4, 5, 6, 7]$.
    5. Node 4 dequeued; children 8, 9 enqueued: $Q = [5, 6, 7, 8, 9]$.
    6. **Node 5 is dequeued**: Its children in a Complete Binary Tree are at indices $2 \times 5 = 10$ and $2 \times 5 + 1 = 11$ (1-indexed, or using 0-index $2i+1, 2i+2$). Node 5's children are nodes **10 and 11**.
    7. After enqueuing 10 and 11, the queue from front to back contains:
       $$\mathbf{[6, 7, 8, 9, 10, 11]}$$
  - **Justification**:
    - Nodes `1, 2, 3, 4, 5` have been dequeued and visited.
    - Remaining unvisited nodes at level 2: `6, 7`.
    - Children of already-visited level 2 nodes:
      - Children of 4: `8, 9`
      - Children of 5: `10, 11`
    - By FIFO ordering, the unvisited level 2 nodes (`6, 7`) precede all level 3 nodes (`8, 9, 10, 11`).
- **Grading Rubric**:
  - `[+ 1.0 pt]` Exactly correct queue contents `[6, 7, 8, 9, 10, 11]` in front-to-back order.
  - `[+ 0.5 pt]` Clear justification using level-order FIFO properties and tracking visited nodes.
  - `[- 0.5 pt]` Missing one element or inverted order.
  - `[+ 0.0 pt]` Incorrect list of nodes.

---

### 1.3 Concurrency: Threads, Processes & Deadlock (2 points)

#### (a) Processes vs Threads Memory Space (0.5 points)
- **Model Solution**:
  - **Processes** have separate, completely isolated virtual memory spaces. One process cannot access or corrupt another process's memory without explicit IPC.
  - **Threads** within the same process share the identical memory address space (heap, global variables).
  - **Vulnerability**: Because threads share mutable memory, unsynchronized concurrent reads and writes to the same variable result in **race conditions** (data corruption, lost updates). Processes do not share memory, so race conditions on shared memory cannot occur.
- **Grading Rubric**:
  - `[+ 0.25 pt]` Stating processes have isolated memory while threads share memory.
  - `[+ 0.25 pt]` Explaining that shared mutable memory causes race conditions.

---

#### (b) Deadlock Execution Trace (1.0 point)
- **Model Solution**:
  ```text
  Time Step    Thread T1 (with L1: with L2:)     Thread T2 (with L2: with L1:)
  ---------------------------------------------------------------------------------
  t0           T1 acquires L1                    (Idle / waiting)
  t1           [Context switch to T2]
  t2           (Blocked / Idle)                  T2 acquires L2
  t3           (Blocked / Idle)                  T2 attempts to acquire L1 -> BLOCKS (held by T1)
  t4           [Context switch to T1]
  t5           T1 attempts to acquire L2 -> BLOCKS (held by T2)
  ---------------------------------------------------------------------------------
  Deadlock reached: T1 holds L1 waiting for L2; T2 holds L2 waiting for L1.
  Neither thread can ever proceed (Circular Dependency).
  ```
- **Grading Rubric**:
  - `[+ 1.0 pt]` Valid, complete interleaving trace demonstrating that both locks are acquired and both threads block permanently.
  - `[+ 0.5 pt]` Correct concept of circular wait, but incomplete or flawed trace.

---

#### (c) Beyond Locks: Functional Programming & Actor Model (0.5 points)
- **Model Solution**:
  - **Functional Programming**: Enforces **immutability** (data is never mutated in-place). Because race conditions require at least one concurrent write to shared state, purely reading immutable data across multiple threads/processes (`multiprocessing.Pool().map`) is guaranteed to be 100% thread-safe without locks.
  - **Actor Model**: Eliminates shared memory by giving each Actor **strictly private internal state**. Outside threads communicate only by sending messages to the Actor's **Mailbox** (queue). The Actor processes messages sequentially one at a time, modifying its private state with zero shared access and zero locks.
- **Grading Rubric**:
  - `[+ 0.25 pt]` Correct FP explanation (immutability $\implies$ zero shared mutable state).
  - `[+ 0.25 pt]` Correct Actor Model explanation (private state + sequential message processing via mailbox).

---

## Question 2: Code Execution, Scoping & Concurrency [6 points]

### 2.1 Functional Scoping, Closures & Late Binding (3 points)

#### (a) Output of `print(res_a)` (1.0 point)
- **Model Solution**:
  ```python
  res_a = f[2](5)
  ```
  - `funcs` is populated via: `lambda x, s=step: x + s * 2 + init`
  - In Python, **default parameter values are evaluated and bound at function definition time**.
  - During the loop over `[2, 3, 5]`:
    - Iteration 1 (`step = 2`): `s = 2` is stored in function's `__defaults__`.
    - Iteration 2 (`step = 3`): `s = 3` is stored.
    - Iteration 3 (`step = 5`): `s = 5` is stored.
  - `f[2]` refers to the third closure created (`step = 5`), so its default parameter `s = 5`.
  - When `f[2](5)` is invoked, `x = 5`, `s = 5`, and `init = 1`.
  - Evaluation:
    $$\text{res\_a} = x + s \times 2 + \text{init} = 5 + 5 \times 2 + 1 = 5 + 10 + 1 = \mathbf{16}$$
  - **Output**: `16`
- **Grading Rubric**:
  - `[+ 0.5 pt]` Correct numeric answer `16`.
  - `[+ 0.5 pt]` Correct step-by-step arithmetic ($5 + 5 \times 2 + 1$).
  - `[+ 0.0 pt]` Incorrect answer.

---

#### (b) Output of `print(res_b)` (1.0 point)
- **Model Solution**:
  ```python
  res_b = l[0](3)
  ```
  - `late_funcs` is populated via: `lambda x: x + step * 3 + init`
  - In Python, variables in enclosing scopes that are not local parameters are **free variables**.
  - Closures capture free variables by **reference via cell objects**, not by value.
  - The loop iterates through `[2, 3, 5]`. When the loop terminates, the variable `step` in the enclosing scope `make_evaluators` has the final value **`5`**.
  - When `l[0](3)` is invoked, Python resolves `step` at **call time** by inspecting the enclosing cell object, which contains `5`.
  - Here `x = 3`, `step = 5`, and `init = 1`.
  - Evaluation:
    $$\text{res\_b} = x + \text{step} \times 3 + \text{init} = 3 + 5 \times 3 + 1 = 3 + 15 + 1 = \mathbf{19}$$
  - **Output**: `19`
- **Grading Rubric**:
  - `[+ 0.5 pt]` Correct numeric answer `19`.
  - `[+ 0.5 pt]` Correct step-by-step arithmetic ($3 + 5 \times 3 + 1$).
  - `[+ 0.0 pt]` If answer is 10 (common misconception $3 + 2 \times 3 + 1$), 0 points.

---

#### (c) Lexical Scoping Mechanism Explanation (1.0 point)
- **Model Solution**:
  - **Default Argument Binding (Early Binding in `funcs`)**:
    When `s=step` is written in the parameter list, Python evaluates the expression `step` when the `lambda` statement is executed (at definition time). The resulting integer object is placed into the function object's `__defaults__` tuple. Each function in `funcs` receives its own distinct default value corresponding to the loop's current iteration ($s=2, s=3, s=5$).
  - **Closure Cell Binding (Late Binding in `late_funcs`)**:
    When `lambda x: x + step * 3 + init` is written, `step` is an unadorned name in the function body. Python marks `step` as a cell variable (`__closure__`). All three lambdas created in the loop share a reference to the exact same cell object representing `step` in the activation record of `make_evaluators`.
    By the time any closure is invoked, the loop has completely finished, leaving `step = 5` in that cell. Thus, calling `l[0](3)` looks up `step` dynamically at invocation time, sees `5`, and computes $3 + 5 \times 3 + 1 = 19$, rather than using the historical loop value `2`.
- **Grading Rubric**:
  - `[+ 0.5 pt]` Clear distinction between definition-time binding (via default parameters) vs call-time / late lookup.
  - `[+ 0.5 pt]` Explicit mention of shared cell objects / enclosing scope reference lookup.
  - `[- 0.25 pt]` Vague explanation that doesn't mention when lookup occurs.

---

### 2.2 Heap-Down Sift Trace & Thread-Safe Synchronization (3 points)

#### (a) Execution Trace of `heap_down(H, 0, 7)` (1.0 point)
- **Model Solution**:
  Initial array: $H = [40, 10, 20, 15, 12, 25, 30]$, $n = 7$.
  
  - **Iteration 1**: Current index $i = 0$. Value $H[0] = 40$.
    - Left child: index $2(0) + 1 = 1$ ($H[1] = 10$).
    - Right child: index $2(0) + 2 = 2$ ($H[2] = 20$).
    - Compare children: $H[1] = 10 < H[2] = 20 \implies \text{smallest} = 1$.
    - Compare with parent: $H[0] = 40 > H[1] = 10 \implies$ swap $H[0]$ and $H[1]$.
    - **Array after Swap 1**:
      $$[10, 40, 20, 15, 12, 25, 30]$$
    - Update: $i \leftarrow 1$.

  - **Iteration 2**: Current index $i = 1$. Value $H[1] = 40$.
    - Left child: index $2(1) + 1 = 3$ ($H[3] = 15$).
    - Right child: index $2(1) + 2 = 4$ ($H[4] = 12$).
    - Compare children: $H[4] = 12 < H[3] = 15 \implies \text{smallest} = 4$.
    - Compare with parent: $H[1] = 40 > H[4] = 12 \implies$ swap $H[1]$ and $H[4]$.
    - **Array after Swap 2**:
      $$[10, 12, 20, 15, 40, 25, 30]$$
    - Update: $i \leftarrow 4$.

  - **Iteration 3**: Current index $i = 4$.
    - Left child: $2(4) + 1 = 9 \ge n = 7$. Loop condition `2 * i + 1 < n` is `False`.
    - While loop terminates.
  
  **Final Array Contents**:
  $$\mathbf{[10, 12, 20, 15, 40, 25, 30]}$$
- **Grading Rubric**:
  - `[+ 0.5 pt]` Intermediate states correct: Swap 1 gives $[10, 40, 20, 15, 12, 25, 30]$ (swapping indices 0 and 1).
  - `[+ 0.5 pt]` Swap 2 gives $[10, 12, 20, 15, 40, 25, 30]$ (swapping indices 1 and 4), and final array matches.
  - `[- 0.25 pt]` Off-by-one or swapped wrong child (e.g. swapped with 15 instead of 12).

---

#### (b) Concurrency Race Condition Interleaving (1.0 point)
- **Model Solution**:
  - Both threads access overlapping indices (specifically index 1, which is the child of node 0 processed by $T_1$, and the root of the subtree processed by $T_2$).
  - Python's list indexing and tuple multi-assignment `H[i], H[smallest] = H[smallest], H[i]` is **not atomic** at the bytecode level (it decomposes into multiple distinct bytecode instructions: `LOAD_FAST`, `BINARY_SUBSCR`, `SWAP`, `STORE_SUBSCR`, `STORE_SUBSCR`).
  - **Concrete Race Interleaving Scenario 1 (Torn Read / Inconsistent State Preemption)**:
    1. Initially $H = [40, 10, 20, 15, 12, 25, 30]$ ($n = 7$).
    2. $T_1$ runs `heap_down(H, 0, 7)`. At index 0, it determines `smallest = 1` ($H[1] = 10 < H[2] = 20$) and begins swapping $H[0]$ and $H[1]$.
    3. $T_1$ evaluates the RHS `(H[1], H[0]) = (10, 40)` and executes its first store: `H[0] = 10`.
    4. **Context switch to $T_2$** occurs before $T_1$ executes its second store (`H[1] = 40`).
    5. The shared array in memory is now in an inconsistent intermediate state: `H = [10, 10, 20, 15, 12, 25, 30]`. (The key 40 exists only in $T_1$'s private interpreter stack).
    6. $T_2$ invokes `heap_down(H, 1, 7)`. It reads $H[1] = 10$. Its children are $H[3] = 15$ and $H[4] = 12$, so `smallest = 4`.
    7. $T_2$ evaluates `if H[1] <= H[4]:` ($10 \le 12$), which is `True`! Because it observed the stale duplicate 10 instead of 40, $T_2$ assumes the heap invariant at node 1 is satisfied and **terminates prematurely without performing any swap**.
    8. **Context switch to $T_1$**. $T_1$ resumes and completes its second store: `H[1] = 40`.
    9. **Corrupted State / Invariant Violation**: Node 1 now contains 40, while its children are 15 and 12 ($40 > 12$ and $40 > 15$). If $T_1$ finishes or is descheduled, the min-heap property at node 1 is completely broken because $T_2$'s work was bypassed due to the torn read.
  - **Concrete Race Interleaving Scenario 2 (Concurrent Overlapping Sift on Node 1 / Lost Update)**:
    1. Suppose $T_1$ finishes its first swap ($H = [10, 40, 20, 15, 12, 25, 30]$) and sets its local loop index $i = 1$.
    2. Concurrently, $T_2$ begins executing `heap_down(H, 1, 7)` on node 1. Both threads are now executing on node 1.
    3. Both threads inspect $H[1] = 40$, $H[3] = 15$, $H[4] = 12$, and both determine `smallest = 4`. Both decide to swap index 1 and index 4.
    4. $T_1$ reads $H[4]=12$ and $H[1]=40$.
    5. Context switch to $T_2$. $T_2$ executes its swap non-atomically: writes `H[1] = 12`, then context switches to $T_1$ before writing `H[4] = 40`.
    6. $T_1$ executes its write: `H[1] = 12`. Then context switches to $T_2$ which writes `H[4] = 40`.
    7. If another thread or operation concurrently writes to $H[4]$, or if writes interleave, one of the updates is lost (lost update) or an element is permanently duplicated while another is erased.
- **Grading Rubric**:
  - `[+ 0.5 pt]` Identifying that node 1 is a shared mutable overlap between both threads.
  - `[+ 0.5 pt]` Demonstrating an explicit, valid interleaving leading to a stale read, premature loop termination, heap invariant violation, or lost update.
  - `[- 0.25 pt]` Claiming that on the initial array $H[1]=10$ would be swapped with $H[4]=12$ without $T_1$ first placing 40 into $H[1]$ (in a min-heap, $10 \le 12$ breaks immediately).
  - `[+ 0.0 pt]` Vague statement that "threads will collide" without showing an instruction sequence.

---

#### (c) Thread-Safe Implementation & Linearizability (1.0 point)
- **Model Solution**:
  ```python
  import threading

  def safe_heap_down(H, i, n, lock):
      with lock:
          heap_down(H, i, n)
  ```
  - **Why Mutual Exclusion Restores Correctness / Linearizability**:
    The `with lock:` context manager guarantees mutual exclusion by acquiring the underlying mutex prior to entering the critical section and releasing it upon exit.
    Because only one thread can execute `heap_down` at any time, all memory reads and writes across the array $H$ for one operation strictly **happen-before** the next operation starts.
    This eliminates all race conditions, guaranteeing that concurrent executions are **serializable** (equivalent to some sequential execution of the operations) and **linearizable** (each operation appears to take effect instantaneously at its lock-acquisition linearization point).
- **Grading Rubric**:
  - `[+ 0.5 pt]` Correct code using `threading.Lock` (`with lock:` or `acquire()` / `release()` in `try...finally`).
  - `[+ 0.5 pt]` Rigorous explanation referencing mutual exclusion, elimination of interleaving, and serializability / happens-before.

---

## Question 3: Formal Correctness & Algorithmic Analysis of Fast Build-Heap [8 points]

### 3.1 Loop Invariant Inductive Step (3 points)

#### (a) Base Case (0.5 points)
- **Model Solution**:
  - **Goal**: Show $\mathcal{P}(\lfloor n/2 \rfloor - 1)$ holds prior to the first iteration.
  - **Proof**:
    For any index $j \ge \lfloor n/2 \rfloor$, the index of its left child is:
    $$2j + 1 \ge 2 \left\lfloor \frac{n}{2} \right\rfloor + 1 \ge 2 \left(\frac{n-1}{2}\right) + 1 = n$$
    Because $2j + 1 \ge n$, node $j$ has no children in array $A$ (and consequently no right child either, since $2j + 2 > 2j + 1 \ge n$).
    Thus, every node $j \in \{\lfloor n/2 \rfloor, \dots, n-1\}$ is a **leaf**.
    A tree consisting of a single leaf node vacuously satisfies the min-heap property because there are no child nodes to violate the inequality $A[\text{parent}] \le A[\text{child}]$.
    Therefore, for every $j \in \{\lfloor n/2 \rfloor, \dots, n-1\}$, subtree $T_j$ is a valid binary min-heap.
    Thus, $\mathcal{P}(\lfloor n/2 \rfloor - 1)$ holds.
- **Grading Rubric**:
  - `[+ 0.5 pt]` Complete algebraic justification showing $2j+1 \ge n \implies$ leaf node $\implies$ vacuously satisfies min-heap property.
  - `[+ 0.25 pt]` Stated leaves are heaps without showing $2j+1 \ge n$.
  - `[+ 0.0 pt]` Incorrect base case argument.

---

##### (b) Inductive Step (2.5 points)
- **Model Solution**:
  - **Inductive Hypothesis**: Assume $\mathcal{P}(i)$ holds immediately before the loop executes for index $i$. That is, for all $j \in \{i+1, \dots, n-1\}$, subtree $T_j$ is a valid min-heap.
  - **Proof that $\mathcal{P}(i-1)$ holds after `heap_down(A, i, n)`**:
    1. **Precondition of `heap_down` on node $i$**:
       Because $0 \le i \le \lfloor n/2 \rfloor - 1$, its left child index is:
       $$2i + 1 \le 2\left(\left\lfloor \frac{n}{2} \right\rfloor - 1\right) + 1 \le 2\left(\frac{n}{2} - 1\right) + 1 = n - 1 < n$$
       Thus, the left child $2i + 1$ **always exists** within array bounds.
       Furthermore, because $i \ge 0$, we have:
       $$2i + 1 = i + (i + 1) > i$$
       By the inductive hypothesis $\mathcal{P}(i)$, since $2i + 1 \in \{i+1, \dots, n-1\}$, subtree $T_{2i+1}$ is already a valid min-heap.
       
       **Child Boundary Analysis (Even vs Odd $n$)**:
       - *Case I (Two Children exist, $2i + 2 < n$)*:
         Since $2i + 2 > i$, by $\mathcal{P}(i)$ subtree $T_{2i+2}$ is also a valid min-heap. Thus, both left and right subtrees are valid min-heaps.
       - *Case II (Single Left Child, $2i + 2 = n$)*:
         This occurs exclusively when $n$ is even and $i = n/2 - 1$ (e.g. for $n = 50$, $i = 24$, left child $2(24)+1 = 49$, right child $50 = n$).
         Here, node $i$ has no right child. Subtree $T_{2i+1}$ is a leaf ($49 = n - 1$), which is a valid min-heap. The right child condition holds vacuously.
       In both cases, the precondition for `heap_down` (that all existing child subtrees are valid min-heaps) is strictly satisfied.

    2. **Correctness of `heap_down(A, i, n)` on $T_i$**:
       - If $A[i] \le A[\text{child}]$ for all existing children, no swap occurs. Since all child subtrees are valid min-heaps, and the root $A[i]$ is less than or equal to its existing children, $T_i$ satisfies the min-heap property.
       - If $A[i] > A[\text{smallest\_child}]$, `heap_down` swaps $A[i]$ with its smallest child, say index $c \in \{2i+1, 2i+2\}$:
         - After the swap, node $c$ holds the minimum among $\{A[i], \text{existing children}\}$, so the new root of $T_i$ is $\le$ both of its children.
         - The untouched child subtree (if it exists) remains a valid min-heap.
         - In the chosen subtree $T_c$, its left and right child subtrees are unchanged and remain valid min-heaps, but its new root holds the swapped value $A[i]$.
         - The `while` loop continues sifting $A[i]$ down along the path of smallest children in $T_c$ until either $A[i] \le$ its children or a leaf is reached.
         By structural induction on the height of $T_i$, when `heap_down` terminates, $T_i$ satisfies the binary min-heap property.

    3. **Preservation of Non-Interference for $j > i$**:
       `heap_down(A, i, n)` exclusively accesses and modifies node $i$ and its descendants in $T_i$.
       For any other index $j \in \{i+1, \dots, n-1\}$:
       - If $j$ is not a descendant of $i$, $T_j$ shares no nodes with $T_i$'s descent path, so $T_j$ remains completely unmodified.
       - If $j$ is a descendant of $i$, its heap property was preserved by the invariant of `heap_down`.
       Therefore, all subtrees $T_j$ for $j \in \{i+1, \dots, n-1\}$ remain valid min-heaps.

    - **Conclusion**:
      Combining (2) and (3), all subtrees $T_j$ for $j \in \{i, i+1, \dots, n-1\}$ are valid min-heaps.
      This is precisely the statement $\mathcal{P}(i-1)$. The inductive step is proven.
- **Grading Rubric**:
  - `[+ 1.0 pt]` Proving child subtrees $T_{2i+1}, T_{2i+2}$ are valid heaps by inductive hypothesis since $2i+1 > i$ (with explicit note of existence for left child and boundary check for right child).
  - `[+ 1.0 pt]` Proving $T_i$ becomes a valid heap via sift-down mechanics.
  - `[+ 0.5 pt]` Explicit non-interference argument showing subtrees $T_j$ ($j > i$) are preserved.

---

### 3.2 Correctness upon Termination (1 point)

- **Model Solution**:
  The `for` loop decrements $i$ down to 0, terminating after the iteration for $i = 0$ finishes, at which point $i = -1$.
  By the established loop invariant $\mathcal{P}(-1)$, every subtree $T_j$ for $j \in \{(-1)+1, \dots, n-1\} = \{0, 1, \dots, n-1\}$ satisfies the binary min-heap property.
  In particular, for $j = 0$, $T_0$ is the subtree rooted at the root of the tree, which contains all $n$ nodes of array $A$.
  Therefore, the entire array $A$ is a valid binary min-heap.
- **Grading Rubric**:
  - `[+ 0.5 pt]` Stating loop terminates when $i = -1$.
  - `[+ 0.5 pt]` Applying $\mathcal{P}(-1)$ to $j = 0$ (root covers all $n$ nodes).

---

### 3.3 Termination Argument (1 point)

- **Model Solution**:
  - **Outer Loop**: The loop variable $i$ is initialized to $\lfloor n/2 \rfloor - 1$ and decrements by 1 in each step. The metric:
    $$\mu_{\text{outer}} = i + 1$$
    is a non-negative integer ($\mu_{\text{outer}} \in \mathbb{N} \cup \{0\}$) that strictly decreases by 1 in each iteration. When $\mu_{\text{outer}} = 0$, the loop terminates.
  - **Inner While Loop (`heap_down`)**: In each iteration where the loop does not break, the current node index $k$ is updated to one of its children ($2k+1$ or $2k+2$). This strictly increases the depth of $k$ by 1. Since the height of the tree is finite ($\le \lfloor \log_2 n \rfloor$), the metric:
    $$\mu_{\text{inner}} = \lfloor \log_2 n \rfloor - \text{depth}(k)$$
    is a non-negative integer that strictly decreases by at least 1 per swap.
  - Because both metrics are well-founded (strictly decreasing over the well-ordered set $\mathbb{N} \cup \{0\}$), the algorithm is guaranteed to terminate in a finite number of steps.
- **Grading Rubric**:
  - `[+ 0.5 pt]` Valid termination metric for outer loop ($i$ decrements to -1).
  - `[+ 0.5 pt]` Valid termination metric for inner `heap_down` (depth strictly increases towards bounded tree height).

---

### 3.4 Asymptotic Time Complexity Analysis (3 points)

#### (a) Summation Expression & Node Count Bounds (1.0 point)
- **Model Solution**:
  - In an ACBT of $n$ elements, the height of a node is defined as the number of edges on the longest downward path to a leaf (leaves have height 0, root has height $\lfloor \log_2 n \rfloor$).
  - The maximum number of swaps `heap_down` performs on a node of height $h$ is $h$.
  - Each swap takes $O(1)$ constant time (at most 2 child comparisons and 1 swap), so the work on a node of height $h$ is at most $c \cdot h$.
  - In any ACBT of size $n$, the number of nodes at height $h$ is at most:
    $$N(h) \le \left\lceil \frac{n}{2^{h+1}} \right\rceil$$
  - Leaves ($h=0$) require 0 swaps. Summing over all internal nodes with heights $h = 1$ to $\lfloor \log_2 n \rfloor$:
    $$T(n) \le \sum_{h=1}^{\lfloor \log_2 n \rfloor} \left\lceil \frac{n}{2^{h+1}} \right\rceil c \cdot h \le c \cdot n \sum_{h=1}^{\infty} \frac{h}{2^{h+1}} = \frac{c \cdot n}{2} \sum_{h=1}^{\infty} \frac{h}{2^h}$$
- **Grading Rubric**:
  - `[+ 0.5 pt]` Correct upper bound on node count at height $h$: $\lceil n / 2^{h+1} \rceil$.
  - `[+ 0.5 pt]` Correct summation formulation $T(n) \le c \cdot n \sum \frac{h}{2^{h+1}}$.

---

#### (b) Arithmetico-Geometric Progression (AGP) Proof (1.5 points)
- **Model Solution**:
  Consider the infinite summation:
  $$S = \sum_{h=1}^{\infty} \frac{h}{2^h} = \frac{1}{2^1} + \frac{2}{2^2} + \frac{3}{2^3} + \frac{4}{2^4} + \dots \quad \text{--- (Equation 1)}$$
  Multiply Equation 1 by $\frac{1}{2}$:
  $$\frac{1}{2} S = \frac{1}{2^2} + \frac{2}{2^3} + \frac{3}{2^4} + \dots \quad \text{--- (Equation 2)}$$
  Subtract Equation 2 from Equation 1 term-by-term:
  $$S - \frac{1}{2} S = \frac{1}{2^1} + \left(\frac{2}{2^2} - \frac{1}{2^2}\right) + \left(\frac{3}{2^3} - \frac{2}{2^3}\right) + \left(\frac{4}{2^4} - \frac{3}{2^4}\right) + \dots$$
  $$\frac{1}{2} S = \frac{1}{2^1} + \frac{1}{2^2} + \frac{1}{2^3} + \frac{1}{2^4} + \dots = \sum_{k=1}^{\infty} \frac{1}{2^k}$$
  The right-hand side is an infinite geometric series with first term $a = \frac{1}{2}$ and common ratio $r = \frac{1}{2}$:
  $$\sum_{k=1}^{\infty} \frac{1}{2^k} = \frac{a}{1 - r} = \frac{1/2}{1 - 1/2} = \frac{1/2}{1/2} = 1$$
  Therefore:
  $$\frac{1}{2} S = 1 \implies \mathbf{S = 2}$$
- **Grading Rubric**:
  - `[+ 0.5 pt]` Setting up $S$ and $\frac{1}{2}S$.
  - `[+ 0.5 pt]` Subtracting to obtain the geometric series $\sum_{k=1}^\infty \frac{1}{2^k}$.
  - `[+ 0.5 pt]` Evaluating geometric series to 1 and concluding $S = 2$.

---

#### (c) Asymptotic Tight Bound $\Theta(n)$ (0.5 points)
- **Model Solution**:
  Substituting $S = 2$ into our upper bound for $T(n)$:
  $$T(n) \le \frac{c \cdot n}{2} \sum_{h=1}^{\infty} \frac{h}{2^h} = \frac{c \cdot n}{2} \cdot 2 = c \cdot n = O(n)$$
  To establish the lower bound, notice that the algorithm must execute the outer loop $\lfloor n/2 \rfloor$ times. Even if a node requires only 1 comparison to verify the heap condition, at least $\lfloor n/2 \rfloor \times 1 = \Omega(n)$ operations must be executed.
  Since $T(n) = O(n)$ and $T(n) = \Omega(n)$, we conclude:
  $$T(n) = \mathbf{\Theta(n)}$$
  `fast_build_min_heap` runs in strictly linear time.
- **Grading Rubric**:
  - `[+ 0.5 pt]` Concluding $O(n)$ with substitution, noting $\Omega(n)$ lower bound, and stating $\Theta(n)$.
