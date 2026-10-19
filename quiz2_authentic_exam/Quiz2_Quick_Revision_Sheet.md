# COL1101 Quiz 2: High-Yield Revision Sheet

> **Syllabus Coverage**: Lectures 12–21 (Functional Programming, Concurrency, Binary Trees, ACBT/CBT, Binary Min-Heaps, Fast Build Heap, HeapSort). Strictly aligned with lecture slides (no IEEE 754, no out-of-syllabus topics).

---

## 1. Binary Trees, CBT & ACBT (Lectures 17–18)

### Height & Node Count Conventions (IIT Delhi Definition)
- **Depth of node $v$**: Number of edges from root to $v$. Root depth $= 0$.
- **Height $h$ of Tree**: Number of **levels** on longest root-to-leaf path:
  $$h = \text{max\_depth} + 1 \quad (h \ge 1 \text{ for non-empty trees}; \; h = 0 \text{ for empty tree})$$
- **Complete Binary Tree (CBT)**:
  - All levels $0 \dots h-2$ have $2^l$ nodes.
  - Level $h-1$ nodes are all leaves.
  - Total nodes: $n = 2^h - 1$.
- **Almost Complete Binary Tree (ACBT)**:
  - Levels $0 \dots h-2$ are completely full.
  - Bottom level $h-1$ nodes are packed as far left as possible.
  - Node count range: $2^{h-1} \le n \le 2^h - 1$.
  - Exact height formula: $h = \lfloor \log_2 n \rfloor + 1$.

### 0-Indexed Array Mapping Formulas
For an ACBT with $n$ nodes stored in array $A[0 \dots n-1]$:
| Relationship | Formula | Condition |
| :--- | :--- | :--- |
| **Parent of node $i$** | $\lfloor (i - 1) / 2 \rfloor$ | $i > 0$ |
| **Left child of node $i$** | $2i + 1$ | $2i + 1 < n$ |
| **Right child of node $i$** | $2i + 2$ | $2i + 2 < n$ |
| **Internal Nodes Range** | $0 \le i \le \lfloor n/2 \rfloor - 1$ | Nodes with $\ge 1$ child |
| **Leaf Nodes Range** | $\lfloor n/2 \rfloor \le i \le n - 1$ | Nodes with 0 children ($2i+1 \ge n$) |

---

## 2. Binary Min-Heaps (Lectures 19–21)

### Definition & Order Property
1. **Shape**: Must be an Almost Complete Binary Tree (ACBT).
2. **Order**: For every node $i > 0$, $A[\lfloor (i-1)/2 \rfloor] \le A[i]$.

### Candidate Positions for $k$-th Smallest Element
- A node at depth $d$ has strictly $d$ ancestors on its path to the root.
- In a min-heap with distinct elements, all $d$ ancestors are strictly smaller than the node.
- **Consequence**: Any node at depth $d$ has rank $\ge d + 1$.
  - 1st smallest (minimum): Exclusively at **depth 0** (index 0).
  - 2nd smallest: Can only be at **depth 1** (indices 1, 2).
  - 3rd smallest: Can only be at **depth 1 or depth 2** (indices 1, 2, 3, 4, 5, 6).
  - Can NEVER appear at depth $\ge 3$ (indices $\ge 7$) because it would have $\ge 3$ ancestors!

### Operations Summary
- `find_min()`: Return $A[0]$ $\implies \Theta(1)$.
- `heap_up(i)` (Sift-Up): Swap with parent while $A[\text{parent}] > A[i]$ $\implies O(\log n)$.
- `heap_down(i)` (Sift-Down): Swap with smaller child while $A[i] > A[\text{smaller\_child}]$ $\implies O(\log n)$.
- `insert(x)`: Append to end, `heap_up(n-1)` $\implies O(\log n)$.
- `extract_min()`: Swap $A[0]$ with $A[n-1]$, pop, `heap_down(0)` $\implies O(\log n)$.
- `fast_build_min_heap(A)`: Bottom-up sift-down $\implies \mathbf{\Theta(n)}$ linear time.

### Fast Build Heap AGP Summation Proof
$$\sum_{h=1}^\infty \frac{h}{2^h} = 2$$
- $S = \frac{1}{2} + \frac{2}{4} + \frac{3}{8} + \dots$
- $\frac{1}{2}S = \frac{1}{4} + \frac{2}{8} + \dots$
- Subtracting: $\frac{1}{2}S = \frac{1}{2} + \frac{1}{4} + \frac{1}{8} + \dots = 1 \implies \mathbf{S = 2}$.
- Total work $T(n) \le n \sum_{h=1}^\infty \frac{h}{2^h} = 2n \implies \mathbf{T(n) = \Theta(n)}$.

---

## 3. Python Functional Programming & Closures (Lectures 13–14)

### Closures: Default Binding vs Late Binding
```python
# 1. Eager / Definition-time binding (Fixes the loop trap)
funcs = [lambda x, s=step: x + s for step in [1, 2, 3]]
# funcs[0](10) -> 11, funcs[1](10) -> 12, funcs[2](10) -> 13

# 2. Late binding / Lexical cell lookup (The loop trap)
late_funcs = [lambda x: x + step for step in [1, 2, 3]]
# All lambdas look up 'step' when called. Loop finished at step = 3!
# late_funcs[0](10) -> 13, late_funcs[1](10) -> 13, late_funcs[2](10) -> 13
```

### Pipelines with `reduce`
$$\text{reduce}(f, [f_1, f_2, f_3], x) = f_3(f_2(f_1(x)))$$

---

## 4. Concurrency from Slides (Lectures 15–16)

### Processes vs Threads
- **Process**: Private virtual memory, OS-isolated, heavy context switch.
- **Thread**: Shared heap/globals, lightweight, fast, but vulnerable to **race conditions**.

### Race Condition & Lost Updates
- Even `balance += 10` is 3 bytecode instructions: `LOAD_FAST` $\to$ `INPLACE_ADD` $\to$ `STORE_FAST`.
- A context switch between read and write causes another thread's update to be overwritten!

### Critical Section & `threading.Lock()`
- Protect shared access: `with lock: balance += amt`.
- **Contention**: Threads waiting in line degrades performance.
- **Deadlock**: Two threads acquire two locks in reverse order:
  - $T_1$: `with L1: with L2:`
  - $T_2$: `with L2: with L1:`
  - **Prevention**: Global lock ordering (all threads acquire $L_1$ before $L_2$).

### Beyond Locks
1. **Functional Programming**: Immutability $\implies$ zero shared mutable state $\implies$ thread-safe. Parallel computation via `multiprocessing.Pool().map()` (`parallel_sum`).
2. **Actor Model**: Private state + message queues (mailboxes). Threads send messages; actor processes them sequentially with **zero locks and zero race conditions**.
