# Module 04: Concurrency Hazards, Deadlock Theory & Prevention Protocols

---

## 1. Data Race vs Race Condition: The Fundamental Distinction

A prevalent point of confusion in systems programming is the conflation of **Data Races** and **Race Conditions**. They reside at entirely different conceptual layers:

```
+-----------------------------------------------------------------------------+
| Data Race:      HARDWARE / MEMORY MODEL Level (Undefined Behavior / Torn R/W)  |
| Race Condition: SEMANTIC / LOGIC Level (Timing-dependent application error)  |
+-----------------------------------------------------------------------------+
```

### 1.1 Formal Comparative Definition

| Dimension | Data Race | Race Condition |
|---|---|---|
| **Formal Definition** | Two concurrent instructions access the same memory location, at least one is a write, and no happens-before relation connects them ($\neg(e_1 \xrightarrow{hb} e_2) \land \neg(e_2 \xrightarrow{hb} e_1)$). | An execution where the correctness of a program depends on the relative timing or interleaving of concurrent threads. |
| **Language Consequence** | In C/C++/Rust: **Undefined Behavior (UB)**. Compiler optimizes assuming it never occurs, causing arbitrary silent corruption. | Valid program execution; generates logically incorrect or unexpected business state. |
| **Occurrence with Atomics/Locks** | Cannot occur if accesses use proper atomics or locks. | **Can easily occur** even with 100% atomic or mutex-protected operations. |

### 1.2 Race Condition with Zero Data Races: Check-Then-Act
Consider a thread-safe map:
```java
// ConcurrentHashMap is internally synchronized; ZERO data races exist
if (!map.containsKey(key)) {          // Step 1: Check
    map.put(key, computeValue(key));  // Step 2: Act
}
```
**The Hazard**:
Between Step 1 and Step 2, another thread may execute `map.put(key, otherValue)`.
Even though neither `containsKey()` nor `put()` contains a data race (both are internally atomic), the compound operation is **not atomic**. This is a **Semantic Race Condition** (specifically a Time-Of-Check to Time-Of-Use / TOCTOU bug).
*Fix*: Atomic compound operations (e.g., `computeIfAbsent(key, ...)`).

---

## 2. Deadlock: The Coffman Conditions

A **Deadlock** is a permanent state where a set of processes is blocked because each process in the set holds a resource and waits for another resource held by another process in the same set.

### 2.1 Coffman 4 Necessary and Sufficient Conditions (Coffman et al., 1971)
Deadlock can arise if and only if all four of the following conditions hold simultaneously in the system:

1. **Mutual Exclusion**:
   At least one resource must be held in a non-shareable mode (exclusive access).
2. **Hold and Wait**:
   A process must currently hold at least one resource while waiting to acquire additional resources that are held by other processes.
3. **No Preemption**:
   Resources cannot be forcibly confiscated from a process; a resource can be released only voluntarily by the process holding it after completing its task.
4. **Circular Wait**:
   A closed chain of processes $\{P_0, P_1, \dots, P_{k-1}\}$ exists such that $P_0$ is waiting for a resource held by $P_1$, $P_1$ is waiting for a resource held by $P_2$, $\dots$, and $P_{k-1}$ is waiting for a resource held by $P_0$.

---

## 3. The Deadlock Handling Triad

There are three foundational strategies for handling deadlocks:

```
                              [ Deadlock Handling ]
                                       |
          +----------------------------+----------------------------+
          |                            |                            |
    [ Prevention ]               [ Avoidance ]              [ Detection & Recovery ]
(Eliminate >=1 Coffman      (Dynamic safety checking:     (Allow deadlocks, detect
  structural conditions)        Banker's Algorithm)         via WFG, abort/rollback)
```

---

### 3.1 Deadlock Prevention: Havender's Resource Ordering Principle

Deadlock prevention structurally guarantees that at least one of the four Coffman conditions **can never hold**.

