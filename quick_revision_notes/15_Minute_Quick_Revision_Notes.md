# COL1101: 15-Minute Master Revision Sheet

> **Exam Timing:** Review this sheet 15 minutes before the exam.  
> **Structure:** Part 1 covers the core foundations from earlier (L1–L11), and Part 2 covers the new afterward syllabus (L12–L21) in full exam-tested detail.

---

# PART 1: EARLIER CORE FOUNDATIONS (Lectures 1–11)

### 1. Asymptotic Complexity & Recurrences
- **Definitions**:
  - $f(n) = O(g(n)) \iff \exists c > 0, n_0 : \forall n \ge n_0, \; f(n) \le c \cdot g(n)$ (Upper bound)
  - $f(n) = \Omega(g(n)) \iff \exists c > 0, n_0 : \forall n \ge n_0, \; f(n) \ge c \cdot g(n)$ (Lower bound)
  - $f(n) = \Theta(g(n)) \iff f(n) = O(g(n)) \text{ and } f(n) = \Omega(g(n))$ (Tight bound)
- **Recurrence Unrolling (Ternary / Valley Search from Quiz 1)**:
  $$T(n) = T\left(\frac{2n}{3}\right) + c \implies T(n) = c \log_{3/2} n = \mathbf{\Theta(\log n)}$$
  $$T(n) = 2T\left(\frac{n}{2}\right) + c \cdot n \implies \mathbf{\Theta(n \log n)}$$
  $$T(n) = T(n-1) + c \cdot n \implies \sum_{i=1}^n c \cdot i = \mathbf{\Theta(n^2)}$$

### 2. The 4-Step Loop Invariant Induction Framework (Quiz 1 Format)
Whenever asked to prove a loop invariant $\mathcal{P}(i)$ on an exam:
1. **Base Case**: State why $\mathcal{P}$ holds *prior to iteration 0* (or for the initial index).
2. **Inductive Step**: Assume $\mathcal{P}(i-1)$ (or $\mathcal{P}(i)$). Prove $\mathcal{P}(i)$ (or $\mathcal{P}(i-1)$) holds after the iteration.
   - *CRITICAL GRADER TIP FROM QUIZ 1*: Prove **strict inequalities** (e.g. $m < \text{rmid}$, or $2i+1 > i$) and show why the branch conditions guarantee the bound.
3. **Termination**: State a **well-founded metric** that strictly decreases each iteration (e.g., `right - left`, or remaining subtree height) bounded below by a finite threshold.
4. **Correctness at Termination**: Show that when the loop exits, the invariant combined with the termination condition directly implies the final post-condition.

### 3. Stacks & Queues: LIFO vs FIFO & Permutations
- **Stack**: Last-In, First-Out (LIFO). Operations: `push`, `pop`, `peek` ($O(1)$).
- **Queue**: First-In, First-Out (FIFO). Operations: `enqueue`, `dequeue` ($O(1)$).
- **Producible Permutations (Quiz 1 Q1)**: Shifting $0, 1, \dots, n-1$ from Queue to Stack and popping can generate any permutation **except** those containing the forbidden pattern (cannot pop a smaller element that was buried under a larger element without popping the larger one first).

### 4. Python OOP, Inheritance & C3 MRO (Quiz 1 Q2)
- **Method Resolution Order (MRO)**: Python resolves method calls via C3 Linearization.
  - For `class D(B, C)` where `B(A)` and `C(A)`:
    $$\text{MRO}(D) = [D, B, C, A, \text{object}]$$
  - `super().who()` in class $B$ does NOT necessarily call $A$! It calls the **next class in the MRO of the instance `self`** (which is $C$ when called on an instance of $D$).
- **Class Attributes vs Instance Attributes**:
  - `class B: step = A()` defines `step` at **class level** (shared by all instances unless overridden).

---

# PART 2: THE NEW SYLLABUS (Lectures 12–21)

---

## 5. Functional Programming & Closures (Lectures 12–14, Lab 5)

