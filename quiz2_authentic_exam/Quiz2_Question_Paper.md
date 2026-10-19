# COL1101-Diwali2026 Quiz 2 Duration: 1 hour

**Name**: ____________________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Entry number**: ________________________  
**Course**: COL1101 (Data Structures and Algorithms)  
**Total Points**: 20 pts  

---

### Instructions:
- This exam consists of **3 questions** totaling **20 points**.
- Write your answers clearly and concisely in the space provided.
- For Question 1, answers with incorrect or missing justification get 0 points.
- In this course, the **height $h$ of a binary tree** is defined as the number of levels ($h = \text{max\_depth} + 1$, where the empty tree has height 0 and a single-node tree has height 1).

---

## 1. Binary Min-Heap Permutations & Ancestor Properties [6 points]

Recall that a **binary min-heap** containing distinct elements $\{0, 1, \dots, n-1\}$ is an Almost Complete Binary Tree (ACBT) stored in a 0-indexed contiguous array $A[0 \dots n-1]$ mapped via Level-Order Traversal (LOT). 
For any node at index $i$:
- Its left child (if it exists) is at index $2i + 1$.
- Its right child (if it exists) is at index $2i + 2$.
- Its parent (for $i > 0$) is at index $\lfloor (i - 1) / 2 \rfloor$.

The **min-heap order property** mandates that for every index $i > 0$:
$$A[\lfloor (i - 1) / 2 \rfloor] < A[i]$$

Let $n = 7$ (a Complete Binary Tree of height $h = 3$ with indices $0, 1, 2, 3, 4, 5, 6$). Determine whether each of the following permutations of $\{0, 1, 2, 3, 4, 5, 6\}$ represents a valid binary min-heap stored in array $A[0 \dots 6]$, and justify your answer (**answers with incorrect justification get 0 points**):

**(a)** (2 points) $A = [0, 2, 1, 5, 4, 6, 3]$

\
\
\
\
\
____________________________________________________________________________________________________

**(b)** (2 points) $A = [0, 3, 1, 2, 4, 5, 6]$

\
\
\
\
\
____________________________________________________________________________________________________

**(c)** (2 points) Now consider a binary min-heap containing $n = 15$ distinct elements stored in array $A[0 \dots 14]$. Determine whether the **3rd smallest** element can reside at index 7. Justify your answer.

\
\
\
\
\
____________________________________________________________________________________________________

---

## 2. Python Semantics: Closures & Concurrency [6 points]

Study the following program carefully, then answer parts (a) and (b). Assume it runs top to bottom with no errors.

```python
import threading
from functools import reduce

# Part 1: Closures and higher-order pipeline
def make_pipeline(base):
    ops = []
    for step in [1, 2, 3]:
        ops.append(lambda x, s=step: x + s * base)
    
    late_ops = []
    for step in [1, 2, 3]:
        late_ops.append(lambda x: x + step * base)
        
    return ops, late_ops

ops, late_ops = make_pipeline(2)
pipe_a = lambda x: reduce(lambda acc, f: f(acc), ops, x)
pipe_b = lambda x: reduce(lambda acc, f: f(acc), late_ops, x)

# Part 2: Shared account with locks
class Account:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()

    def deposit_unsafe(self, amt):
        t = self.balance
        # Context switch simulated at critical instant
        self.balance = t + amt

    def deposit_safe(self, amt):
        with self.lock:
            t = self.balance
            self.balance = t + amt
```

**(a)** (3 points)
1. Give the exact integer output of `print(pipe_a(10))`. Show the intermediate accumulator values produced by `reduce`.
2. Give the exact integer output of `print(pipe_b(10))`.
3. Explain the precise difference in Python variable scoping and closure binding between `ops` and `late_ops` that causes this discrepancy.

\
\
\
\
\
\
\
____________________________________________________________________________________________________

