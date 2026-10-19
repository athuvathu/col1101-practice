# COL1101 Quiz 2: High-Yield Comprehensive Quick Study Sheet

> **Syllabus Coverage**: Lectures 12–21 (Functional Programming, Concurrency, Binary Trees, ACBT/CBT, Binary Heaps, Fast Build Heap, HeapSort) + IEEE 754 Floating Point + COL1000 Core Foundations.

---

## 1. Binary Trees, CBT, and ACBT (Lectures 17–18)

### Exact IIT Delhi Definitions & Height Conventions
- **Depth of a Node $v$**: The distance (number of edges) on the path from the root to $v$. Root has depth $0$.
- **Height $h$ of a Tree**: The number of **levels / nodes** on the longest root-to-leaf path:
  $$h = 1 + \max_{v \in T} \text{depth}(v) \quad (h \ge 1 \text{ for non-empty trees}; \quad h = 0 \text{ for empty tree})$$
  *(Note: Be careful! Some standard textbooks define height by edges, but in COL1101 slides L17–L19, height is explicitly the number of levels!)*
- **Complete Binary Tree (CBT)**:
  - All levels $l \in \{0, 1, \dots, h-2\}$ have exactly $2^l$ nodes (both children exist for every node).
  - All nodes at level $h-1$ are leaves.
  - Number of nodes in CBT of height $h$:
    $$n = 1 + 2 + 4 + \dots + 2^{h-1} = 2^h - 1$$
- **Almost Complete Binary Tree (ACBT)**:
  - Every level $l \in \{0, 1, \dots, h-2\}$ is completely full ($2^l$ nodes).
  - All nodes at bottom level $h-1$ are packed as far to the left as possible.
  - Node count range for ACBT of height $h$:
    $$2^{h-1} \le n \le 2^h - 1 \quad \iff \quad 2^{h-1} \le n < 2^h$$
  - Exact height formula given $n$ nodes:
    $$h = \lfloor \log_2 n \rfloor + 1$$

### Array Representation Formulas (0-Indexed)
An ACBT with $n$ nodes is mapped into array $A[0 \dots n-1]$ in level-order traversal order:
| Relationship | Array Index Formula | Condition |
| :--- | :--- | :--- |
| **Parent of node $i$** | $\lfloor (i - 1) / 2 \rfloor$ | $i > 0$ (root has no parent) |
| **Left Child of node $i$** | $2i + 1$ | $2i + 1 < n$ (else no left child) |
| **Right Child of node $i$** | $2i + 2$ | $2i + 2 < n$ (else no right child) |
| **Internal Nodes Range** | $0 \le i \le \lfloor n/2 \rfloor - 1$ | Indices with at least one child |
| **Leaf Nodes Range** | $\lfloor n/2 \rfloor \le i \le n - 1$ | Indices with no children ($2i + 1 \ge n$) |

### Level-Order Traversal (LOT) & Queue Invariant (L18)
- **LOT Algorithm**: Initialize FIFO queue with root. In a loop, dequeue node $x$, visit $x$, and enqueue $x$'s left then right children (if non-None).
- **Queue Loop Invariant**: If node $x$ at depth $d$ is at the front of the queue, the queue consists of:
  1. Node $x$, followed by
  2. All unvisited nodes at level $d$ to the right of $x$ (left-to-right), followed by
  3. The children of all nodes at level $d$ to the left of $x$ (which are at depth $d+1$, left-to-right).
- **Two-Depth Property**: Every node currently inside the queue is at depth $d$ or $d+1$.

---

## 2. Binary Min-Heaps & Fast Heap Operations (Lectures 19–21)

### Min-Heap Definition
A binary min-heap is a binary tree $T$ satisfying:
1. **Structural Property**: $T$ is an Almost Complete Binary Tree (ACBT).
2. **Min-Heap Order Property**: For every node $v \ne \text{root}$, $A[\text{parent}(v)] \le A[v]$.