### Core FP Principles
- **Pure Functions**: Return values depend solely on arguments; zero side-effects (no I/O, no mutating global or outside state).
- **Immutability**: Once created, objects cannot be altered. State updates return **new instances**.
- **Structural Sharing (Lab 5 `PQ` & `Cell`)**: Unmodified portions of persistent data structures are shared via references, giving $O(1)$ non-destructive updates.
- **Higher-Order Functions**:
  - `map(f, [x1, x2]) = [f(x1), f(x2)]`
  - `filter(p, [x1, x2]) = [x for x in ... if p(x)]`
  - `reduce(f, [x1, x2, x3], init) = f(f(f(init, x1), x2), x3)`

### The Python Closure Trap: Eager vs. Late Binding
```python
# 1. EAGER BINDING (Default Parameter snapshot):
funcs_eager = [lambda x, s=step: x + s for step in [1, 2, 3]]
# 's=step' evaluates at DEFINITION TIME, stored in __defaults__.
# funcs_eager[0](10) -> 11, funcs_eager[1](10) -> 12, funcs_eager[2](10) -> 13

# 2. LATE BINDING (Lexical Cell Lookup):
funcs_late = [lambda x: x + step for step in [1, 2, 3]]
# 'step' is looked up at CALL TIME via __closure__ cell object.
# Loop terminates with step = 3. All lambdas see step = 3!
# funcs_late[0](10) -> 13, funcs_late[1](10) -> 13, funcs_late[2](10) -> 13
```

---

## 6. Concurrency from Slides (Lectures 15–16)

### Processes vs. Threads
| Dimension | Process | Thread |
| :--- | :--- | :--- |
| **Address Space** | **Isolated / Private** memory space. Safe from interference. | **Shared** memory (Heap, Globals, Code) within process. |
| **Context Switch** | **Heavyweight**: OS swaps page tables and virtual memory. | **Lightweight**: Only CPU registers, PC, and stack pointer. |
| **Communication** | Slow: Requires Inter-Process Communication (IPC, pipes, sockets). | Fast: Read/write shared memory variables directly. |
| **Primary Danger** | Complex IPC setup. | **Race Conditions & Data Corruption** on shared mutable state! |

### The Bank Account Race Condition (Lost Update)
```python
class Account:
    def deposit(self, amt):
        t = self.balance        # Step 1: READ
        time.sleep(0)           # Step 2: Context switch / preemption
        self.balance = t + amt  # Step 3: WRITE
```
- **Why it Fails**: Even `balance += amt` is 3 bytecode operations (`LOAD_FAST` $\to$ `INPLACE_ADD` $\to$ `STORE_FAST`). A context switch between read and write causes another thread's update to be silently overwritten!
- **The 3 Conditions for a Race Condition**: (1) Shared memory, (2) Mutable state, (3) Unsynchronized concurrent access.

### Critical Sections & `threading.Lock()`
- **Critical Section**: Code accessing shared mutable state.
- **Mutual Exclusion**: At most 1 thread inside the critical section at a time.
- **Python Syntax**: `with lock: balance += amt` (automatically acquires and releases).

### The Two Locking Pitfalls
1. **Contention (Serialization Overhead)**: Threads spend all their time blocked waiting for a coarse lock, making multi-threaded code slower than sequential code.
2. **Deadlock (Circular Wait)**:
   - Thread 1 holds Lock 1 and waits for Lock 2.
   - Thread 2 holds Lock 2 and waits for Lock 1.
   - Both wait forever!
   - **Fix**: **Global Lock Ordering** (all threads must acquire locks in strictly increasing order, e.g. `min(L1, L2)` then `max(L1, L2)`).

### Alternative Paradigms (Beyond Locks)
- **Functional Programming**: Immutability $\implies$ no shared mutable state $\implies$ zero race conditions. Parallelize with `multiprocessing.Pool().map()` (`parallel_sum`).
- **The Actor Model**: *"Do not communicate by sharing memory; share memory by communicating!"*
  - Actors have **strictly private state**.
  - Threads send requests to the Actor's **FIFO Mailbox**.
  - Actor processes messages sequentially with **zero locks, zero race conditions, zero deadlocks**.

