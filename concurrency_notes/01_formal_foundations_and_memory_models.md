# Module 01: Formal Foundations & Memory Consistency Models

---

## 1. Formal Transition Systems & Interleaving Semantics

### 1.1 The Mathematical Model of Concurrency
A concurrent system is formally specified as a **Labeled Transition System (LTS)**:
$$\mathcal{T} = \langle \mathcal{S}, \mathcal{S}_0, \Sigma, \to \rangle$$

Where:
- $\mathcal{S}$ is the set of global system states:
  $$\mathcal{S} = \prod_{i=1}^N \mathcal{L}_i \times \mathcal{M}$$
  where $\mathcal{L}_i$ is the local state space of thread $T_i$ (program counter $PC_i$, register file $\mathcal{R}_i$, call stack) and $\mathcal{M}: \text{Addr} \to \text{Val}$ represents shared memory.
- $\mathcal{S}_0 \subseteq \mathcal{S}$ is the set of valid initial states.
- $\Sigma = \bigcup_{i=1}^N \Sigma_i \cup \{\tau\}$ is the alphabet of actions. An action $\alpha \in \Sigma_i$ corresponds to an atomic instruction executed by thread $T_i$ (e.g., $\text{read}(x, v)$, $\text{write}(x, v)$, $\text{CAS}(x, old, new)$), while $\tau$ denotes internal unobservable transitions.
- $\to \subseteq \mathcal{S} \times \Sigma \times \mathcal{S}$ is the transition relation, denoted $s \xrightarrow{\alpha} s'$.

### 1.2 Interleaving Semantics vs True Concurrency
In classical concurrency semantics (interleaving semantics), concurrency is modeled by the non-deterministic interleaving of atomic actions. Given two threads executing sequence $\alpha_1; \alpha_2$ and $\beta_1; \beta_2$, the set of valid execution traces is the **shuffle product** (shuffle operator $\otimes$):
$$\{\alpha_1 \alpha_2\} \otimes \{\beta_1 \beta_2\} = \{\alpha_1 \alpha_2 \beta_1 \beta_2, \; \alpha_1 \beta_1 \alpha_2 \beta_2, \; \alpha_1 \beta_1 \beta_2 \alpha_2, \; \beta_1 \alpha_1 \alpha_2 \beta_2, \; \beta_1 \alpha_1 \beta_2 \alpha_2, \; \beta_1 \beta_2 \alpha_1 \alpha_2\}$$

**Fundamental Theorem (Interleaving Sufficiency for Sequential Observers)**:
If all primitive operations are atomic and memory access is sequentially consistent, any true concurrent execution (simultaneous multi-core execution in real physical time) is observationally indistinguishable from an arbitrary sequential interleaving in the shuffle product.

*Limitation*: As demonstrated in Section 3 and 4, modern superscalar pipelined processors with out-of-order execution, store buffers, and cache hierarchies break naive interleaving semantics at the hardware level.

---

## 2. Lamport's Happens-Before Relation ($\xrightarrow{hb}$)

Introduced by Leslie Lamport (1978), the **happens-before** relation formalizes causality in distributed and concurrent systems without reference to physical time.

### 2.1 Formal Definition as a Strict Partial Order
Let $E$ be the set of all events executed in a system. The relation $\xrightarrow{hb} \subseteq E \times E$ is the smallest binary relation satisfying three axioms:

1. **Program Order Rule ($\xrightarrow{po}$)**:
   $$\forall e_1, e_2 \in E, \quad (\text{thread}(e_1) = \text{thread}(e_2) \land e_1 \prec_{\text{prog}} e_2) \implies e_1 \xrightarrow{hb} e_2$$
2. **Synchronization / Message Passing Rule ($\xrightarrow{sw}$)**:
   $$\forall e_{\text{send}}, e_{\text{recv}} \in E, \quad (e_{\text{send}} \text{ sends message } m \land e_{\text{recv}} \text{ receives } m) \implies e_{\text{send}} \xrightarrow{hb} e_{\text{recv}}$$
   In shared memory: if $w$ writes a synchronization variable and $r$ observes that write, $w \xrightarrow{sw} r \implies w \xrightarrow{hb} r$.