### Candidate Positions for the $k$-th Smallest Element
In a min-heap with $n$ distinct elements:
- **Root (depth 0)**: Exclusively holds the 1st smallest element.
- **Depth 1 (indices 1, 2)**: Can hold the 2nd or 3rd smallest element.
- **Depth 2 (indices 3, 4, 5, 6)**: Can hold the 3rd, 4th, 5th, 6th, or 7th smallest element.
- **Theorem**: A node at depth $d$ has $d$ distinct ancestors. Since every ancestor is strictly smaller, any node at depth $d$ is at best the $(d+1)$-th smallest element.
  - Therefore, the **3rd smallest** element can only appear at **depth 1 or depth 2** (indices $\{1, 2, 3, 4, 5, 6\}$). It can **never** appear at depth $\ge 3$.

### Core Operations & Time Complexities
| Operation | Description | Worst-Case Time |
| :--- | :--- | :--- |
| `find_min()` / `peek()` | Return $A[0]$ | $\Theta(1)$ |
| `heap_up(i)` / Sift-Up | Swap with parent while $A[\text{parent}] > A[i]$ | $O(\text{depth}(i)) = O(\log n)$ |
| `insert(x)` | Append $x$ at $A[n]$, increment size, `heap_up(n-1)` | $O(\log n)$ |
| `heap_down(i)` / Sift-Down | Swap with smallest child while $A[i] > A[\text{smallest\_child}]$ | $O(\text{height}(i)) = O(\log n)$ |
| `extract_min()` | Swap $A[0]$ with $A[n-1]$, pop, `heap_down(0)` | $O(\log n)$ |
| `fast_build_min_heap(A)` | Bottom-up sift-down for $i = \lfloor n/2 \rfloor - 1$ down to 0 | $\mathbf{\Theta(n)}$ (Linear!) |
| `heap_sort(A)` (In-Place) | Build Max-Heap in $O(n)$, repeatedly swap root with end and sift-down | $\mathbf{\Theta(n \log n)}$ time, $O(1)$ space |

### Fast Build-Heap: The AGP Summation Proof
Naive insertion takes $\sum_{i=1}^n O(\log i) = \Theta(n \log n)$. Bottom-up fast build heap takes $\Theta(n)$:
1. Number of nodes at height $h$ is at most $\lceil \frac{n}{2^{h+1}} \rceil$.
2. Work done on each node of height $h$ is at most $c \cdot h$.
3. Total work:
   $$T(n) \le \sum_{h=1}^{\lfloor \log_2 n \rfloor} \left\lceil \frac{n}{2^{h+1}} \right\rceil c \cdot h \le \frac{c \cdot n}{2} \sum_{h=1}^{\infty} \frac{h}{2^h}$$
4. **Solving the AGP**: Let $S = \sum_{h=1}^\infty \frac{h}{2^h}$:
   $$S = \frac{1}{2^1} + \frac{2}{2^2} + \frac{3}{2^3} + \frac{4}{2^4} + \dots$$
   $$\frac{1}{2}S = \frac{1}{2^2} + \frac{2}{2^3} + \frac{3}{2^4} + \dots$$
   Subtracting:
   $$\frac{1}{2}S = \frac{1}{2^1} + \frac{1}{2^2} + \frac{1}{2^3} + \dots = \sum_{k=1}^\infty \frac{1}{2^k} = \frac{1/2}{1 - 1/2} = 1 \implies \mathbf{S = 2}$$
5. Substituting $S = 2$:
   $$T(n) \le \frac{c \cdot n}{2} \cdot 2 = c \cdot n = \mathbf{\Theta(n)}$$

---

## 3. Functional Programming & Python Closures (Lectures 12–14, Lab 5)

### Core FP Principles
- **Immutability**: Data structures are never mutated in-place; state transformations return new instances.
- **Structural Sharing**: Unmodified substructures are shared between old and new versions (e.g. `Cell(customer, rest)` in `lab/qfpw5.py`).
- **Higher-Order Functions**: Functions that take functions as arguments or return functions (`map`, `filter`, `reduce`).
- **Fold / Reduce**:
  $$\text{reduce}(f, [x_1, x_2, \dots, x_k], s_0) = f(\dots f(f(s_0, x_1), x_2) \dots, x_k)$$

