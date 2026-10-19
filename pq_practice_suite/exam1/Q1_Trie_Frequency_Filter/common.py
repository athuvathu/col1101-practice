"""
common.py - Pre-implemented BinaryTrie for Exam 1 Problem 1
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 1)

This class is PRE-IMPLEMENTED and provided to you.
Use its methods in your solution. Do not modify this file.
"""

from typing import Tuple, Optional


class BinaryTrieNode:
    def __init__(self):
        self.children = [None, None]  # index 0: bit 0, index 1: bit 1
        self.count = 0                # count of active integers passing through node


class BinaryTrie:
    """
    Pre-implemented 32-bit Binary Trie for Fast XOR Queries and Dynamic Deletions.
    """
    def __init__(self, bit_len: int = 32):
        self.root = BinaryTrieNode()
        self.bit_len = bit_len

    def insert(self, num: int) -> None:
        """Inserts integer into trie in O(bit_len) time."""
        curr = self.root
        curr.count += 1
        for i in range(self.bit_len - 1, -1, -1):
            bit = (num >> i) & 1
            if curr.children[bit] is None:
                curr.children[bit] = BinaryTrieNode()
            curr = curr.children[bit]
            curr.count += 1

    def remove(self, num: int) -> bool:
        """Removes one instance of num from trie in O(bit_len). Returns True if removed."""
        if not self.contains(num):
            return False
        curr = self.root
        curr.count -= 1
        for i in range(self.bit_len - 1, -1, -1):
            bit = (num >> i) & 1
            child = curr.children[bit]
            child.count -= 1
            if child.count == 0:
                curr.children[bit] = None
                break
            curr = child
        return True

    def contains(self, num: int) -> bool:
        """Checks if num is currently active in trie in O(bit_len)."""
        curr = self.root
        for i in range(self.bit_len - 1, -1, -1):
            bit = (num >> i) & 1
            if curr.children[bit] is None or curr.children[bit].count == 0:
                return False
            curr = curr.children[bit]
        return curr.count > 0

    def find_max_xor(self, num: int) -> Tuple[Optional[int], int]:
        """
        Finds the number in the trie that maximizes (num ^ match).
        Returns: (matching_number, max_xor_value)
        If trie is empty, returns (None, 0).
        Time complexity: O(bit_len).
        """
        if self.root.count == 0:
            return (None, 0)
        curr = self.root
        match_val = 0
        for i in range(self.bit_len - 1, -1, -1):
            bit = (num >> i) & 1
            wanted = 1 - bit
            if curr.children[wanted] is not None and curr.children[wanted].count > 0:
                match_val |= (wanted << i)
                curr = curr.children[wanted]
            elif curr.children[bit] is not None and curr.children[bit].count > 0:
                match_val |= (bit << i)
                curr = curr.children[bit]
            else:
                break
        return (match_val, num ^ match_val)

    def size(self) -> int:
        return self.root.count
