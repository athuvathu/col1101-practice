# COL1101-Diwali2026 Quiz 2

**Name**: ____________________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Entry number**: ________________________  
**Course**: COL1101 (Data Structures and Algorithms)  
**Date**: 19 September 2026 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Duration**: 1 hour &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Total Points**: 20 pts  

---

### Instructions:
- This exam consists of **3 questions** totaling **20 points**.
- Write your answers clearly and concisely in the space provided.
- For all proofs, state your inductive hypotheses, base cases, contradiction steps, and justifications explicitly.
- In this course, the **height $h$ of a binary tree** is defined as the number of nodes on the longest root-to-leaf path ($h \ge 1$ for non-empty trees; $h = 0$ for the empty tree).
- Assume standard 64-bit Linux execution environment with CPython 3.

---

## Question 1: Algorithmic Concepts & Architectural Foundations [6 points]

### 1.1 Tree & Min-Heap Structural Bounds (2 points)

Recall that an **Almost Complete Binary Tree (ACBT)** of height $h$ is a binary tree in which every level $l \in \{0, 1, \dots, h-2\}$ is completely full (containing $2^l$ nodes), and all nodes at the bottommost level $h-1$ are packed as far to the left as possible.

Consider an ACBT containing exactly $n = 50$ nodes, mapped into a standard 0-indexed contiguous array $A[0 \dots 49]$ via Level-Order Traversal (LOT), such that for node $i$, its left child is at $2i + 1$, its right child is at $2i + 2$, and its parent is at $\lfloor (i - 1) / 2 \rfloor$.

**(a)** (0.5 points) Determine the exact height $h$ of this tree. Show the inequality relating $n$ and $h$.

\
\
\
____________________________________________________________________________________________________

**(b)** (0.5 points) What is the exact index range $[i_{\min}, i_{\max}]$ in array $A$ that contains all leaf nodes? Justify in one sentence.

\
\
\
____________________________________________________________________________________________________

**(c)** (1.0 point) Suppose array $A$ represents a valid **binary min-heap** of $n = 50$ *distinct* integers. 
- What is the maximum depth (distance from the root, where root is depth 0) at which the **3rd smallest** element can appear?
- List all possible array indices in $A$ where the 3rd smallest element could possibly be located. Provide a rigorous justification explaining why no node at greater depth can hold this element.

\
\
\
\
\
\
____________________________________________________________________________________________________

---

#### 1.2 Level-Order Traversal & Queue Invariant (2 points)

Recall the Level-Order Traversal (LOT) algorithm from Lecture 18, which traverses a binary tree using a FIFO queue $Q$, initialized with `Q.enqueue(root)`. In each iteration, LOT executes:
```python
x = Q.dequeue()
visit(x)
if x.left is not None:  Q.enqueue(x.left)
if x.right is not None: Q.enqueue(x.right)
```

Suppose LOT is executed on a Complete Binary Tree (CBT) of height $h = 4$ containing exactly $n = 15$ nodes labeled $1, 2, \dots, 15$ in level-order (so root is 1, level 1 is 2, 3, level 2 is 4, 5, 6, 7, and level 3 is 8 through 15).

**(a)** (0.5 points) State the formal **Loop Invariant** for queue $Q$ taught in Lecture 18 regarding the depths of nodes currently present in $Q$ at any iteration.

\
\
\
____________________________________________________________________________________________________

**(b)** (1.5 points) At the exact instant when node 5 is dequeued from the front of $Q$ and its children are enqueued:
- List every node currently present in $Q$, in order from front to back.
- Rigorously justify your answer using the loop invariant and stating which nodes have already been visited.

\
\
\
\
\
\
____________________________________________________________________________________________________

---

### 1.3 Concurrency: Threads, Processes & Deadlock (2 points)

**(a)** (0.5 points) In modern operating systems, state the fundamental difference between a **process** and a **thread** regarding memory space, and state why threads are vulnerable to race conditions while processes are not.

