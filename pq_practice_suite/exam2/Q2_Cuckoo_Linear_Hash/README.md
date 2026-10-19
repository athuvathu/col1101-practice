# Problem 2: Longest Divisible Subarray (Hash Table Prefix Matching)

**Course:** COL1101 (Programming with Data Structures)  
**Exam:** Programming Quiz 2 (Exam 2 - Problem 2)  
**Marks:** 60 points  
**Target Time:** 55 minutes  

---

## 1. Problem Statement

A high-speed quantum network receives a telemetry buffer of phase measurements $A = [a_0, a_1, \dots, a_{N-1}]$ (positive, negative, or zero integers). Phase interference collapses whenever the sum of phase angles across a contiguous subsegment is an exact multiple of the quantum resonance modulus $K$.

To identify the largest resonance window, you must find the **longest contiguous subarray** whose elements sum to a multiple of $K$:
$$\left( \sum_{i = l}^{r} a_i \right) \equiv 0 \pmod K$$

You are provided with a pre-implemented `FastHashTable` class in `common.py` that supports:
- `put(key, val)`: $O(1)$ expected insertion
- `get(key, default=None)`: $O(1)$ expected lookup
- `contains(key) -> bool`: $O(1)$ expected membership check

---

## 2. Function Contract

Implement `longest_divisible_subarray(arr: List[int], k: int)` in `student_code.py`:

```python
def longest_divisible_subarray(arr: List[int], k: int) -> Tuple[int, int, int]:
    """
    Finds the length and 0-based boundary indices of the longest contiguous subarray
    whose sum is divisible by k.
    
    Returns:
      (max_length, start_index, end_index)
      
    Tie-breaking:
      If multiple subarrays achieve the same maximum length, return the one
      with the smallest start_index.
      If no valid non-empty subarray exists, return (0, -1, -1).
      
    Complexity Requirement:
      Time: O(N) expected time using FastHashTable.
      Space: O(min(N, K)) auxiliary space.
    """
```

---

## 3. Mathematical Invariant

Let $P[i] = \sum_{j=0}^{i-1} a_j$ be the prefix sum (with $P[0] = 0$).  
The subarray sum from index $l$ to $r$ (inclusive) is:
$$\sum_{j=l}^{r} a_j = P[r+1] - P[l]$$

This sum is divisible by $K$ if and only if:
$$P[r+1] \equiv P[l] \pmod K$$

By mapping each prefix sum remainder $P[i] \bmod K$ to its **earliest occurrence index** in `FastHashTable`, any subsequent index with the same remainder immediately identifies a valid divisible subarray!

---

## 4. Example Trace

```python
arr = [2, 7, 6, 1, 4, 5]
k = 3

# Prefix sums mod 3:
# Index -1 (empty): sum 0 % 3 = 0
# Index 0 (2): sum 2 % 3 = 2
# Index 1 (7): sum 9 % 3 = 0  -> matches remainder 0 at index -1 -> len 2 (arr[0..1] = [2, 7], sum=9)
# Index 2 (6): sum 15 % 3 = 0 -> matches remainder 0 at index -1 -> len 3 (arr[0..2] = [2, 7, 6], sum=15)
# Index 3 (1): sum 16 % 3 = 1 -> new remainder 1
# Index 4 (4): sum 20 % 3 = 2 -> matches remainder 2 at index 0  -> len 4 (arr[1..4] = [7, 6, 1, 4], sum=18)
# Index 5 (5): sum 25 % 3 = 1 -> matches remainder 1 at index 3  -> len 2 (arr[4..5] = [4, 5], sum=9)

# Maximum length is 4: arr[1..4] = [7, 6, 1, 4] with sum 18 (divisible by 3)
assert longest_divisible_subarray(arr, 3) == (4, 1, 4)
```

---

## 5. Constraints

- $0 \le N \le 100,000$
- $-10^9 \le arr[i] \le 10^9$
- $1 \le K \le 10^9$
