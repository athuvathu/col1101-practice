# Concurrency: Comprehensive Lecture Notes (COL 1101)

> **Course Reference:** COL 1101 — Lecture 15 (*August 25, 2026*) & Lecture 16 (*August 27, 2026*)  
> **Topic:** Concurrency, Shared Memory Hazards, Synchronization with Locks, Locking Pitfalls, and Alternative Paradigms (Functional Parallelism & The Actor Model)

---

## 1. Context & "The Story So Far"

Across previous lectures, programming has been explored through two dominant paradigms:

1. **Imperative / Object-Oriented Programming (OOP):**
   - Data structures and operations are bundled together into objects/classes.
   - Programs manipulate and evolve state through **in-place mutation** of variables and object attributes.

2. **Functional Programming:**
   - Computation is treated as the evaluation of mathematical functions: `(f (g (h ...)))`.
   - Emphasizes **immutable data** and **pure functions** (functions without side effects).

```
   ┌─────────────────────────────────────────────────────────────┐
   │                       THE STORY SO FAR                      │
   ├──────────────────────────────┬──────────────────────────────┤
   │   #1: Imperative / OOP       │   #2: Functional Programming │
   │   - Data + Operations        │   - Immutable Data           │
   │   - Mutable Data / State     │   - Pure Functions           │
   │   - In-place Updates         │   - Function Composition     │
   └──────────────────────────────┴──────────────────────────────┘
```

### The Single-Threaded Assumption
Every program encountered up to this point operated under one foundational assumption:

> *"A program executes sequentially — one line at a time, and strictly in order."*

Consider sequential updates to a bank balance:
```python
balance += 100
balance += 10
balance -= 50
balance -= 50
```

If this sequence is executed **one million times**, it produces the exact same result every single time.
- **Why?** There is a **single reader** and a **single writer**. The execution path is completely deterministic.
- **The Core Question:** *What happens when two or more independent execution flows touch the exact same data at the same time?*

---

## 2. Motivation: Why Concurrency?

Sequential execution is simple and deterministic, but real-world computing environments demand concurrency for four primary reasons:

1. **Web Servers & High-Throughput Services:**
   - A web server must handle requests from thousands of users simultaneously. Servicing users strictly one-by-one in sequence would cause unacceptable response times and timeouts.

2. **User Interface (UI) Responsiveness in GUI & Mobile Apps:**
   - Mobile and desktop applications run a dedicated UI thread. If a heavy computation or network download runs on that same thread, the user interface freezes. Running background work concurrently keeps the UI fluid and interactive.

3. **I/O Latency vs. CPU Idle Time:**
   - Network calls (e.g., web scrapers, database queries) and disk I/O operate orders of magnitude slower than CPU clock cycles. In a sequential program, the CPU sits idle while waiting for an I/O response. Concurrency allows the CPU to switch to another useful task while the first task waits for I/O.

4. **Multi-Core Processor Utilization:**
   - Modern computing hardware contains multiple physical CPU cores (e.g., 4, 8, 16 cores). A purely sequential single-threaded program can utilize at most one core (leaving 75%–90%+ of hardware computational capacity unused). Concurrency enables programs to utilize all available CPU cores in parallel.

---

## 3. Units of Execution: Processes vs. Threads

When running multiple tasks concurrently, the operating system provides two primary abstractions: **Processes** and **Threads**.