---

## 7. Binary Trees, CBT, & ACBT (Lectures 17–18)

### Height & Node Formulas (IIT Delhi Convention)
- **Depth of node $v$**: Number of edges from root to $v$. $\text{depth}(\text{root}) = 0$.
- **Height $h$ of Tree**: **Number of levels** ($h = \text{max\_depth} + 1$).
  - Empty tree has $h = 0$. Single-node tree has $h = 1$.
- **Complete Binary Tree (CBT)**:
  - All levels $0 \dots h-2$ full ($2^l$ nodes). All nodes at level $h-1$ are leaves.
  - Total nodes: $n = 1 + 2 + \dots + 2^{h-1} = \mathbf{2^h - 1}$.
- **Almost Complete Binary Tree (ACBT)**:
  - Levels $0 \dots h-2$ full. Level $h-1$ leaves packed as far left as possible.
  - Node bounds: $\mathbf{2^{h-1} \le n \le 2^h - 1} \iff 2^{h-1} \le n < 2^h$.
  - Exact height formula: $\mathbf{h = \lfloor \log_2 n \rfloor + 1}$.

### Level-Order Traversal (LOT) & Queue Invariant (L18)
- Uses a FIFO queue $Q$, initialized with `Q.enqueue(root)`. Repeatedly `dequeue()`, visit, and enqueue left then right children.
- **Queue Loop Invariant**:
  - **Two-Level Property**: All nodes currently in $Q$ reside at **depth $d$ or $d+1$**.
  - $Q$ contains: unvisited nodes at depth $d$ (left to right), followed by children of already-visited depth $d$ nodes (at depth $d+1$, left to right).

---

## 8. Binary Min-Heaps & Array Mapping (Lectures 19–20)

### 0-Indexed Array Mapping Formulas
For an ACBT with $n$ nodes in array $A[0 \dots n-1]$:
- **Left Child of $i$**: $2i + 1$ (exists iff $2i + 1 < n$)
- **Right Child of $i$**: $2i + 2$ (exists iff $2i + 2 < n$)
- **Parent of $i$**: $\lfloor (i - 1) / 2 \rfloor$ (for $i > 0$)
- **Internal Nodes Range**: $0 \le i \le \lfloor n/2 \rfloor - 1$
- **Leaf Nodes Range**: $\lfloor n/2 \rfloor \le i \le n - 1$

### Ancestor Rank Theorem ($k$-th Smallest Candidate Positions)
- **Theorem**: A node at depth $d$ has strictly $d$ ancestors. Since every ancestor is strictly smaller, any node at depth $d$ has rank $\ge d + 1$.
- **Consequence for Min-Heap with distinct elements**:
  - **1st smallest (minimum)**: Exclusively at **depth 0** (index 0).
  - **2nd smallest**: Must be at **depth 1** (indices 1, 2).
  - **3rd smallest**: Must be at **depth 1 or depth 2** (indices 1 to 6). Can NEVER be at depth $\ge 3$ (indices $\ge 7$)!
  - **4th smallest**: Must be at **depth 1, 2, or 3** (indices 1 to 14). Can NEVER be at depth $\ge 4$!

### Core Operations
| Operation | Method | Time Complexity |
| :--- | :--- | :--- |
| `find_min()` | Return $A[0]$ | $\Theta(1)$ |
| `heap_up(i)` | Swap with parent while $A[\text{parent}] > A[i]$ | $O(\text{depth}(i)) = O(\log n)$ |
| `heap_down(i)` | Swap with smaller child while $A[i] > A[\text{smallest\_child}]$ | $O(\text{height}(i)) = O(\log n)$ |
| `insert(x)` | Append to end, `heap_up(n-1)` | $O(\log n)$ |
| `extract_min()` | Swap $A[0]$ with $A[n-1]$, pop, `heap_down(0)` | $O(\log n)$ |

---

## 9. Fast Build Heap & HeapSort (Lecture 21)

### The Fast Build Heap Algorithm
```python
def fast_build_min_heap(A):
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        heap_down(A, i, n)
```

