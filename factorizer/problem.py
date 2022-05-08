from typing import Dict

from pulp import *
import networkx as nx

from factorizer import D, F_s


def build_problem(G: nx.DiGraph, c: Dict) -> LpProblem:
    """Build the problem from the instance.

    Args:
        G: The graph of the instance.
        c: The costs of the instance.
    """
    V_all = G.nodes
    V_grid = [v for v in V_all if G.nodes[v]["grid"]]

    A = G.edges

    n: int = G.graph["n"]
    m: int = G.graph["m"]
    B = G.graph["B"]
    E = G.graph["E"]
    R_u: range = range(1, G.graph["R"] + 1)

    problem = LpProblem(f"balancer_{n}_{m}", LpMinimize)

    # --- VARIABLES ---

    # Build a transport belt at node v in direction d?
    t = {(v, d): LpVariable(f"t_{v}_{d}", cat=LpBinary) for v in V_grid for d in D}

    # Build underground belt with range r at node v in direction d?
    u = {(v, d, r): LpVariable(f"u_{v}_{d}_{r}", cat=LpBinary) for v in V_grid for d in D for r in R_u}

    # Build splitter fragment f at node v?
    # For now, we assume splitters always point rightwards
    s = {(v, f): LpVariable(f"s_{v}_{f}", cat=LpBinary) for v in V_grid for f in F_s}

    # Send how much from start point b over arc a?
    x = {(a, b): LpVariable(f"x_{a}_{b}", cat=LpContinuous) for a in A for b in B}

    # Activate arc a?
    y = {a: LpVariable(f"y_{a}", cat=LpBinary) for a in A}

    # --- OBJECTIVE ---

    problem += lpSum(
        lpSum(
            c["transport"] * t[v, d]
            + lpSum(c["underground"] * u[v, d, r] for r in R_u)
            for d in D
        )
        + lpSum(c["splitter"] * s[v, f] for f in F_s)
        for v in V_grid
    )

    # --- CONSTRAINTS ---

    # Only place at most one entity on each tile
    for v in V_grid:
        problem += (
            lpSum(
                t[v, d]
                + lpSum(u[v, d, r] for r in R_u)
                for d in D
            )
            + lpSum(s[v, f] for f in F_s)
        ) <= 1

    # Only one non-splitter arc can be activated per tile
    for v in V_grid:
        # Outgoing
        problem += (
            lpSum(y[a] for a in G.out_edges(v))
            <= 1
        )

        # Incoming
        problem += (
            lpSum(y[a] for a in G.in_edges(v))
            <= 1
        )

    # A transport belt has flow in its direction
    for v in V_grid:
        for d in D:
            if t_edge := dir_out_edge(G, v, d, 1):
                problem += (
                    t[v, d]
                    <= y[t_edge]
                )

    # Only allow flow over activated arcs
    for a in A:
        for b in B:
            problem += (
                x[a, b]
                <= len(E) * y[a]
            )

    # Respect belt capacity
    for a in A:
        problem += (
            lpSum(x[a, b] for b in B)
            <= len(E)
        )

    # Flow conservation
    for v in V_grid:
        for b in B:
            problem += (
                lpSum(x[a, b] for a in G.out_edges(v))
                - lpSum(x[a, b] for a in G.in_edges(v))
                == 0
            )

    # Supply
    for b1 in B:
        for b2 in B:
            supply = len(E) if b1 == b2 else 0

            problem += x[((-1, b2), (0, b2)), b1] == supply

    # Demand
    for b in B:
        for e in E:
            problem += x[((n - 1, e), (n, e)), b] == 1

    return problem


def dir_out_edge(G: nx.DiGraph, v, d: str, r: int):
    edges = [a for a in G.out_edges(v) if G.edges[a]["d"] == d and G.edges[a]["r"] == r]

    return edges[0] if len(edges) > 0 else None

