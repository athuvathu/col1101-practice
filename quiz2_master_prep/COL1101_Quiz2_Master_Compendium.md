# COL1101 (Data Structures and Algorithms) — Quiz 2 Master Compendium
## Comprehensive Theoretical Treatise, Formal Proofs, Execution Mechanics, and Exam Arsenal
### Academic Year: Spring Semester | Post-Quiz 1 Syllabus (Lectures 12 to 21)

---

## Table of Contents
1. [Curriculum Architecture & Scope Delimitation](#1-curriculum-architecture--scope-delimitation)
2. [Functional Programming & CPython Execution Mechanics](#2-functional-programming--cpython-execution-mechanics)
3. [Concurrency Theory Grounded in Lecture Slides](#3-concurrency-theory-grounded-in-lecture-slides)
4. [Binary Trees, CBT, ACBT, & Traversal Invariants](#4-binary-trees-cbt-acbt--traversal-invariants)
5. [Binary Heaps, Array Topology, & Rank Analysis](#5-binary-heaps-array-topology--rank-analysis)
6. [Fast Build Heap, Invariant Induction, & AGP Summation Proof](#6-fast-build-heap-invariant-induction--agp-summation-proof)
7. [In-Place HeapSort & Priority Queue Applications](#7-in-place-heapsort--priority-queue-applications)
8. [Authentic Practice Exam 1 (IIT Delhi Rubric Fidelity)](#8-authentic-practice-exam-1-iit-delhi-rubric-fidelity)
9. [Creative Practice Exam 2 (Advanced Duality & Edge Cases)](#9-creative-practice-exam-2-advanced-duality--edge-cases)
10. [Diagnostic Pitfall Guide & 10 Lethal Exam Traps](#10-diagnostic-pitfall-guide--10-lethal-exam-traps)

---

# 1. Curriculum Architecture & Scope Delimitation

### Exact Course Context
In the IIT Delhi COL1101 (Data Structures and Algorithms) curriculum, **Quiz 1** evaluated fundamental mathematical foundations, asymptotic analysis, basic ADTs (Stacks, Queues, Linked Lists), Object-Oriented Programming (MRO, `super()`, inheritance), and recursive loop invariants.

**Quiz 2** tests the curriculum immediately following Quiz 1, spanning **Lectures 12 through 21**:
* **Lecture 12**: Functional Programming Foundations — Pure functions, Referential Transparency, Immutability, Higher-Order Functions, Closures, and Lexical Scoping.
* **Lecture 13**: Advanced FP, Sequences & Pipelines — Currying, Partial Application, Iterators, Generators, Lazy Evaluation, `map`, `filter`, and `reduce`.
* **Lecture 14**: Persistent Data Structures & Tail Recursion — Structural sharing, cons lists, persistent list operations, and tail-call optimization principles.
* **Lecture 15**: Concurrency Foundations — Process vs. Thread distinction, Address space virtualization, Shared memory hazards, Race conditions, Check-Then-Act flaws (Bank Account withdrawal), and Unsynchronized Counter increments.
* **Lecture 16**: Synchronization Primitives & Alternative Paradigms — Critical Sections, Mutual Exclusion, `threading.Lock()`, Context Managers (`with lock:`), Lock contention bottlenecks, Deadlock (Coffman conditions and circular wait cycles), Havender Lock Ordering, FP Parallelism (`multiprocessing.Pool`), and the Actor Model (isolated state with message mailboxes).
* **Lecture 17**: Binary Trees, CBT, and ACBT — Formal recursive definition, tree height convention ($h = \text{number of levels}$), Complete Binary Trees ($n = 2^h - 1$), and Almost Complete Binary Trees ($2^{h-1} \le n \le 2^h - 1$).
* **Lecture 18**: Tree Traversals & Level-Order Queue Invariants — DFS (Pre, In, Post-order), BFS / Level-Order Traversal (LOT), Two-Level Queue Invariant, and Array embedding of Complete Binary Trees.
* **Lecture 19**: Binary Heaps & Priority Queues — Min-Heap and Max-Heap invariants, 0-indexed vs. 1-indexed array mapping, leaf and internal node index bounds, and $k$-th smallest candidate rank analysis.
* **Lecture 20**: Heap Dynamic Operations — Sift-Up (`bubble_up`) in $O(\log n)$, Sift-Down (`bubble_down`) in $O(\log n)$, `insert()`, `extract_min()`, and `decrease_key()`.
* **Lecture 21**: Fast Build Heap & HeapSort — $\Theta(n)$ Bottom-Up construction, formal Inductive Loop Invariant proof (requiring strict inequalities), Well-founded termination metric, AGP Summation proof ($\sum h/2^h = 2$), and In-place HeapSort.

> [!IMPORTANT]
> **Strict Boundary Directive**:
> 1. **IEEE 754 Floating-Point Arithmetic is NOT in the syllabus** and is completely omitted from this compendium.
> 2. **Concurrency is strictly bounded to the lecture slides (Lec 15 & 16)**. Advanced graduate operating system topics (e.g., MESI cache coherence, Peterson SC proofs, TSO hardware memory reordering, Herlihy consensus hierarchy, lock-free Treiber stacks) are omitted. Concurrency analysis adheres strictly to CPython threads/processes, race conditions, locks, deadlock cycles, FP multiprocessing, and the Actor model.

---

# 2. Functional Programming & CPython Execution Mechanics

## 2.1 Core Pillars of Functional Programming
1. **Pure Functions**: A function $f: X \to Y$ is pure if and only if:
   * **Determinism**: For any identical input $x$, $f(x)$ always yields identical output $y$.
   * **No Side Effects**: Evaluation of $f(x)$ causes zero observable mutation of external program state (no global variable mutation, no I/O, no in-place modification of arguments).
2. **Referential Transparency**: An expression $e$ is referentially transparent if it can be replaced with its evaluated value without altering program behavior:
   $$\forall x, \quad g(f(x), f(x)) \equiv \text{let } v = f(x) \text{ in } g(v, v)$$
3. **Immutability & Structural Sharing**: Rather than modifying an existing object in place, operations return a new object referencing unmodified subcomponents of the original structure.

## 2.2 Closures, Lexical Scope, and the CPython Cell Mechanism
A **closure** is a first-class function paired with an environment binding of its free variables (variables referenced in the function body that are neither local parameters nor global).

### The CPython Scoping Resolution Order (LEGB Rule)
CPython searches for variable bindings in four strict scopes:
1. **L (Local)**: Defined within the current function body (`STORE_FAST`).
2. **E (Enclosing / Nonlocal)**: Defined in outer nested function scopes (`LOAD_DEREF`).
3. **G (Global)**: Defined at module root level (`LOAD_GLOBAL`).
4. **B (Built-in)**: Standard Python built-ins (`range`, `len`, `sum`, etc.).

### Why Loops with Lambdas Create Late-Binding Traps
Consider the classic interview and exam trap:
```python
# Late binding (Closure Trap)
funcs = [lambda x: x + step for step in [1, 2, 3]]
print([f(10) for f in funcs])  # Prints: [13, 13, 13], NOT [11, 12, 13]!
```

#### Under the Hood: The CPython Cell Object
When CPython compiles a function referencing an enclosing variable (`step`), it creates a **closure cell** (`PyCellObject`).
* The lambda's code object contains `co_freevars = ('step',)`.
* Each of the three lambda functions in `funcs` receives a reference to the **exact same cell object** in memory (`f.__closure__[0]`).
* The `for step in [1, 2, 3]` loop mutates the contents of this single cell. When the loop terminates, `cell_contents` is `3`.
* When `f(10)` is invoked later, CPython executes `LOAD_DEREF(step)`. It dereferences the cell at call time, reading `3`.
* Hence:
  $$\forall i \in \{0, 1, 2\}, \quad \text{funcs}[i](10) = 10 + 3 = 13$$

### The Canonical Fix: Eager Binding via Parameter Defaults
```python
# Eager binding (Parameter Default)
funcs_fixed = [lambda x, s=step: x + s for step in [1, 2, 3]]
print([f(10) for f in funcs_fixed])  # Prints: [11, 12, 13]
```
#### Why this works:
* Function parameter defaults (`__defaults__`) are evaluated **once at definition time**, when the `def` or `lambda` expression is executed.
* In iteration 1: `step = 1` $\implies$ default `s = 1` stored in `funcs_fixed[0].__defaults__ = (1,)`.
* In iteration 2: `step = 2` $\implies$ default `s = 2` stored in `funcs_fixed[1].__defaults__ = (2,)`.
* In iteration 3: `step = 3` $\implies$ default `s = 3` stored in `funcs_fixed[2].__defaults__ = (3,)`.
* When called without a second argument (`f(10)`), Python binds `s` to the pre-stored default integer in `__defaults__`.

## 2.3 Higher-Order Pipelines & Function Composition
Functions that take functions as arguments or return functions are **higher-order functions**.
* `map(fn, iterable)`: Computes $[fn(x_0), fn(x_1), \dots]$.
* `filter(predicate, iterable)`: Selects elements where $predicate(x) \equiv \text{True}$.
* `functools.reduce(fn, iterable, initial)`: Folds a sequence left-to-right:
  $$\text{reduce}(f, [x_1, x_2, x_3], x_0) = f(f(f(x_0, x_1), x_2), x_3)$$

### Pipeline Composition with `reduce`
```python
from functools import reduce

pipeline = lambda x, fns: reduce(lambda acc, f: f(acc), fns, x)
```
If $fns = [f_1, f_2, f_3]$, then:
$$\text{pipeline}(x, [f_1, f_2, f_3]) = f_3(f_2(f_1(x)))$$

---

# 3. Concurrency Theory Grounded in Lecture Slides

*All concepts in this section are strictly derived from Lectures 15 and 16.*

## 3.1 Processes vs. Threads
Operating systems provide two distinct execution abstractions:

| Dimension | Process | Thread |
| :--- | :--- | :--- |
| **Definition** | An independent executing program instance with its own virtual address space. | An independent unit of execution *within* a process. |
| **Address Space** | **Isolated**: Separate code, data, heap, and file descriptors. Cannot access another process's memory directly. | **Shared**: All threads in a process share the exact same address space (heap, global variables, open files). Each thread has its own private execution stack and registers. |
| **Overhead** | Heavyweight: High creation time and substantial context-switch cost (page table swapping, TLB flush). | Lightweight: Low creation time and fast context switching. |
| **Communication** | Requires Inter-Process Communication (IPC): pipes, sockets, shared memory segments, or message passing. | Directly via shared variables in the heap (fast, but hazardous). |
| **Crash Isolation** | High: One process crashing does not crash neighboring processes. | Low: An uncaught fatal exception or segmentation fault in one thread terminates the entire process. |

### Python Threading API (`threading` module)
```python
import threading

def worker(task_id, iterations):
    for _ in range(iterations):
        pass

# Instantiating threads
t1 = threading.Thread(target=worker, args=(1, 1000))
t2 = threading.Thread(target=worker, args=(2, 1000))

t1.start()  # Spawns thread and begins execution
t2.start()

t1.join()   # Caller blocks until t1 terminates
t2.join()   # Caller blocks until t2 terminates
```

## 3.2 Shared Memory & Race Conditions
A **race condition** occurs when the outcome of a concurrent program depends non-deterministically on the uncontrollable order of thread interleaving and scheduling.

### Trap 1: The ATM / Shared Bank Account Check-Then-Act Flaw
From Lecture 15, consider two ATM terminals concurrently withdrawing from a shared bank account:
```python
# Shared state: account_balance = 100
def withdraw(amount):
    global account_balance
    if account_balance >= amount:        # Step 1: Check
        # Context switch / preemption occurs here!
        time.sleep(0.0001)
        account_balance -= amount        # Step 2: Act
```
#### Interleaving Trace Leading to Account Overdraft:
Suppose `account_balance = 100`. Thread 1 attempts to withdraw $80, and Thread 2 attempts to withdraw $70:

```
Thread 1 (Withdraw 80)               Thread 2 (Withdraw 70)           Shared Balance
-------------------------------------------------------------------------------------
1. Check: 100 >= 80 (True)                                            100
   [Thread 1 preempted]
                                      2. Check: 100 >= 70 (True)      100
                                      3. Act: balance = 100 - 70      30
   [Thread 1 resumes]
4. Act: balance = 30 - 80                                             -50 (OVERDRAFT!)
```
**Diagnostic**: The gap between the **check** (`balance >= amount`) and the **act** (`balance -= amount`) creates a race condition window where invariant validity is violated.

### Trap 2: Unsynchronized Counter Increment (`counter += 1`)
Even a single Python line `counter += 1` is **not atomic**. At the CPython bytecode level, it is compiled into three distinct instructions:
1. `LOAD_GLOBAL (counter)`: Read current value from heap into thread's local eval stack.
2. `BINARY_OP (+ 1)`: Add 1 to the top-of-stack value.
3. `STORE_GLOBAL (counter)`: Write the result back to heap.

#### Interleaving Causing Lost Update:
Suppose `counter = 0`:
```
Thread A                              Thread B                        Heap counter
----------------------------------------------------------------------------------
1. LOAD_GLOBAL (reads 0)                                              0
                                      2. LOAD_GLOBAL (reads 0)        0
                                      3. BINARY_OP (0 + 1 = 1)        0
                                      4. STORE_GLOBAL (writes 1)      1
5. BINARY_OP (0 + 1 = 1)                                              1
6. STORE_GLOBAL (writes 1)                                            1 (LOST UPDATE!)
```
Both threads executed `counter += 1`, but the final value is `1` instead of `2`!

## 3.3 Critical Sections & Mutual Exclusion
A **Critical Section** is a code segment that accesses shared mutable state and must not be concurrently executed by more than one thread at any given time.

### Mutual Exclusion via `threading.Lock()`
A Lock (Mutex) has two states: `unlocked` and `locked`.
* `lock.acquire()`: If unlocked, sets state to locked and returns immediately. If locked, blocks the calling thread until another thread releases it.
* `lock.release()`: Sets state to unlocked and wakes up a blocked thread.

### Idiomatic Context Manager (`with lock:`)
```python
account_lock = threading.Lock()

def safe_withdraw(amount):
    global account_balance
    with account_lock:  # Automatically acquires on enter, releases on exit (even on exception!)
        if account_balance >= amount:
            account_balance -= amount
            return True
        return False
```

## 3.4 The Two Main Pitfalls of Locking
As identified in Lecture 16:
1. **Contention & Performance Degradation**:
   Coarse-grained locking forces threads to wait sequentially in line. If threads spend the majority of their time waiting for a single global lock, parallel execution collapses to sequential execution, incurring context-switching overhead without throughput gains.
2. **Deadlock**:
   A state where two or more threads are permanently blocked, each waiting for a lock held by the other.

### The Canonical 2-Lock Deadlock Trace
Consider two locks, $L_1$ and $L_2$, and two accounts:
```python
# Thread 1: Transfer from Account A to B
def transfer_1():
    with lockA:              # Acquires lockA successfully
        time.sleep(0.001)    # Context switch!
        with lockB:          # Blocked: lockB is held by Thread 2!
            perform_transfer()

# Thread 2: Transfer from Account B to A
def transfer_2():
    with lockB:              # Acquires lockB successfully
        time.sleep(0.001)    # Context switch!
        with lockA:          # Blocked: lockA is held by Thread 1!
            perform_transfer()
```
```
   [Thread 1] holds lockA  ------ waits for ------>  [lockB] held by [Thread 2]
       ^                                                 |
       |                                                 |
       +------------------- waits for -------------------+
```
Both threads sleep forever.

### The Algorithmic Fix: Strict Global Lock Ordering (Havender's Principle)
To prevent circular wait, establish a global strict total ordering on all locks (e.g., sort locks by their memory address `id(lock)` or account number):
```python
def safe_transfer(acc1, acc2, amount):
    first_lock, second_lock = (acc1.lock, acc2.lock) if id(acc1.lock) < id(acc2.lock) else (acc2.lock, acc1.lock)
    with first_lock:
        with second_lock:
            acc1.balance -= amount
            acc2.balance += amount
```
Since every thread always acquires locks in monotonically increasing order, circular wait is mathematically impossible.

## 3.5 Alternative Paradigms (Avoiding Locks Altogether)
From Lecture 16, concurrent programming can avoid locking bugs entirely by adopting alternative models:

1. **Functional Programming Paradigm (Immutability)**:
   * By eliminating mutable state, data cannot be corrupted by simultaneous access.
   * Parallel execution is achieved by distributing chunks of pure functional operations across independent worker processes via `multiprocessing.Pool().map()`:
   ```python
   from multiprocessing import Pool

   def square(x):
       return x * x

   with Pool(processes=4) as pool:
       results = pool.map(square, [1, 2, 3, 4, 5, 6, 7, 8])
   ```
2. **Actor Model Paradigm**:
   * Entities called **Actors** encapsulate their own private state.
   * Actors **never share state** directly.
   * Actors interact exclusively by sending and receiving asynchronous messages deposited into recipient mailboxes.
   * Each actor processes messages sequentially from its mailbox, ensuring local single-threaded safety without explicit locking.

---

# 4. Binary Trees, CBT, ACBT, & Traversal Invariants

## 4.1 Tree Height Definition (COL1101 Strict Standard)
In COL1101, tree height $h$ is defined as the **number of levels of nodes** from root to leaf:
* An **empty tree** has height $h = 0$.
* A tree containing a **single root node** has height $h = 1$.
* The root is at level 1 (depth 0).
* A node at level $k$ has depth $d = k - 1$.

```
Level 1 (Depth 0):           [ O ]             <- Single node: h = 1
                            /     \
Level 2 (Depth 1):        [ O ]   [ O ]         <- Full 2-level: h = 2 (n = 3)
                         /   \     /   \
Level 3 (Depth 2):     [O]   [O] [O]   [O]     <- Full 3-level: h = 3 (n = 7)
```

## 4.2 Complete vs. Almost Complete Binary Trees
* **Complete Binary Tree (CBT)**: Every level $1, 2, \dots, h$ is completely filled with nodes.
  $$\text{Node count } n = \sum_{i=0}^{h-1} 2^i = 2^h - 1$$
  $$\text{Number of leaves } L = 2^{h-1} = \frac{n + 1}{2}$$
  $$\text{Number of internal nodes } I = 2^{h-1} - 1 = \frac{n - 1}{2}$$
* **Almost Complete Binary Tree (ACBT)**: Levels $1, 2, \dots, h-1$ are completely filled. Level $h$ is filled strictly from left to right without gaps.
  $$\text{Bounds on node count: } 2^{h-1} \le n \le 2^h - 1$$
  Taking logarithms base 2:
  $$h - 1 \le \log_2 n < h \implies h = \lfloor \log_2 n \rfloor + 1$$

## 4.3 Level-Order Traversal (LOT) & Queue Invariants
Level-Order Traversal visits nodes level by level, left to right, implemented using a FIFO Queue.

```python
from collections import deque

def level_order_traversal(root):
    if not root:
        return []
    queue = deque([root])
    result = []
    while queue:
        level_size = len(queue)
        for _ in range(level_size):
            node = queue.popleft()
            result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result
```
### Formal Two-Level Queue Invariant
At the start of the $k$-th iteration of the outer `while` loop:
1. The queue contains **strictly and exclusively** all nodes situated at level $k$.
2. The nodes in the queue are ordered strictly from left to right as they appear in the tree.
3. All nodes at levels $1, 2, \dots, k-1$ have been completely visited and popped.

---

# 5. Binary Heaps, Array Topology, & Rank Analysis

## 5.1 Array Representation of an ACBT
Because an ACBT has no missing nodes except possibly at the right end of the bottom level, it can be mapped into a contiguous array without pointers:

| Metric | 0-Indexed Array Mapping | 1-Indexed Array Mapping |
| :--- | :--- | :--- |
| **Root Index** | $0$ | $1$ |
| **Left Child of node $i$** | $2i + 1$ | $2i$ |
| **Right Child of node $i$** | $2i + 2$ | $2i + 1$ |
| **Parent of node $i$** | $\lfloor (i - 1) / 2 \rfloor$ | $\lfloor i / 2 \rfloor$ |
| **Internal Nodes Range** | $0 \le i \le \lfloor n / 2 \rfloor - 1$ | $1 \le i \le \lfloor n / 2 \rfloor$ |
| **Leaf Nodes Range** | $\lfloor n / 2 \rfloor \le i \le n - 1$ | $\lfloor n / 2 \rfloor + 1 \le i \le n$ |
| **Last Non-Leaf Node** | $\lfloor n / 2 \rfloor - 1$ | $\lfloor n / 2 \rfloor$ |

## 5.2 Binary Heap Invariants
* **Min-Heap Invariant**: For every node $i > 0$:
  $$A[\text{parent}(i)] \le A[i] \implies A\left[\left\lfloor \frac{i-1}{2} \right\rfloor\right] \le A[i]$$
  Every path from the root down to any node is a monotonically non-decreasing sequence.
* **Max-Heap Invariant**: For every node $i > 0$:
  $$A[\text{parent}(i)] \ge A[i] \implies A\left[\left\lfloor \frac{i-1}{2} \right\rfloor\right] \ge A[i]$$
  Every path from the root down to any node is a monotonically non-increasing sequence.

## 5.3 Rank Bounding & $k$-th Smallest Search Spaces
Suppose a min-heap $H$ contains $n$ distinct elements. Let rank 1 denote the global minimum.
* **Property**: A node at depth $d$ has exactly $d$ ancestors on the path from root. Each ancestor is strictly smaller than the node.
* **Consequence**: The rank $R(u)$ of any node $u$ at depth $d$ satisfies:
  $$R(u) \ge d + 1$$
* **Finding candidate positions for the $k$-th smallest element**:
  $$d + 1 \le k \implies d \le k - 1$$
  Therefore, the $k$-th smallest element must reside at depth $0 \le d \le k - 1$.
  * **1st smallest (minimum)**: $d \le 0 \implies d = 0 \implies \text{Index } 0$.
  * **2nd smallest**: $d \le 1 \implies d \in \{0, 1\}$. Since index 0 is 1st smallest, it must be at depth 1: **Indices $\{1, 2\}$**.
  * **3rd smallest**: $d \le 2 \implies d \in \{1, 2\}$: **Indices $\{1, 2, 3, 4, 5, 6\}$** (provided $n \ge 7$).
  * **4th smallest**: $d \le 3 \implies d \in \{1, 2, 3\}$: **Indices $\{1, 2, \dots, 14\}$** (provided $n \ge 15$).

## 5.4 Min-Max Heap Duality (Advanced Exam Challenge)
**Problem**: Suppose $H_1$ is a binary min-heap and $H_2$ is a binary max-heap, both containing the exact same set of unique elements $\{1, 2, 3, 4, 5, 6, 7\}$. Can $H_1[1] = H_2[1]$? If so, what values are possible?

### Mathematical Derivation:
1. **Min-Heap $H_1$ Rank Bounds for Index 1**:
   * Node 1 is a child of root 0 $\implies H_1[1] > H_1[0]$. Thus at least 1 element is smaller $\implies \text{Rank} \ge 2$.
   * Node 1 is parent to nodes 3 and 4 $\implies H_1[1] < H_1[3]$ and $H_1[1] < H_1[4]$. Thus at least 2 elements are larger $\implies \text{Rank} \le 7 - 2 = 5$.
   * Min-heap rank constraint for index 1: $\text{Rank}(H_1[1]) \in \{2, 3, 4, 5\}$.
2. **Max-Heap $H_2$ Rank Bounds for Index 1**:
   * Node 1 is a child of root 0 $\implies H_2[1] < H_2[0]$. Thus at least 1 element is larger $\implies \text{Rank} \le 6$.
   * Node 1 is parent to nodes 3 and 4 $\implies H_2[1] > H_2[3]$ and $H_2[1] > H_2[4]$. Thus at least 2 elements are smaller $\implies \text{Rank} \ge 3$.
   * Max-heap rank constraint for index 1: $\text{Rank}(H_2[1]) \in \{3, 4, 5, 6\}$.
3. **Intersection of Feasible Ranks**:
   $$\{2, 3, 4, 5\} \cap \{3, 4, 5, 6\} = \{3, 4, 5\}$$
4. **Conclusion**:
   Yes, it is completely possible! The shared element $H_1[1] = H_2[1]$ can be any value in $\{3, 4, 5\}$.
   * Concrete configuration for value 4:
     * Min-Heap $H_1 = [1, 4, 2, 5, 6, 3, 7]$ (Node 1 is 4; valid min-heap).
     * Max-Heap $H_2 = [7, 4, 6, 2, 1, 5, 3]$ (Node 1 is 4; valid max-heap).

---

# 6. Fast Build Heap, Invariant Induction, & AGP Summation Proof

## 6.1 Bottom-Up Heap Construction Algorithm
```python
def heap_down(A, i, n):
    while 2 * i + 1 < n:
        left = 2 * i + 1
        right = 2 * i + 2
        smallest = left
        if right < n and A[right] < A[left]:
            smallest = right
        if A[i] <= A[smallest]:
            break
        A[i], A[smallest] = A[smallest], A[i]
        i = smallest

def fast_build_heap(A):
    n = len(A)
    # Start from last non-leaf node down to root
    for i in range(n // 2 - 1, -1, -1):
        heap_down(A, i, n)
```

## 6.2 Formal Inductive Proof of Fast Build Heap
*This proof follows the strict structural rubric required by IIT Delhi COL1101 graders.*

### Formal Invariant Definition $P(i)$
At the start of the loop iteration for index $i$ (where $i$ ranges from $\lfloor n/2 \rfloor - 1$ down to $0$):
$$\text{For every index } j \text{ such that } i < j < n, \text{ the subtree rooted at node } j \text{ is a valid binary min-heap.}$$

### Inductive Proof
1. **Initialisation (Base Case)**:
   * Prior to the first iteration, $i = \lfloor n/2 \rfloor - 1$.
   * All indices $j > i$ satisfy $\lfloor n/2 \rfloor \le j \le n - 1$.
   * In a 0-indexed ACBT of size $n$, any node $j \ge \lfloor n/2 \rfloor$ has left child $2j + 1 \ge 2\lfloor n/2 \rfloor + 1 > n - 1$.
   * Thus, every node $j > i$ is a **leaf node**.
   * A subtree consisting of a single leaf has no children, so it trivially satisfies the min-heap property.
   * Hence, $P(\lfloor n/2 \rfloor - 1)$ holds prior to loop entry.

2. **Maintenance (Inductive Step)**:
   * Assume invariant $P(i)$ holds at the start of iteration for index $i$.
   * During this iteration, we execute `heap_down(A, i, n)`.
   * The left and right children of node $i$ are $2i + 1$ and $2i + 2$.
   * For all $i \ge 0$, we have the **strict inequalities**:
     $$2i + 1 > i \quad \text{and} \quad 2i + 2 > i$$
   * By the inductive hypothesis $P(i)$, because both child indices are strictly greater than $i$, the subtrees rooted at $2i + 1$ and $2i + 2$ are **already valid min-heaps**.
   * This guarantees that the essential precondition of `heap_down(A, i, n)` is strictly satisfied.
   * `heap_down(A, i, n)` sifts $A[i]$ down to its valid position, restoring the min-heap property at node $i$ while preserving the heap property in all subtrees $j > i$.
   * Upon decrementing the loop index to $i - 1$, the min-heap property holds for all nodes $j > i - 1$.
   * Hence, $P(i - 1)$ holds for the next iteration.

3. **Termination**:
   * The loop terminates when $i = -1$.
   * Substituting $i = -1$ into invariant $P(i)$:
     $$\forall j \text{ such that } -1 < j < n \implies 0 \le j \le n - 1$$
   * Every node $j \in [0, n - 1]$ roots a valid binary min-heap.
   * In particular, for $j = 0$, the subtree rooted at the root is the entire tree.
   * Therefore, the entire array $A[0 \dots n - 1]$ is a valid binary min-heap. $\blacksquare$

### Termination Metric for `heap_down`
To prove that `heap_down(A, i, n)` itself terminates:
* Let the well-founded termination metric be:
  $$M(k) = \text{height of the subtree rooted at node } k$$
* At each sift-down step, if a swap occurs, the node moves to child index $k' \in \{2k+1, 2k+2\}$.
* In an ACBT, the height of a child's subtree is strictly less than the height of the parent's subtree:
  $$M(k') \le M(k) - 1 < M(k)$$
* Since tree height is a non-negative integer bounded below by 0, the loop must terminate in at most $\lfloor \log_2 n \rfloor$ iterations.

## 6.3 Asymptotic Complexity: The AGP Summation Proof
Why does bottom-up `fast_build_heap` achieve $\Theta(n)$ linear time, whereas naive top-down insertion requires $\Theta(n \log n)$?

### Mathematical Derivation
In an ACBT of size $n$, the work done by `heap_down` on a node at height $h$ (where leaf height is 0) is at most $O(h)$ comparisons and swaps.
* Number of nodes at height $h$ is at most $\lceil n / 2^{h+1} \rceil$.
* Total comparisons and swaps:
  $$T(n) \le \sum_{h=1}^{\lfloor \log_2 n \rfloor} \left\lceil \frac{n}{2^{h+1}} \right\rceil c \cdot h \le c n \sum_{h=1}^{\infty} \frac{h}{2^{h+1}} = \frac{c n}{2} \sum_{h=1}^{\infty} \frac{h}{2^h}$$

Let $S = \sum_{h=1}^{\infty} \frac{h}{2^h}$. We evaluate this Arithmetico-Geometric Progression (AGP):
$$S = \frac{1}{2^1} + \frac{2}{2^2} + \frac{3}{2^3} + \frac{4}{2^4} + \cdots$$
Multiply both sides by $\frac{1}{2}$:
$$\frac{1}{2}S = \frac{1}{2^2} + \frac{2}{2^3} + \frac{3}{2^4} + \cdots$$
Subtract $\frac{1}{2}S$ from $S$:
$$S - \frac{1}{2}S = \frac{1}{2^1} + \left(\frac{2}{2^2} - \frac{1}{2^2}\right) + \left(\frac{3}{2^3} - \frac{2}{2^3}\right) + \cdots$$
$$\frac{1}{2}S = \sum_{k=1}^{\infty} \left(\frac{1}{2}\right)^k$$
The right-hand side is a geometric series with ratio $r = 1/2$ and first term $a = 1/2$:
$$\sum_{k=1}^{\infty} \left(\frac{1}{2}\right)^k = \frac{1/2}{1 - 1/2} = 1$$
Therefore:
$$\frac{1}{2}S = 1 \implies S = 2$$
Substituting $S = 2$ back into our work bound:
$$T(n) \le \frac{c n}{2} \cdot (2) = c n = \Theta(n)$$

### Intuitive Structural Comparison
* **Top-Down Build** (`insert` each element): Work is proportional to **depth**. The vast majority of nodes (~$n/2$ leaves) are at maximum depth $\approx \log_2 n$, doing maximum work:
  $$T(n) = \sum_{i=1}^n O(\log i) = \Theta(n \log n)$$
* **Bottom-Up Fast Build**: Work is proportional to **height**. The vast majority of nodes (~$n/2$ leaves) are at height 0, doing **zero work**. Only the 1 root node is at height $\approx \log_2 n$:
  $$T(n) = \Theta(n)$$

---

# 7. In-Place HeapSort & Priority Queue Applications

## 7.1 In-Place HeapSort Algorithm
To sort an array in **ascending order** in-place without auxiliary memory:
1. **Phase 1: Build Max-Heap** in $\Theta(n)$ time using bottom-up `heap_down`.
2. **Phase 2: Extract Maximum Elements** into the rear of the array:
   * For $i$ from $n - 1$ down to $1$:
     * Swap $A[0]$ (current maximum) with $A[i]$ (current boundary).
     * Call `heap_down(A, 0, i)` on the reduced heap of size $i$.

```python
def heapsort(A):
    n = len(A)
    # Phase 1: Build Max-Heap
    for i in range(n // 2 - 1, -1, -1):
        max_heap_down(A, i, n)
    # Phase 2: In-place sorting
    for i in range(n - 1, 0, -1):
        A[0], A[i] = A[i], A[0]  # Move maximum to sorted region
        max_heap_down(A, 0, i)  # Restore heap property on A[0...i-1]
```
* **Time Complexity**: $\Theta(n) + \sum_{i=1}^{n-1} O(\log i) = \Theta(n \log n)$ in Best, Average, and Worst cases.
* **Auxiliary Space Complexity**: $\Theta(1)$ auxiliary space (in-place).
* **Stability**: **Unstable** (long-distance swaps disrupt relative order of equal keys).

---

# 8. Authentic Practice Exam 1 (IIT Delhi Rubric Fidelity)

**Time Allowed**: 60 Minutes  
**Total Points**: 20 Points  
**Format**: 3 Questions (Q1: 6 pts, Q2: 6 pts, Q3: 8 pts)  

---

### Question 1: ADT & Data Structure Permutations [6 Points]
*(Strict Rubric: +1 pt for correct answer, +1 pt for correct explanation. 0 pts total if answer is incorrect.)*

#### 1.1 Min-Max Heap Sharing [2 Points]
Consider an array containing the 7 distinct integers $\{10, 20, 30, 40, 50, 60, 70\}$.
Is it possible to arrange these 7 integers into:
1. A valid binary min-heap $H_1$, AND
2. A valid binary max-heap $H_2$,  
such that $H_1[1] = H_2[1]$? If yes, state all possible values that can occupy index 1 in both heaps. If no, prove why it is impossible.

#### 1.2 Root-to-Leaf Extremum Constraint [2 Points]
In a binary min-heap $H_1$ and binary max-heap $H_2$, both containing the distinct integers $\{1, 2, 3, 4, 5, 6, 7\}$, is it possible that $H_1[0] = H_2[2]$? Explain rigorously.

#### 1.3 Depth Bounds on Rank [2 Points]
In a binary min-heap containing $n = 31$ distinct elements, what is the exact array index range $[i_{\min}, i_{\max}]$ where the 3rd smallest element can possibly be located?

---

### Question 2: Python Execution & Concurrency Tracing [6 Points]

#### 2.1 Closure Late-Binding vs. Eager Defaults [3 Points]
Examine the following Python script:
```python
from functools import reduce

steps = [1, 2, 3]

# Definition Group A
pipeline_a = [lambda x, s=s: x + s * 2 for s in steps]

# Definition Group B
pipeline_b = [lambda x: x + s * 2 for s in steps]

val_a = reduce(lambda acc, f: f(acc), pipeline_a, 10)
val_b = reduce(lambda acc, f: f(acc), pipeline_b, 10)

print(f"val_a = {val_a}")
print(f"val_b = {val_b}")
```
* **Part A (1.5 pts)**: What is the exact integer printed for `val_a`? Show step-by-step evaluation.
* **Part B (1.5 pts)**: What is the exact integer printed for `val_b`? Explain why it differs from `val_a` referencing CPython cell semantics.

#### 2.2 Concurrency Interleaving & Deadlock [3 Points]
Consider two shared locks `lock1 = threading.Lock()` and `lock2 = threading.Lock()`, and two bank balances `A = 500`, `B = 300`.
Two threads execute concurrently:
```python
# Thread 1
def transfer_A_to_B():
    with lock1:
        with lock2:
            balance_A -= 100
            balance_B += 100

# Thread 2
def transfer_B_to_A():
    with lock2:
        with lock1:
            balance_B -= 50
            balance_A += 50
```
* **Part A (1.5 pts)**: Describe a specific interleaving of execution steps that produces a **deadlock**. State the status of each thread and each lock.
* **Part B (1.5 pts)**: State the specific Coffman condition responsible for this deadlock and rewrite the lock acquisition logic to mathematically prevent deadlock.

---

### Question 3: Loop Invariants & Algorithmic Rigor [8 Points]

Consider the `fast_build_heap` algorithm for an array $A[0 \dots n - 1]$:
```python
def fast_build_heap(A):
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        heap_down(A, i, n)
```

#### 3.1 Inductive Loop Invariant Proof [3 Points]
State the loop invariant $P(i)$ maintained by `fast_build_heap` and prove the **Maintenance (Inductive Step)** showing why $P(i) \implies P(i-1)$.
*(Important: Graders will deduct points if child index inequalities are not stated strictly).*

#### 3.2 Termination Proof [2 Points]
Define a formal well-founded metric $M$ for `heap_down(A, i, n)` and prove that every call to `heap_down` must terminate in at most $O(\log n)$ operations.

#### 3.3 Asymptotic Derivation via AGP Summation [3 Points]
Prove algebraically that `fast_build_heap` runs in $\Theta(n)$ time by formulating the sum of heights and evaluating the Arithmetico-Geometric Progression $\sum_{h=1}^\infty \frac{h}{2^h}$.

---

## Model Solutions & Marking Rubric (Exam 1)

### Q1.1 Model Solution (2 Points)
* **Answer**: **Yes**, it is possible. The possible values are **$\{30, 40, 50\}$**. (+1 pt)
* **Explanation**:
  * In min-heap $H_1$, index 1 has 1 ancestor (root 0) and 2 children (indices 3 and 4). Thus $H_1[1] > H_1[0]$ (at least 1 smaller) and $H_1[1] < H_1[3], H_1[4]$ (at least 2 larger). Feasible ranks in $H_1$: $\{2, 3, 4, 5\}$.
  * In max-heap $H_2$, index 1 has 1 ancestor (root 0) and 2 children (indices 3 and 4). Thus $H_2[1] < H_2[0]$ (at least 1 larger) and $H_2[1] > H_2[3], H_2[4]$ (at least 2 smaller). Feasible ranks in $H_2$: $\{3, 4, 5, 6\}$.
  * Intersection of feasible ranks: $\{2, 3, 4, 5\} \cap \{3, 4, 5, 6\} = \{3, 4, 5\}$, corresponding to elements $\{30, 40, 50\}$.
  * Valid heaps for value 40: $H_1 = [10, 40, 20, 50, 60, 30, 70]$, $H_2 = [70, 40, 60, 20, 10, 50, 30]$. (+1 pt)

### Q1.2 Model Solution (2 Points)
* **Answer**: **No**, it is impossible. (+1 pt)
* **Explanation**:
  * In min-heap $H_1$, root $H_1[0] = 1$ (the global minimum).
  * In max-heap $H_2$, node 2 is an internal node with children at indices $2(2)+1 = 5$ and $2(2)+2 = 6$.
  * By the max-heap property, $H_2[2] \ge H_2[5]$ and $H_2[2] \ge H_2[6]$. Since all 7 elements are distinct, $H_2[2] > H_2[5] \ge 1 \implies H_2[2] \ge 2$.
  * Therefore, $H_2[2] > 1 = H_1[0]$, so they can never be equal. (+1 pt)

### Q1.3 Model Solution (2 Points)
* **Answer**: Array index range **$[1, 6]$**. (+1 pt)
* **Explanation**:
  * For distinct elements, a node at depth $d$ has $d$ strictly smaller ancestors.
  * Thus, rank $\ge d + 1$. For rank $= 3$, we must have $d + 1 \le 3 \implies d \le 2$.
  * Depth 0 (index 0) contains the 1st smallest element (rank 1).
  * Candidate depths for 3rd smallest are depth 1 (indices 1, 2) and depth 2 (indices 3, 4, 5, 6).
  * Thus, the exact range is $[1, 6]$. (+1 pt)

### Q2.1 Model Solution (3 Points)
* **Part A**: `val_a = 22`. (+1.5 pts)
  * In `pipeline_a`, parameter default `s=s` binds eagerly at definition time.
  * $f_0(x) = x + 2$, $f_1(x) = x + 4$, $f_2(x) = x + 6$.
  * Reduction: $10 \xrightarrow{f_0} 12 \xrightarrow{f_1} 16 \xrightarrow{f_2} 22$.
* **Part B**: `val_b = 28`. (+1.5 pts)
  * In `pipeline_b`, `s` is a free variable captured via a CPython `cell` object (`__closure__`).
  * When the loop finishes, the cell contains the terminal value `s = 3`.
  * At call time during `reduce`, all three functions dereference `s = 3`, adding $3 \times 2 = 6$.
  * Reduction: $10 + 6 + 6 + 6 = 28$.

### Q2.2 Model Solution (3 Points)
* **Part A**: Interleaving producing deadlock (+1.5 pts):
  1. Thread 1 acquires `lock1`.
  2. Context switch to Thread 2.
  3. Thread 2 acquires `lock2`.
  4. Thread 2 attempts to acquire `lock1` $\implies$ blocks (held by Thread 1).
  5. Context switch to Thread 1.
  6. Thread 1 attempts to acquire `lock2` $\implies$ blocks (held by Thread 2).
  7. **Status**: Both threads blocked in circular waiting; neither can make progress.
* **Part B**: Prevention (+1.5 pts):
  * Coffman condition: **Circular Wait**.
  * Fix: **Global Lock Ordering (Havender's principle)**. Both functions must acquire locks in the exact same order (e.g. always `lock1` then `lock2`):
  ```python
  def transfer_B_to_A_fixed():
      with lock1:
          with lock2:
              balance_B -= 50
              balance_A += 50
  ```

### Q3.1 Model Solution (3 Points)
* **Invariant $P(i)$**: For all $j$ such that $i < j < n$, the subtree rooted at $j$ is a valid binary min-heap. (+1 pt)
* **Inductive Step ($P(i) \implies P(i-1)$)**:
  * Consider iteration $i$. Children of $i$ are $L = 2i + 1$ and $R = 2i + 2$.
  * For any $i \ge 0$, we have **$2i + 1 > i$** and **$2i + 2 > i$** (strict inequalities). (+1 pt)
  * By inductive hypothesis $P(i)$, since both child indices exceed $i$, the subtrees rooted at $L$ and $R$ are already valid min-heaps.
  * This satisfies the exact precondition of `heap_down(A, i, n)`.
  * After `heap_down(A, i, n)` executes, the subtree rooted at $i$ satisfies the min-heap property, and all subtrees rooted at $j > i$ remain valid min-heaps.
  * Decrementing $i$ to $i-1$, the property holds for all $j > i-1$, establishing $P(i-1)$. (+1 pt)

### Q3.2 Model Solution (2 Points)
* **Termination Metric**: $M(k) = \text{height of the subtree rooted at node } k$. (+1 pt)
* **Proof**:
  * In each iteration of the while loop in `heap_down`, if a swap occurs with child $c \in \{2k+1, 2k+2\}$, the next node has height $M(c) \le M(k) - 1$.
  * Thus $M(k)$ strictly decreases at every swap step.
  * Since height is non-negative ($M(k) \ge 0$), the loop must terminate in at most $M(\text{initial node}) \le \lfloor \log_2 n \rfloor$ iterations. (+1 pt)

### Q3.3 Model Solution (3 Points)
* Maximum height in an ACBT of size $n$ is $H = \lfloor \log_2 n \rfloor$.
* Number of nodes at height $h$ is at most $\lceil n / 2^{h+1} \rceil$.
* Total cost: $T(n) \le \sum_{h=1}^H \lceil \frac{n}{2^{h+1}} \rceil c h \le \frac{c n}{2} \sum_{h=1}^\infty \frac{h}{2^h}$. (+1 pt)
* Let $S = \sum_{h=1}^\infty \frac{h}{2^h}$.
  $$S = \frac{1}{2} + \frac{2}{4} + \frac{3}{8} + \frac{4}{16} + \cdots$$
  $$\frac{1}{2}S = \frac{1}{4} + \frac{2}{8} + \frac{3}{16} + \cdots$$
  Subtracting gives:
  $$\frac{1}{2}S = \frac{1}{2} + \frac{1}{4} + \frac{1}{8} + \cdots = \frac{1/2}{1 - 1/2} = 1 \implies S = 2$$ (+1 pt)
* Therefore: $T(n) \le \frac{c n}{2} (2) = c n = \Theta(n)$. (+1 pt)

---

# 9. Creative Practice Exam 2 (Advanced Duality & Edge Cases)

**Time Allowed**: 60 Minutes | **Total Points**: 20 Points  

### Q1: Creative Duality & Topology [6 Points]
1.1 In an ACBT with $n = 50$ nodes, what is the exact index of the last internal node, and how many leaf nodes are in the tree? [2 pts]  
1.2 In a binary min-heap of size $n = 100$ with distinct keys, what is the maximum depth at which the 5th smallest element can possibly be located? Give the exact index range $[i_{\min}, i_{\max}]$ corresponding to all candidate nodes. [2 pts]  
1.3 Given an array $A = [1, 2, 3, 4, 5, 6, 7]$. How many distinct valid binary min-heaps can be formed using all these 7 elements? [2 pts]

### Q2: Advanced CPython Scoping & Concurrency Edge Cases [6 Points]
2.1 Consider the following code:
```python
x = 10
def outer():
    x = 20
    def inner():
        nonlocal x
        x += 5
        return lambda y: x + y
    fn = inner()
    x += 10
    return fn

closure_fn = outer()
print(closure_fn(100))
```
What is the exact integer output printed? Trace the lifecycle of `x` across stack frames and closure cells. [3 pts]

2.2 Two threads share a single `threading.Lock()`. Thread 1 acquires the lock, then attempts to acquire it again inside a nested helper function without releasing it first:
```python
lock = threading.Lock()
def helper():
    with lock:
        print("Helper executed")

def main_task():
    with lock:
        helper()
```
What happens when `main_task()` is executed? What specific lock primitive from Python's standard library resolves this issue without changing the call hierarchy? [3 pts]

### Q3: Fast Build Heap Invariant Induction on Edge Topologies [8 Points]
3.1 Consider building a heap on an array where $n$ is an even number (e.g. $n = 10$). What is unique about the last non-leaf node during the first iteration of `fast_build_heap`? How does `heap_down` maintain correctness when right child $2i + 2 \ge n$? [3 pts]  
3.2 Prove that an array sorted in strictly descending order $A = [n, n-1, \dots, 2, 1]$ represents the worst-case input for `fast_build_heap(A)` into a min-heap. Does its asymptotic complexity exceed $\Theta(n)$? [3 pts]  
3.3 Why does `heap_down` compare against the *smaller* of the two children rather than swapping with the first child that is smaller than the parent? Give a 3-element counterexample showing invariant violation. [2 pts]

---

## Model Solutions (Exam 2)

### Q1.1 Model Solution
* Last non-leaf node index: $\lfloor 50/2 \rfloor - 1 = 25 - 1 = \mathbf{24}$.
* Leaf node indices: from $\lfloor 50/2 \rfloor = 25$ to $49$.
* Total leaf nodes: $49 - 25 + 1 = \mathbf{25}$ leaves.

### Q1.2 Model Solution
* For the 5th smallest element, rank $= 5$.
* A node at depth $d$ has $d$ strictly smaller ancestors $\implies d + 1 \le 5 \implies d \le 4$.
* Depth 0 (index 0) has rank 1 (minimum).
* Candidate depths: $d \in \{1, 2, 3, 4\}$.
* Depth 1 starts at index 1.
* Depth 4 ends at index $2^5 - 2 = 30$ (since $30 < 100$).
* Candidate index range: **$[1, 30]$**.

### Q1.3 Model Solution
* In any min-heap of size 7, the root must be 1 (1 choice).
* The left subtree has size 3 (nodes 1, 3, 4) and right subtree has size 3 (nodes 2, 5, 6).
* We must choose 3 elements out of the remaining 6 for the left subtree: $\binom{6}{3} = 20$ choices.
* For a subtree of size 3, its root must be the minimum of its 3 elements (1 choice), and the remaining 2 elements can be placed on left and right in $2! = 2$ ways.
* Total valid min-heaps:
  $$\binom{6}{3} \times 2 \times 2 = 20 \times 4 = \mathbf{80}$$

### Q2.1 Model Solution
* Output: **`135`**.
* Trace:
  1. `outer()` binds local `x = 20` in a closure cell shared with `inner()`.
  2. `inner()` executes `x += 5`, updating the cell to `25`.
  3. `inner()` returns `lambda y: x + y`, which captures the cell for `x`.
  4. `outer()` then executes `x += 10`, updating the exact same cell to `25 + 10 = 35`.
  5. `outer()` returns `fn`.
  6. `closure_fn(100)` evaluates `x + 100`. It dereferences the cell containing `35`, yielding $35 + 100 = 135$.

### Q2.2 Model Solution
* `main_task()` experiences a **self-deadlock (re-entrancy deadlock)**.
* Standard `threading.Lock()` cannot be acquired again by the same thread if it is already locked; `helper()` blocks forever waiting for `main_task()` to release the lock.
* Fix: Use `threading.RLock()` (**Re-entrant Lock**), which allows the acquiring thread to re-enter nested critical sections by maintaining an internal recursion count.

### Q3.1 Model Solution
* When $n$ is even, the last internal node $i = n/2 - 1$ has left child $2i + 1 = n - 1$ (the very last element in the array), but right child $2i + 2 = n$, which is out of bounds.
* Correctness: `heap_down` checks `if right < n` before comparing children. When $right \ge n$, it skips the right-child comparison and compares node $i$ directly with its sole left child.

### Q3.2 Model Solution
* When $A$ is in descending order, every internal node is strictly greater than both its children, forcing `heap_down` to execute the maximum possible number of swaps all the way down to a leaf.
* Even though this triggers the maximum number of swaps, the sum of heights is still bounded by $\sum h \lceil n/2^{h+1} \rceil \le n$. Thus, its time complexity is still strictly **$\Theta(n)$**!

### Q3.3 Model Solution
* If a parent swaps with the larger of two invalid children, the heap property will be violated at the parent.
* Counterexample: $A = [10, 5, 2]$.
  * If parent 10 swapped with left child 5: array becomes $[5, 10, 2]$.
  * But right child is $2 < 5$, violating the min-heap invariant at root!
  * Swapping with the minimum child (2) gives $[2, 5, 10]$, which is a valid min-heap.

---

# 10. Diagnostic Pitfall Guide & 10 Lethal Exam Traps

```
+---------------------------------------------------------------------------------------------------------+
|                                    10 LETHAL EXAM TRAPS IN COL1101 QUIZ 2                                |
+----+------------------------------------+---------------------------------------------------------------+
| #  | Traps & Misconceptions             | The Absolute Truth & Exam Remedy                              |
+----+------------------------------------+---------------------------------------------------------------+
| 1  | "Single node tree has height 0"    | WRONG. In COL1101, height is the number of levels:            |
|    |                                    | Empty tree = 0, Single node = 1. Complete tree n = 2^h - 1.    |
+----+------------------------------------+---------------------------------------------------------------+
| 2  | "Writing 2i+1 >= i in invariant"   | ZERO MARKS. Graders strictly require STRICT inequalities:     |
|    |                                    | 2i + 1 > i and 2i + 2 > i for all i >= 0.                      |
+----+------------------------------------+---------------------------------------------------------------+
| 3  | "lambda captures variable value"   | WRONG. Lambda captures a shared Cell pointer (late binding).  |
|    |                                    | Use default arg `lambda x, s=s: x + s` for eager binding!     |
+----+------------------------------------+---------------------------------------------------------------+
| 4  | "counter += 1 is thread-safe"      | WRONG. += desugars to LOAD, BINARY_OP, STORE. Context switch   |
|    |                                    | between LOAD and STORE causes Lost Updates!                   |
+----+------------------------------------+---------------------------------------------------------------+
| 5  | "Fast Build Heap takes O(n log n)" | WRONG. Bottom-up takes Theta(n) because leaves (height 0) do  |
|    |                                    | zero work. Only top-down takes Theta(n log n).               |
+----+------------------------------------+---------------------------------------------------------------+
| 6  | "Deadlock fix is time.sleep()"     | WRONG. Fix is Global Lock Ordering (Havender's principle):   |
|    |                                    | all threads acquire locks in the exact same monotonic order.  |
+----+------------------------------------+---------------------------------------------------------------+
| 7  | "3rd smallest is at depth 3"       | WRONG. Rank >= depth + 1. For rank 3, depth <= 2.             |
|    |                                    | It can only be at depth 1 (indices 1,2) or 2 (indices 3..6).  |
+----+------------------------------------+---------------------------------------------------------------+
| 8  | "HeapSort is stable"               | WRONG. HeapSort is UNSTABLE because distant array swaps       |
|    |                                    | invert the original order of equal elements.                  |
+----+------------------------------------+---------------------------------------------------------------+
| 9  | "Leaf nodes start at n/2 + 1"      | In 0-indexed arrays, leaves start at floor(n / 2) to n - 1.   |
|    |                                    | Last non-leaf node is at floor(n / 2) - 1.                    |
+----+------------------------------------+---------------------------------------------------------------+
| 10 | "IEEE 754 is in Quiz 2"            | EXCLUDED! IEEE floating point has been removed from syllabus. |
+----+------------------------------------+---------------------------------------------------------------+
```

---
*End of COL1101 Quiz 2 Master Compendium.*