The most powerful and widely used prevention technique is eliminating **Circular Wait** via **Havender's Resource Hierarchy** (J.W. Havender, 1968).

#### Formal Statement
Let $\mathcal{R} = \{r_1, r_2, \dots, r_m\}$ be the set of all system resource types.
Define a bijective priority indexing function:
$$f: \mathcal{R} \to \{1, 2, \dots, m\}$$
which establishes a **strict total order** $\prec$ over $\mathcal{R}$:
$$r_a \prec r_b \iff f(r_a) < f(r_b)$$

**Havender's Protocol Rule**:
A process currently holding a set of resources $H \subseteq \mathcal{R}$ can request resource $r_{\text{new}}$ if and only if $r_{\text{new}}$ has a strictly higher index than all resources currently held:
$$\forall r_h \in H, \quad f(r_h) < f(r_{\text{new}})$$
*(Alternatively, if a process needs a lower-indexed resource, it must release all higher-indexed resources first).*

#### Mathematical Proof of Deadlock-Freedom
**Theorem**: A system adhering strictly to Havender's protocol is deadlock-free.

**Proof by Contradiction**:
1. Suppose a deadlock exists. Since Mutual Exclusion, Hold-and-Wait, and No-Preemption hold, the system must contain a Circular Wait.
2. Therefore, there exists a cycle of processes and resources:
   $$P_0 \xrightarrow{\text{waiting}} r_{(1)} \xrightarrow{\text{held by}} P_1 \xrightarrow{\text{waiting}} r_{(2)} \xrightarrow{\text{held by}} \dots \xrightarrow{\text{waiting}} r_{(k)} \xrightarrow{\text{held by}} P_0$$
3. Consider process $P_0$:
   - $P_0$ holds resource $r_{(k)}$ and is requesting resource $r_{(1)}$.
   - By Havender's rule: $f(r_{(k)}) < f(r_{(1)})$.
4. Consider process $P_1$:
   - $P_1$ holds resource $r_{(1)}$ and is requesting resource $r_{(2)}$.
   - By Havender's rule: $f(r_{(1)}) < f(r_{(2)})$.
5. Continuing along the chain for all $i \in \{1, \dots, k-1\}$:
   $$f(r_{(i)}) < f(r_{(i+1)})$$
6. By transitivity of the strict total order:
   $$f(r_{(1)}) < f(r_{(2)}) < \dots < f(r_{(k)}) < f(r_{(1)})$$
   $$\implies f(r_{(1)}) < f(r_{(1)})$$
7. But the relation $<$ over integers is **irreflexive**: $\forall x \in \mathbb{N}, \; x \not< x$. Contradiction!
8. Hence, no directed cycle can exist. The system is provably deadlock-free. $\blacksquare$

---

### 3.2 Deadlock Avoidance: Dijkstra's Banker's Algorithm

Unlike prevention (which restricts static behavior), **Deadlock Avoidance** dynamically examines every resource request and permits it only if the resulting state remains **Safe**.

#### Safe vs Unsafe States
- **Safe State**: There exists at least one **safe sequence** $\langle P_1, P_2, \dots, P_n \rangle$ of all processes such that for each $P_i$, the maximum resources $P_i$ could still request can be satisfied by the currently available resources plus the resources already held by all preceding processes $P_j$ ($j < i$).
- **Unsafe State**: Not deadlocked yet, but a sequence of maximum demands could inevitably force a deadlock.
- **Deadlocked State**: A deadlock has actively materialized.

$$\text{Deadlocked} \subset \text{Unsafe} \subset \text{All States}$$

```
+----------------------------------------------------+
| Unsafe States                                      |
|    +------------------------------------------+    |
|    | Deadlocked States                        |    |
|    +------------------------------------------+    |
+----------------------------------------------------+
       \
        +--- Safe States (No deadlock possible)
```

