"""
solution.py - Master Reference Solution for Exam 2 Problem 1
COL1101 Diwali 2026 Programming Quiz 2 (Exam 2 - Problem 1)
"""

from typing import List, Dict, Tuple
from common import OrderBST


def simulate_order_book(order_stream: List[Dict]) -> Tuple[int, List[Tuple[str, str, int, int]]]:
    bids = OrderBST()  # Max bid is best
    asks = OrderBST()  # Min ask is best

    total_volume = 0
    trades: List[Tuple[str, str, int, int]] = []

    for order in order_stream:
        o_id = order["id"]
        o_type = order["type"]
        o_price = order["price"]
        o_qty = order["qty"]

        if o_type == "BUY":
            # Match against asks while lowest ask <= o_price
            while o_qty > 0 and not asks.is_empty():
                best_ask_node = asks.get_min_node()
                if best_ask_node.price > o_price:
                    break

                # Match with resting ask orders at this price level
                resting_order = best_ask_node.orders[0]
                ask_id, ask_qty = resting_order[0], resting_order[1]
                traded = min(o_qty, ask_qty)

                total_volume += traded
                trades.append((o_id, ask_id, best_ask_node.price, traded))

                o_qty -= traded
                resting_order[1] -= traded

                if resting_order[1] == 0:
                    best_ask_node.orders.pop(0)
                    if len(best_ask_node.orders) == 0:
                        asks.delete_min()

            # If unfulfilled remainder, rest in bids
            if o_qty > 0:
                bids.insert(o_price, o_id, o_qty)

        elif o_type == "SELL":
            # Match against bids while highest bid >= o_price
            while o_qty > 0 and not bids.is_empty():
                best_bid_node = bids.get_max_node()
                if best_bid_node.price < o_price:
                    break

                resting_order = best_bid_node.orders[0]
                bid_id, bid_qty = resting_order[0], resting_order[1]
                traded = min(o_qty, bid_qty)

                total_volume += traded
                trades.append((bid_id, o_id, best_bid_node.price, traded))

                o_qty -= traded
                resting_order[1] -= traded

                if resting_order[1] == 0:
                    best_bid_node.orders.pop(0)
                    if len(best_bid_node.orders) == 0:
                        bids.delete_max()

            # If unfulfilled remainder, rest in asks
            if o_qty > 0:
                asks.insert(o_price, o_id, o_qty)

    return (total_volume, trades)