```
PROCESS (Heavyweight)
┌────────────────────────────────────────────────────────────────────────┐
│ Virtual Address Space                                                  │
│                                                                        │
│  [ Code / Text ]          [ Global / Data ]          [ Heap ]          │
│                                                                        │
│  ┌────────────────────────┐              ┌──────────────────────────┐  │
│  │ Thread A               │              │ Thread B                 │  │
│  │ - Program Counter (PC) │              │ - Program Counter (PC)   │  │
│  │ - CPU Registers        │              │ - CPU Registers          │  │
│  │ - Private Stack        │              │ - Private Stack          │  │
│  └────────────────────────┘              └──────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Architectural Comparison

| Dimension | Process ("Program") | Thread ("Lightweight Process") |
| :--- | :--- | :--- |
| **Address Space** | **Isolated / Private** memory space. Processes do not share address space. | **Shared** memory space within the parent process. |
| **What is Shared?** | Nothing by default. | Shared **Code**, shared **Global Data**, shared **Heap**. |
| **What is Private?** | Entire address space, file descriptors, OS resources. | Private **Stack** (local variables), private **Program Counter (PC)**, private **Registers**. |
| **Context Switching** | **Heavyweight**: OS must switch page tables, memory maps, cache mappings, and CPU state. | **Lightweight**: Only CPU registers, stack pointer, and PC need to be saved/restored. |
| **Communication** | Requires **Inter-Process Communication (IPC)**: network sockets, pipes, files, OS shared memory. | **Direct Memory Access**: Read and write shared variables in Heap/Data directly. |
| **Safety vs. Danger** | **Safe isolation**: A crash in one process does not corrupt memory in another process. | **High Danger**: Uncoordinated simultaneous memory access can corrupt data (race conditions). |

### Python Threading Interface
Python provides the `threading` module to spawn and manage threads:

```python
import threading

def worker_task(worker_id):
    print(f"Worker {worker_id} executing")

# Creating threads: specify target function and arguments tuple
t1 = threading.Thread(target=worker_task, args=(1,))
t2 = threading.Thread(target=worker_task, args=(2,))

# Starting threads (spawns execution in OS/runtime)
t1.start()
t2.start()

# Joining threads: caller blocks until the thread finishes execution
t1.join()
t2.join()
```

---

## 4. Shared Memory & Race Conditions

### The Motivating Example: Two Cash Machines (ATMs)
Consider two separate ATM machines connected to the same central bank account with an initial balance of **$1,000**:

```
                       Central Bank Account
                      [ Balance = $1,000 ]
                              ▲     ▲
                     ┌────────┘     └────────┐
              ATM 1  │                       │  ATM 2
         [ balance -= 50 ]              [ balance -= 50 ]
```

- ATM 1 and ATM 2 issue withdrawal commands at overlapping times.
- Both read the account balance, modify it, and write it back.
- **Claim from slides:** *The outcome of this concurrent execution is not always deterministic!*

### The Check-Then-Act Hazard (Overdraft / Negative Balance)
In a real-world withdrawal, code must verify sufficient funds before dispensing money:

```python
# Intended business logic:
if balance >= amount:
    # <--- Context switch can happen here!
    balance -= amount
    dispense_cash(amount)
