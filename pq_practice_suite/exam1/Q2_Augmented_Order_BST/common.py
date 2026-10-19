"""
common.py - Pre-implemented MinHeap and MaxHeap for Exam 1 Problem 2
COL1101 Diwali 2026 Programming Quiz 2 (Exam 1 - Problem 2)

These classes are PRE-IMPLEMENTED and provided to you.
Use them in your solution. Do not modify this file.
"""

from typing import Any, Optional


class MinHeap:
    """Pre-implemented Binary Min-Heap with standard O(log N) push/pop."""
    def __init__(self):
        self.data = []

    def push(self, val: Any) -> None:
        self.data.append(val)
        self._sift_up(len(self.data) - 1)

    def pop(self) -> Any:
        if not self.data:
            raise IndexError("pop from empty MinHeap")
        ret = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0)
        return ret

    def peek(self) -> Optional[Any]:
        return self.data[0] if self.data else None

    def __len__(self) -> int:
        return len(self.data)

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            if self.data[idx] < self.data[parent]:
                self.data[idx], self.data[parent] = self.data[parent], self.data[idx]
                idx = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self.data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            if left < n and self.data[left] < self.data[smallest]:
                smallest = left
            if right < n and self.data[right] < self.data[smallest]:
                smallest = right
            if smallest != idx:
                self.data[idx], self.data[smallest] = self.data[smallest], self.data[idx]
                idx = smallest
            else:
                break


class MaxHeap:
    """Pre-implemented Binary Max-Heap with standard O(log N) push/pop."""
    def __init__(self):
        self.data = []

    def push(self, val: Any) -> None:
        self.data.append(val)
        self._sift_up(len(self.data) - 1)

    def pop(self) -> Any:
        if not self.data:
            raise IndexError("pop from empty MaxHeap")
        ret = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0)
        return ret

    def peek(self) -> Optional[Any]:
        return self.data[0] if self.data else None

    def __len__(self) -> int:
        return len(self.data)

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            if self.data[idx] > self.data[parent]:
                self.data[idx], self.data[parent] = self.data[parent], self.data[idx]
                idx = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self.data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            largest = idx
            if left < n and self.data[left] > self.data[largest]:
                largest = left
            if right < n and self.data[right] > self.data[largest]:
                largest = right
            if largest != idx:
                self.data[idx], self.data[largest] = self.data[largest], self.data[idx]
                idx = largest
            else:
                break
