# Module 06: Modern Concurrency Paradigms & Python Runtime Architecture

---

## 1. High-Level Concurrency Paradigms: Actor Model vs CSP

Shared-memory concurrency with explicit locks is notoriously bug-prone. Two dominant declarative paradigms emerged to eliminate shared mutable state: the **Actor Model** and **Communicating Sequential Processes (CSP)**.

```
+-----------------------------------------------------------------------------+
| Actor Model: Entities are primary (Actors own mailboxes, address by identity)|
| CSP:         Channels are primary (Anonymous processes synchronize on chans) |
+-----------------------------------------------------------------------------+
```

### 1.1 The Actor Model (Carl Hewitt 1973, Gul Agha 1986, Erlang / Akka)
An **Actor** is an autonomous concurrent computational entity encapsulating state, behavior, and a mailbox.

#### Axioms of Actor Computation
Upon receiving a message, an actor can execute only three operations:
1. **Send** a finite number of messages to other actors (whose addresses it knows).
2. **Create** a finite number of new actors.
3. **Designate** the behavior/state to be used for the next incoming message.

#### Properties
- **No Shared State**: Each actor's local state is strictly private.
- **Asynchronous Message Passing**: Messages are enqueued into an unbounded or bounded FIFO mailbox. The sender continues execution immediately without blocking.
- **Fault Tolerance**: Hierarchical supervision trees ("Let it crash" philosophy); supervisors detect child failure via signals and restart actors from clean states.

---

### 1.2 Communicating Sequential Processes (CSP - C.A.R. Hoare 1978, Go, Occam)
In CSP, concurrent entities are sequential processes that communicate through first-class **synchronization channels**.

#### Core Principles
- **Channels as First-Class Citizens**: Processes are anonymous; they do not address each other directly. Instead, they read from and write to named channels (`c <- val`, `val := <-c`).
- **Rendezvous Synchronization (Unbuffered Channels)**: A send operation blocks until a receiver is ready to read, and a receive blocks until a sender is ready to write. The transfer of data is an instantaneous atomic handshake.
- **Buffered Channels**: Decouple sender and receiver up to buffer capacity $K$. Once full, senders block; once empty, receivers block.
- **Multiplexing via `select`**: Allows a process to wait non-deterministically on multiple channel read/write operations simultaneously.

### 1.3 Architectural Comparison

| Dimension | Actor Model (Erlang, Akka) | CSP (Go, Occam) | Shared Memory (Pthreads, C++11) |
|---|---|---|---|
| **Primary Abstraction** | Actor (Entity) | Channel (Pipe) | Memory Address / Variable |
| **Addressing** | Explicit (Recipient Actor PID / URL) | Anonymous (Write to Channel) | Shared Pointer / Reference |
| **Synchronization** | Asynchronous (Buffered Mailbox) | Synchronous (Rendezvous) or Bounded | Locks, Atomics, Barriers |
| **State Sharing** | Zero (Strict Message Copying) | Zero (Pass-by-value on Channel) | Ubiquitous (Shared Heap) |
| **Failure Handling** | Supervision Trees / Erlang Links | Explicit error returns / Panics | Exceptions / Crashes |

---

## 2. Event Loops & Cooperative Concurrency

Cooperative concurrency implements multitasking in user-space without kernel thread preemption.

### 2.1 OS Notification Primitives: Evolution of I/O Multiplexing

```
  select() / poll()               epoll() / kqueue()                 io_uring
   [ O(N) linear scan ]    -->     [ O(1) event-driven ]     -->   [ Zero-syscall ring ]
   Kernel scans all FDs          Kernel notifies active FDs       Kernel & user share rings
```

1. **`select` / `poll` ($O(N)$)**:
   The application passes an array of $N$ file descriptors to the kernel on every syscall. The kernel scans all $N$ descriptors to check readiness. Scales terribly for high-concurrency servers ($C10K$ problem).
