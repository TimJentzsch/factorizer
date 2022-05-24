from typing import Dict, Tuple

from pulp import *
import networkx as nx

from factorizer import D, F_s
from factorizer.utils import splitter_out_edge, dir_out_edge

VarDict = Dict[Tuple, LpVariable]


def build_problem(
    G: nx.DiGraph, c: Dict
) -> Tuple[LpProblem, VarDict, VarDict, VarDict, VarDict, VarDict]:
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
    R_u: range = range(2, G.graph["R"] + 1)

    problem = LpProblem(G.graph["name"], LpMinimize)

    # --- VARIABLES ---

    # Build a transport belt at node v?
    t = {v: LpVariable(f"t_{v}", cat=LpBinary) for v in V_grid}

    # Build underground belt with range r at node v in direction d?
    u = {
        (v, d, r): LpVariable(f"u_{v}_{d}_{r}", cat=LpBinary)
        for v in V_grid
        for d in D
        for r in R_u
    }

    # Build splitter fragment f at node v?
    # For now, we assume splitters always point rightwards
    s = {(v, f): LpVariable(f"s_{v}_{f}", cat=LpBinary) for v in V_grid for f in F_s}

    # Send how much from start point b over arc a?
    x = {
        (a, b): LpVariable(f"x_{a}_{b}", cat=LpContinuous, lowBound=0.0)
        for a in A
        for b in B
    }

    # Activate arc a?
    y = {a: LpVariable(f"y_{a}", cat=LpBinary) for a in A}

    # --- OBJECTIVE ---

    problem += lpSum(
        (
            c["transport"] * t[v]
            + lpSum(c["underground"] * u[v, d, r] for r in R_u for d in D)
            + lpSum(c["splitter"] * s[v, f] for f in F_s)
        )
        for v in V_grid
    )

    # --- CONSTRAINTS ---

    # Only place at most one entity on each tile
    for v in V_grid:
        problem += (
            t[v]
            + lpSum(u[v, d, r] for r in R_u for d in D)
            + lpSum(s[v, f] for f in F_s)
        ) <= 1

    # Only one non-splitter arc can be activated per tile
    for v in V_grid:
        # Outgoing
        problem += lpSum(y[a] for a in G.out_edges(v) if not G.edges[a]["split"]) <= 1

        # Incoming
        problem += lpSum(y[a] for a in G.in_edges(v) if not G.edges[a]["split"]) <= 1

    # Splitter arcs can only be activated by splitters
    for v in V_grid:
        for a in G.out_edges(v):
            if G.edges[a]["split"]:
                if G.edges[a]["d"] == "up":
                    problem += y[a] <= s[v, "right"]
                elif G.edges[a]["d"] == "down":
                    problem += y[a] <= s[v, "left"]

    # Always place splitter fragments together
    for i in range(n):
        for j in range(m - 1):
            problem += s[(i, j), "right"] == s[(i, j + 1), "left"]

    # Balance splitter output
    for v in V_grid:
        for b in B:
            for f in F_s:
                splitter_edge = splitter_out_edge(G, v, f)
                normal_edge = dir_out_edge(G, v, "right", 1)

                if splitter_edge and normal_edge:
                    balanced_flow = 0.5 * lpSum(x[a, b] for a in G.in_edges(v))
                    M = (1 - y[splitter_edge]) * 0.5 * len(E)

                    problem += balanced_flow + M >= x[splitter_edge, b]
                    problem += balanced_flow + M >= x[normal_edge, b]

    # A splitter can only have flow to the right
    for v in V_grid:
        for f in F_s:
            for d in D:
                if d != "right":
                    if dir_edge := dir_out_edge(G, v, d, 1):
                        problem += y[dir_edge] <= 1 - s[v, f]

    # Activated arcs must come from an entity and go to an entity
    for v in V_grid:
        entity = (
            t[v]
            + lpSum(u[v, d, r] for r in R_u for d in D)
            + lpSum(s[v, f] for f in F_s)
        )

        for a in G.in_edges(v):
            problem += entity >= y[a]

        for a in G.out_edges(v):
            problem += entity >= y[a]

    # Only underground belts can have underground flow
    for d in D:
        for v in V_grid:
            for r in R_u:
                if underground_edge := dir_out_edge(G, v, d, r):
                    problem += y[underground_edge] == u[v, d, r]
                else:
                    problem += u[v, d, r] == 0

                for d2 in D:
                    if transport_belt_edge := dir_out_edge(G, v, d2, 1):
                        # Underground belts cannot have transport belt flow
                        problem += y[transport_belt_edge] <= 1 - u[v, d, r]

    # An underground belt must have a transport belt as "end piece"
    for v in V_grid:
        for d in D:
            for r in R_u:
                if underground_edge := dir_out_edge(G, v, d, r):
                    (start, end) = underground_edge

                    if transport_belt_edge := dir_out_edge(G, end, d, 1):
                        problem += u[v, d, r] <= t[end]
                        problem += u[v, d, r] <= y[transport_belt_edge]
                    else:
                        problem += u[v, d, r] == 0

    # Only allow flow over activated arcs
    for a in A:
        for b in B:
            problem += x[a, b] <= len(E) * y[a]

    # Respect belt capacity
    for a in A:
        problem += lpSum(x[a, b] for b in B) <= len(E)

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
