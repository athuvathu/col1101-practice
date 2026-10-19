"""
Module: test_deadlock_cycle_detector.py
Formal Deadlock Detection via Wait-For Graph (WFG) Cycle Analysis and Tarjan's DFS.

Demonstrates:
1. Exact cycle path extraction using Tarjan-style DFS with path tracking.
2. Necessary and Sufficient Condition for Single-Unit Systems: Directed cycle <==> Deadlock.
3. Insufficiency of simple cycles in Multi-Unit Resource Allocation Graphs (RAG)
   without the knot condition.
4. Edge cases: DAGs (acyclic), disjoint graph components, self-loops, and multi-cycle graphs.
"""

from typing import Dict, List, Optional, Set, Tuple


# ============================================================================
# 1. Wait-For Graph (WFG) & Cycle Detector
# ============================================================================
class WaitForGraph:
    """
    Represents a directed Wait-For Graph (WFG) where edges U -> V denote
    that process U is waiting for a resource held by process V.
    """

    def __init__(self):
        self.adj: Dict[str, List[str]] = {}
        self.nodes: Set[str] = set()

    def add_node(self, u: str):
        self.nodes.add(u)
        if u not in self.adj:
            self.adj[u] = []

    def add_edge(self, u: str, v: str):
        """Add directed edge u -> v (u waits for v)."""
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append(v)

    def find_cycle(self) -> Optional[List[str]]:
        """
        Tarjan-style DFS cycle detection with 3-color vertex marking:
        - 0 (WHITE): unvisited
        - 1 (GRAY): currently in active recursion stack
        - 2 (BLACK): completely visited

        Returns the exact directed cycle path [v_start, ..., v_start] if found,
        or None if the graph is a DAG (deadlock-free).
        """
        color: Dict[str, int] = {node: 0 for node in self.nodes}
        parent_map: Dict[str, str] = {}
        cycle_path: Optional[List[str]] = None

        def dfs(u: str, current_path: List[str]) -> bool:
            nonlocal cycle_path
            color[u] = 1  # GRAY: in current DFS stack
            current_path.append(u)

            for v in self.adj.get(u, []):
                if color[v] == 1:
                    # Found back-edge u -> v! Cycle detected!
                    idx = current_path.index(v)
                    cycle_path = current_path[idx:] + [v]
                    return True
                elif color[v] == 0:
                    parent_map[v] = u
                    if dfs(v, current_path):
                        return True

            current_path.pop()
            color[u] = 2  # BLACK: done
            return False

        for node in sorted(self.nodes):
            if color[node] == 0:
                if dfs(node, []):
                    return cycle_path

        return None

    def is_deadlocked(self) -> bool:
        """For single-unit resource systems: cycle <==> deadlock."""
        return self.find_cycle() is not None

    def tarjan_scc(self) -> List[List[str]]:
        """
        Tarjan's Strongly Connected Components (SCC) algorithm.
        Time complexity: O(|V| + |E|).
        Uses DFS with discovery indices (dfn), low-link numbers, and an explicit stack.
        Returns all SCCs. Any SCC with >1 node (or self-loop) contains a directed cycle.
        """
        index = 0
        indices: Dict[str, int] = {}
        lowlink: Dict[str, int] = {}
        on_stack: Dict[str, bool] = {node: False for node in self.nodes}
        stack: List[str] = []
        sccs: List[List[str]] = []

        def strongconnect(u: str):
            nonlocal index
            indices[u] = index
            lowlink[u] = index
            index += 1
            stack.append(u)
            on_stack[u] = True

            for v in self.adj.get(u, []):
                if v not in indices:
                    strongconnect(v)
                    lowlink[u] = min(lowlink[u], lowlink[v])
                elif on_stack[v]:
                    lowlink[u] = min(lowlink[u], indices[v])

            if lowlink[u] == indices[u]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == u:
                        break
                sccs.append(scc)

        for node in sorted(self.nodes):
            if node not in indices:
                strongconnect(node)

        return sccs