\
\
\
____________________________________________________________________________________________________

**(b)** (1.0 point) Consider two threads $T_1$ and $T_2$ and two locks `L1 = threading.Lock()` and `L2 = threading.Lock()`.
- Thread 1 executes: `with L1: with L2: work()`
- Thread 2 executes: `with L2: with L1: work()`
Provide an explicit interleaving execution trace showing how a **deadlock** occurs.

\
\
\
\
\
\
____________________________________________________________________________________________________

**(c)** (0.5 points) In Lecture 16, two alternative concurrency paradigms are introduced to avoid locks entirely: (1) **Functional Programming** and (2) the **Actor Model**. In one or two sentences each, explain how each paradigm guarantees freedom from race conditions without using locks.

\
\
\
____________________________________________________________________________________________________

---

## Question 2: Code Execution, Scoping & Concurrency [6 points]

Study the two Python 3 programs below carefully, then answer parts 2.1 and 2.2. Assume they execute from top to bottom on a standard CPython 3 interpreter without errors.

### 2.1 Functional Scoping, Closures & Late Binding (3 points)

Consider the following Python function that constructs and returns two lists of closures:

```python
def make_evaluators(init=1):
    funcs = []
    for step in [2, 3, 5]:
        funcs.append(lambda x, s=step: x + s * 2 + init)
    
    late_funcs = []
    for step in [2, 3, 5]:
        late_funcs.append(lambda x: x + step * 3 + init)
        
    return funcs, late_funcs

f, l = make_evaluators(1)
res_a = f[2](5)
res_b = l[0](3)
print(res_a)
print(res_b)
```

**(a)** (1.0 point) What is the exact integer output printed by `print(res_a)`? Show your step-by-step arithmetic.

\
\
\
____________________________________________________________________________________________________

**(b)** (1.0 point) What is the exact integer output printed by `print(res_b)`? Show your step-by-step arithmetic.

\
\
\
____________________________________________________________________________________________________

**(c)** (1.0 point) Explain why `l[0](3)` evaluates to your answer in part (b) rather than $3 + 2 \times 3 + 1 = 10$. In your explanation, explicitly contrast **definition-time default argument binding** (`s=step`) versus **enclosing scope lexical name lookup via cell objects** (late binding).

\
\
\
\
\
\
____________________________________________________________________________________________________

---

### 2.2 Heap-Down Sift Trace & Thread-Safe Synchronization (3 points)

The function `heap_down(H, i, n)` below restores the min-heap property on an array $H$ of length $n$ starting at node $i$:

```python
def heap_down(H, i, n):
    while 2 * i + 1 < n:
        left = 2 * i + 1
        right = 2 * i + 2
        smallest = left
        if right < n and H[right] < H[left]:
            smallest = right
        if H[i] <= H[smallest]:
            break
        H[i], H[smallest] = H[smallest], H[i]
        i = smallest
```

**(a)** (1.0 point) Let $H = [40, 10, 20, 15, 12, 25, 30]$ with $n = 7$. Trace the execution of `heap_down(H, 0, 7)`. 
- State which indices are swapped at each step.
- Write the exact array contents after each swap.
- Give the final contents of $H$ upon loop termination.

\
\
\
\
\
\
____________________________________________________________________________________________________

**(b)** (1.0 point) Suppose two threads $T_1$ and $T_2$ share the same array $H$. $T_1$ invokes `heap_down(H, 0, 7)` while $T_2$ concurrently invokes `heap_down(H, 1, 7)` with no synchronization. Describe a specific interleaving of operations between $T_1$ and $T_2$ that causes a race condition (e.g. data loss or violation of the heap invariant).

\
\
\
\
\
\
____________________________________________________________________________________________________

**(c)** (1.0 point) Write a thread-safe wrapper function `safe_heap_down(H, i, n, lock)` in Python using `threading.Lock`. Explain why mutual exclusion restores linearizability/serializability.

\
\
\
\
\
\
____________________________________________________________________________________________________