#### The Formal Model
- $n$: number of processes, $m$: number of resource types.
- $\text{Available}[1..m]$: vector of currently unallocated resources.
- $\text{Max}[1..n, 1..m]$: matrix of maximum resource demand per process.
- $\text{Allocation}[1..n, 1..m]$: matrix of resources currently held.
- $\text{Need}[1..n, 1..m]$: matrix of remaining need:
  $$\text{Need}[i, j] = \text{Max}[i, j] - \text{Allocation}[i, j]$$

#### The Safety Algorithm: Complexity $O(m \cdot n^2)$
```python
def is_safe_state(available, allocation, need, n, m):
    work = list(available)          # O(m)
    finish = [False] * n            # O(n)
    safe_sequence = []

    while len(safe_sequence) < n:
        # Find an unfinished process whose needs can be satisfied by current work
        found = False
        for i in range(n):
            if not finish[i]:
                # Check if Need[i, :] <= Work[:]
                if all(need[i][j] <= work[j] for j in range(m)):
                    # Speculatively assume process i completes and releases all held resources
                    for j in range(m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(i)
                    found = True
                    break
        if not found:
            # Cannot find any candidate process -> state is UNSAFE
            return False, []
            
    return True, safe_sequence
```

#### Resource-Request Algorithm
When process $P_i$ makes request $\text{Request}[1..m]$:
1. If $\exists j : \text{Request}[j] > \text{Need}[i, j]$, abort with error (process exceeded declared max).
2. If $\exists j : \text{Request}[j] > \text{Available}[j]$, process $P_i$ must wait (resources not available).
3. **Speculative Allocation**:
   $$\text{Available} \leftarrow \text{Available} - \text{Request}$$
   $$\text{Allocation}[i] \leftarrow \text{Allocation}[i] + \text{Request}$$
   $$\text{Need}[i] \leftarrow \text{Need}[i] - \text{Request}$$
4. Run `is_safe_state()`:
   - If **Safe**: Grant resources to $P_i$.
   - If **Unsafe**: Rollback speculative allocation; $P_i$ must wait.

---

### 3.3 Deadlock Detection & Recovery: Graph Theory

When prevention and avoidance are too conservative, the runtime allows threads to acquire resources freely and periodically runs a **Deadlock Detection Algorithm**.

#### Resource Allocation Graph (RAG) & Wait-For Graph (WFG)
A directed bipartite graph $G = (V, E)$ where $V = \mathcal{P} \cup \mathcal{R}$.
- Request edge: $P_i \to r_j$ (process $P_i$ is waiting for resource $r_j$).
- Assignment edge: $r_j \to P_i$ (resource $r_j$ is allocated to $P_i$).

In a **Wait-For Graph (WFG)**, resource nodes are collapsed:
$$P_i \to P_j \iff \exists r : (P_i \text{ waits for } r \land r \text{ is held by } P_j)$$

#### Single-Unit vs Multi-Unit Deadlock Criteria
1. **Single-Unit Resource System** (each resource type has exactly 1 instance):
   $$\text{Directed Cycle in WFG} \iff \text{Deadlock}$$
   Cycle existence is both **necessary and sufficient**.