```

If the balance is **$100**, and two users simultaneously attempt to withdraw **$80**:
1. ATM 1 checks `balance >= 80` $\to$ `100 >= 80` is **True**.
2. Before ATM 1 executes the deduction, the OS preempts ATM 1 and schedules ATM 2.
3. ATM 2 checks `balance >= 80` $\to$ `100 >= 80` is **True** (stale read!).
4. ATM 2 deducts $80 (`balance = 20`) and dispenses $80.
5. OS resumes ATM 1. ATM 1 already passed the check, so it proceeds to deduct $80: `balance = 20 - 80 = -60` and dispenses $80.
- **Result:** $160 cash was dispensed from a $100 account, leaving a negative balance (overdraft).

---

### Anatomy of an Update: Desugaring `balance += amt`
High-level expressions like `balance += amt` or `counter += 1` are **not atomic** (they are not a single indivisible CPU instruction). At the machine/bytecode level, they desugar into **three distinct operations**:

$$\text{Step 1: Read} \longrightarrow \text{Step 2: Add} \longrightarrow \text{Step 3: Write}$$

1. **Read:** Load the current value of `balance` from shared memory into a local CPU register / thread stack.
2. **Add:** Add `amt` to the register value.
3. **Write:** Store the updated register value back into shared memory.

---

### Execution Traces: Sequential vs. Interleaved

Let initial shared `balance = 100`.  
- **Thread A:** deposits `100` (`balance += 100`)
- **Thread B:** deposits `50` (`balance += 50`)

#### Scenario 1: Sequential Execution (Deterministic & Correct)

| Step | Thread | Action | Local Computation | Shared `balance` |
| :---: | :---: | :--- | :--- | :---: |
| 0 | — | *Initial state* | — | **100** |
| 1 | **Thread A** | `read balance` | `reg_A = 100` | 100 |
| 2 | **Thread A** | `add amt (100)` | `reg_A = 100 + 100 = 200` | 100 |
| 3 | **Thread A** | `write balance` | write `200` to memory | **200** |
| 4 | **Thread B** | `read balance` | `reg_B = 200` | 200 |
| 5 | **Thread B** | `add amt (50)` | `reg_B = 200 + 50 = 250` | 200 |
| 6 | **Thread B** | `write balance` | write `250` to memory | **250** |

$$\text{Final Balance} = \mathbf{250} \quad (\text{Correct: } 100 + 100 + 50 = 250)$$

---

#### Scenario 2: Interleaved Execution (Race Condition / Lost Update)

When instructions from Thread A and Thread B interleave:

| Step | Thread | Action | Local Computation | Shared `balance` |
| :---: | :---: | :--- | :--- | :---: |
| 0 | — | *Initial state* | — | **100** |
| 1 | **Thread A** | `read balance` | `reg_A = 100` | 100 |
| 2 | **Thread B** | `read balance` | `reg_B = 100` *(stale read!)* | 100 |
| 3 | **Thread A** | `add amt (100)` | `reg_A = 100 + 100 = 200` | 100 |
| 4 | **Thread B** | `add amt (50)` | `reg_B = 100 + 50 = 150` | 100 |
| 5 | **Thread A** | `write balance` | write `200` to memory | **200** |
| 6 | **Thread B** | `write balance` | write `150` to memory | **150** |

$$\text{Final Balance} = \mathbf{150} \quad (\text{INCORRECT: Thread A's \$100 deposit was completely obliterated!})$$

---

### Definition of a Race Condition
> **Race Condition:** A flaw in concurrent software where the correctness or final outcome of a program depends on the **relative timing, scheduling, or interleaving** of instructions executed by multiple threads.

### The Three Essential Conditions
For a race condition to exist, all three of the following conditions must hold simultaneously:

```
                  ┌─────────────────────────────────────────┐
                  │ 1. SHARED DATA                          │
                  │    Multiple threads access the same     │
                  │    memory location.                     │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ 2. MUTABLE STATE                        │
                  │    The shared data can be modified      │
                  │    (written to).                        │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ 3. CONCURRENT ACCESS                    │
                  │    Multiple threads access the data at  │
                  │    the same time (with ≥ 1 writer).     │
                  └─────────────────────────────────────────┘
```

> **Key Rule for Solutions:** To eliminate a race condition, you must **break at least one** of these three conditions!

---

### Is It Only a Problem with Multiple Processors?

> **Question from Slide 14–15:** *Is a race condition only a problem when running on a machine with multiple physical processors/cores?*  
> **Answer:** **NO.**

Even on a single-core CPU:
- The OS kernel scheduler uses **preemptive multitasking / time-slicing** ($T_1, T_2, T_3$).
- A hardware timer periodically interrupts the CPU, giving the OS scheduler control to swap running threads (context switch).
- The context switch can occur **at any machine instruction boundary** — including halfway through an evaluation like `reg = balance; [PREEMPTION] balance = reg + amt`.
- Therefore, race conditions occur just as easily on a **single-core** system as on a multi-core system. Concurrency hazards are algorithmic and structural, not purely hardware phenomena.

---

## 5. Critical Sections & Mutual Exclusion with Locks

### Breaking Condition 3: Enforcing Order with Locks
In the Imperative / OOP paradigm, data is inherently shared and mutable. Therefore, the strategy to eliminate race conditions is to **break Condition 3 (Concurrent Access)** by enforcing order and mutual exclusion.

### Definitions
- **Critical Section:** A block of code that accesses shared mutable state (e.g., updating `counter += 1` or reading and updating `self.balance`).
- **Mutual Exclusion (Mutex):** Ensuring that when one thread enters a critical section, all other threads are prevented from entering until the first thread exits.
- **Lock (`threading.Lock()`):** A synchronization primitive used to enforce mutual exclusion.

```
                    Thread 1                       Thread 2
                       │                              │
               lock.acquire()                         │
           ┌───────────────────────┐                  │
