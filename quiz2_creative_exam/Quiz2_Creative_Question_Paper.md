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

## 1. Min-Max Heap Duality & Ancestor Rank Bounds [6 points]

Recall that an Almost Complete Binary Tree (ACBT) of size $n$ is stored in a 0-indexed contiguous array $A[0 \dots n-1]$ mapped via Level-Order Traversal (LOT).
- In a **binary min-heap**, for every node $i > 0$, $A[\lfloor (i - 1) / 2 \rfloor] < A[i]$.
- In a **binary max-heap**, for every node $i > 0$, $A[\lfloor (i - 1) / 2 \rfloor] > A[i]$.

Let $S = \{1, 2, 3, 4, 5, 6, 7\}$ be a set of 7 distinct integers. Answer parts (a) and (b) below (**answers with incorrect justification get 0 points**):

**(a)** (2 points) Suppose $H_1$ is a valid binary min-heap and $H_2$ is a valid binary max-heap, both of size $n = 7$ and both containing the exact same set of elements $S$.  
Determine whether it is possible for both heaps to have the exact same element at index 1 (that is, $H_1[1] = H_2[1]$).  
If yes, provide an explicit valid array for both $H_1$ and $H_2$. If not, prove why it is impossible.

\
\
\
\
\
\
____________________________________________________________________________________________________

**(b)** (2 points) Again consider a binary min-heap $H_1$ and a binary max-heap $H_2$, both of size $n = 7$ containing the set $S$.  
Determine whether it is possible for $H_1[0] = H_2[2]$. Justify your answer rigorously using the structural and ordering properties of heaps.

\
\
\
\
\
\
____________________________________________________________________________________________________

**(c)** (2 points) Consider an ACBT of size $n = 30$ stored as a 0-indexed array $A[0 \dots 29]$ representing a valid binary min-heap of 30 distinct elements.  
Determine the exact range of array indices $[i_{\min}, i_{\max}]$ where the **4th smallest** element can possibly reside.  
Prove why no index outside this range can hold the 4th smallest element.

\
\
\
\
\
\
____________________________________________________________________________________________________

---

## 2. Python Semantics: Discount Pipeline & Concurrent Ledger [6 points]

Study the following program carefully, then answer parts (a) and (b). Assume it runs top to bottom with no errors.

```python
import threading
from functools import reduce

# Section 1: Discount Pipeline Engine
def make_discount_pipeline(rates):
    # rates is a list of percentage discounts, e.g. [10, 20, 50]
    rules_eager = []
    for r in rates:
        rules_eager.append(lambda amt, rate=r: amt - (amt * rate) // 100)
        
    rules_late = []
    for r in rates:
        rules_late.append(lambda amt: amt - (amt * r) // 100)
        
    return rules_eager, rules_late

eager_rules, late_rules = make_discount_pipeline([10, 20, 50])
apply_eager = lambda x: reduce(lambda acc, f: f(acc), eager_rules, x)
apply_late = lambda x: reduce(lambda acc, f: f(acc), late_rules, x)

# Section 2: Shared Bank Ledger
class Ledger:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.lock = threading.Lock()

    def withdraw_unsafe(self, amt):
        current = self.balance
        # Context switch simulated at critical instant
        self.balance = current - amt

    def withdraw_safe(self, amt):
        with self.lock:
            current = self.balance
            self.balance = current - amt

def transfer_flawed(acc_from, acc_to, amt):
    with acc_from.lock:
        with acc_to.lock:
            acc_from.balance -= amt
            acc_to.balance += amt
```

**(a)** (3 points)
1. Compute the exact integer output of `print(apply_eager(1000))`. Show the value of the accumulator `acc` after each of the three pipeline stages.
2. Compute the exact integer output of `print(apply_late(1000))`.
3. Explain why `apply_late(1000)` produces your answer in part 2 rather than 360. In your explanation, explicitly contrast the CPython evaluation timing of parameter default tuples (`__defaults__`) versus closure cell objects (`__closure__`).

\
\
\
\
\
\
\
____________________________________________________________________________________________________

