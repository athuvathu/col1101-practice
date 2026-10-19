"""
student_code.py - Problem 1: Sliding Window Maximum XOR
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 1)

BinaryTrie is pre-implemented in common.py. You may also inspect its methods below.
"""

from typing import List
from common import BinaryTrie


def max_xor_in_window(stream: List[int], window_size: int) -> int:
    """
    Computes the maximum XOR value between any two packets that appear
    within the same sliding window of length at most window_size.

    Parameters:
      stream: list of non-negative integers
      window_size: maximum span between indices (|i - j| < window_size)

    Returns:
      Integer representing maximum XOR value (or 0 if len(stream) < 2 or window_size < 2).
    """
    # TODO: Implement using the pre-implemented BinaryTrie in O(N * 32) time.
    pass
