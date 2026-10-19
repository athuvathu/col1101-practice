# Problem 1: Sliding Window Maximum XOR (Binary Trie)

**Course:** COL1101 (Programming with Data Structures)  
**Exam:** Programming Quiz 2 (Exam 1 - Problem 1)  
**Marks:** 40 points  
**Target Time:** 35 minutes  

---

## 1. Problem Statement

Deep-space probes transmit encrypted 32-bit integer packets in a continuous telemetry stream. Interference causes packet phase shifts, where the interference energy between any two packets $A$ and $B$ is measured by their bitwise XOR value $A \oplus B$.

To monitor peak packet dissonance, your task is to compute the **maximum XOR value** between any two distinct packets that arrive within a sliding window of length at most $W$.

You are provided with a pre-implemented `BinaryTrie` class in `common.py` that supports:
- `insert(num: int)`: Inserts an integer into the trie in $O(32)$ time.
- `remove(num: int)`: Deletes an integer from the trie in $O(32)$ time.
- `find_max_xor(num: int) -> Tuple[Optional[int], int]`: Finds the active number in the trie maximizing $(num \oplus match)$ in $O(32)$ time.

---

## 2. Function Contract

Implement the following function in `student_code.py`:

```python
def max_xor_in_window(stream: List[int], window_size: int) -> int:
    """
    Computes the maximum XOR value between any two packets that appear
    within the same sliding window of length at most window_size.
    
    If len(stream) < 2 or window_size < 2, return 0.
    
    Complexity Requirement:
      Time: O(N * 32) where N = len(stream)
      Space: O(W * 32) auxiliary space inside the trie
    """
```

---

## 3. Example

```python
stream = [3, 10, 5, 25, 2, 8]
window_size = 3

# Window [3, 10]: 3 ^ 10 = 9
# Window [3, 10, 5]: max pair (10, 5) -> 10 ^ 5 = 15
# Window [10, 5, 25]: max pair (5, 25) -> 5 ^ 25 = 28
# Window [5, 25, 2]: max pair (25, 2) -> 25 ^ 2 = 27
# Window [25, 2, 8]: max pair (25, 2) -> 25 ^ 2 = 27, (25, 8) -> 17
# Overall Maximum XOR = 28

assert max_xor_in_window(stream, 3) == 28
```

---

## 4. Constraints

- $0 \le N \le 100,000$
- $0 \le \text{stream}[i] < 2^{31}$
- $1 \le W \le N$
