# COL1101 Quiz 2: Key Conceptual Insights & Problem Solving Guide

> **Purpose:** Deep dive into the intuition, core theorems, and elegant patterns behind the Creative Quiz 2 exam.

---

## 1. Min-Max Heap Duality & Subtree Rank Constraints

### Insight 1: Subtree Size Imposes Absolute Rank Bounds
In an ACBT, knowing the position of a node immediately restricts its rank (its position in sorted order):
- Let $D(v)$ be the number of descendants of node $v$ (including $v$).
- Let $A(v)$ be the number of ancestors of node $v$ (excluding $v$).
- Total tree size is $n$.

In a **Binary Min-Heap**:
1. All $A(v)$ ancestors are strictly smaller than $v$.
   $$\text{rank}(v) \ge A(v) + 1$$
2. All $D(v) - 1$ proper descendants are strictly larger than $v$.
   $$\text{rank}(v) \le n - (D(v) - 1)$$

Putting both together:
$$A(v) + 1 \le \text{rank}(v) \le n - D(v) + 1$$

#### Applied to Node 1 in Size $n = 7$:
- Node 1 has 1 ancestor (root, node 0) $\implies A(1) = 1$.
- Node 1 has 2 descendants (nodes 3, 4) plus itself $\implies D(1) = 3$.
- In Min-Heap:
  $$1 + 1 \le \text{rank}(H_1[1]) \le 7 - 3 + 1 \implies \mathbf{2 \le \text{rank}(H_1[1]) \le 5}$$
- In Max-Heap (all inequalities flip):
  - Descendants are smaller, ancestors are larger!
  $$D(1) \le \text{rank}(H_2[1]) \le n - A(1) \implies 3 \le \text{rank}(H_2[1]) \le 7 - 1 \implies \mathbf{3 \le \text{rank}(H_2[1]) \le 6}$$
- **The Intersection**:
  $$\{2, 3, 4, 5\} \cap \{3, 4, 5, 6\} = \mathbf{\{3, 4, 5\}}$$
  Any value with rank 3, 4, or 5 (e.g. value 4) can simultaneously sit at index 1 in both a min-heap and a max-heap!

---

### Insight 2: The Extreme Element Leaf Theorem
- **Theorem**: In any binary max-heap, the **minimum element** must reside at a **leaf node**.
- **Proof**: Suppose the minimum element $m$ resided at an internal node $u$. By definition of an internal node, $u$ has at least one child $v$. In a max-heap, $A[u] > A[v]$, which means $m > A[v]$. This contradicts the fact that $m$ is the minimum element! Thus, $m$ cannot be an internal node; it must be a leaf.
- **Consequence for 1(b)**: In a size-7 heap, node 2 has children at indices 5 and 6, so it is an internal node. Therefore, node 2 in a max-heap can **never** hold the minimum element 1 ($H_2[2] \ne 1$). Since $H_1[0] = 1$, $H_1[0] = H_2[2]$ is impossible!

---

## 2. Python Closures: Under the Hood in CPython

### Why `late_rules` produces 125 instead of 360
When Python compiles a function containing closures:
1. **Eager Default Arguments (`lambda x, rate=r: ...`)**:
   - Evaluated **once**, at definition time.
   - The evaluated value is stored in the function's `__defaults__` tuple.
   - Subsequent changes to `r` have zero effect on the function.
2. **Late-Binding Free Variables (`lambda x: ... r ...`)**:
   - Python does NOT store the value of `r`.
   - Instead, the compiler marks `r` as a cell variable in the enclosing frame.
   - All lambdas created in that loop receive a reference to the **exact same cell object**:
     `lambda_fn.__closure__[0]` $\to$ points to the heap cell of `r`.
   - When the lambdas are called later, they dereference the cell, which now holds the terminal loop value (`r = 50`).
   - Hence, every stage applies a 50% discount ($1000 \to 500 \to 250 \to 125$).

---

## 3. Concurrency: The Deadlock Elimination Invariant

### Why Reverse Locking Deadlocks
When Thread 1 executes `with L_A: with L_B:` and Thread 2 executes `with L_B: with L_A:`, they create a dependency graph:
$$T_1 \to L_B \to T_2 \to L_A \to T_1$$
This is a **directed cycle** (Circular Wait).

### The Mathematical Fix: Havender's Total Ordering
If we assign every lock an integer priority (e.g. `id(lock)`):
$$L_{\text{low}} = \min(L_1, L_2), \quad L_{\text{high}} = \max(L_1, L_2)$$
Every thread is forced to acquire $L_{\text{low}}$ before $L_{\text{high}}$.
- Thread 1 attempts to acquire $L_{\text{low}}$.
- Thread 2 also attempts to acquire $L_{\text{low}}$.
- One thread wins and gets $L_{\text{low}}$; the other blocks *before* holding any lock!
- A cycle requires at least one thread to hold a higher lock while waiting for a lower lock. Because no thread can ever request a lower lock after acquiring a higher lock, **cycles are mathematically impossible**.

---

## 4. Fast Build Heap: Why Bottom-Up is $O(n)$ while Top-Down is $O(n \log n)$

### The Intuition: Where is the Heavy Work Done?
In an Almost Complete Binary Tree:
- **Top-Down (Repeated `insert`)**:
  - Elements are inserted at the leaves and sift up to the root.
  - Sifting up takes work proportional to the **depth** of the node.
  - Most nodes ($\approx n/2$) are at the bottom (depth $\approx \log_2 n$).
  - Thus, the majority of nodes perform maximum work ($O(\log n)$):
    $$\frac{n}{2} \times \log_2 n = \Theta(n \log n)$$
- **Bottom-Up (`fast_build_min_heap`)**:
  - Elements are sifted **down** towards the leaves.
  - Sifting down takes work proportional to the **height** of the node (distance to leaf).
  - Most nodes ($\approx n/2$) are leaves with **height 0** (0 comparisons!).
  - Next level has $\approx n/4$ nodes with **height 1** (1 comparison).
  - Only **1 node** (the root) has height $\log_2 n$!
  - The heavy work is done by the fewest nodes:
    $$T(n) \approx \sum_{h=1}^\infty \frac{n}{2^{h+1}} \cdot 2h = n \sum_{h=1}^\infty \frac{h}{2^h} = n \cdot 2 = \mathbf{\Theta(n)}$$
