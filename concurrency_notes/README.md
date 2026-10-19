# Formal Concurrency: Mathematical Foundations, Memory Models, and Synchronization

> A mathematically rigorous, concise, and comprehensive treatise on concurrent computing, memory consistency models, lock-free data structures, and modern runtime architectures.

---

## Master Index

1. **[01. Formal Foundations & Memory Consistency Models](01_formal_foundations_and_memory_models.md)**
   - Labeled Transition Systems (LTS), interleaving semantics, state invariants.
   - Lamport's happens-before relation ($\xrightarrow{hb}$), strict partial orders, vector clocks.
   - Hardware memory subsystems: store buffers, invalidate queues, MESI protocol state machine.
   - Consistency models: Sequential Consistency (SC), x86 Total Store Order (TSO), Weak/Relaxed memory (ARM/RISC-V).
   - C++11 / Rust memory model: the 6 `memory_order` levels, synchronization edges ($\xrightarrow{sw}$), and formal data race definition.

2. **[02. Mutual Exclusion & Hardware Synchronization Primitives](02_mutual_exclusion_and_hardware_primitives.md)**
   - Critical section criteria: Safety (Mutual Exclusion), Progress (Deadlock-Freedom), Bounded Waiting (Starvation-Freedom).
   - Peterson's algorithm: SC safety proof and formal proof of failure under TSO Store-Load reordering without `MFENCE`.
   - Lamport's Bakery algorithm for $N$ threads: lexicographic ordering and invariants.
   - Herlihy's Consensus Hierarchy: consensus numbers ($1, 2, \infty$), proof that atomic R/W registers cannot solve 2-consensus, CAS universality.
   - Spinlocks: TAS vs TTAS, cache line bouncing, false sharing, MCS and CLH queue locks.

3. **[03. Synchronization Primitives & Classical Concurrent Problems](03_synchronization_primitives_and_classics.md)**
   - Semaphores: fundamental algebraic invariant $S(t) = S_0 + \#V(t) - \#P(t) \ge 0$, binary vs counting, wait queue semantics.
   - Monitors & Condition Variables: Hoare ("Signal and Wait") vs Mesa ("Signal and Continue") vs Brinch Hansen ("Signal and Exit").
   - Mesa predicate mandate: 3 formal reasons why `while (!predicate) cv.wait()` is required (preemption, spurious wakeups, broadcast fanout).
   - Classical problems: Bounded Buffer with dual CVs, Readers-Writers (3 variants: reader-preference, writer-preference, fair), Dining Philosophers under Havender resource ordering.