### Invariant Proof $\mathcal{P}(i)$
- **Invariant**: $\mathcal{P}(i)$: "Every node $j \in \{i+1, \dots, n-1\}$ roots a valid min-heap."
- **Base Case**: Prior to loop ($i = \lfloor n/2 \rfloor - 1$), nodes $j \ge \lfloor n/2 \rfloor$ are all leaves with no children ($2j+1 \ge n$), so they are vacuously valid min-heaps.
- **Inductive Step**:
  1. For node $i \ge 0$, children are $2i+1$ and $2i+2$.
  2. Because $i \ge 0$, we have **strictly $2i+1 > i$ and $2i+2 > i$**.
  3. By $\mathcal{P}(i)$, the subtrees at $2i+1$ and $2i+2$ are already valid heaps $\implies$ `heap_down` precondition holds!
  4. Sifting down restores heap order for subtree $T_i$ without modifying disjoint subtrees $T_j$ ($j > i$). Thus, $\mathcal{P}(i-1)$ holds!
- **Termination**: Loop exits at $i = -1 \implies \mathcal{P}(-1)$ holds $\implies T_0$ is a valid min-heap containing all $n$ elements.

### The AGP Summation Proof: Why it is $\Theta(n)$ Linear Time!
- Sifting down a node at height $h$ takes at most $2h$ comparisons.
- Number of nodes at height $h$ is at most $\lceil \frac{n}{2^{h+1}} \rceil \le \frac{n}{2^h}$.
- Total work: $T(n) \le n \sum_{h=1}^\infty \frac{h}{2^h}$.
- **Solving the AGP**:
  $$S = \frac{1}{2^1} + \frac{2}{2^2} + \frac{3}{2^3} + \dots$$
  $$\frac{1}{2}S = \frac{1}{2^2} + \frac{2}{2^3} + \dots$$
  Subtracting:
  $$\frac{1}{2}S = \sum_{k=1}^\infty \left(\frac{1}{2}\right)^k = 1 \implies \mathbf{S = 2}$$
  $$T(n) \le n \cdot 2 = 2n \implies \mathbf{T(n) = \Theta(n)}$$

### In-Place HeapSort
```python
def heapsort(A):
    fast_build_max_heap(A)  # O(n) bottom-up
    for i in range(len(A) - 1, 0, -1):
        A[0], A[i] = A[i], A[0]  # Move maximum to sorted region
        max_heap_down(A, 0, i)   # Restore heap on A[0 ... i-1]
```
- **Loop Invariant**: $A[0 \dots i]$ is a max-heap of the smallest $i+1$ elements; $A[i+1 \dots n-1]$ is sorted in ascending order.
- **Complexity**: $\Theta(n \log n)$ time in all cases, $\mathbf{O(1)}$ auxiliary space (in-place).

---

## 10. Exam Hall Quick-Check (Common Traps to Avoid)
1. **Tree Height**: Check whether the question defines height by levels ($h = \lfloor \log_2 n \rfloor + 1$) or edges ($\lfloor \log_2 n \rfloor$). In COL1101, it is **number of levels** ($n = 2^h - 1$ for CBT)!
2. **Strict Inequalities in Invariant Proofs**: Graders penalize writing $2i+1 \ge i$. You MUST write $2i+1 > i$ and $2i+2 > i$ for $i \ge 0$.
3. **Closure Loop Trap**: If a lambda in a loop uses `step` without a default argument, it evaluates to the **last loop value**. If it uses `s=step`, it binds **eagerly**.
4. **Deadlock Trace**: Show that Thread 1 holds Lock 1 waiting for Lock 2, while Thread 2 holds Lock 2 waiting for Lock 1. State the fix: **Global lock acquisition order**.
5. **Fast Build Heap vs Naive**:
   - Naive (top-down repeated insert): $O(n \log n)$ because leaves ($\approx n/2$ nodes) do the maximum work ($O(\log n)$ sift-up).
   - Bottom-Up Fast Build: $O(n)$ because leaves ($\approx n/2$ nodes) do **0 work**, and only 1 node does $O(\log n)$ sift-down!
