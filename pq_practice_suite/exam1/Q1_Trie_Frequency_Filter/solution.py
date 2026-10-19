"""
solution.py - Master Reference Solution for Exam 1 Problem 1
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 1)
"""

from typing import List
from common import BinaryTrie


def max_xor_in_window(stream: List[int], window_size: int) -> int:
    """
    Computes maximum XOR of any pair within a sliding window of size <= window_size.
    Complexity: O(N * 32) time, O(W * 32) space.
    """
    n = len(stream)
    if n < 2 or window_size < 2:
        return 0

    trie = BinaryTrie(bit_len=32)
    max_xor = 0

    for i in range(n):
        val = stream[i]
        
        # Query max XOR against currently active window elements (indices in [i - window_size + 1, i - 1])
        if trie.size() > 0:
            match_val, xor_val = trie.find_max_xor(val)
            if xor_val > max_xor:
                max_xor = xor_val

        # Add current value to trie
        trie.insert(val)

        # Evict element that falls out of the sliding window
        if i >= window_size - 1:
            outdated_idx = i - window_size + 1
            trie.remove(stream[outdated_idx])

    return max_xor