# ============================================================================
# 2. Multi-Unit Resource Allocation Graph (RAG) Simulator
# ============================================================================
class MultiUnitRAG:
    """
    Resource Allocation Graph with multi-unit resources.
    Evaluates whether a cycle leads to deadlock or can be resolved
    by external threads releasing units (the Knot vs Cycle distinction).
    """

    def __init__(self):
        self.processes: Set[str] = set()
        self.resources: Set[str] = set()
        self.total_units: Dict[str, int] = {}
        self.allocated: Dict[str, Dict[str, int]] = {}  # proc -> {res: count}
        self.requested: Dict[str, Dict[str, int]] = {}  # proc -> {res: count}

    def add_resource(self, res: str, total_units: int):
        self.resources.add(res)
        self.total_units[res] = total_units

    def add_process(self, proc: str):
        self.processes.add(proc)
        self.allocated[proc] = {}
        self.requested[proc] = {}

    def allocate(self, proc: str, res: str, count: int = 1):
        self.allocated[proc][res] = self.allocated[proc].get(res, 0) + count

    def request(self, proc: str, res: str, count: int = 1):
        self.requested[proc][res] = self.requested[proc].get(res, 0) + count

    def is_knot(self, candidate_nodes: Set[str]) -> bool:
        """
        Checks if candidate_nodes form a knot in the process wait-for graph:
        A non-empty set K is a knot iff for every process u in K:
        1. u has non-empty reachability (is actively waiting).
        2. All processes reachable from u belong to K (no path escapes K).
        3. All processes in K are mutually reachable from u (Reach(u) == K).
        """
        if not candidate_nodes:
            return False

        # Build process wait-for adjacency
        adj: Dict[str, Set[str]] = {p: set() for p in self.processes}
        for p in self.processes:
            for r, req_cnt in self.requested[p].items():
                if req_cnt > 0:
                    for other_p in self.processes:
                        if other_p != p and self.allocated[other_p].get(r, 0) > 0:
                            adj[p].add(other_p)

        def reachable_from(src: str) -> Set[str]:
            visited = set()
            stack = [src]
            while stack:
                curr = stack.pop()
                for neighbor in adj.get(curr, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)
            return visited

        for u in candidate_nodes:
            reach_u = reachable_from(u)
            # Must have non-empty reachability and match candidate_nodes exactly
            if not reach_u or reach_u != candidate_nodes:
                return False
        return True

    def find_deadlocked_processes(self) -> Set[str]:
        """
        Dijkstra / Coffman / Silberschatz RAG reduction algorithm
        for general multi-unit systems.
        Returns the set of permanently deadlocked processes.
        """
        # 1. Compute available units for each resource
        available: Dict[str, int] = {}
        for r, total in self.total_units.items():
            allocated_total = sum(self.allocated[p].get(r, 0) for p in self.processes)
            available[r] = total - allocated_total

        work = dict(available)
        unmarked = set(self.processes)

        # 2. Iteratively reduce graph by completing unblocked processes
        while True:
            found = False
            for p in sorted(unmarked):
                # Check if process p can be satisfied with current work
                can_finish = True
                for r, req_cnt in self.requested[p].items():
                    if req_cnt > work.get(r, 0):
                        can_finish = False
                        break
                if can_finish:
                    # Process p finishes and releases all allocated units
                    for r, alloc_cnt in self.allocated[p].items():
                        work[r] = work.get(r, 0) + alloc_cnt
                    unmarked.remove(p)
                    found = True
                    break
            if not found:
                break

        return unmarked


# ============================================================================
# Pytest Test Cases
# ============================================================================
def test_single_unit_cycle_equivalence_to_deadlock():
    """
    Theorem: In a single-unit resource WFG, a directed cycle exists
    if and only if there is a deadlock.
    Verify detection and exact cycle extraction.
    """
    wfg = WaitForGraph()
    # Cycle: T1 -> T2 -> T3 -> T1
    wfg.add_edge("T1", "T2")
    wfg.add_edge("T2", "T3")
    wfg.add_edge("T3", "T1")

    # Non-cycle dependency
    wfg.add_edge("T4", "T1")

    assert wfg.is_deadlocked() is True
    cycle = wfg.find_cycle()
    assert cycle is not None

    # Verify cycle starts and ends on the same node
    assert cycle[0] == cycle[-1]

    # Verify every directed step in the cycle is an actual edge in the graph
    for i in range(len(cycle) - 1):
        u, v = cycle[i], cycle[i + 1]
        assert v in wfg.adj[u], f"Edge {u} -> {v} does not exist in graph"

    # Verify length of cycle
    assert len(cycle) == 4  # e.g. T1 -> T2 -> T3 -> T1


def test_acyclic_wfg_has_no_deadlock():
    """Verify that a DAG has no cycle and reports deadlock-free."""
    wfg = WaitForGraph()
    # DAG: T1 -> T2 -> T4, T1 -> T3 -> T4
    wfg.add_edge("T1", "T2")
    wfg.add_edge("T1", "T3")
    wfg.add_edge("T2", "T4")
    wfg.add_edge("T3", "T4")

    assert wfg.find_cycle() is None
    assert wfg.is_deadlocked() is False


def test_self_loop_cycle_detection():
    """Verify that a thread waiting on a resource it holds (self-loop) is detected."""
    wfg = WaitForGraph()
    wfg.add_edge("T1", "T1")

    cycle = wfg.find_cycle()
    assert cycle == ["T1", "T1"]
    assert wfg.is_deadlocked() is True


def test_disconnected_components_cycle():
    """Verify cycle detection in disconnected graph components."""
    wfg = WaitForGraph()
    # Component 1 (Acyclic): A -> B -> C
    wfg.add_edge("A", "B")
    wfg.add_edge("B", "C")

    # Component 2 (Cyclic): X -> Y -> X
    wfg.add_edge("X", "Y")
    wfg.add_edge("Y", "X")

    cycle = wfg.find_cycle()
    assert cycle is not None
    assert set(cycle) == {"X", "Y"}
    assert cycle[0] == cycle[-1]


