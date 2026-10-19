# Module 02: Mutual Exclusion & Hardware Synchronization Primitives

---

## 1. The Critical Section Problem

A **Critical Section (CS)** is a block of code accessing shared resources that must not be concurrently executed by more than one thread of control.

### 1.1 Formal Requirements
Any valid mutual exclusion algorithm for $N$ threads must satisfy three fundamental properties:

1. **Safety (Mutual Exclusion)**:
   At most one thread may reside in its critical section at any instant of physical or logical time $t$:
   $$\forall t \ge 0, \quad \sum_{i=1}^N \mathbb{I}(\text{state}_i(t) = \text{CS}) \le 1$$
   *(Invariant property: prefix-closed, safety)*.

2. **Liveness (Progress / Deadlock-Freedom)**:
   If the critical section is empty and one or more threads wish to enter, only those threads competing for entry participate in the selection, and the selection cannot be postponed indefinitely:
   $$\left( \forall i, \; \text{state}_i(t) \neq \text{CS} \land \exists k : \text{state}_k(t) = \text{WantCS} \right) \implies \lozenge \left( \exists j : \text{state}_j(t') = \text{CS} \right)$$
   *(Liveness property)*.

3. **Fairness (Bounded Waiting / Starvation-Freedom)**:
   There exists a bound $B \in \mathbb{N}$ on the number of times other threads are granted entry to the critical section after a thread $T_i$ requests entry, before $T_i$'s request is granted:
   $$\forall i, \quad \text{state}_i(t) = \text{WantCS} \implies \lozenge \left( \text{state}_i(t') = \text{CS} \right)$$

---

## 2. Peterson's Algorithm (Two Threads)

Gary L. Peterson (1981) introduced an elegant algorithm providing mutual exclusion for two threads using only atomic read and write registers under Sequential Consistency.

### 2.1 Algorithm Listing
Shared variables:
```c
bool flag[2] = {false, false};
int turn = 0;
```

**Thread $i \in \{0, 1\}$ (with peer $j = 1 - i$):**
```c
// Entry protocol
flag[i] = true;                     // Statement W1: indicate intent
turn = j;                           // Statement W2: offer precedence to peer
while (flag[j] && turn == j) {      // Statement R1: spin wait
    // busy wait
}

// Critical Section
// ...

// Exit protocol
flag[i] = false;                    // Statement W3: release
```

### 2.2 Formal Proof of Safety under Sequential Consistency
We prove safety by contradiction.

**Proof**:
Suppose both threads $T_0$ and $T_1$ reside simultaneously in the Critical Section at time $t$.
Let $W1_i$ denote `flag[i] = true`, $W2_i$ denote `turn = j`, and $R1_i$ denote the final evaluation of `(flag[j] && turn == j)` that yielded `false`, allowing $T_i$ into the CS.

By program order ($\xrightarrow{po}$):
$$W1_0 \xrightarrow{po} W2_0 \xrightarrow{po} R1_0$$
$$W1_1 \xrightarrow{po} W2_1 \xrightarrow{po} R1_1$$

Under Sequential Consistency, there exists a single global total order $<$.
The variable `turn` can hold only one value at a time. Without loss of generality, assume $T_0$ performed $W2_0$ before $T_1$ performed $W2_1$:
$$W2_0 < W2_1$$

Since $W2_1$ sets `turn = 0` and no other writes to `turn` occur before $R1_0$ and $R1_1$:
1. At the time $T_1$ reaches $R1_1$, `turn == 0` (or was overwritten by another operation, but here $W2_1$ was the last write).
2. For $T_1$ to enter the critical section, its loop condition `(flag[0] && turn == 0)` must evaluate to `false`.
3. Since $T_0$ is in the CS, $W1_0$ has already completed:
   $$W1_0 < W2_0 < W2_1 < R1_1$$
   Therefore, at $R1_1$, `flag[0] == true`.
4. Since `flag[0] == true`, for the condition to be `false`, $T_1$ must have read `turn != 0`.
5. But $W2_1$ was the last write to `turn`, so `turn == 0` when read by $T_1$.
6. Contradiction: $T_1$ cannot evaluate `turn != 0` while $T_0$ is in the CS.

Hence, mutual exclusion holds under SC. $\blacksquare$

### 2.3 Formal Proof of Failure under x86-TSO (Store-Load Reordering)
Recall that x86 hardware permits $W \to R$ reordering across different memory addresses due to FIFO store buffers.

In Peterson's entry:
- $W1_i$: `flag[i] = true` is a **Store** to address `&flag[i]`.
- $W2_i$: `turn = j` is a **Store** to address `&turn`.
- $R1_i$: reading `flag[j]` is a **Load** from address `&flag[j]`.

Notice that $W1_i$ and $R1_i$ access **distinct memory locations** (`flag[0]` vs `flag[1]`).

**Failure Execution Trace**:
1. $T_0$ executes $W1_0$ (`flag[0] = true`) and $W2_0$ (`turn = 1`). Both writes are placed into $T_0$'s private local **Store Buffer** and have not yet been drained to the L1 cache.
2. $T_1$ executes $W1_1$ (`flag[1] = true`) and $W2_1$ (`turn = 0`). Both writes are placed into $T_1$'s private local **Store Buffer** and have not drained to L1 cache.
3. $T_0$ proceeds to read `flag[1]`. Because $T_1$'s write is still in $T_1$'s private store buffer, $T_0$ reads `flag[1]` from shared L1 cache, which contains the initial value `false`.
4. $T_0$ evaluates `flag[1] == false`, bypasses the while loop immediately, and **enters the Critical Section**.
5. Concurrently, $T_1$ proceeds to read `flag[0]`. Because $T_0$'s write is still in $T_0$'s private store buffer, $T_1$ reads `flag[0]` from shared L1 cache, which contains `false`.
6. $T_1$ evaluates `flag[0] == false`, bypasses the while loop immediately, and **also enters the Critical Section**!

**Result**: $\sum_{i=0}^1 \mathbb{I}(\text{CS}_i) = 2 > 1$. Catastrophic safety violation.

**The Fix**: A full hardware memory barrier (`MFENCE` on x86, or `atomic_thread_fence(memory_order_seq_cst)`) must be placed immediately between the writes (`flag[i]`, `turn`) and the read of `flag[j]`.

---

## 3. Lamport's Bakery Algorithm ($N$ Threads)

Leslie Lamport (1974) generalized mutual exclusion to $N$ threads without requiring hardware atomics, modeling a traditional bakery ticket system.

### 3.1 Algorithm Listing
Shared variables:
```c
bool entering[N] = {false};
int number[N] = {0};
```

**Thread $i \in \{0, \dots, N-1\}$:**
```c
// Entry protocol
entering[i] = true;
// Compute ticket: strictly greater than all current numbers
int max_num = 0;
for (int k = 0; k < N; ++k) {
    if (number[k] > max_num) max_num = number[k];
}
number[i] = max_num + 1;
entering[i] = false;

// Wait for threads with lower tickets or higher priority
for (int j = 0; j < N; ++j) {
    // Wait if thread j is in the middle of choosing its ticket
    while (entering[j]) { /* spin */ }
    
    // Wait while thread j has a valid ticket with higher priority
    // Priority order: (number[j], j) < (number[i], i)
    while (number[j] != 0 && (number[j] < number[i] || (number[j] == number[i] && j < i))) {
        /* spin */
    }
}

// Critical Section
// ...

// Exit protocol
number[i] = 0;
```

### 3.2 Lexicographical Ordering and Invariants
The algorithm defines a strict total order $\prec$ on pairs of `(number, thread_id)`:
$$(a, b) \prec (c, d) \iff (a < c) \lor (a == c \land b < d)$$

**Lemma (Ticket Ordering Invariant)**:
If thread $T_i$ is in the Critical Section, and for any $T_k$ ($k \neq i$) that has completed ticket selection (`entering[k] == false` and `number[k] != 0`):
$$(number[i], i) \prec (number[k], k)$$

**Proof Sketch**:
When $T_i$ entered the CS, it verified the inner loop for $j = k$.
Either $number[k] == 0$ at that moment (meaning $T_k$ had not chosen its ticket, so when $T_k$ eventually chooses, $number[k] > number[i]$), or $T_i$ observed $(number[i], i) \prec (number[k], k)$.
Since tickets are monotonically chosen, $T_k$ will spin in its own wait loop until $T_i$ resets $number[i] = 0$.
Thus, mutual exclusion, progress, and strict FIFO bounded waiting are maintained.

---

## 4. Herlihy's Consensus Hierarchy & Universality

In his seminal paper (1991), Maurice Herlihy established the theoretical limits of concurrent synchronization by analyzing the **Wait-Free Consensus Problem**.

### 4.1 The $N$-Consensus Problem
An object solves $N$-consensus if $N$ concurrent threads, each proposing an input value $v_i \in \{0, 1\}$, can agree on a decision value $D$ such that:
1. **Agreement**: All non-faulty threads decide the exact same value:
   $$\forall i, j, \quad D_i = D_j$$
2. **Validity**: The decision value $D$ must be the input of some thread:
   $$D \in \{v_1, \dots, v_N\}$$
3. **Wait-Free Termination**: Every non-faulty thread decides in a finite number of its own execution steps.

### 4.2 Definition of Consensus Number
> The **Consensus Number** of an object type $T$, denoted $C(T)$, is the maximum number of threads $N$ for which a wait-free consensus protocol can be implemented using instances of $T$ and standard atomic Read/Write registers. If no such finite maximum exists, $C(T) = \infty$.

### 4.3 The Consensus Hierarchy

| Level | Synchronization Primitives | Solves Consensus For |
|:---:|---|:---:|
| **1** | Atomic Read/Write Registers | $N = 1$ only |
| **2** | Test-And-Set, Swap, Fetch-And-Add, Bounded FIFO Queues | $N = 2$ |
| $\dots$ | $k$-assignment registers | $N = 2k - 2$ |
| $\mathbf{\infty}$ | Compare-And-Swap (CAS), LL/SC (Load-Linked / Store-Conditional) | Any $N \ge 1$ |

### 4.4 Impossibility Proof: Level 1 (Read/Write Registers cannot solve 2-Consensus)
**Theorem**: $C(\text{Atomic Read/Write}) = 1$.

**Proof by Bivalence Argument (Fischer, Lynch, Paterson / Herlihy)**:
1. Consider a 2-thread system $\{T_0, T_1\}$ with binary inputs $v_0 = 0, v_1 = 1$.
2. A system state $s$ is **bivalent** if both 0 and 1 are reachable decision outcomes from $s$. A state is **univalent** (0-valent or 1-valent) if the decision value is completely fixed regardless of future scheduling.
3. The initial state $s_{01}$ (where $T_0$ has 0 and $T_1$ has 1) is bivalent. (If $T_0$ runs alone, validity forces decision 0; if $T_1$ runs alone, validity forces decision 1).
4. By finite termination, there must exist a **critical bivalent state** $s^*$ such that:
   - $s^*$ is bivalent, but
   - For any step $\alpha_0$ of $T_0$, state $s_0 = s^* \xrightarrow{\alpha_0} s'$ is 0-valent, and
   - For any step $\alpha_1$ of $T_1$, state $s_1 = s^* \xrightarrow{\alpha_1} s''$ is 1-valent.
5. Consider the possible operations $\alpha_0, \alpha_1$ at state $s^*$:
   - *Case 1: Both access different memory locations.* The operations commute: $\alpha_0 \alpha_1 \equiv \alpha_1 \alpha_0$. The state reached from $s^*$ by $\alpha_0 \alpha_1$ is identical to $\alpha_1 \alpha_0$. But $\alpha_0 \alpha_1$ is 0-valent while $\alpha_1 \alpha_0$ is 1-valent. Contradiction.
   - *Case 2: One thread reads and the other writes the same location $x$.* Without loss of generality, let $T_0$ execute a Read $\alpha_0 = R(x)$ and $T_1$ execute a Write $\alpha_1 = W(x)$. Compare state $s_{01} = s^* \xrightarrow{\alpha_0} s_0 \xrightarrow{\alpha_1} s_{01}$ (reachable from 0-valent state $s_0$) with state $s_1 = s^* \xrightarrow{\alpha_1} s_1$ (which is 1-valent). Because $\alpha_0$ only alters $T_0$'s private local register, shared memory in $s_{01}$ is bitwise identical to $s_1$, and $T_1$'s private state is identical. If $T_1$ now runs alone to decision, it cannot distinguish $s_{01}$ from $s_1$, forcing it to decide 1 in both executions. But $s_{01}$ was derived from 0-valent state $s_0$, where all executions must decide 0. Contradiction!
   - *Case 3: Both write to the same location $x$.* The sequence $\alpha_0 \alpha_1$ results in $T_1$'s write completely overwriting $T_0$'s write. The state of shared memory after $\alpha_0 \alpha_1$ is indistinguishable from the state after $s^* \xrightarrow{\alpha_1} s_1$. Since $s_1$ is 1-valent, $\alpha_0 \alpha_1$ must also be 1-valent. But by definition, applying $\alpha_0$ first moved the system into a 0-valent state. Contradiction!
6. Hence, no such critical state can exist, meaning a deterministic wait-free protocol cannot guarantee decision. $\blacksquare$

### 4.5 Why CAS has Consensus Number $\infty$
A Compare-And-Swap operation:
$$\text{CAS}(addr, expected, new) \to bool$$
atomically tests if $*addr == expected$; if true, updates $*addr = new$ and returns `true`; else returns `false`.

Solving $N$-consensus with CAS:
```c
int consensus_cell = -1; // Uninitialized

int decide(int thread_id, int my_val) {
    CAS(&consensus_cell, -1, my_val);
    return consensus_cell; // First CAS wins and fixes value forever
}
```
Because CAS atomically tests and commits without race, all $N$ threads observe the value committed by the winning CAS. Hence, $C(\text{CAS}) = \infty$.

### 4.6 Herlihy's Universality Theorem
> **Herlihy's Universality Theorem (1991)**:
> Any concurrent object with a deterministic sequential specification can be implemented in a wait-free and lock-free manner for $N$ threads using consensus objects of level $N$ (e.g., CAS) combined with atomic read/write registers.

*Implication*: Hardware architectures providing CAS (x86 `CMPXCHG`, ARM `LDREX/STREX` or `CAS`) are computationally universal for concurrent data structure design.

---

## 5. Spinlocks and Hardware Contention

When locks protect short critical sections, spinning (busy-waiting in user space) avoids expensive OS context-switch overhead ($\sim 1\text{--}5\,\mu\text{s}$).

### 5.1 Test-And-Set (TAS) Spinlock
```c
typedef struct { atomic_bool state; } tas_lock_t;

void tas_lock(tas_lock_t* l) {
    while (atomic_exchange_explicit(&l->state, true, memory_order_acquire)) {
        // Spin: continuously execute atomic exchange
    }
}
void tas_unlock(tas_lock_t* l) {
    atomic_store_explicit(&l->state, false, memory_order_release);
}
```
**Fatal Performance Flaw**:
Every invocation of `atomic_exchange` issues a `BusRdX` (Read Invalidate) bus transaction.
With $N$ cores spinning, each attempt invalidates the cache line in all $N-1$ other caches, saturating the coherent interconnect bus ($O(N)$ traffic per spin step, $O(N^2)$ aggregate bus bandwidth).

### 5.2 Test-and-Test-And-Set (TTAS) Spinlock
```c
void ttas_lock(tas_lock_t* l) {
    while (true) {
        // 1. Spin locally on cached read (Shared state in MESI)
        while (atomic_load_explicit(&l->state, memory_order_relaxed) == true) {
            _mm_pause(); // Low-power pipeline spin hint
        }
        // 2. Attempt atomic acquisition only when observed free
        if (!atomic_exchange_explicit(&l->state, true, memory_order_acquire)) {
            return; // Acquired!
        }
    }
}
```
**Analysis**:
- While the lock is held, all spinning threads read the cache line in the **Shared (S)** state locally from L1/L2 cache: **Zero bus traffic**.
- **Contention Spike (Cache-Line Bouncing / Thundering Herd)**: When the owner releases the lock (`state = false`), its write invalidates all $N-1$ shared copies. All $N-1$ cores simultaneously detect `state == false` and concurrently execute `atomic_exchange` (issuing $N-1$ competing `BusRdX` operations).
- Traffic per release is $O(N)$.

### 5.3 False Sharing
Occurs when distinct variables accessed by different threads reside on the **same 64-byte hardware cache line**.

```
Cache Line [64 Bytes]
+-------------------------------+-------------------------------+
|   thread_0_counter (8 Bytes)  |   thread_1_counter (8 Bytes)  |
+-------------------------------+-------------------------------+
```
Even if $T_0$ and $T_1$ never access the same variable, $T_0$'s writes force MESI invalidations of $T_1$'s entire cache line, destroying multicore scaling.
*Remedy*: Explicit alignment and padding (`alignas(64)` in C++11, `#[repr(align(64))]` in Rust).

---

## 6. Scalable Queue Locks: MCS & CLH

Queue locks eliminate cache-line bouncing by having each thread **spin on a distinct, thread-local memory location**.

### 6.1 The MCS Lock (Mellor-Crummey & Scott, 1991)
MCS creates an explicit distributed linked list of waiting nodes. Each thread allocates a node and spins on that node's own boolean flag.

```
       Tail
         |
         v
[Node A] <-- next -- [Node B] <-- next -- [Node C]
(in CS)              (spinning)           (spinning)
```

#### MCS Implementation
```c
typedef struct mcs_node {
    struct mcs_node* next;
    bool locked;
} mcs_node_t;

typedef struct {
    mcs_node_t* tail;
} mcs_lock_t;

void mcs_lock(mcs_lock_t* lock, mcs_node_t* my_node) {
    my_node->next = NULL;
    my_node->locked = true;

    // Atomically swap tail with my_node
    mcs_node_t* pred = atomic_exchange(&lock->tail, my_node);
    if (pred != NULL) {
        pred->next = my_node; // Link predecessor to self
        while (my_node->locked) {
            // Spin locally on my own cache line!
            _mm_pause();
        }
    }
}

void mcs_unlock(mcs_lock_t* lock, mcs_node_t* my_node) {
    if (my_node->next == NULL) {
        // Check if we are indeed the last node in the queue
        mcs_node_t* expected = my_node;
        if (atomic_compare_exchange_strong(&lock->tail, &expected, NULL)) {
            return; // No successor, queue is now empty
        }
        // Wait for successor to link their pointer
        while (my_node->next == NULL) {
            _mm_pause();
        }
    }
    // Hand over lock to successor
    my_node->next->locked = false;
}
```

**MCS Invariants & Properties**:
1. **$O(1)$ Bus Transactions per Release**: Unlocking invalidates *only* the single successor node's cache line.
2. **NUMA-Friendly**: Each thread spins on memory allocated on its local NUMA node.
3. **Strict FIFO**: Fair, starvation-free ordering guaranteed by queue structure.

### 6.2 The CLH Lock (Craig, Landin, and Hägersten)
CLH uses an implicit linked list where each thread spins on the **predecessor's node** instead of its own node.

- Acquisition: Atomically swing `tail` to self; keep pointer to predecessor `pred`; spin on `pred->locked`.
- Release: Set `my_node->locked = false`. The successor immediately detects the change and enters.
- Advantage: Extremely fast on cache-coherent architectures (CC-NUMA); requires only 1 atomic operation per acquire and 0 atomic operations per release.

### 6.3 Architectural Comparison

| Lock Type | Traffic during Spin | Traffic on Release | Space Complexity | Starvation-Free? |
|---|:---:|:---:|:---:|:---:|
| **TAS** | $O(N)$ bus transactions/cycle | $O(1)$ | $O(1)$ | No |
| **TTAS** | $0$ (local cache read) | $O(N)$ (invalidation storm) | $O(1)$ | No |
| **MCS** | $0$ (spins on local node) | $O(1)$ (direct successor notify) | $O(N)$ ($1$ node/thread) | **Yes (FIFO)** |
| **CLH** | $0$ (spins on predecessor) | $O(1)$ (direct predecessor write)| $O(N)$ | **Yes (FIFO)** |
