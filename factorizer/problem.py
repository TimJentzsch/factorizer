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
    V = [v for v in G.nodes if G.nodes[v]["grid"]]
    B = [v for v in G.nodes if not G.nodes[v]["grid"] and G.nodes[v]["start"]]
    E = [v for v in G.nodes if not G.nodes[v]["grid"] and G.nodes[v]["end"]]

    A = G.edges

    n: int = G.graph["n"]
    m: int = G.graph["m"]
    R_u: range = range(1, G.graph["R"] + 1)

    problem = LpProblem("Factorio Balancer", LpMinimize)

    # --- VARIABLES ---

    # Build a transport belt at node v in direction d?
    t = {(v, d): LpVariable(f"t_{v}_{d}", cat=LpBinary) for v in V for d in D}

    # Build underground belt with range r at node v in direction d?
    u = {(v, d, r): LpVariable(f"u_{v}_{d}_{r}", cat=LpBinary) for v in V for d in D for r in R_u}

    # Build splitter fragment f at node v?
    # For now, we assume splitters always point rightwards
    s = {(v, f): LpVariable(f"s_{v}_{f}", cat=LpBinary) for v in V for f in F_s}

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
        for v in V
    )

    # --- CONSTRAINTS ---

    # Only place at most one entity on each tile
    for v in V:
        problem += (
            lpSum(
                t[v, d]
                + lpSum(v[v, d, r] for r in R_u)
                for d in D
            )
            + lpSum(s[v, f] for f in F_s)
        ) <= 1

    # Only one non-splitter arc can be activated per tile
    for v in V:
        # Outgoing
        problem += (
            lpSum(y[a] for a in G.out_edges[v])
            <= 1
        )

        # Incoming
        problem += (
            lpSum(y[a] for a in G.in_edges[v])
            <= 1
        )

    # A transport belt has flow in its direction
    for v in V:
        for d in D:
            problem += (
                t[v, d]
                <= y[dir_out_edge(G, v, d, 1)]
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
    for v in V:
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

            problem += x[(-1, b1), (0, b1)] == supply

    # Demand
    for b in B:
        for e in E:
            problem += x[(n - 1, e), (n, e)] == 1

    return problem


def dir_out_edge(G: nx.DiGraph, v, d: str, r: int):
    edges = [w for w in G.out_edges(v) if G.nodes[w][d] and G.nodes[w]["r"] == r]

    return edges[0]