---

## Question 3: Formal Correctness & Algorithmic Analysis of Fast Build-Heap [8 points]

Consider the following bottom-up algorithm `fast_build_min_heap(A)` which constructs a binary min-heap in-place from an arbitrary array $A$ of $n$ elements:

```python
def fast_build_min_heap(A):
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        heap_down(A, i, n)
```

where `heap_down(A, i, n)` is identical to the function defined in Question 2.2.

We wish to formally prove the correctness and analyze the worst-case running time of `fast_build_min_heap`.

For any index $k \in \{0, 1, \dots, n-1\}$, let $T_k$ denote the subtree rooted at index $k$.

Consider the following loop invariant for the `for` loop, parameterized by the loop counter $i$:
$$\mathcal{P}(i): \text{For every index } j \in \{i+1, i+2, \dots, n-1\}, \text{ the subtree } T_j \text{ satisfies the binary min-heap property.}$$

---

### 3.1 Loop Invariant Inductive Step (3 points)

**(a)** (0.5 points) **Base Case**: Prove that $\mathcal{P}(\lfloor n/2 \rfloor - 1)$ holds prior to the first iteration of the `for` loop. (Hint: Consider the children of nodes with index $j \ge \lfloor n/2 \rfloor$).

\
\
\
____________________________________________________________________________________________________

**(b)** (2.5 points) **Inductive Step**: Assume that $\mathcal{P}(i)$ holds immediately before the loop executes for index $i$ ($0 \le i \le \lfloor n/2 \rfloor - 1$). Prove that immediately after `heap_down(A, i, n)` executes, $\mathcal{P}(i-1)$ holds. 
*(Your proof must establish: (1) why the preconditions of `heap_down` on node $i$ are satisfied, (2) that $T_i$ becomes a valid min-heap, and (3) why no previously verified subtree $T_j$ ($j > i$) has its heap property destroyed).*

\
\
\
\
\
\
\
\
\
\
\
\
____________________________________________________________________________________________________

---

### 3.2 Correctness upon Termination (1 point)

Hence, prove (in at most three sentences) that when `fast_build_min_heap` terminates, the entire array $A$ represents a valid binary min-heap.

\
\
\
\
\
____________________________________________________________________________________________________

---

### 3.3 Termination Argument (1 point)

Define a well-founded termination metric for the execution of `fast_build_min_heap` (accounting for both the outer `for` loop and the inner `while` loop of `heap_down`) and prove that the algorithm must terminate in a finite number of steps.

\
\
\
\
\
____________________________________________________________________________________________________

---

### 3.4 Asymptotic Time Complexity Analysis (3 points)

Unlike naive heap construction (which repeatedly inserts elements and takes $\Theta(n \log n)$ time), `fast_build_min_heap` achieves linear time complexity $\Theta(n)$.

Let the **height** of a node $v$ in an ACBT be defined as the length of the longest simple path from $v$ down to a leaf in its subtree (so leaves have height 0, their parents height 1, etc.).

**(a)** (1.0 point) Express the worst-case running time $T(n)$ of `fast_build_min_heap` as a summation over node heights $h$, from $h = 1$ to $\lfloor \log_2 n \rfloor$. State the upper bound on the number of nodes at height $h$ in an ACBT of size $n$, and the maximum work done by `heap_down` on a node of height $h$.

\
\
\
\
\
____________________________________________________________________________________________________

**(b)** (1.5 points) Evaluate the infinite Arithmetico-Geometric Progression (AGP):
$$S = \sum_{h=1}^{\infty} \frac{h}{2^h}$$
Solve this summation rigorously by unrolling and computing $S - \frac{1}{2}S$.

\
\
\
\
\
\
\
\
____________________________________________________________________________________________________

**(c)** (0.5 points) Substitute the evaluated summation back into your bound for $T(n)$ to prove that $T(n) = \Theta(n)$.

\
\
\
\
\
____________________________________________________________________________________________________