**(b)** (3 points)
1. Suppose `acc = Account(100)`. Two threads $T_1$ and $T_2$ concurrently execute:
   - $T_1$ executes `acc.deposit_unsafe(10)`
   - $T_2$ executes `acc.deposit_unsafe(20)`  
   Describe a specific interleaving execution trace (in terms of read and write steps of $T_1$ and $T_2$) that causes a **lost update**, and state the final value of `acc.balance` in your trace.
2. Suppose two accounts `acc1` and `acc2` are initialized. Thread $T_1$ executes:
   ```python
   with acc1.lock:
       with acc2.lock:
           transfer(acc1, acc2, 10)
   ```
   while Thread $T_2$ concurrently executes:
   ```python
   with acc2.lock:
       with acc1.lock:
           transfer(acc2, acc1, 10)
   ```
   Provide an explicit interleaving trace showing how a **deadlock** occurs, and explain how to prevent this deadlock without changing the lock implementation.

\
\
\
\
\
\
\
____________________________________________________________________________________________________

---

## 3. Formal Correctness & Complexity of Fast Build Heap [8 points]

Recall the Fast Build Heap algorithm taught in Lecture 21 of this course, which converts an arbitrary array $A$ of $n$ elements into a binary min-heap in bottom-up fashion:

```python
def fast_build_min_heap(A):
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        heap_down(A, i, n)
```

Here, `heap_down(A, i, n)` sifts $A[i]$ down by repeatedly swapping it with its smaller child until the subtree rooted at index $i$ satisfies the min-heap property. `heap_down` assumes that the left and right subtrees of index $i$ (rooted at $2i + 1$ and $2i + 2$) are already valid min-heaps.

For any index $k \in \{0, 1, \dots, n-1\}$, let $T_k$ denote the subtree rooted at index $k$.

We are going to prove the correctness of `fast_build_min_heap` by establishing that for every iteration of the `for` loop, the following statement is an invariant:
$$\mathcal{P}(i): \text{"For every index } j \in \{i+1, i+2, \dots, n-1\}, \text{ the subtree } T_j \text{ is a valid binary min-heap."}$$

Clearly, prior to the first iteration of the `for` loop (when $i = \lfloor n/2 \rfloor - 1$), the statement $\mathcal{P}(\lfloor n/2 \rfloor - 1)$ holds because all nodes with index $j \ge \lfloor n/2 \rfloor$ are leaf nodes in an ACBT of size $n$, and any single-node subtree is vacuously a valid min-heap.

---

**(a)** (3 points) Suppose that immediately before executing the loop for an arbitrary index $i$ ($0 \le i \le \lfloor n/2 \rfloor - 1$), the statement $\mathcal{P}(i)$ holds. Prove (ideally, in at most four sentences) that after executing `heap_down(A, i, n)`, the statement $\mathcal{P}(i-1)$ holds.

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

**(b)** (1 point) Hence, prove (ideally, in at most two sentences) that when `fast_build_min_heap` terminates, the array $A$ represents a valid binary min-heap across all $n$ elements. *(For this part, you may assume that $\mathcal{P}(i)$ is a loop invariant even if you couldn't prove it in the earlier part.)*

\
\
\
\
____________________________________________________________________________________________________

**(c)** (1 point) Why does a call to the function `fast_build_min_heap` necessarily terminate?

\
\
\
\
____________________________________________________________________________________________________

**(d)** (3 points) Let $T(n)$ denote the worst-case number of key comparisons performed by `fast_build_min_heap` on an array of size $n$.
1. Express $T(n)$ as a summation across node heights $h \in \{1, 2, \dots, \lfloor \log_2 n \rfloor\}$, where leaves have height $h = 0$, given that an ACBT of size $n$ has at most $\lceil \frac{n}{2^{h+1}} \rceil$ nodes at height $h$.
2. Evaluate the summation rigorously using the Arithmetico-Geometric Progression (AGP) technique by computing $S - \frac{1}{2}S$ for $S = \sum_{h=1}^{\infty} \frac{h}{2^h}$.
3. Deduce that $T(n) = \Theta(n)$.

\
\
\
\
\
\
\
\
____________________________________________________________________________________________________
