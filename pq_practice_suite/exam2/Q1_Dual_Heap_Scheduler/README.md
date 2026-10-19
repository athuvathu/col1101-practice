# Problem 1: Limit Order Book Matching Engine

**Course:** COL1101 (Programming with Data Structures)  
**Exam:** Programming Quiz 2 (Exam 2 - Problem 1)  
**Marks:** 40 points  
**Target Time:** 35 minutes  

---

## 1. Problem Statement

Financial electronic markets process thousands of incoming limit orders every second. An exchange maintains two order books:
1. **Bids (Buy Orders):** Buyers looking to purchase an asset.
2. **Asks (Sell Orders):** Sellers looking to sell an asset.

When a buy order arrives, if its limit price is greater than or equal to the **lowest current ask price** in the market, a trade occurs immediately (crossing the book). The trade executes at the maker's price (the resting ask order's price).

Symmetrically, when a sell order arrives, if its limit price is less than or equal to the **highest current bid price**, it crosses the market at the resting bid order's price.

You are provided with a pre-implemented **standard Binary Search Tree** (`OrderBST`) in `common.py`. It organizes orders by price levels without AVL rotations:
- `insert(price, order_id, qty)`
- `get_min_node() -> Optional[BSTNode]`
- `get_max_node() -> Optional[BSTNode]`
- `delete_min()`
- `delete_max()`
- `is_empty() -> bool`

---

## 2. Function Contract

Implement `simulate_order_book(order_stream: List[Dict])` in `student_code.py`:

```python
def simulate_order_book(order_stream: List[Dict]) -> Tuple[int, List[Tuple[str, str, int, int]]]:
    """
    Simulates order execution over incoming limit orders using OrderBST.
    
    Each order is a dictionary:
      {"id": str, "type": "BUY" | "SELL", "price": int, "qty": int}
      
    Returns:
      (total_volume_traded, executed_trades)
      where executed_trades is a list of tuples in chronological execution order:
      (buy_order_id, sell_order_id, execution_price, traded_qty)
    """
```

---

## 3. Matching Rules

1. **Price-Time Priority:**
   - At any time, a crossing buy matches with the lowest available ask. If multiple asks exist at the same price, match in arrival order (FIFO).
   - A crossing sell matches with the highest available bid.
2. **Execution Price:**
   - Always trades at the resting (maker) order's price that was already sitting in the book.
3. **Partial Fills:**
   - If an incoming order's quantity exceeds the matched resting order, the resting order is filled and removed, and the incoming order continues matching with the next best resting order.
   - Any unfilled residual quantity of the incoming order is added into its respective book.

---

## 4. Example Trace

```python
orders = [
    {"id": "S1", "type": "SELL", "price": 105, "qty": 10},
    {"id": "S2", "type": "SELL", "price": 100, "qty": 5},
    {"id": "B1", "type": "BUY",  "price": 102, "qty": 8}
]

# 1. S1 resting at 105 (qty 10)
# 2. S2 resting at 100 (qty 5)
# 3. B1 arrives at 102 (qty 8).
#    Best ask is S2 at 100 <= 102.
#    Match 5 units at price 100! (B1 has 3 left). S2 filled and removed.
#    Next best ask is S1 at 105 > 102. No more matches.
#    Remaining 3 units of B1 placed as bid at 102.

total_vol, trades = simulate_order_book(orders)
assert total_vol == 5
assert trades == [("B1", "S2", 100, 5)]
```
