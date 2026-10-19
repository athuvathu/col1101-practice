"""
solution.py - Master Reference Solution for Exam 1 Problem 2
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 2)
"""

import math
from typing import Optional
from common import MinHeap, MaxHeap


class RunningQuantile:
    """
    Maintains the p-th quantile of a stream using dual heaps.
    Lower heap: MaxHeap containing the smallest K = ceil(p * N) elements.
    Upper heap: MinHeap containing the remaining N - K elements.
    """
    def __init__(self, p: float):
        if not (0.0 < p < 1.0):
            raise ValueError("p must be strictly between 0 and 1.")
        self.p = p
        self.lower = MaxHeap() # contains K smallest elements
        self.upper = MinHeap() # contains remaining elements
        self.count = 0

    def add(self, val: float) -> None:
        self.count += 1
        
        # Initial routing
        if len(self.lower) == 0 or val <= self.lower.peek():
            self.lower.push(val)
        else:
            self.upper.push(val)

        # Rebalance so that len(self.lower) == target_k
        target_k = math.ceil(self.p * self.count)

        while len(self.lower) > target_k:
            self.upper.push(self.lower.pop())

        while len(self.lower) < target_k:
            self.lower.push(self.upper.pop())

    def get_quantile(self) -> Optional[float]:
        if self.count == 0:
            return None
        return self.lower.peek()

    def __len__(self) -> int:
        return self.count
