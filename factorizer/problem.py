from typing import Dict

from pulp import *
import networkx as nx

from factorizer import D, F_s


def build_problem(G: nx.DiGraph, R_u: int, c: Dict) -> LpProblem:
    """Build the problem from the instance.

    Args:
        G: The graph of the instance.
        R_u: The maximum range of underground belts.
    """
    V = [v for v in G.nodes if G.nodes[v]["grid"]]
    B = [v for v in G.nodes if not G.nodes[v]["grid"] and G.nodes[v]["start"]]
    E = [v for v in G.nodes if not G.nodes[v]["grid"] and G.nodes[v]["end"]]

    A = G.edges

    problem = LpProblem("Factorio Balancer", LpMinimize)

    # --- VARIABLES ---

    # Build a transport belt at node v in direction d?
    t = {(v, d): LpVariable(f"t_{v}_{d}", cat=LpBinary) for v in V for d in D}

    # Build underground belt with range r at node v in direction d?
    u = {(v, d, r): LpVariable(f"u_{v}_{d}_{r}", cat=LpBinary) for v in V for d in D for r in range(1, R_u)}

    # Build splitter fragment f at node v?
    # For now, we assume splitters always point rightwards
    s = {(v, f): LpVariable(f"s_{v}_{f}", cat=LpBinary) for v in V for f in F_s}

    # Send how much from start point b over arc a?
    x = {(a, b): LpVariable(f"x_{a}_{b}", cat=LpContinuous) for a in A for b in B}

    # Activate arc a?
    y = {a: LpVariable(f"y_{a}", cat=LpBinary) for a in A}

    # --- OBJECTIVE ---

    problem += lpSum(((c["transport"] * t[v, d] + (c["underground"] * u[v, d, r] for r in range(1, R_u))) for d in
                      D + (c["splitter"] * s[v, f] for f in F_s)) for v in V)

    return problem