2. **`epoll` (Linux) / `kqueue` (BSD / macOS) ($O(1)$)**:
   The application registers interest in file descriptors once via a kernel red-black tree. When an I/O event occurs, the kernel places the ready descriptor onto an event ready list. `epoll_wait()` returns only the active events in $O(1)$ time.
   - *Level-Triggered*: `epoll_wait` notifies repeatedly as long as the buffer contains unread data.
   - *Edge-Triggered*: `epoll_wait` notifies **only once** when a new state transition occurs. The application must drain the entire buffer until `EAGAIN` / `EWOULDBLOCK`.
3. **`io_uring` (Linux 5.1+)**:
   Eliminates system call overhead entirely via two memory-mapped ring buffers shared between user-space and kernel-space:
   - **Submission Queue (SQ)**: Application writes asynchronous I/O requests without syscalls.
   - **Completion Queue (CQ)**: Kernel places completed results directly into the ring.
   - Can run in kernel polling mode (`IORING_SETUP_SQPOLL`), achieving millions of IOPS with zero syscall context switches.

---

### 2.2 Coroutine State Machines: Desugaring `async`/`await`

Coroutines are cooperative execution units that can pause execution (yield control) and resume later while preserving their local stack/variables.

- **Stackful Coroutines (Fibers / Green Threads)**: Each fiber possesses its own dynamically allocated stack; can yield from arbitrarily deep nested function calls.
- **Stackless Coroutines (Python `asyncio`, JavaScript, Rust)**: The compiler transforms the coroutine function into a **finite state machine (FSM)**.

#### Python Coroutine Desugaring
When Python compiles an `async def` function:
```python
async def fetch_data(url):
    req = build_request(url)
    res = await socket_read(req)
    return parse(res)
```
The compiler desugars the function into a generator-like state machine object implementing the `__await__()` protocol:
1. Local variables (`req`, `res`) are stored as attributes on the coroutine frame object on the heap.
2. The `await` expression is compiled into a `YIELD_VALUE` bytecode instruction.
3. The event loop calls `coro.send(val)`. Execution advances until the `await`, which returns control back to the event loop with a future/socket token.
4. When the OS signals that the socket is readable, the event loop wakes the coroutine by calling `coro.send(data)` or `coro.throw(exc)`.

---

### 2.3 The Async "Await-Point" Race Hazard

A ubiquitous myth among developers is:
> *"Because my event loop is single-threaded, my asynchronous code is immune to concurrency hazards and race conditions."*

**This belief is mathematically false.**

While single-threaded event loops eliminate *hardware data races* (two threads writing memory simultaneously), they **do not eliminate semantic race conditions**.

**The Await-Point Invariant**:
Every `await` statement is an explicit **yield point** where the current task yields the CPU to the event loop. The event loop can execute any other pending task before resuming the current task.

#### Concrete Bug Example: Bank Account Withdrawal
```python
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    async def withdraw(self, amount):
        # Step 1: Check balance
        if self.balance >= amount:
            # Yield point! Simulated network database verification
            await asyncio.sleep(0.01)
            # Step 2: Act (Deduct)
            self.balance -= amount
            return True
        return False
```
If two concurrent tasks call `account.withdraw(80)` on an account with `balance = 100`:
1. Task 1 checks `self.balance >= 80` (100 >= 80 $\to$ True).
2. Task 1 encounters `await asyncio.sleep(0.01)` and suspends.
3. Event loop switches to Task 2.
4. Task 2 checks `self.balance >= 80` (100 >= 80 $\to$ True).
5. Task 2 encounters `await asyncio.sleep(0.01)` and suspends.
6. Timer expires; Task 1 resumes: `self.balance = 100 - 80 = 20`.
7. Timer expires; Task 2 resumes: `self.balance = 20 - 80 = -60`!

**Invariant Violation**: The balance drops below zero despite the check.
*Rule*: Critical sections across `await` points must be protected by asynchronous locks (`asyncio.Lock()`) or implemented as atomic state transitions.

---

## 3. Structured Concurrency