CRITICAL   │  read counter         │          lock.acquire() (BLOCKS!)
SECTION    │  increment            │                  ┊ (waiting...)
           │  write counter        │                  ┊
           └───────────────────────┘                  ┊
               lock.release()                         ▼
                       │                      [acquires lock]
                                          ┌───────────────────────┐
                                          │  read counter         │
                                          │  increment            │
                                          │  write counter        │
                                          └───────────────────────┘
                                              lock.release()
```

### Low-Level Lock API vs. Context Manager (`with lock:`)
Python provides two ways to use locks:

```python
import threading

counter = 0
lock = threading.Lock()

# 1. Manual acquire / release (Prone to errors if an exception occurs):
lock.acquire()
try:
    counter += 1
finally:
    lock.release()

# 2. Idiomatic Python Context Manager (Guarantees release on exit):
with lock:
    counter += 1  # CRITICAL SECTION
```

---

### Bank Account Example with Locks (from Slide 20)
To demonstrate that a lock protects critical sections even when thread switching is artificially forced, the lecture slides introduce `time.sleep(0)` (which yields the CPU to the OS scheduler):

```python
import threading
import time

lock = threading.Lock()

class Account:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amt):
        with lock:
            # CRITICAL SECTION START
            t = self.balance
            time.sleep(0)          # Voluntarily yields CPU / forces context switch
            self.balance = t + amt
            # CRITICAL SECTION END

acc = Account(0)

def work():
    for _ in range(10000):
        acc.deposit(10)

# Two threads simultaneously performing 10,000 deposits of 10
t1 = threading.Thread(target=work)
t2 = threading.Thread(target=work)

t1.start()
t2.start()
t1.join()
t2.join()

print(f"Final Balance: {acc.balance}")  # Exactly 200,000 (Deterministic!)
```

- Without `with lock:`, `time.sleep(0)` causes rampant lost updates, leaving `balance` far below `200000`.
- With `with lock:`, mutual exclusion guarantees that even if a thread yields the CPU mid-deposit, no other thread can enter `deposit()` until the lock is released.

---

## 6. The Two Major Pitfalls of Locking (Lecture 16)

While locks solve race conditions, they introduce two severe software engineering and performance pitfalls:

```
                      PITFALLS OF LOCKING
                     ┌───────────────────┐
         ┌───────────┤   Lec 16 Slides   ├───────────┐
         │           └───────────────────┘           │
         ▼                                           ▼
   PITFALL 1: CONTENTION                       PITFALL 2: DEADLOCK
   - Serialization bottleneck                  - Circular waiting:
   - Parallel code runs sequentially             T1 holds L1, wants L2
   - Context-switch overhead                     T2 holds L2, wants L1
   - Harms performance                         - Both sleep forever!
```

---

### Pitfall 1: Contention & Performance Degradation
A lock forces threads to execute one at a time. This introduces two major performance problems:

1. **Serialization Bottleneck:**
   - If multiple threads spend most of their execution time waiting to acquire a lock, concurrent code degenerates into sequential code. Adding more CPU cores will not speed up the program.
2. **Locking Overhead & Granularity:**
   - **What to lock?**
     - **Coarse-Grained Locking:** Locking a large block of code or using one global lock for all accounts. Simple to write, but creates massive contention (every thread waits on everyone else).
     - **Fine-Grained Locking:** Using smaller locks (e.g., a lock per individual bank account). Improves concurrency, but dramatically increases code complexity and deadlock risk.
   - **Critical Section Size:** Critical sections must be kept as small as possible. Never place slow operations (I/O, network requests, long sleep calls) inside a critical section.

---

### Pitfall 2: Deadlock
Deadlock occurs when two or more threads are permanently blocked because each is waiting for a lock held by the other.

#### The Classic Deadlock Trace (from Slide 10 of Lec 16)
- System has two locks: $L_1$ and $L_2$.
- Two threads execute concurrently: Thread 1 ($T_1$) and Thread 2 ($T_2$).

```
Thread 1 (T1)                                 Thread 2 (T2)
----------------------------------            ----------------------------------
with lock_1:                                  with lock_2:
    # T1 acquires L1                              # T2 acquires L2
    ...                                           ...
    with lock_2:                                  with lock_1:
        # T1 BLOCKS (waiting for L2!)                 # T2 BLOCKS (waiting for L1!)
