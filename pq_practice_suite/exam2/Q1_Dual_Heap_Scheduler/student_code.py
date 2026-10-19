"""
student_code.py - Problem 1: Limit Order Book Matching Engine
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 1)

OrderBST is pre-implemented in common.py.
"""

from typing import List, Dict, Tuple
from common import OrderBST


def simulate_order_book(order_stream: List[Dict]) -> Tuple[int, List[Tuple[str, str, int, int]]]:
    """
    Simulates the limit order book using pre-implemented OrderBST.

    Parameters:
      order_stream: list of dicts:
        {"id": str, "type": "BUY" | "SELL", "price": int, "qty": int}

    Returns:
      (total_volume_traded, executed_trades)
      where each trade is (buy_order_id, sell_order_id, execution_price, traded_qty)
    """
    # TODO: Implement this function using OrderBST for bids and asks
    pass