### The Python Closure Pitfall: Late Binding vs Default Parameter Binding
```python
# PITFALL: Late Binding (Captures variable by reference in cell object)
funcs = [lambda x: x + i for i in [2, 3, 5]]
# When funcs[0](10) is called, loop is done and i = 5!
# funcs[0](10) -> 10 + 5 = 15 (NOT 10 + 2!)

# FIX: Early Binding via Default Argument (Evaluated at definition time)
funcs_fixed = [lambda x, i=i: x + i for i in [2, 3, 5]]
# funcs_fixed[0](10) -> 10 + 2 = 12
```
- **Execution Mechanism**:
  - Without default arguments, `i` is stored as a free variable in a `cell` object inside `fn.__closure__`. All closures created in the loop point to the **same cell**, which reflects the variable's final value when the loop exits.
  - With default argument `i=i`, Python evaluates `i` during function definition time and binds the evaluated integer directly into `fn.__defaults__`.

---

## 4. Concurrency, Race Conditions & Deadlocks (Lectures 15–16)

### Key Contrasts: Process vs Thread
- **Process**: Independent execution environment with its own private virtual memory address space. Expensive IPC (pipes, sockets, shared memory).
- **Thread**: Light-weight execution unit within a process. Shares heap, global variables, and file descriptors with peer threads. Has private stack and registers.

### Concurrency Hazards
- **Race Condition**: A semantic flaw where the correctness of output depends on non-deterministic thread interleaving or scheduling.
- **Data Race**: Low-level unsynchronized concurrent access where at least two threads access the same memory location, at least one access is a write, and no happens-before synchronization exists.
- **Critical Section**: A block of code accessing shared mutable state that must not be concurrently executed by more than one thread.

### The 4 Coffman Deadlock Conditions
A deadlock can occur if and only if all four conditions hold:
1. **Mutual Exclusion**: Resources cannot be simultaneously shared.
2. **Hold and Wait**: A process holding resources can request new resources without releasing what it holds.
3. **No Preemption**: Resources cannot be forcibly taken from a holding process.
4. **Circular Wait**: A closed loop of threads exists where each waits for a resource held by the next.

### Havender's Resource Ordering Protocol
- Impose a strict total order $\prec$ on all lock identifiers ($L_1 \prec L_2 \prec \dots \prec L_m$).
- **Rule**: A thread may acquire lock $L_j$ only if $L_i \prec L_j$ for all locks $L_i$ currently held by that thread.
- **Proof of Deadlock Freedom**:
  If a cycle existed: $L_{a_1} \prec L_{a_2} \prec \dots \prec L_{a_k} \prec L_{a_1}$. By transitivity, $L_{a_1} \prec L_{a_1}$, contradicting irreflexivity of strict orders. Thus Circular Wait is impossible.

### Python Global Interpreter Lock (GIL) & FP Parallelism
- **CPython GIL**: A mutex protecting CPython internal memory management (`ob_refcnt`). Prevents multiple native threads from executing Python bytecodes simultaneously on multiple CPU cores.
- **CPU-bound parallelism**: Standard threads do NOT achieve multi-core speedup. Use **Functional Programming Parallelism** via `multiprocessing.Pool().map`:
  ```python
  from multiprocessing import Pool

  def pure_task(x):
      return x * x  # Pure function: deterministic, no shared side-effects

  with Pool() as pool:
      results = pool.map(pure_task, [1, 2, 3, 4, 5])
  ```
  - **FP Invariance**: Because pure functions do not mutate shared state, parallel chunks require zero locks or mutexes, completely eliminating race conditions, deadlocks, and lock contention.
  - Separate worker processes each possess their own private address space and independent GIL, achieving linear multi-core speedup.

### High-Level Concurrency Paradigms: Actor Model vs CSP
| Dimension | Actor Model (Erlang, Akka) | CSP (Go Channels) | Shared Memory (Threads + Mutex) |
| :--- | :--- | :--- | :--- |
| **Primary Unit** | **Actor** (Autonomous Entity) | **Channel** (Anonymous Pipe) | Memory Address / Shared Variable |
| **Addressing** | Explicit: Recipient Actor PID / Address | Anonymous: Read/Write to Channel | Shared Pointer / Reference |
| **State Sharing** | **Zero shared state** (Private mailbox) | **Zero shared state** (Message passing) | Shared mutable memory |
| **Synchronization** | Asynchronous message queues (Mailbox) | Synchronous rendezvous (or buffered) | Locks, Semaphores, Condition Variables |
| **Failure Handling** | Supervision Trees ("Let It Crash") | Manual error propagation over channels | Unhandled exceptions crash whole process |