```

```
                  ┌────────────┐
                  │  Thread 1  │
                  └─────┬──────┘
             Holds L1   │   Waiting for L2
                        ▼
                  ┌────────────┐
                  │   Lock 2   │
                  └─────┬──────┘
                        ▲
             Holds L2   │   Waiting for L1
                  ┌─────┴──────┐
                  │  Thread 2  │
                  └────────────┘
```

#### Step-by-Step Deadlock Timeline

| Time | Thread 1 ($T_1$) | Thread 2 ($T_2$) | State of Locks |
| :---: | :--- | :--- | :--- |
| $t_1$ | Acquires $L_1$ | — | $L_1$ held by $T_1$ |
| $t_2$ | — | Acquires $L_2$ | $L_1$ held by $T_1$, $L_2$ held by $T_2$ |
| $t_3$ | Attempts to acquire $L_2$ $\to$ **Blocks** | — | $T_1$ sleeping, waiting on $T_2$ |
| $t_4$ | — | Attempts to acquire $L_1$ $\to$ **Blocks** | $T_2$ sleeping, waiting on $T_1$ |
| $\infty$ | **Waiting for $L_2$** | **Waiting for $L_1$** | **DEADLOCK: Both threads sleep forever.** |

The application freezes completely, consumes zero CPU, and will never recover without process termination.

---

### Pointer to Other Synchronization Primitives (Slide 11 of Lec 16)
The slides briefly identify other classical synchronization primitives:
1. **Semaphores:** A counter-based primitive that allows up to $N$ threads to access a resource concurrently (generalization of a binary mutex).
2. **Conditionals / Wait (`Condition` variables):** Allows threads to release a lock and sleep until another thread signals that a state condition has become true (wait/notify pattern).
3. **Barriers / Events:** Coordination points where threads synchronize arrival before proceeding.

> **Slide 11 Note:** *"You will meet them in Operating Systems course!"*

---

## 7. Alternative Paradigms: Avoiding Locks Altogether

Because locks introduce contention, overhead, and deadlocks, modern software design explores alternative paradigms that **break the conditions for race conditions without using locks**.

Recall the 3 conditions:
1. Shared data
2. Mutable data
3. Concurrent access

---

### Alternative 1: Functional Programming (Breaking Condition 2 — Mutable State)
- **Principle:** If data is **immutable**, it can never be modified in place.
- **Result:** Multiple threads or processes can read the exact same data simultaneously with zero synchronization and zero risk of corruption.
- **Takeaway:** *Immutable data is **thread-safe by construction!***

```
                  ┌─────────────────────────────────────────┐
                  │        FUNCTIONAL PARADIGM              │
                  │   - Immutable Data Structures           │
                  │   - Pure Functions (No Side-Effects)    │
                  │   - Breaks Condition 2 (Mutable State)  │
                  │   ===> THREAD-SAFE BY DESIGN!           │
                  └─────────────────────────────────────────┘
```

#### Parallelization with `multiprocessing.Pool` (from Slide 15 of Lec 16)
Because pure functions do not mutate shared state, computing tasks can be split across processes running in parallel on separate CPU cores:

```python
import multiprocessing as mp