3. **Transitivity**:
   $$\forall a, b, c \in E, \quad (a \xrightarrow{hb} b \land b \xrightarrow{hb} c) \implies a \xrightarrow{hb} c$$

**Algebraic Properties**:
- **Irreflexivity**: $\forall e \in E, \; \neg(e \xrightarrow{hb} e)$.
- **Asymmetry (strict antisymmetry)**: $\forall a, b \in E, \; a \xrightarrow{hb} b \implies \neg(b \xrightarrow{hb} a)$.
- **Transitivity**: $\forall a, b, c \in E, \; (a \xrightarrow{hb} b \land b \xrightarrow{hb} c) \implies a \xrightarrow{hb} c$.
Hence, $\langle E, \xrightarrow{hb} \rangle$ is a **strict partial order** (poset).

### 2.2 Concurrency
Two events $a, b \in E$ are concurrent ($a \parallel b$) if and only if they are causally independent:
$$a \parallel b \iff \neg(a \xrightarrow{hb} b) \land \neg(b \xrightarrow{hb} a)$$

### 2.3 Vector Clocks
Scalar Lamport timestamps satisfy the consistency condition:
$$a \xrightarrow{hb} b \implies C(a) < C(b)$$
However, the converse fails: $C(a) < C(b) \not\implies a \xrightarrow{hb} b$.

**Vector Clocks (Mattern / Fidge 1988)** establish an exact isomorphism (strict causal equivalence):
$$a \xrightarrow{hb} b \iff V(a) < V(b)$$

For $N$ threads, each process $T_i$ maintains an integer vector $V_i \in \mathbb{N}^N$, initialized to $\mathbf{0}$.
- **Local Event by $T_i$**:
  $$V_i[i] \leftarrow V_i[i] + 1$$
- **Send / Release Event**: Thread $i$ increments $V_i[i]$ and attaches snapshot $V_i$ to message/synchronization token $M$.
- **Receive / Acquire Event with message $M$ carrying $V_M$**:
  $$V_i[k] \leftarrow \max(V_i[k], V_M[k]), \quad \forall k \in \{1, \dots, N\}$$
  $$V_i[i] \leftarrow V_i[i] + 1$$

Vector comparison is defined as:
$$V_a \le V_b \iff \forall k \in \{1, \dots, N\}, \; V_a[k] \le V_b[k]$$
$$V_a < V_b \iff (V_a \le V_b) \land (V_a \neq V_b)$$
$$a \parallel b \iff \neg(V(a) \le V(b)) \land \neg(V(b) \le V(a))$$

---

## 3. Hardware Memory Architecture: Coherence vs Consistency

A critical source of concurrency bugs is conflating **Cache Coherence** with **Memory Consistency**.

```
+-------------------------------------------------------------+
| Coherence:   Per-variable (single memory address) invariant |
| Consistency: Inter-variable (across multiple addresses) order|
+-------------------------------------------------------------+
```

### 3.1 The Physical Memory Subsystem
Modern CPUs cannot wait $\sim 50\text{--}100\text{ ns}$ for DRAM writes. They utilize hardware buffers:

```
[ CPU Core 0 ]                   [ CPU Core 1 ]
      |                                |
[ Store Buffer ]                 [ Store Buffer ]
      |                                |
  [ L1 Cache ] <--- Interconnect ---> [ L1 Cache ]
[ Invalidate Q ]                 [ Invalidate Q ]
      |                                |
      +--------------+-----------------+
                     |
                [ L2 / L3 ]
                     |
                [ Main RAM ]
```

1. **Store Buffer (Write Buffer)**: FIFO queue sitting between core and L1 cache. Allows the CPU to issue a write and immediately proceed with subsequent instructions without waiting for cache line ownership.
2. **Store Forwarding**: If a core issues a read to an address currently sitting in its own store buffer, it reads the speculative value directly from the store buffer.
3. **Invalidate Queue**: Instead of immediately invalidating a cache line upon receiving an invalidation message from the bus, a core places the request into an Invalidate Queue and acknowledges immediately, delaying the actual invalidation.

