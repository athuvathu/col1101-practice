"""
common.py - Pre-implemented OrderBST (Standard BST) for Exam 2 Problem 1
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 1)

This class is PRE-IMPLEMENTED and provided to you.
Use its methods in your solution. Do not modify this file.
"""

from typing import Optional, Tuple, List, Dict


class BSTNode:
    def __init__(self, price: int, order_id: str, qty: int):
        self.price = price
        # List of (order_id, qty) at this price level in arrival order
        self.orders: List[List[Any]] = [[order_id, qty]]
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class OrderBST:
    """
    Standard Binary Search Tree (unbalanced, no AVL rotations).
    Stores price levels. At each price level, holds FIFO list of orders.
    """
    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._count = 0

    def insert(self, price: int, order_id: str, qty: int) -> None:
        """Inserts an order at the specified price level."""
        self._count += 1
        if self.root is None:
            self.root = BSTNode(price, order_id, qty)
            return

        curr = self.root
        while True:
            if price == curr.price:
                curr.orders.append([order_id, qty])
                return
            elif price < curr.price:
                if curr.left is None:
                    curr.left = BSTNode(price, order_id, qty)
                    return
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = BSTNode(price, order_id, qty)
                    return
                curr = curr.right

    def get_min_node(self) -> Optional[BSTNode]:
        """Returns the node with the lowest price (leftmost node), or None."""
        if self.root is None:
            return None
        curr = self.root
        while curr.left is not None:
            curr = curr.left
        return curr

    def get_max_node(self) -> Optional[BSTNode]:
        """Returns the node with the highest price (rightmost node), or None."""
        if self.root is None:
            return None
        curr = self.root
        while curr.right is not None:
            curr = curr.right
        return curr

    def delete_min(self) -> None:
        """Deletes the node with the minimum price."""
        if self.root is None:
            return

        parent = None
        curr = self.root
        while curr.left is not None:
            parent = curr
            curr = curr.left

        # curr is the min node; curr has at most a right child
        if parent is None:
            self.root = curr.right
        else:
            parent.left = curr.right

    def delete_max(self) -> None:
        """Deletes the node with the maximum price."""
        if self.root is None:
            return

        parent = None
        curr = self.root
        while curr.right is not None:
            parent = curr
            curr = curr.right

        # curr is the max node; curr has at most a left child
        if parent is None:
            self.root = curr.left
        else:
            parent.right = curr.left

    def is_empty(self) -> bool:
        return self.root is None
