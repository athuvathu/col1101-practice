# Module 05: Non-Blocking Algorithms & Lock-Free Data Structures

---

## 1. Linearizability vs Serializability

The correctness of concurrent data structures requires a rigorous mathematical criterion. Maurice Herlihy and Jeannette Wing (1990) introduced **Linearizability**.

### 1.1 Formal Definition of Linearizability
An operation $op$ executed by a thread is an interval bounded by an invocation event $\text{inv}(op)$ at physical time $t_{\text{start}}(op)$ and a response event $\text{res}(op)$ at physical time $t_{\text{end}}(op)$.
The **real-time order** $\prec_{RT}$ on operations is defined as:
$$op_1 \prec_{RT} op_2 \iff t_{\text{end}}(op_1) < t_{\text{start}}(op_2)$$

A concurrent execution history $H$ is **linearizable** if there exists a valid sequential execution history $S$ containing the same operations such that:
1. **Sequential Specification**: $S$ satisfies the single-threaded sequential semantics of the data structure (e.g. FIFO for queue, LIFO for stack).
2. **Real-Time Precedence Preservation**:
   $$\forall op_1, op_2 \in H, \quad op_1 \prec_{RT} op_2 \implies op_1 <_S op_2$$

**Operational Interpretation (The Linearization Point)**:
Every operation $op$ must appear to take effect instantaneously at a discrete, atomic point in physical time:
$$t_{\text{LP}}(op) \in [t_{\text{start}}(op), \; t_{\text{end}}(op)]$$

### 1.2 The Locality (Composability) Theorem
Linearizability is a **local** (composable) property:
> **Theorem (Herlihy & Wing 1990)**:
> A concurrent system execution history $H$ is linearizable if and only if for every individual shared object $x$, the projection of history $H$ onto object $x$ ($H \mid x$) is linearizable.

*Significance*: You can design, verify, and prove the correctness of concurrent data structures modularly. If Queue $A$ and Stack $B$ are individually linearizable, their combined system is automatically linearizable.

### 1.3 Linearizability vs Serializability
Linearizability and Serializability are fundamentally different concepts:

| Property | Linearizability | Serializability (Database Transactions) |
|---|---|---|
| **Origin** | Herlihy & Wing (1990) | Papadimitriou (1979) |
| **Target** | Single operations on individual concurrent objects | Multi-operation transactions across many records |
| **Real-time order** | **Mandatory**: Preserves wall-clock non-overlapping precedence ($\prec_{RT}$). | **Ignored**: Requires only that execution matches *some* serial order, even if order contradicts real-time. |
| **Composability** | **Composably Local**: System is linearizable iff each object is linearizable. | **Non-Composable**: Union of serializable subsystems is not necessarily serializable. |

**Strict Serializability (External Consistency)**: The intersection of both: a transactional schedule that is both serializable and linearizable.

---

## 2. Non-Blocking Progress Hierarchy

Non-blocking synchronization avoids OS mutexes, guaranteeing forward progress even when threads are arbitrarily delayed or suspended.

```
+-------------------------------------------------------------+
|                     Obstruction-Free                        |
|   +-----------------------------------------------------+   |
|   |                   Lock-Free                         |   |
|   |   +---------------------------------------------+   |   |
|   |   |                 Wait-Free                   |   |   |
|   |   +---------------------------------------------+   |   |
|   +-----------------------------------------------------+   |
+-------------------------------------------------------------+
               Wait-Free  subset  Lock-Free  subset  Obstruction-Free
```

### 2.1 Obstruction-Freedom (Herlihy, Luchangco, Moir 2003)
A method is **Obstruction-Free** if any thread, executing in isolation (all competing threads suspended or delayed), completes its operation in a bounded number of steps.
- Solves livelock using contention managers or randomized backoff.
- Weakest non-blocking guarantee.

### 2.2 Lock-Freedom (System-Wide Progress)
A data structure is **Lock-Free** if infinitely often, at least one active thread completes an operation in a finite number of system execution steps:
$$\forall \text{ infinite traces } \tau, \quad \sum_{op \in \text{CompletedOps}} 1 = \infty$$
- **Property**: The system as a whole makes forward progress.
- **Starvation**: Individual threads may starve due to repeated contention, but a total system stall/deadlock is mathematically impossible.

