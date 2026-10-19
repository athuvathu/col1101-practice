"""
common.py - Pre-implemented FastHashTable for Exam 2 Problem 2
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 2)

This class is PRE-IMPLEMENTED and provided to you.
Use its methods in your solution. Do not modify this file.
"""

from typing import Any, Optional


class FastHashTable:
    """
    Pre-implemented Open-Addressing Hash Table with Linear Probing.
    Automatically doubles capacity when load factor exceeds 0.65.
    """
    def __init__(self, initial_capacity: int = 16):
        self.capacity = initial_capacity
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.size = 0

    def _hash(self, key: Any) -> int:
        return hash(key) % self.capacity

    def put(self, key: Any, val: Any) -> None:
        """Inserts or updates (key, val) in O(1) expected time."""
        if self.size / self.capacity >= 0.65:
            self._rehash(self.capacity * 2)

        idx = self._hash(key)
        while self.keys[idx] is not None:
            if self.keys[idx] == key:
                self.values[idx] = val
                return
            idx = (idx + 1) % self.capacity

        self.keys[idx] = key
        self.values[idx] = val
        self.size += 1

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Returns value associated with key, or default if absent. O(1) expected."""
        idx = self._hash(key)
        initial_idx = idx
        while self.keys[idx] is not None:
            if self.keys[idx] == key:
                return self.values[idx]
            idx = (idx + 1) % self.capacity
            if idx == initial_idx:
                break
        return default

    def contains(self, key: Any) -> bool:
        """Returns True if key is present in the table. O(1) expected."""
        return self.get(key, default=None) is not None or key in self.keys

    def __len__(self) -> int:
        return self.size

    def _rehash(self, new_cap: int) -> None:
        old_keys = self.keys
        old_vals = self.values
        self.capacity = new_cap
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.size = 0

        for k, v in zip(old_keys, old_vals):
            if k is not None:
                self.put(k, v)
