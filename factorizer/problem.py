from typing import Dict, Tuple

from pulp import *
import networkx as nx

from factorizer import D, F_s


VarDict = Dict[Tuple, LpVariable]


def build_problem(G: nx.DiGraph, c: Dict) -> Tuple[LpProblem, VarDict, VarDict, VarDict, VarDict, VarDict]:
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

    problem = LpProblem(G.graph["name"], LpMinimize)

    # --- VARIABLES ---

    # Build a transport belt at node v in direction d?
    t = {(v, d): LpVariable(f"t_{v}_{d}", cat=LpBinary) for v in V_grid for d in D}

    # Build underground belt with range r at node v in direction d?
    u = {(v, d, r): LpVariable(f"u_{v}_{d}_{r}", cat=LpBinary) for v in V_grid for d in D for r in R_u}

    # Build splitter fragment f at node v?
    # For now, we assume splitters always point rightwards
    s = {(v, f): LpVariable(f"s_{v}_{f}", cat=LpBinary) for v in V_grid for f in F_s}

    # Send how much from start point b over arc a?
    x = {(a, b): LpVariable(f"x_{a}_{b}", cat=LpContinuous, lowBound=0.0) for a in A for b in B}

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
            lpSum(y[a] for a in G.out_edges(v) if not G.edges[a]["split"])
            <= 1
        )

        # Incoming
        problem += (
            lpSum(y[a] for a in G.in_edges(v) if not G.edges[a]["split"])
            <= 1
        )

    # Activated arcs must come from an entity and go to an entity
    for v in V_grid:
        entity = lpSum(t[v, d] + lpSum(u[v, d, r] for r in R_u) for d in D) + lpSum(s[v, f] for f in F_s)

        for a in G.in_edges(v):
            problem += entity >= y[a]

        for a in G.out_edges(v):
            problem += entity >= y[a]

    # A transport belt can only have flow in its direction
    for v in V_grid:
        for d1 in D:
            for d2 in D:
                if d1 != d2:
                    if t_edge := dir_out_edge(G, v, d2, 1):
                        problem += (
                            y[t_edge]
                            <= 1 - t[v, d1]
                        )

    # Only underground belts can have underground flow
    for d in D:
        for v in V_grid:
            for a in G.out_edges(v):
                r = G.edges[a]["r"]
                if r > 1:
                    problem += y[a] <= u[v, d, r]

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

    return problem, t, u, s, x, y


def dir_out_edge(G: nx.DiGraph, v, d: str, r: int):
    edges = [a for a in G.out_edges(v) if G.edges[a]["d"] == d and G.edges[a]["r"] == r and not G.edges[a]["split"]]

    return edges[0] if len(edges) > 0 else None