def test_multi_unit_rag_cycle_without_deadlock():
    """
    Demonstrate that in a Multi-Unit system, a simple cycle is NOT sufficient
    for deadlock unless the knot condition holds.

    Scenario:
    - Resource R1 has 2 units.
    - P1 holds 1 unit of R1, requests R2 (held by P2).
    - P2 holds 1 unit of R2, requests R1.
    - (Cycle: P1 -> R2 -> P2 -> R1 -> P1).
    - HOWEVER, P3 also holds 1 unit of R1, and P3 requests NOTHING.
    - When P3 completes, it releases R1, satisfying P2's request and breaking the cycle!
    - Hence: Cycle exists, but NO DEADLOCK exists (not a knot).
    """
    rag = MultiUnitRAG()
    rag.add_resource("R1", total_units=2)
    rag.add_resource("R2", total_units=1)

    rag.add_process("P1")
    rag.add_process("P2")
    rag.add_process("P3")

    # P1 holds 1 unit of R1, requests R2
    rag.allocate("P1", "R1", 1)
    rag.request("P1", "R2", 1)

    # P2 holds 1 unit of R2, requests R1
    rag.allocate("P2", "R2", 1)
    rag.request("P2", "R1", 1)

    # P3 holds 1 unit of R1, requests nothing
    rag.allocate("P3", "R1", 1)

    # Verify that P1 and P2 can reach P3 (since P3 holds R1), but P3 cannot reach P1/P2.
    # Therefore {P1, P2} is NOT a knot!
    assert rag.is_knot({"P1", "P2"}) is False, (
        "Cycle with external releasing process should NOT form a knot"
    )

    # In addition, RAG reduction confirms no deadlock exists because P3 unblocks the system
    assert rag.find_deadlocked_processes() == set(), (
        "Expected RAG reduction to resolve all processes via P3"
    )


def test_is_knot_validation_and_edge_cases():
    """
    Rigorously verify the knot condition edge cases:
    1. An unblocked node with no requests must NOT be a knot (Reach(u) is empty).
    2. A proper subset of a 2-node cycle must NOT be a knot (path escapes the subset).
    3. An empty set is never a knot.
    4. A genuine closed cycle with no external paths IS a knot.
    """
    rag = MultiUnitRAG()
    rag.add_resource("R1", 1)
    rag.add_resource("R2", 1)
    rag.add_process("P1")
    rag.add_process("P2")
    rag.add_process("P3")

    # P1 holds R1, requests R2 (held by P2)
    # P2 holds R2, requests R1 (held by P1)
    rag.allocate("P1", "R1", 1)
    rag.request("P1", "R2", 1)
    rag.allocate("P2", "R2", 1)
    rag.request("P2", "R1", 1)

    # Edge Case 1: Empty set
    assert rag.is_knot(set()) is False

    # Edge Case 2: P3 is completely idle (requests nothing) -> must NOT be a knot
    assert rag.is_knot({"P3"}) is False

    # Edge Case 3: Proper subset {"P1"} alone is NOT a knot because P1 reaches P2 which is outside {"P1"}
    assert rag.is_knot({"P1"}) is False

    # Closed cycle: {P1, P2} mutually reach each other and cannot reach P3 -> IS a knot!
    assert rag.is_knot({"P1", "P2"}) is True


def test_multi_unit_rag_reduction_deadlock():
    """
    Demonstrates true multi-unit deadlock detection via RAG reduction (Banker's method):
    When no process can proceed, the knot of blocked processes is identified.
    """
    rag = MultiUnitRAG()
    rag.add_resource("R1", 1)
    rag.add_resource("R2", 1)

    rag.add_process("P1")
    rag.add_process("P2")

    rag.allocate("P1", "R1", 1)
    rag.request("P1", "R2", 1)

    rag.allocate("P2", "R2", 1)
    rag.request("P2", "R1", 1)

    # Available: R1: 0, R2: 0. Neither P1 nor P2 can proceed!
    deadlocked = rag.find_deadlocked_processes()
    assert deadlocked == {"P1", "P2"}, f"Expected deadlock between P1 and P2, got {deadlocked}"
    assert rag.is_knot({"P1", "P2"}) is True


def test_tarjan_scc_decomposition():
    """
    Verify Tarjan's SCC algorithm on a graph with:
    1. Acyclic component: A -> B
    2. 3-node cycle: C1 -> C2 -> C3 -> C1
    3. 2-node cycle: D1 -> D2 -> D1
    """
    wfg = WaitForGraph()
    wfg.add_edge("A", "B")
    wfg.add_edge("B", "C1")  # A -> B -> cycle C

    wfg.add_edge("C1", "C2")
    wfg.add_edge("C2", "C3")
    wfg.add_edge("C3", "C1")

    wfg.add_edge("D1", "D2")
    wfg.add_edge("D2", "D1")

    sccs = wfg.tarjan_scc()
    scc_sets = [set(scc) for scc in sccs]

    # Verify that the 3-node cycle and 2-node cycle form distinct SCCs
    assert {"C1", "C2", "C3"} in scc_sets
    assert {"D1", "D2"} in scc_sets
    assert {"A"} in scc_sets
    assert {"B"} in scc_sets