### 2.3 Wait-Freedom (Per-Thread Progress / Starvation-Free)
A data structure is **Wait-Free** if **every thread** completes its operation in a bounded number of its own execution steps, regardless of the execution speed or scheduling of other threads:
$$\forall i \in \{1, \dots, N\}, \; \forall op \in \text{Ops}_i, \quad \text{steps}(op) \le B < \infty$$
- **Property**: Complete immunity to starvation, priority inversion, and indefinite delays.
- Subtypes:
  - *Population-Oblivious Wait-Free*: Bound $B$ depends only on the algorithm, independent of the number of threads $N$.
  - *Population-Dependent Wait-Free*: Bound $B(N)$ scales with thread count $N$.

---

## 3. The ABA Problem and Memory Reclamation

The ABA problem is a fatal concurrency hazard inherent to atomic Read-Modify-Write primitives (like CAS) operating on raw memory addresses.

### 3.1 Step-by-Step Memory Corruption Trace
Consider a concurrent stack implemented as a singly-linked list:
`Top -> A -> B -> C`

```
Initial State:
  Top ----> [ Node A ] ----> [ Node B ] ----> [ Node C ]
```

1. **Thread 1 intends to pop**:
   - Reads `old_top = Top` (which is `&A`).
   - Reads `next_node = old_top->next` (which is `&B`).
   - *Thread 1 is preempted immediately before executing CAS!*
2. **Thread 2 executes while Thread 1 sleeps**:
   - Thread 2 pops `A`: `Top` becomes `B`. `free(A)` is called.
   - Thread 2 pops `B`: `Top` becomes `C`. `free(B)` is called.
   - Thread 2 creates a new node $D$ and pushes it: `Top -> D -> C`.
   - Thread 2 pushes an element whose allocated memory address happens to be identical to `&A` (standard behavior of memory allocators reusing recently freed blocks).
   - New stack state: `Top -> A -> D -> C`.
3. **Thread 1 awakens and executes its CAS**:
   ```c
   CAS(&Top, old_top, next_node); // CAS(&Top, &A, &B)
   ```
4. **The Disaster**:
   - CAS compares the bitwise address: `*Top == &A`.
   - The comparison succeeds because address `&A` was recycled!
   - CAS sets `Top = next_node` (which is `&B`).
   - **Catastrophic Failure**: `B` was already freed in Step 2! The stack top now points to deallocated or corrupted memory. Node $D$ is orphaned and leaked.

```
Corrupted State after Thread 1's CAS:
  Top ----> [ Node B (FREED / GARBAGE) ]
  (Node D is leaked; Node A is detached; memory is corrupted)
```

### 3.2 Mitigation 1: Tagged Pointers / Double-Width CAS
We couple every memory pointer with an integer version counter (tag):
$$\text{TaggedPointer} = \langle \text{address}: 64\text{ bits}, \; \text{tag}: 64\text{ bits} \rangle$$
Every update increments the tag:
```c
struct TaggedPointer {
    Node* ptr;
    uint64_t tag;
};
```
In Step 2, when Thread 2 pushes `A` back, the tag increments:
$$(A, 0) \to (B, 1) \to (C, 2) \to (A, 3)$$
When Thread 1 executes CAS expecting `(A, 0)`, the check fails because current value is `(A, 3)`.
Implemented via hardware Double-Width CAS:
- x86-64: `CMPXCHG16B`
- ARM64: `CASP` or `LDXP/STXP`

### 3.3 Mitigation 2: Safe Memory Reclamation (SMR)
The ABA problem fundamentally occurs because memory is reclaimed while another thread holds a dangling pointer. SMR prevents memory from being freed until all active references vanish.

#### 1. Hazard Pointers (Maged Michael, 2004)
- Each thread owns a small set of global single-writer, multi-reader `HazardPointer` slots.
- Before dereferencing a node $N$, a thread stores $N$ into its hazard pointer and validates that $N$ is still current.
- When a thread detaches a node, it places it into a thread-local retirement list.
- A retired node is freed if and only if it does not match any active hazard pointer across all threads in the system.

