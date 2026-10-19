"""
student_code.py - Problem 2: Dual-Heap Running Quantile Monitor
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 2)

MinHeap and MaxHeap are pre-implemented in common.py.
"""

import math
from typing import Optional
from common import MinHeap, MaxHeap


class RunningQuantile:
    """
    Maintains the p-th quantile of a streaming dataset in O(log N) per insertion
    and O(1) per query using dual heaps.
    """
    def __init__(self, p: float):
        if not (0.0 < p < 1.0):
            raise ValueError("p must be strictly between 0 and 1.")
        self.p = p
        # TODO: Initialize your heaps and count
        pass

    def add(self, val: float) -> None:
        """Adds a value to the monitor and rebalances heaps in O(log N)."""
        # TODO: Implement this method
        pass

    def get_quantile(self) -> Optional[float]:
        """Returns the current p-th quantile in O(1) time (or None if empty)."""
        # TODO: Implement this method
        pass

    def __len__(self) -> int:
        """Returns the total number of items currently in the monitor."""
        # TODO: Implement this method
        pass