def parallel_sum(data, cores=4):
    # 1. Split data into manageable, independent chunks
    size = max(1, len(data) // cores)
    chunks = [data[i:i + size] for i in range(0, len(data), size)]

    # 2. Map built-in pure 'sum' to each chunk in parallel across CPU cores
    with mp.Pool(cores) as pool:
        # pool.map distributes chunks to worker processes
        # Outer sum aggregates the partial sums
        return sum(pool.map(sum, chunks))

if __name__ == '__main__':
    # 10,000,001 elements computed in parallel
    total = parallel_sum(list(range(10_000_001)))
    print(f"Parallel Result: {total}")
```

#### Why This is Superior to Shared-Memory Locking:
- No shared mutable memory $\implies$ No locks needed.
- No locks $\implies$ Zero contention, zero chance of deadlock.
- Scales linearly with the number of CPU cores for CPU-bound computations.

---

### Alternative 2: The Actor Model (Breaking Condition 1 — Shared Data)

In systems where state **must evolve** over time (e.g., bank accounts, shopping carts, game servers), pure immutability alone is insufficient. How do we mutate state without shared memory and without locks?

> **Foundational Motto (Slide 18 of Lec 16):**  
> *"Do not communicate by sharing memory; instead, share memory by communicating!"*

#### Core Architecture of the Actor Model
1. **The Actor:** An autonomous, independent worker that encapsulates **strictly private state** (e.g., `balance` is private to the Actor). Outside threads can never read or write the actor's variables directly.
2. **The Mailbox (Message Queue):** Every actor owns a FIFO message queue (mailbox). External threads submit tasks/requests by sending messages into the mailbox.
3. **Sequential Event Loop:** The actor runs its own private sequential loop, pulling one message at a time from its mailbox and updating its private state.

```
Threads / Clients                 Mailbox (Queue)                 Actor (Private State)
─────────────────                 ───────────────                 ─────────────────────
  Thread 1 ─── [ "deposit 10" ] ───┐
                                   ├──► ┌─────────────┐            ┌─────────────────┐
  Thread 2 ─── [ "withdraw 10" ] ──┤    │ deposit 10  │            │  Private State: │
                                   │    │ withdraw 10 │ ──pop()──► │  balance = 1000 │
  Thread 3 ─── [ "withdraw 50" ] ──┘    │ withdraw 50 │            │                 │
                                        └─────────────┘            │  (Single-thread │
                                                                   │   event loop)   │
                                                                   └─────────────────┘
                                                                     NO LOCKS NEEDED!
```

#### Why the Actor Model Eliminates Concurrency Bugs:
- **No Shared State:** No external thread ever touches `balance` directly (Condition 1 broken).
- **Sequential Processing:** Because the actor processes messages strictly one-by-one from its mailbox, state updates are serialized naturally without locks.
- **No Contention & No Deadlocks:** Calling threads don't block on locks; they simply enqueue a message and move on. Deadlock cannot occur because threads do not hold locks on each other's resources.

---

## 8. Comprehensive Summary & Paradigm Comparison

| Feature / Paradigm | Imperative / OOP with Locks | Functional Programming | The Actor Model |
| :--- | :--- | :--- | :--- |
| **Primary Mechanism** | Mutual Exclusion via `threading.Lock()` | Immutable Data Structures & Pure Functions | Autonomous Actors with Private State & Message Queues |
| **Which Race Condition is Broken?** | **Breaks Condition 3:** Prevents concurrent access to shared mutable memory | **Breaks Condition 2:** Eliminates mutable state altogether | **Breaks Condition 1:** Eliminates shared memory; state is strictly private |
| **Slide Example** | `Account.deposit()` with `with lock:` and `time.sleep(0)` | `parallel_sum()` using `multiprocessing.Pool().map()` | Central Account Actor processing deposit/withdrawal messages |
| **Key Advantage** | Familiar, fits standard OOP models | Thread-safe by construction, trivially parallelizable | Clean state evolution without locks, deadlocks, or shared memory bugs |
| **Main Pitfalls / Drawbacks** | - **Contention** (performance loss)<br>- **Deadlocks** ($T_1 \leftrightarrow T_2$) | Cannot represent mutable state in-place without returning new structures | Requires asynchronous messaging architecture and message serialization |

---
*End of Notes — Faithfully compiled and synthesized from COL 1101 Concurrency Lecture Slides (Lec 15 & Lec 16).*