#### 2. Epoch-Based Reclamation (EBR)
- The system maintains a global integer epoch counter $E \in \{0, 1, 2\}$.
- Active threads register their entry into the current epoch.
- When an object is retired in epoch $E$, its reclamation is deferred to epoch $(E + 2) \pmod 3$.
- The global epoch advances only when all threads have exited epoch $E-1$.
- Advantage: Extremely fast ($O(1)$ read overhead); disadvantage: a suspended thread stalls reclamation for the entire system.

#### 3. Read-Copy-Update (RCU)
- Readers execute with zero synchronization overhead (pure memory loads).
- Writers allocate a new copy of the data structure, mutate it, and atomically swing the pointer.
- The writer then waits for a **Grace Period** (until all CPU cores have undergone a context switch / quiescent state) before freeing the old version.

---

## 4. Canonical Lock-Free Data Structures

### 4.1 The Treiber Stack (R. Kent Treiber, 1986)
A lock-free LIFO stack represented as a singly-linked list.

```cpp
template <typename T>
class TreiberStack {
    struct Node {
        T value;
        Node* next;
        Node(T val) : value(val), next(nullptr) {}
    };

    std::atomic<Node*> head{nullptr};

public:
    void push(T val) {
        Node* new_node = new Node(val);
        new_node->next = head.load(std::memory_order_relaxed);
        // Linearization Point: successful CAS
        while (!head.compare_exchange_weak(new_node->next, new_node,
                                           std::memory_order_release,
                                           std::memory_order_relaxed)) {
            // Spin: new_node->next is automatically updated with current head
        }
    }

    bool pop(T& result) {
        Node* old_head = head.load(std::memory_order_relaxed);
        while (old_head != nullptr) {
            // Linearization Point: successful CAS (or detecting old_head == nullptr)
            if (head.compare_exchange_weak(old_head, old_head->next,
                                           std::memory_order_acquire,
                                           std::memory_order_relaxed)) {
                result = old_head->value;
                // Note: old_head must be retired via SMR to prevent ABA / use-after-free
                delete old_head;
                return true;
            }
        }
        return false; // Stack empty
    }
};
```

**Linearization Points**:
- `push()`: The instant the `CAS(&head, old_head, new_node)` succeeds.
- `pop()` on non-empty: The instant the `CAS(&head, old_head, old_head->next)` succeeds.
- `pop()` on empty: The instant `head.load()` returns `nullptr`.

---

### 4.2 The Michael-Scott Queue (Maged Michael & Michael Scott, 1996)
A lock-free FIFO queue using a singly-linked list with a **sentinel dummy node**.

```
Head                                        Tail
  |                                           |
  v                                           v
[ Dummy Node ] -- next --> [ Node 1 ] -- next --> [ Node 2 ] -- next --> NULL
```

#### The Helping Mechanism
In concurrent queues, appending a node requires two distinct pointer updates:
1. `Tail->next = new_node` (links new node to end of queue).
2. `Tail = new_node` (swings tail pointer forward).

Because hardware CAS updates only **one** memory address atomically, an unassisted queue could be stalled if a thread is preempted between Step 1 and Step 2.
**The MS-Queue Innovation**: Any thread that encounters a lagging tail pointer (`tail->next != NULL`) **helps** advance the tail before proceeding with its own operation.