4. **[04. Concurrency Hazards, Deadlock Theory & Prevention Protocols](04_concurrency_hazards_and_deadlocks.md)**
   - Data race (UB / hardware memory model level) vs Race condition (semantic atomicity violation).
   - Coffman 4 necessary conditions for deadlock.
   - Deadlock triad: Prevention (Havender's strict partial ordering theorem & proof), Avoidance (Dijkstra's Banker's algorithm, $O(m \cdot n^2)$ safety test), Detection & Recovery (Wait-For Graph cycle detection, single-unit cycle $\iff$ deadlock vs multi-unit knot requirement).
   - Priority Inversion: Mars Pathfinder case study, Priority Inheritance Protocol (PIP), Priority Ceiling Protocol (PCP).

5. **[05. Non-Blocking Algorithms & Lock-Free Data Structures](05_non_blocking_and_lock_free_structures.md)**
   - Linearizability (Herlihy & Wing 1990) vs Serializability: real-time order preservation, sequential specification, composability/locality.
   - Non-blocking progress hierarchy: $\text{Wait-Free} \subset \text{Lock-Free} \subset \text{Obstruction-Free}$.
   - The ABA problem: step-by-step memory corruption trace, tagged pointers / double-width CAS, Safe Memory Reclamation (Hazard Pointers, Epoch-Based Reclamation, RCU).
   - Canonical lock-free structures: Treiber Stack and Michael-Scott Queue with explicit linearization points.
   - Comparison with sequential Binary Heaps (connecting to COL1101 Lec 21): multi-level coordination bottlenecks and contention bounds.

6. **[06. Modern Concurrency Paradigms & Python Runtime Architecture](06_modern_paradigms_and_python_runtime.md)**
   - Actor model vs CSP: message passing mailboxes vs rendezvous channels.
   - Event loops & cooperative multitasking: I/O multiplexing (`epoll`, `kqueue`, `io_uring`), coroutine state machines, await-point race hazards.
   - Structured Concurrency: lifetime encapsulation, Python `asyncio.TaskGroup`, Trio nurseries, error propagation.
   - CPython runtime internals: Global Interpreter Lock (GIL) mechanics, reference count cache-line contention, free-threading (PEP 703: biased refcounting, deferred refcounting, mimalloc allocator), comparative performance analysis.

7. **[Executable Python Verification Test Suite](code/)**
   - [`test_peterson_mutex.py`](code/test_peterson_mutex.py): Peterson's algorithm in SC and proof of failure under simulated TSO Store-Load reordering.
   - [`test_producer_consumer_cv.py`](code/test_producer_consumer_cv.py): Mesa condition variable bounded buffer under simulated spurious wakeups (`while` vs `if`).
   - [`test_dining_philosophers_hierarchy.py`](code/test_dining_philosophers_hierarchy.py): Havender resource hierarchy ordering ($\min(L, R)$ first) under high contention.
   - [`test_treiber_stack.py`](code/test_treiber_stack.py): Lock-free Treiber stack, ABA memory corruption reproduction, and tagged pointer prevention.
   - [`test_deadlock_cycle_detector.py`](code/test_deadlock_cycle_detector.py): Wait-For Graph cycle detector implementing Tarjan's DFS returning exact cycle paths.

---

## Formal Notation & Mathematical Foundations

### 1. Labeled Transition Systems (LTS)
A concurrent system is formally modeled as a tuple:
$$\mathcal{T} = \langle \mathcal{S}, S_0, \Sigma, \to \rangle$$
where:
- $\mathcal{S}$ is the set of global system states: $\mathcal{S} = \mathcal{S}_1 \times \mathcal{S}_2 \times \dots \times \mathcal{S}_n \times \mathcal{M}$, where $\mathcal{S}_i$ is the local state of thread $i$ (including program counter $PC_i$ and registers) and $\mathcal{M}$ is the shared memory state.
- $S_0 \in \mathcal{S}$ is the initial state.
- $\Sigma = \bigcup_{i=1}^n \Sigma_i$ is the set of atomic actions (events) performed by threads.
- $\to \subseteq \mathcal{S} \times \Sigma \times \mathcal{S}$ is the transition relation, written $s \xrightarrow{\alpha} s'$.

An **execution trace** $\tau$ is a finite or infinite sequence of transitions:
$$\tau = s_0 \xrightarrow{\alpha_1} s_1 \xrightarrow{\alpha_2} s_2 \xrightarrow{\alpha_3} \dots$$

### 2. State Invariants & Inductive Proofs
A property $P: \mathcal{S} \to \{0, 1\}$ is an **invariant** of $\mathcal{T}$ (denoted $\square P$) iff for every state $s$ reachable from $S_0$ via $\to^*$, $P(s) = 1$.

To establish an invariant inductively:
1. **Base Case**: $P(S_0) = 1$.
2. **Inductive Step**: $\forall s, s' \in \mathcal{S}, \forall \alpha \in \Sigma: (P(s) = 1 \land s \xrightarrow{\alpha} s') \implies P(s') = 1$.

### 3. Relations and Orderings
- **Strict Partial Order**: A binary relation $\prec$ over a set $E$ that is:
  1. *Irreflexive*: $\forall a \in E, \; \neg(a \prec a)$.
  2. *Asymmetric (strict antisymmetry)*: $\forall a, b \in E, \; a \prec b \implies \neg(b \prec a)$.
  3. *Transitive*: $\forall a, b, c \in E, \; (a \prec b \land b \prec c) \implies a \prec c$.
  *(Note: In order theory, asymmetry follows directly from irreflexivity and transitivity; non-strict partial orders instead require reflexivity and weak antisymmetry: $a \le b \land b \le a \implies a = b$)*.
- **Strict Total Order**: A strict partial order that satisfies *totality*:
  $$\forall a \neq b \in E, \; (a \prec b) \lor (b \prec a)$$

### 4. Lamport's Happens-Before Relation ($\xrightarrow{hb}$)
Let $E$ be the set of events in an execution. The happens-before relation $\xrightarrow{hb} \subseteq E \times E$ is the smallest relation satisfying:
1. **Program Order**: If events $a$ and $b$ occur in the same thread and $a$ precedes $b$, then $a \xrightarrow{po} b \implies a \xrightarrow{hb} b$.
2. **Synchronization**: If $a$ is a synchronization send (e.g. unlock, message send) and $b$ is the corresponding synchronization receive (e.g. lock acquisition, message receive), then $a \xrightarrow{sw} b \implies a \xrightarrow{hb} b$.
3. **Transitivity**: If $a \xrightarrow{hb} b$ and $b \xrightarrow{hb} c$, then $a \xrightarrow{hb} c$.

Two events $a, b$ are **concurrent** ($a \parallel b$) iff:
$$\neg(a \xrightarrow{hb} b) \land \neg(b \xrightarrow{hb} a)$$

### 5. Safety vs Liveness (Alpern-Schneider Theorem)
Every formal specification $\Phi \subseteq \Sigma^\omega$ can be uniquely decomposed into the intersection of a **Safety property** and a **Liveness property**:
$$\Phi = \text{Safety} \cap \text{Liveness}$$
- **Safety ("Bad things never happen")**:
  $$\forall \sigma \notin \text{Safety}, \exists \text{ finite prefix } \hat{\sigma} \sqsubset \sigma, \forall \tau \in \Sigma^\omega: \hat{\sigma} \cdot \tau \notin \text{Safety}$$
  Safety properties are prefix-closed and verifiable over finite traces (e.g., Mutual Exclusion, Absence of Deadlock).
- **Liveness ("Good things eventually happen")**:
  $$\forall \text{ finite prefix } \hat{\sigma} \in \Sigma^*, \exists \tau \in \Sigma^\omega: \hat{\sigma} \cdot \tau \in \text{Liveness}$$
  Liveness violations cannot be detected in finite time; they require infinite traces (e.g., Starvation-Freedom, Termination).

---

## Running the Verification Suite

The repository includes a rigorous Python test suite covering each core theoretical principle. The suite executes standard library components and requires `pytest`:

```bash
cd /home/atrv/Desktop/col
python3 -m pytest concurrency_notes/code/ -v
```
