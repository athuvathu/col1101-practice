# Module 03: Synchronization Primitives & Classical Concurrent Problems

---

## 1. Semaphores: Mathematical Formalization & Invariants

Invented by Edsger W. Dijkstra (1965), a **semaphore** is an integer synchronization variable $S$ accessed exclusively through two atomic operations: $P()$ (from Dutch *proberen*, "to test", often called `wait`) and $V()$ (from Dutch *verhogen*, "to increment", often called `signal` or `post`).

### 1.1 The Fundamental Semaphore Invariant
Let $S_0 \in \mathbb{N}_0$ be the initial non-negative capacity of the semaphore.
For any execution time $t \ge 0$:
- $\#V_{\text{comp}}(t)$: The cumulative number of completed $V()$ operations up to time $t$.
- $\#P_{\text{comp}}(t)$: The cumulative number of completed $P()$ operations up to time $t$.
- $\#P_{\text{req}}(t)$: The cumulative number of initiated $P()$ requests up to time $t$.

**Invariant 1 (Non-Negative Semaphore Invariant)**:
$$\forall t \ge 0, \quad S(t) = S_0 + \#V_{\text{comp}}(t) - \#P_{\text{comp}}(t) \ge 0$$

**Corollary (Conservation of Permits)**:
$$\#P_{\text{comp}}(t) \le S_0 + \#V_{\text{comp}}(t)$$
The number of threads that can pass through the semaphore is strictly bounded by the initial count plus the number of released permits.

### 1.2 Binary vs Counting Semaphores
- **Counting Semaphore**: $S_0 \ge 0$, unbounded integer domain. Used for resource pool allocation (e.g. database connection pools, memory blocks).
- **Binary Semaphore**: $S_0 \in \{0, 1\}$ and $S(t) \in \{0, 1\}$ for all $t$.
  - *Distinction from Mutex*: A **Mutex** has ownership semantics: only the thread that acquired the mutex can release it, and mutexes support priority inheritance. A **Binary Semaphore** has no ownership: any thread (or an ISR / interrupt handler) can execute $V()$ to unblock another thread waiting in $P()$.

### 1.3 Non-Negative vs Negative Wait-Queue Semantics
There are two classical operational formulations:

#### Model A: Non-Negative Semaphore (Dijkstra)
The integer value $S$ never drops below 0:
```c
void P() {
    acquire_internal_lock();
    while (S == 0) {
        enqueue_thread(wait_queue, current_thread);
        release_internal_lock_and_sleep();
        acquire_internal_lock();
    }
    S--;
    release_internal_lock();
}

void V() {
    acquire_internal_lock();
    S++;
    if (!empty(wait_queue)) {
        thread = dequeue_thread(wait_queue);
        wake(thread);
    }
    release_internal_lock();
}
```

#### Model B: Negative Semaphore (POSIX / Linux `sem_t`)
The integer value $S$ can become negative. If $S < 0$, its absolute value $|S|$ represents the exact number of blocked threads currently waiting in the queue:
$$\forall t, \quad S(t) < 0 \implies |\text{Queue}(t)| = -S(t)$$

```c
void P() {
    acquire_internal_lock();
    S--;
    if (S < 0) {
        enqueue_thread(wait_queue, current_thread);
        release_internal_lock_and_sleep();
    } else {
        release_internal_lock();
    }
}

void V() {
    acquire_internal_lock();
    S++;
    if (S <= 0) {
        thread = dequeue_thread(wait_queue);
        wake(thread);
    }
    release_internal_lock();
}
```

---

## 2. Monitors & Condition Variables

Introduced by Per Brinch Hansen (1973) and C.A.R. Hoare (1974), a **Monitor** is an abstract data type encapsulating shared state, an entry mutex, and one or more **Condition Variables (CV)**.

A Condition Variable $CV$ is an explicit synchronization queue supporting three operations:
- `cv.wait(lock)`: Atomically releases `lock` and suspends the calling thread on $CV$'s wait set. Upon awakening, reacquires `lock` before returning.
- `cv.signal()` (or `notify()`): Wakes at least one thread waiting on $CV$. If none are waiting, the signal is a no-op (unlike semaphores, CVs have no memory/counter).
- `cv.broadcast()` (or `notify_all()`): Wakes all threads currently waiting on $CV$.

### 2.1 Signaling Semantics: Hoare vs Mesa vs Brinch Hansen