Coined by Martin Sústrik (2016) and popularized by Nathaniel J. Smith (Trio, 2018) and Roman Elizarov (Kotlin Coroutines), **Structured Concurrency** applies the principles of structured programming (Dijkstra's *Go To Statement Considered Harmful*) to concurrent task lifecycles.

### 3.1 The Flaw of Unstructured Concurrency
In unstructured concurrency (`go func()`, `threading.Thread.start()`, `asyncio.create_task()`), tasks are launched into the background with arbitrary, unbounded lifetimes:
- Background tasks can easily outlive the scope that created them ("orphaned tasks").
- Leaked resources (unclosed sockets, database connections, memory).
- Unhandled exceptions disappear into background logs or crash the process unpredictably.
- Cancellation does not propagate reliably down call trees.

### 3.2 The Structured Concurrency Axiom
> **Axiom**: A concurrent control flow block (nursery / task group) cannot exit until **all** child tasks spawned within that block have terminated (either by completion, failure, or cancellation).

```
          Structured Scope (TaskGroup)
          +---------------------------------------------+
Entry --> |  +--- Child Task 1 (Networking) --------+   |
          |  +--- Child Task 2 (Database) ----------+   |
          |  +--- Child Task 3 (Compute) -----------+   |
          +---------------------------------------------+
                               |
                   Wait for ALL children to finish
                               |
Exit <-------------------------+
```

### 3.3 Python 3.11+ `asyncio.TaskGroup`
Python 3.11 integrated structured concurrency natively:

```python
async def fetch_all(urls):
    results = []
    # Scope guarantees complete cleanup
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_url(url)) for url in urls]
    
    # Guaranteed: When reaching this line, all tasks are finished.
    return [task.result() for task in tasks]
```

#### Exception Propagation via `ExceptionGroup`
If one child task crashes:
1. The `TaskGroup` immediately issues cancellation requests (`task.cancel()`) to all sibling tasks within the group.
2. The `TaskGroup` awaits the completion/cancellation of all sibling tasks.
3. If multiple tasks raise exceptions, they are packed into an **`ExceptionGroup`** (PEP 654), which can be handled with the new `except*` syntax:

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(task_a())
        tg.create_task(task_b())
except* ValueError as eg:
    handle_value_errors(eg.exceptions)
except* OSError as eg:
    handle_io_errors(eg.exceptions)
```

---

## 4. CPython Runtime Internals & The GIL

CPython (the reference C implementation of Python) employs runtime architecture decisions with profound concurrency consequences.

### 4.1 The Global Interpreter Lock (GIL)

#### Why Does the GIL Exist?
CPython's internal memory management is fundamentally **not thread-safe**:
1. **Reference Counting**: Every Python object header (`PyObject_HEAD`) begins with an integer reference counter:
   ```c
   struct _object {
       _PyObject_HEAD_EXTRA
       Py_ssize_t ob_refcnt;
       struct _typeobject *ob_type;
   };
   ```
   Every variable assignment, argument pass, or list append executes `Py_INCREF()` and `Py_DECREF()`. If multiple OS threads modified `ob_refcnt` concurrently without locking, memory leaks and use-after-free crashes would be pervasive.
2. **C Extension Ecosystem**: Thousands of legacy C extensions (NumPy, SciPy, etc.) were written assuming single-threaded CPython internals without manual locking.

#### GIL Mechanics: `gil_drop_request` and Switch Intervals
The GIL is an OS-level mutex (`pthread_mutex_t` or semaphore) that an OS thread must hold to execute Python bytecode.
- **Switch Interval**: By default, `sys.getswitchinterval()` is 5 milliseconds.
- When an execution thread runs for 5ms, the runtime sets the atomic flag:
  $$\text{gil\_drop\_request} = 1$$
- Upon encountering the next bytecode evaluation checkpoint (`eval_frame`), the executing thread releases the GIL and yields the CPU via a condition variable.
- Competing threads wait on the GIL mutex.

#### The Convoy Effect & Multicore CPU Penalty
On multi-core systems, CPU-bound Python threads suffer severe performance degradation compared to single-core execution:
- Core 0 runs Thread 1 holding GIL.
- Core 1 wakes Thread 2 and attempts to acquire GIL $\to$ blocks.
- Core 0 reaches switch interval, drops GIL, and signals condition variable.
- Core 0 immediately attempts to reacquire the GIL. Because Core 0's cache line is hot, Core 0 frequently wins the reacquisition race before Core 1 can wake up, causing massive OS context switch thrashing without real parallelism.

---

### 4.2 Cache-Line Contention on `PyObject_HEAD`
Even if reference counting instructions were converted to atomic instructions (`atomic_fetch_add` / `LOCK XADD`):
- Incrementing a refcount requires an atomic write to the object's cache line.
- When multiple cores read a shared object (e.g. `None`, `True`, global functions, built-in types), every read forces a MESI `BusRdX` cache line invalidation across all CPU cores!
- **Result**: Atomic reference counting degrades multicore performance by $30\%\text{--}60\%$ compared to the GIL.

---

### 4.3 Free-Threading in Python: PEP 703 (Python 3.13+)

PEP 703 ("Making the Global Interpreter Lock Optional in CPython") by Sam Gross introduces a free-threaded CPython build (`python3.13t`) that removes the GIL while preserving multicore scalability through four architectural innovations:

#### 1. Biased Reference Counting (BRC)
Objects are divided into two categories:
- **Thread-Local Objects**: Objects accessed exclusively by the thread that created them. Uses non-atomic local increments (extremely fast).
- **Shared Objects**: When an object is shared across threads, reference counts are split into local and shared counters, avoiding atomic bus locks for local operations.

#### 2. Immortal Objects (PEP 683)
Objects that live for the duration of the process (e.g. `None`, `True`, `False`, interned strings, built-in types `int`, `str`, `dict`) have their reference count initialized to a special bit pattern:
$$\text{ob\_refcnt} = 2^{30} - 1 \quad (\approx 10^9)$$
`Py_INCREF` and `Py_DECREF` check if an object is immortal using a single bitwise branch:
```c
static inline void _Py_INCREF(PyObject *op) {
    if (_Py_IsImmortal(op)) return;
    op->ob_refcnt++;
}
```
Shared immutable objects never modify their cache lines, completely eliminating cache-line bouncing across multi-core systems!

#### 3. Deferred Reference Counting
Top-level stack frame references and module variables skip reference counting altogether, relying on the garbage collector's cycle detection sweeps to reclaim dead references.

#### 4. Thread-Safe Memory Allocation with `mimalloc`
CPython's classical allocator (`PyMalloc`) is replaced with Microsoft's **`mimalloc`**, which provides thread-local memory pools, thread-local free lists, and lock-free block recycling, eliminating memory allocation contention.

---

## 5. Comparative Concurrency Matrix: Threading vs Multiprocessing vs Asyncio

| Dimension | `threading` (POSIX / Win32) | `multiprocessing` (Fork / Spawn) | `asyncio` (Event Loop Coroutines) |
|---|---|---|---|
| **Concurrency Model** | Preemptive OS threads | Preemptive separate OS processes | Cooperative user-space event loop |
| **GIL Bound?** | **Yes** (Only 1 thread runs Python code at a time) | **No** (Each process has its own GIL and memory space) | **Yes** (Single thread, single GIL) |
| **Ideal Workload** | I/O-bound (network, disk) or C-extension parallel (NumPy) | CPU-bound computation (data processing, ML training) | High-concurrency I/O-bound ($10^4\text{--}10^6$ sockets, websockets) |
| **Memory Overhead** | Low ($\sim 8\text{ MB}$ stack/thread) | High (Separate address space, COW memory pages) | Minimal ($\sim 1\text{--}2\text{ KB}$ per coroutine frame) |
| **Communication / IPC** | Shared memory (requires locks/queues) | Inter-Process Communication (Pipes, Sockets, Pickling overhead) | Single memory space (direct object references) |
| **Deadlock Risk** | High (Mutex deadlocks, lock ordering) | Low (Isolated memory; IPC deadlocks possible) | Medium (Await-point race conditions) |