#### The 3 Axioms of Actor Computation (Carl Hewitt & Gul Agha)
An **Actor** encapsulates private state, behavior, and a message queue (mailbox). Upon processing a message, an actor can execute only three fundamental actions:
1. **Send** a finite number of messages to other actors whose addresses it knows.
2. **Create** a finite number of new actors.
3. **Designate** the replacement behavior (state update) to be used for the next incoming message.

---

## 5. In-Place HeapSort & Complete Binary Tree Invariants (Lecture 21)

### In-Place HeapSort Algorithm
```python
def heapsort(A):
    # Step 1: Build max-heap bottom-up in O(n) time
    fast_build_max_heap(A)
    
    # Step 2: Extract elements from right to left
    for i in range(len(A) - 1, 0, -1):
        # Swap root (current maximum) with end of unsorted region
        A[0], A[i] = A[i], A[0]
        # Restore max-heap on reduced range A[0 ... i-1]
        max_heap_down(A, 0, i)
```

### Invariants & Complexity
- **Loop Invariant**: At the start of iteration $i$:
  1. $A[0 \dots i]$ is a valid Max-Heap containing the $i+1$ smallest elements.
  2. $A[i+1 \dots n-1]$ contains the $n - 1 - i$ largest elements in **sorted ascending order**.
  3. Every element in $A[0 \dots i] \le$ every element in $A[i+1 \dots n-1]$.
- **Time Complexity**:
  - Build Heap: $\Theta(n)$ time.
  - Sift-Down loop: $\sum_{i=1}^{n-1} O(\log i) = \Theta(n \log n)$ time.
  - Total Time: $\mathbf{\Theta(n \log n)}$ worst, average, and best case.
- **Space Complexity**: $\mathbf{O(1)}$ auxiliary space (in-place).

---

## 6. Exam Quick-Reference Summary for Quiz 2

| Topic | Key Lecture | Core Rules & Formulas to Remember |
| :--- | :--- | :--- |
| **Tree Height ($h$)** | L17–18 | **Number of levels** ($h \ge 1$ for non-empty; $h = \lfloor \log_2 n \rfloor + 1$). Empty tree $h = 0$. |
| **CBT Nodes** | L18 | $n = 2^h - 1$. All levels $0 \dots h-2$ full, level $h-1$ leaves. |
| **ACBT Bounds** | L18 | $2^{h-1} \le n \le 2^h - 1$. |
| **Heap Array Mapping** | L19 | Left child: $2i + 1$, Right child: $2i + 2$, Parent: $\lfloor (i-1)/2 \rfloor$. |
| **Heap Node Ranges** | L19 | Internals: $[0, \lfloor n/2 \rfloor - 1]$, Leaves: $[\lfloor n/2 \rfloor, n - 1]$. |
| **3rd Smallest in Min-Heap** | L19–20 | Node at depth $d$ has $d$ ancestors $\implies$ 3rd smallest must be at **depth 1 or 2** (indices 1 to 6). |
| **Fast Build Heap** | L21 | Bottom-up sift-down: $\sum_{h=1}^\infty \frac{h}{2^h} = 2 \implies \mathbf{\Theta(n)}$ linear time! |
| **Closures & Late Binding** | L13–14 | `lambda x: x + i` looks up $i$ late (takes final loop value). Fix: `lambda x, s=i: x + s` binds default eager at definition. |
| **Processes vs Threads** | L15 | Processes = separate memory (safe, heavy). Threads = shared memory (fast, race conditions). |
| **Race Condition** | L15 | Concurrent unsynchronized read/write to shared state. Fix with `with threading.Lock():`. |
| **Lock Pitfalls** | L16 | **Contention** (serialization slowdown) & **Deadlock** (circular wait with reverse lock ordering). |
| **Beyond Locks** | L16 | **FP** (immutability + `multiprocessing.Pool().map`) & **Actor Model** (private state + mailbox queues). |