| Feature | Hoare ("Signal and Wait") | Mesa ("Signal and Continue") | Brinch Hansen ("Signal and Exit") |
|---|---|---|---|
| **Signaler behavior** | Signaler immediately yields mutex and blocks on an urgent queue; woken thread immediately acquires mutex and runs. | Signaler continues executing inside monitor. Woken thread moves to the mutex Ready Queue. | Signaling thread must exit the monitor immediately as the last statement. |
| **Predicate guarantee** | **Guaranteed true** when woken thread resumes. | **NOT guaranteed**. Predicate may be invalidated before woken thread acquires mutex. | **Guaranteed true** (direct handoff upon exit). |
| **Waiting pattern** | `if (!condition) cv.wait(lock);` | `while (!condition) cv.wait(lock);` | `if (!condition) cv.wait(lock);` |
| **Real-world use** | Theoretical / verification proofs. | **All modern OSs and runtimes** (POSIX pthreads, Java, C++11, C#, Python). | Concurrent Pascal. |

```
Mesa Signaling Execution Timeline:
Thread A (Signaler):     [holds lock] ------> cv.signal() ------> [continues...] ------> unlock()
                                                 |                                          |
Thread B (Woken):        [asleep in wait()] ----+---> [moves to ready queue] ------------> [competes for lock] -> resumes!
                                                                                           ^
Thread C (Interloper):   ---------------------------------------------------------[steals lock first!]
```

### 2.2 The Mesa Predicate Re-Evaluation Mandate: Why `while` is Required

In Mesa-style monitors, wrapping `cv.wait()` in an `if` statement is a catastrophic bug. The loop `while (!predicate) cv.wait(lock)` is mathematically mandatory due to three orthogonal phenomena:

#### 1. Preemption & Interleaving (Third-Party Lock Stealing)
When Thread A signals $CV$, Thread B is moved from the CV wait set to the mutex ready set.
Thread A retains the lock until it unlocks or exits.
Before Thread B is scheduled and acquires the mutex, an interloper Thread C may acquire the mutex, observe that `predicate` is true, consume the resource, render `predicate` false, and release the mutex.
When Thread B finally acquires the mutex, the predicate is **false**. If Thread B was woken with `if`, it continues execution with a broken invariant!

#### 2. Spurious Wakeups (Kernel & Hardware Level)
Under POSIX (`pthread_cond_wait`), Linux, and Windows, a thread waiting on a condition variable may awaken **without any call to `signal()` or `broadcast()`**.
- *Causes*:
  - Unix OS signals (`EINTR` interruption in kernel space).
  - Multiprocessor race resolutions in the kernel scheduler.
  - Futex optimizations where kernel futex hashes collide across memory pages.

#### 3. Broadcast Fanout (`notify_all` / `broadcast`)
If 5 threads are waiting for a resource and 1 resource unit becomes available, a `broadcast()` awakens all 5 threads.
The first thread to obtain the lock consumes the single resource.
The remaining 4 threads acquire the lock subsequently; if they do not loop, they execute on an empty resource pool (underflow).

### 2.3 The Lost Wakeup Problem
A **Lost Wakeup** occurs when a signal is emitted, but no thread observes it, resulting in indefinite hang/deadlock.

**Theorem (Deadlock via Unprotected Wait)**:
If `cv.wait(mutex)` does not release the mutex and sleep **atomically**, or if the condition test is evaluated outside the mutex, a deadlock can occur.

```
Thread 1 (Consumer):                 Thread 2 (Producer):
--------------------                 --------------------
1. test (count == 0) -> true
                                     2. produce item (count = 1)
                                     3. cv.signal()  <-- SIGNAL LOST! (no one waiting)
4. cv.wait(mutex) -> SLEEPS FOREVER!
```
*Atomic release and wait* guarantees that Thread 1 cannot be preempted between deciding to wait and entering the wait queue.

---

## 3. Classical Concurrent Problems

### 3.1 The Bounded Buffer Problem (Producer-Consumer)
A fixed-capacity buffer with $N$ slots shared between $M$ producers and $K$ consumers.

**Safety Invariants**:
1. $0 \le \text{count}(t) \le N$
2. Items consumed match items produced in strict FIFO sequence.
3. No buffer overflow (overwriting unconsumed data).
4. No buffer underflow (reading uninitialized/consumed data).

```cpp
template <typename T, size_t CAPACITY>
class BoundedBuffer {
private:
    T buffer[CAPACITY];
    size_t head = 0;
    size_t tail = 0;
    size_t count = 0;
    std::mutex mtx;
    std::condition_variable not_full;
    std::condition_variable not_empty;

public:
    void put(T item) {
        std::unique_lock<std::mutex> lock(mtx);
        // Mesa wait loop: guards against spurious wakeups and interlopers
        while (count == CAPACITY) {
            not_full.wait(lock);
        }
        buffer[tail] = item;
        tail = (tail + 1) % CAPACITY;
        count++;
        // Invariant: count >= 1, wake at least one waiting consumer
        not_empty.notify_one();
    }

    T get() {
        std::unique_lock<std::mutex> lock(mtx);
        // Mesa wait loop
        while (count == 0) {
            not_empty.wait(lock);
        }
        T item = buffer[head];
        head = (head + 1) % CAPACITY;
        count--;
        // Invariant: count <= CAPACITY - 1, wake at least one waiting producer
        not_full.notify_one();
        return item;
    }
};
```

---

### 3.2 The Readers-Writers Problem

Multiple threads access a shared resource.
- Multiple Readers may read concurrently:
  $$\forall t, \quad (\#W(t) == 0) \implies (\#R(t) \ge 0)$$
- Writers require exclusive access:
  $$\forall t, \quad (\#W(t) \le 1) \land (\#W(t) == 1 \implies \#R(t) == 0)$$

#### Variant 1: Reader-Preference (First Readers-Writers)
No reader is kept waiting unless a writer has already acquired the shared resource.
- *Hazard*: **Writer Starvation**. If readers arrive continuously, the read count never drops to 0, and waiting writers starve indefinitely.

#### Variant 2: Writer-Preference (Second Readers-Writers)
Once a writer requests access, no new reader is permitted to start reading.
- *Hazard*: **Reader Starvation**. Continuous stream of incoming writers prevents readers from ever acquiring the lock.

#### Variant 3: Starvation-Free / Fair (Third Readers-Writers)
Neither readers nor writers starve; requests are processed in approximate arrival order using a FIFO turnstile queue.

```c
// Fair Readers-Writers with Turnstile Semaphore
sem_t turnstile; // initialized to 1
sem_t write_mutex; // initialized to 1
pthread_mutex_t r_mutex; // initialized to 1
int read_count = 0;

void reader() {
    sem_wait(&turnstile);       // Pass through turnstile
    pthread_mutex_lock(&r_mutex);
    read_count++;
    if (read_count == 1) {
        sem_wait(&write_mutex); // First reader locks out writers
    }
    pthread_mutex_unlock(&r_mutex);
    sem_post(&turnstile);       // Release turnstile for next arrival

    // Reading critical section
    do_read();

    pthread_mutex_lock(&r_mutex);
    read_count--;
    if (read_count == 0) {
        sem_post(&write_mutex); // Last reader unlocks writers
    }
    pthread_mutex_unlock(&r_mutex);
}

void writer() {
    sem_wait(&turnstile);       // Block incoming readers & writers
    sem_wait(&write_mutex);     // Wait until active readers finish
    sem_post(&turnstile);

    // Writing critical section
    do_write();

    sem_post(&write_mutex);
}
```

---

### 3.3 The Dining Philosophers Problem

$N$ philosophers sit around a circular table. Between each pair of adjacent philosophers is a single fork (total $N$ forks).
Philosopher $i$ requires both fork $i$ (left) and fork $(i+1)\%N$ (right) to eat.

```
           Philosopher 0
         /               \
     Fork 0             Fork 1
       /                   \
Philosopher 4         Philosopher 1
      |                     |
    Fork 4               Fork 2
       \                   /
  Philosopher 3 ----- Fork 3 ----- Philosopher 2
```

#### The Naive Deadlock
If every philosopher sits down and concurrently executes:
```c
lock(left_fork);
lock(right_fork);
```
Every philosopher acquires their left fork simultaneously.
Every philosopher now attempts to acquire their right fork, which is held by their neighbor.
**Result**: Circular dependency cycle $P_0 \to F_1 \to P_1 \to F_2 \to \dots \to P_{N-1} \to F_0 \to P_0$. System deadlocks permanently.

#### Havender's Resource Hierarchy Solution
Assign a unique global identifier $k \in \{0, \dots, N-1\}$ to each fork.
Define strict ordering:
$$F_0 < F_1 < F_2 < \dots < F_{N-1}$$

**Rule**: Every philosopher must acquire their two required forks in **strictly increasing order of their index**:
$$\text{first} = \min(\text{left}, \text{right}), \quad \text{second} = \max(\text{left}, \text{right})$$

- For philosophers $0, 1, \dots, N-2$:
  $\text{left} = i$, $\text{right} = i+1$.
  Since $i < i+1$, they pick $\text{left}$ first, then $\text{right}$.
- For philosopher $N-1$:
  $\text{left} = N-1$, $\text{right} = 0$.
  $\min(N-1, 0) = 0$. Philosopher $N-1$ must pick fork $0$ (right) first, then fork $N-1$ (left)!

**Proof of Deadlock-Freedom**:
Philosopher $N-1$ and Philosopher $0$ compete for Fork $0$ as their *first* acquisition.
Only one will obtain Fork $0$.
The loser does not hold any fork.
Hence, at most $N-1$ forks are held by $N-1$ philosophers, leaving at least one philosopher able to acquire their second fork and eat.
By induction on the strict partial order of resources, no circular wait can form.