**(b)** (3 points)
1. Suppose `acc = Ledger(1000)`. Two customer threads $T_1$ and $T_2$ concurrently invoke:
   - $T_1$: `acc.withdraw_unsafe(400)`
   - $T_2$: `acc.withdraw_unsafe(700)`  
   Provide a concrete interleaving execution trace (showing the exact read and write operations of $T_1$ and $T_2$) that results in a **lost update** producing a final balance of `600`. Explain why the bank lost money.
2. Suppose Alice and Bob simultaneously transfer money to each other:
   - Thread 1 (Alice): `transfer_flawed(accA, accB, 100)`
   - Thread 2 (Bob): `transfer_flawed(accB, accA, 50)`  
   Show an explicit interleaving execution trace that causes a **deadlock**. Then, write a corrected Python function `transfer_correct(acc1, acc2, amt)` that guarantees deadlock-freedom, and state the formal invariant that eliminates circular wait.

\
\
\
\
\
\
\
____________________________________________________________________________________________________

---

## 3. Formal Invariant Induction & Complexity of Fast Build Heap [8 points]

Recall the Fast Build Heap algorithm from Lecture 21:

```python
def fast_build_min_heap(A):
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        heap_down(A, i, n)
```

where `heap_down(A, i, n)` sifts $A[i]$ down by repeatedly swapping it with its smaller child until the subtree rooted at index $i$ satisfies the min-heap property. `heap_down` assumes that the left and right subtrees of index $i$ (rooted at $2i + 1$ and $2i + 2$) are already valid min-heaps.

For any index $k \in \{0, 1, \dots, n-1\}$, let $T_k$ denote the subtree rooted at index $k$.

Consider the loop invariant for the `for` loop, parameterized by the loop counter $i$:
$$\mathcal{P}(i): \text{"For every index } j \in \{i+1, i+2, \dots, n-1\}, \text{ the subtree } T_j \text{ is a valid binary min-heap."}$$

Prior to the first iteration of the `for` loop (when $i = \lfloor n/2 \rfloor - 1$), the statement $\mathcal{P}(\lfloor n/2 \rfloor - 1)$ holds because all nodes with index $j \ge \lfloor n/2 \rfloor$ are leaf nodes in an ACBT of size $n$, and any single-node subtree is vacuously a valid min-heap.

---

**(a)** (3 points) Suppose that immediately before executing the loop for an arbitrary index $i$ ($0 \le i \le \lfloor n/2 \rfloor - 1$), statement $\mathcal{P}(i)$ holds. Prove (ideally, in at most four sentences) that after executing `heap_down(A, i, n)`, statement $\mathcal{P}(i-1)$ holds.  
*(Your proof must show why child indices satisfy $2i + 1 > i$ and $2i + 2 > i$, satisfy the precondition of `heap_down`, and why subtrees $T_j$ for $j > i$ are not invalidated).*

\
\
\
\
\
\
\
\
____________________________________________________________________________________________________

**(b)** (1 point) Hence, prove (ideally, in at most two sentences) that when `fast_build_min_heap` terminates, the entire array $A$ represents a valid binary min-heap. *(You may assume $\mathcal{P}(i)$ is a valid loop invariant).*

\
\
\
\
____________________________________________________________________________________________________

**(c)** (1 point) Why does a call to `fast_build_min_heap` necessarily terminate? State a well-founded metric that strictly decreases.

\
\
\
\
____________________________________________________________________________________________________

**(d)** (3 points)
1. Express the worst-case number of key comparisons $T(n)$ performed by `fast_build_min_heap` as a summation across node heights $h \in \{1, 2, \dots, \lfloor \log_2 n \rfloor\}$, given that an ACBT of size $n$ has at most $\lceil \frac{n}{2^{h+1}} \rceil$ nodes at height $h$, and sifting down a node at height $h$ takes at most $2h$ comparisons.
2. Solve the summation rigorously using the Arithmetico-Geometric Progression (AGP) method by computing $S - \frac{1}{2}S$ for $S = \sum_{h=1}^{\infty} \frac{h}{2^h}$.
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
