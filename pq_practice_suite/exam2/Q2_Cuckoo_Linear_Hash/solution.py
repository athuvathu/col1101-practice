"""
solution.py - Master Reference Solution for Exam 2 Problem 2
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 2)
"""

from typing import List, Tuple
from common import FastHashTable


def longest_divisible_subarray(arr: List[int], k: int) -> Tuple[int, int, int]:
    """
    Finds (max_length, start_index, end_index) where sum(arr[start..end]) % k == 0.
    Complexity: O(N) expected time, O(min(N, K)) space using FastHashTable.
    """
    if not arr or k <= 0:
        return (0, -1, -1)

    table = FastHashTable()
    # Base case: prefix sum before any elements (at index -1) has remainder 0
    table.put(0, -1)

    prefix_sum = 0
    max_len = 0
    best_start = -1
    best_end = -1

    for i, val in enumerate(arr):
        prefix_sum += val
        rem = (prefix_sum % k + k) % k

        earliest_idx = table.get(rem, default=None)
        if earliest_idx is not None:
            length = i - earliest_idx
            if length > max_len:
                max_len = length
                best_start = earliest_idx + 1
                best_end = i
        else:
            table.put(rem, i)

    if max_len == 0:
        return (0, -1, -1)

    return (max_len, best_start, best_end)