### 3.2 Cache Coherence: The MESI Protocol State Machine
Coherence ensures that **all processors agree on the write serialization of each individual cache line**. MESI classifies every 64-byte cache line into one of 4 states:

| State | Name | Meaning | Can Read? | Can Write? | In Other Caches? |
|---|---|---|---|---|---|
| **M** | Modified | Line is dirty; valid only in this cache; differs from RAM. | Yes | Yes (local) | No |
| **E** | Exclusive | Clean; valid only in this cache; matches RAM. | Yes | Yes (transitions to M) | No |
| **S** | Shared | Clean; valid in this cache; may be in other caches. | Yes | No (requires BusUpgr/BusRdX) | Yes |
| **I** | Invalid | Contains no valid data. | No (requires BusRd) | No (requires BusRdX) | Don't care |

#### Formal MESI Transition Matrix

```
       Local Read (PrRd)                     Local Write (PrWr)
   +-----------------------+             +------------------------+
   | (Hit)                 |             |                        |
   v                       |             v                        |
+------+  PrWr: BusUpgr   +------+   PrWr: BusRdX             +------+
|      | ---------------> |      | <------------------------- |      |
|  S   |                  |  M   |                            |  I   |
|      | <--------------- |      | -------------------------> |      |
+------+  BusRd: Flush    +------+   BusRdX: Flush            +------+
   ^                          |
   | PrRd: BusRd              |
   +--------------------------+
```

- **BusRd**: Bus Read request to read cache line.
- **BusRdX**: Bus Read Invalidate (Request for Ownership - RFO). Asks for data and demands all other caches invalidate their copies.
- **BusUpgr**: Bus Upgrade. Transmitter already has line in **S**, demands others invalidate so it can transition to **M**.
- **Flush**: Snooper supplies data from dirty line to requester and main memory.

**Coherence Invariant (Single-Writer, Multi-Reader / SWMR)**:
For any memory address $x$ and any time $t$:
1. *Write Exclusivity*: At most one cache holds the line in a writable state ($\text{M}$ or $\text{E}$), and if so, all other caches must be in state $\text{I}$:
   $$\sum_{c \in \text{Caches}} \mathbb{I}(\text{state}_c(x) \in \{\text{M}, \text{E}\}) \le 1$$
   $$\left( \exists c : \text{state}_c(x) \in \{\text{M}, \text{E}\} \right) \implies \left( \forall k \neq c : \text{state}_k(x) == \text{I} \right)$$
2. *Read Concurrency*: If any cache holds the line in Shared state ($\text{S}$), all valid copies must have identical data, and no cache may hold $\text{M}$ or $\text{E}$:
   $$\left( \exists c : \text{state}_c(x) == \text{S} \right) \implies \left( \forall k : \text{state}_k(x) \in \{\text{S}, \text{I}\} \right)$$

*Key Takeaway*: MESI guarantees that a single location cannot hold contradictory values simultaneously (Single-Writer Multi-Reader). **MESI does NOT guarantee memory consistency across multiple locations.**

---

## 4. Memory Consistency Models: SC vs TSO vs Weak

A **Memory Consistency Model** defines the architecturally valid orderings of memory reads and writes across different addresses as observed by concurrent cores.

### 4.1 Sequential Consistency (SC - Lamport 1979)
A multiprocessor system is sequentially consistent if:
> "The result of any execution is the same as if the operations of all the processors were executed in some sequential order, and the operations of each individual processor appear in this sequence in the order specified by its program."

Formally, an execution satisfies SC iff there exists a global total order $<_{\text{total}}$ over all events $E$ such that:
1. **Program Order Preservation**:
   $$\forall a, b \in E, \quad a \prec_{\text{prog}} b \implies a <_{\text{total}} b$$
2. **Read-From Coherence**:
   $$\forall r = \text{Read}(x), \quad \text{val}(r) = \text{val}\left(\max_{<_{\text{total}}} \{ w \in E \mid w = \text{Write}(x) \land w <_{\text{total}} r \}\right)$$