```cpp
template <typename T>
class MSQueue {
    struct Node {
        T value;
        std::atomic<Node*> next{nullptr};
        Node() = default;
        Node(T val) : value(val) {}
    };

    std::atomic<Node*> head;
    std::atomic<Node*> tail;

public:
    MSQueue() {
        Node* sentinel = new Node();
        head.store(sentinel);
        tail.store(sentinel);
    }

    void enqueue(T val) {
        Node* new_node = new Node(val);
        while (true) {
            Node* cur_tail = tail.load(std::memory_order_acquire);
            Node* next = cur_tail->next.load(std::memory_order_acquire);

            if (cur_tail == tail.load(std::memory_order_relaxed)) {
                if (next == nullptr) {
                    // Linearization Point 1: Link node to tail
                    if (cur_tail->next.compare_exchange_weak(next, new_node,
                                                            std::memory_order_release,
                                                            std::memory_order_relaxed)) {
                        // Swing tail (helping permitted, so failure is fine)
                        tail.compare_exchange_strong(cur_tail, new_node,
                                                     std::memory_order_release,
                                                     std::memory_order_relaxed);
                        return;
                    }
                } else {
                    // Tail was lagging; help advance it
                    tail.compare_exchange_strong(cur_tail, next,
                                                 std::memory_order_release,
                                                 std::memory_order_relaxed);
                }
            }
        }
    }

    bool dequeue(T& result) {
        while (true) {
            Node* cur_head = head.load(std::memory_order_acquire);
            Node* cur_tail = tail.load(std::memory_order_acquire);
            Node* next = cur_head->next.load(std::memory_order_acquire);

            if (cur_head == head.load(std::memory_order_relaxed)) {
                if (cur_head == cur_tail) {
                    if (next == nullptr) {
                        return false; // Queue is empty
                    }
                    // Tail is falling behind head; help advance tail
                    tail.compare_exchange_strong(cur_tail, next,
                                                 std::memory_order_release,
                                                 std::memory_order_relaxed);
                } else {
                    result = next->value;
                    // Linearization Point 2: Swing head forward
                    if (head.compare_exchange_weak(cur_head, next,
                                                   std::memory_order_release,
                                                   std::memory_order_relaxed)) {
                        // SMR reclamation of cur_head
                        delete cur_head;
                        return true;
                    }
                }
            }
        }
    }
};
```

---

## 5. Lock-Free Structures vs Sequential Binary Heaps (COL1101 Connection)

In standard sequential algorithms (e.g. COL1101 Lecture 21), the **Binary Heap** is the gold standard for priority queues:
- Representation: Contiguous array $A[0..n-1]$.
- Parent of node $i$: $\lfloor (i - 1) / 2 \rfloor$.
- Children of node $i$: $2i + 1$ and $2i + 2$.
- `Insert`: Appends at index $n$, executes `sift_up` ($O(\log n)$ swaps).
- `Extract-Min`: Reads $A[0]$, moves $A[n-1]$ to $A[0]$, executes `sift_down` ($O(\log n)$ swaps).

### 5.1 Why Binary Heaps Resist Scalable Lock-Free Concurrency
While stacks (Treiber) and FIFO queues (Michael-Scott) linearize via single atomic CAS operations at designated endpoints (`Top`, `Head`, `Tail`), a binary heap is **fundamentally hostile** to lock-free concurrency:

#### 1. Multi-Point Non-Local Dependencies
A single `Extract-Min` operation on a heap with depth $d = \log_2 n$ requires coordinating:
1. The root node $A[0]$.
2. The leaf node $A[n-1]$ being removed.
3. The array length variable $n$.
4. A chain of $O(\log n)$ internal nodes along the sift-down path.
Hardware CAS can only modify **one** memory address at a time. Coordinating an atomic swap across multiple disjoint array indices without locks requires a complex multi-word CAS (MCAS / $k$-CAS) or software transactional memory, incurring prohibitive overhead.

#### 2. Root Contention Bottleneck
Every `Extract-Min` must inspect and modify $A[0]$.
With $P$ parallel processors, all threads funnel their operations through the identical root cache line, causing catastrophic cache line bouncing and serialization ($O(P)$ contention).

#### 3. False Sharing on Contiguous Arrays
Because binary heaps store nodes in contiguous array indices ($A[0], A[1], A[2], \dots$), adjacent levels of the heap occupy the same 64-byte hardware cache line. A thread updating node 3 will invalidate the cache line for nodes 0, 1, 2, 4, 5, causing artificial false-sharing stalls.

### 5.2 Concurrent Alternatives
To build high-throughput concurrent priority queues, practitioners abandon array-based binary heaps in favor of:
- **Lock-Free SkipLists** (Lotan & Shavit): Nodes are probabilistically ordered in a linked hierarchy; inserts and extract-mins use local CAS on pointer levels without touching a single root bottleneck.
- **Multi-Queue Priority Queues**: $K$ independent heaps protected by fine-grained locks; threads randomly pick 2 heaps and extract from the one with higher priority, trading strict total priority ordering for near-linear multicore scaling.
