# Problem 2: Dual-Heap Running Quantile Monitor

**Course:** COL1101 (Programming with Data Structures)  
**Exam:** Programming Quiz 2 (Exam 1 - Problem 2)  
**Marks:** 60 points  
**Target Time:** 55 minutes  

---

## 1. Problem Statement

High-frequency telemetry feeds track sensor latencies. Systems engineers must report real-time quantile metrics (e.g. median $p = 0.50$, or 95th-percentile SLA violations $p = 0.95$) as new measurements arrive dynamically.

Sorting the readings upon every query requires $O(N \log N)$ time, which is unacceptable for streaming workloads.

Your task is to implement `RunningQuantile`, which maintains dynamic streaming order statistics using a **dual-heap balancing architecture**.

You are provided with pre-implemented `MinHeap` and `MaxHeap` classes in `common.py` supporting $O(\log N)$ `push` and `pop`, and $O(1)$ `peek` and `len()`.

---

## 2. Quantile Definition

For a stream of $N$ values sorted in non-decreasing order $v_1 \le v_2 \le \dots \le v_N$, the $p$-th quantile ($0 < p < 1$) is defined as the element at 1-based index:
$$K = \lceil p \times N \rceil$$
For example:
- If $p = 0.5$ and $N = 5$: $K = \lceil 2.5 \rceil = 3$ (the 3rd smallest element, exact median).
- If $p = 0.5$ and $N = 4$: $K = \lceil 2.0 \rceil = 2$ (lower median).
- If $p = 0.8$ and $N = 10$: $K = \lceil 8.0 \rceil = 8$ (8th smallest element).

---

## 3. Required Methods

Implement the class `RunningQuantile` in `student_code.py`:

### `1. __init__(self, p: float)`
- Initializes the monitor with quantile parameter $p \in (0, 1)$.
- Must instantiate lower heap (`MaxHeap`) and upper heap (`MinHeap`).

### `2. add(self, val: float) -> None`
- Inserts `val` into the streaming monitor.
- Rebalances the heaps such that the lower heap holds exactly the smallest $K = \lceil p \times N \rceil$ elements, and the upper heap holds the remaining $N - K$ elements.
- **Complexity:** $O(\log N)$ worst-case time.

### `3. get_quantile(self) -> Optional[float]`
- Returns the current $p$-th quantile value.
- If no elements have been added ($N = 0$), returns `None`.
- **Complexity:** $O(1)$ worst-case time.

### `4. __len__(self) -> int`
- Returns total number of active elements $N$.

---

## 4. Example Trace

```python
rq = RunningQuantile(p=0.5) # Median monitor

rq.add(10)
assert rq.get_quantile() == 10 # N=1, K=ceil(0.5)=1

rq.add(20)
assert rq.get_quantile() == 10 # N=2, K=ceil(1.0)=1 -> [10]

rq.add(5)
# Sorted: [5, 10, 20], N=3, K=ceil(1.5)=2 -> 10
assert rq.get_quantile() == 10

rq.add(1)
# Sorted: [1, 5, 10, 20], N=4, K=ceil(2.0)=2 -> 5
assert rq.get_quantile() == 5

rq.add(15)
# Sorted: [1, 5, 10, 15, 20], N=5, K=ceil(2.5)=3 -> 10
assert rq.get_quantile() == 10
```