### 4.2 Total Store Order (TSO - x86, SPARC TSO)
x86 processors implement Total Store Order. Hardware store buffers introduce **Store-Load reordering**: a Write followed by a Read to a *different* address can be reordered:
$$W(x) \prec_{\text{prog}} R(y) \not\implies W(x) <_{\text{total}} R(y)$$

All other orderings are preserved in x86-TSO:
- $W(x) \prec_{\text{prog}} W(y) \implies W(x) <_{\text{total}} W(y)$ (Stores are not reordered with Stores).
- $R(x) \prec_{\text{prog}} R(y) \implies R(x) <_{\text{total}} R(y)$ (Loads are not reordered with Loads).
- $R(x) \prec_{\text{prog}} W(y) \implies R(x) <_{\text{total}} W(y)$ (Loads are not reordered with subsequent Stores).

#### The Canonical Dekker / Peterson Reordering Litmus Test (SB: Store Buffering)
Initial state: `x = 0`, `y = 0`.

| Thread 1 | Thread 2 |
|---|---|
| `x = 1;` (Store) | `y = 1;` (Store) |
| `r1 = y;` (Load) | `r2 = x;` (Load) |

- **Under SC**: Possible outcomes for $(r_1, r_2) \in \{(1, 1), (0, 1), (1, 0)\}$. The outcome $(r_1 = 0, r_2 = 0)$ is **strictly impossible**.
  - *Proof*: In SC, if $r_1 = 0$, then $R(y) < W(y)$. Since $W(x) < R(y)$, by transitivity $W(x) < W(y)$. For Thread 2, $W(y) < R(x)$. Thus $W(x) < R(x)$, forcing $r_2 = 1$. Contradiction.
- **Under x86-TSO**: The outcome $(r_1 = 0, r_2 = 0)$ **can and does occur**!
  - *Hardware mechanism*: Thread 1 writes $x=1$ to its store buffer. Thread 2 writes $y=1$ to its store buffer. Neither store buffer has drained to L1 cache yet. Both threads immediately execute their loads ($R(y)$ and $R(x)$), observing 0 in L1 cache.
- **Hardware Remedy**: `MFENCE` instruction (or `LOCK` prefix instructions like `LOCK CMPXCHG` or `LOCK XADD`). `MFENCE` forces the core to stall until its store buffer is completely drained to the cache.

### 4.3 Weak / Relaxed Memory Models (ARMv8, RISC-V, POWER)
On weakly ordered architectures:
- Any access pair to different addresses can be reordered: $W \to W$, $R \to R$, $R \to W$, $W \to R$.
- The only restrictions preserved automatically are:
  - **Data dependencies**: $r1 = \text{load}(x) \to \text{load}(r1)$.
  - **Address dependencies**: $r1 = \text{load}(x) \to \text{store}(r1, v)$.
  - **Control dependencies**: only for writes following branches (on ARM).

#### Comparison Summary Table

| Architecture | $W \to R$ Reorder? | $W \to W$ Reorder? | $R \to R$ Reorder? | $R \to W$ Reorder? | Full Fence Instruction |
|---|:---:|:---:|:---:|:---:|---|
| **Sequential Consistency** | No | No | No | No | N/A |
| **x86-64 (TSO)** | **Yes** | No | No | No | `MFENCE` / `LOCK` |
| **ARMv8** | **Yes** | **Yes** | **Yes** | **Yes** | `DMB ISH` |
| **RISC-V** | **Yes** | **Yes** | **Yes** | **Yes** | `fence rw, rw` |

---

## 5. Modern Language Memory Models: C++11 & Rust

C++11 and Rust (which adopts the C++20 C11-based formal memory model) bridge the gap between hardware architectures and high-level language semantics via **atomic operations** and explicit memory orderings.

### 5.1 The Six `std::memory_order` Enumerations

```cpp
typedef enum memory_order {
    memory_order_relaxed,
    memory_order_consume,
    memory_order_acquire,
    memory_order_release,
    memory_order_acq_rel,
    memory_order_seq_cst
} memory_order;
```