2. **Multi-Unit Resource System** (resource types have multiple instances):
   $$\text{Directed Cycle in RAG} \not\Longleftrightarrow \text{Deadlock}$$
   - A directed cycle is **necessary, but NOT sufficient**.
   - **Knot Condition (Holt 1972)**: A non-empty subset of vertices $K \subseteq V$ is a **knot** iff for every vertex $u \in K$:
     $$\emptyset \neq \text{Reach}(u) = K$$
     (Every vertex in $K$ can reach all other vertices in $K$, and no directed path leaves $K$). If a knot exists where all processes are blocked, the system is deadlocked.
   - **RAG Reduction / Deadlock Detection**: General multi-unit systems are evaluated via iterative graph reduction (analogous to Banker's algorithm): unblocked processes with $\text{Request}_p \le \text{Work}$ release their allocations until no further reduction is possible. Any remaining unreduced processes are permanently deadlocked.

#### Cycle Detection: Tarjan's Strongly Connected Components (SCC) / DFS
Tarjan's algorithm computes all SCCs in $O(|V| + |E|)$ time using DFS with discovery indices (`index`), low-link numbers (`lowlink`), and an explicit recursion stack:
- An SCC with $> 1$ vertex (or a vertex with a self-loop) contains at least one directed cycle (indicating a deadlock in single-unit WFGs).
- Exact cycle paths are extracted via 3-color DFS path tracking.

---

## 4. Priority Inversion: Mars Pathfinder Case Study & Mitigation

**Priority Inversion** occurs in priority-preemptive schedulers when a high-priority task is indirectly preempted by a low-priority task, inverting the intended scheduling hierarchy.

### 4.1 The Mechanism
Consider three tasks with priorities $\text{Prio}(H) > \text{Prio}(M) > \text{Prio}(L)$:
1. Task $L$ acquires a shared lock $K$.
2. Task $H$ becomes ready, preempts $L$, and attempts to acquire lock $K$.
3. Since $K$ is held by $L$, Task $H$ is blocked. $L$ resumes execution to complete its critical section and release $K$.
4. **The Hazard**: Task $M$ (unrelated to lock $K$) becomes ready.
5. Because $\text{Prio}(M) > \text{Prio}(L)$, the CPU scheduler preempts $L$ to run $M$.
6. Task $M$ runs indefinitely. Task $L$ cannot run to release lock $K$.
7. Task $H$ is transitively blocked by Task $M$, despite $\text{Prio}(H) > \text{Prio}(M)$!

```
Task H (High)    |--------[Blocked on Lock K].............................[Runs]
Task M (Med)     |                     |=======[Preempts L & Runs]========|
Task L (Low)     |--[Locks K]--[Preempted].......................[Unlocks]|
```

### 4.2 The 1997 Mars Pathfinder Incident
On Mars, the Mars Pathfinder rover experienced continuous total system resets.
- Low-priority task: `ASI/MET` (meteorological sensor gathering data, acquiring the `1553` information bus mutex).
- Medium-priority tasks: Communications, attitude control threads.
- High-priority task: `bc_dist` (bus distributor delivering commands to instruments; blocked waiting for the `1553` bus mutex).
- Watchdog timer: Detected that high-priority `bc_dist` had not run for a designated window, concluded system lockup, and triggered a hard hardware reboot.
- *Fix transmitted to Mars*: Enabled **Priority Inheritance** on the `1553` mutex via a VxWorks C interpreter script patch.

### 4.3 Mitigation Protocols

#### 1. Priority Inheritance Protocol (PIP)
When high-priority task $H$ blocks on a lock held by low-priority task $L$:
$$\text{Prio}_{\text{effective}}(L) \leftarrow \max\left(\text{Prio}_{\text{base}}(L), \; \max_{T \in \text{Wait}(L)} \text{Prio}(T)\right)$$
- Task $L$ inherits the priority of $H$ for the duration of the critical section.
- Medium-priority task $M$ cannot preempt $L$. $L$ completes its critical section promptly, unlocks $K$, drops back to its base priority, and $H$ immediately preempts and acquires $K$.
- *Limitation*: Can suffer from chained blocking and does not prevent deadlocks.

#### 2. Priority Ceiling Protocol (PCP - Sha, Rajkumar, Lehoczky 1990)
Each lock $K_j$ is statically assigned a **Priority Ceiling** equal to the highest priority of any task that may ever acquire it:
$$\Pi(K_j) = \max_{T \in \text{Users}(K_j)} \text{Prio}(T)$$
A task $T$ can acquire lock $K_{\text{new}}$ only if $T$'s priority is strictly higher than the priority ceilings of all locks currently locked by *other* tasks in the system:
$$\text{Prio}(T) > \max_{K \in \text{HeldByOthers}} \Pi(K)$$
- **Guarantees**:
  1. Complete prevention of deadlocks.
  2. Bounded priority inversion: a high-priority task is blocked by lower-priority tasks at most **once** during its execution.
