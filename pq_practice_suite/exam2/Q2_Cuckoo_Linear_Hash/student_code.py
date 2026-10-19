"""
student_code.py - Problem 2: Longest Divisible Subarray
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 2)

FastHashTable is pre-implemented in common.py.
"""

from typing import List, Tuple
from common import FastHashTable


def longest_divisible_subarray(arr: List[int], k: int) -> Tuple[int, int, int]:
    """
    Finds the length and 0-based boundary indices of the longest contiguous subarray
    whose sum is divisible by k.

    Parameters:
      arr: list of integers (positive, negative, zero)
      k: modulus (k >= 1)

    Returns:
      (max_length, start_index, end_index)
      If no valid non-empty subarray exists, return (0, -1, -1).
    """
    # TODO: Implement in O(N) expected time using FastHashTable
    pass