#### 1. `memory_order_relaxed`
- Guarantees **atomicity** and **modification order (coherence)** for the single variable.
- Provides **zero synchronization** or happens-before ordering with other variables.
- Translates to plain machine instructions on all architectures (e.g. `mov` on x86, `ldr`/`str` on ARM).

#### 2. `memory_order_release` (Store operation)
- Establishes that **all preceding memory writes (both atomic and non-atomic)** in program order cannot be reordered *after* this release store.
- Emits a release fence or store-release instruction (e.g. `STLR` on ARM; no-op on x86 beyond preventing compiler reordering).

#### 3. `memory_order_acquire` (Load operation)
- Establishes that **all subsequent memory reads and writes** in program order cannot be reordered *before* this acquire load.
- Emits an acquire fence or load-acquire instruction (e.g. `LDAR` on ARM; no-op on x86 beyond preventing compiler reordering).

#### 4. `memory_order_acq_rel` (Read-Modify-Write)
- Combines acquire and release semantics: acts as an acquire load on reading and a release store on writing.

#### 5. `memory_order_seq_cst` (Sequentially Consistent)
- Enforces acquire/release semantics **plus** a globally consistent total order $S$ across all `seq_cst` operations in the entire system.
- Every thread observes all `seq_cst` operations in the exact same sequence.
- Translates to `LOCK CMPXCHG` or `MOV` + `MFENCE` on x86.

#### 6. `memory_order_consume` (Data dependency)
- Restricts ordering only to operations carrying a data dependency from the loaded value.
- Deprecated/unsupported in most current compilers (compilers promote it to `acquire` due to implementation complexity in tracking dependency chains through optimization passes).

### 5.2 Formal Synchronization Relations

#### Synchronizes-With ($\xrightarrow{sw}$)
An atomic operation $A$ (with `release`, `acq_rel`, or `seq_cst`) **synchronizes-with** an atomic operation $B$ (with `acquire`, `acq_rel`, or `seq_cst`) on the same atomic variable $x$ iff:
1. $B$ reads the value stored by $A$, or
2. $B$ reads the value stored by any operation belonging to the **release sequence** headed by $A$.

#### Happens-Before ($\xrightarrow{hb}$)
The complete happens-before relation in C++11/Rust is the transitive closure of program order ($\xrightarrow{po}$) and synchronizes-with ($\xrightarrow{sw}$):
$$\xrightarrow{hb} = (\xrightarrow{po} \cup \xrightarrow{sw})^+$$

If event $e_1 \xrightarrow{po} A$, $A \xrightarrow{sw} B$, and $B \xrightarrow{po} e_2$, then by transitivity:
$$e_1 \xrightarrow{hb} e_2$$
Thus, any non-atomic modifications made before $A$ are fully visible and settled to the thread executing after $B$.

```
Thread 1:                             Thread 2:
data = 42;         (po)
ready.store(1, release)  --[sw]-->  while (!ready.load(acquire));  (po)
                                    assert(data == 42); // Guaranteed OK!
```

### 5.3 Formal Definition of a Data Race & Undefined Behavior
Under the C++11/Rust standard:
> **Definition**: A **Data Race** occurs when two distinct evaluation events $e_1$ and $e_2$ in different threads access the same memory location, at least one access is a non-atomic write, and the events are not ordered by the happens-before relation:
> $$\text{DataRace}(e_1, e_2) \iff \left(\text{loc}(e_1) = \text{loc}(e_2)\right) \land \left(\text{is\_write}(e_1) \lor \text{is\_write}(e_2)\right) \land \neg(e_1 \xrightarrow{hb} e_2) \land \neg(e_2 \xrightarrow{hb} e_1)$$

**Consequence**: In C++ and Rust, a data race constitutes **Undefined Behavior (UB)**. The compiler's optimizer assumes the absence of UB and is legally permitted to reorder, eliminate, speculate, or emit invalid instructions across the entire program compilation unit. In Rust, safe code statically forbids data races via the borrow checker (`Send` and `Sync` traits).
