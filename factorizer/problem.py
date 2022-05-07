from pulp import *


def build_problem(V, D, R_u, F_s, A, B) -> LpProblem:
    """Build the problem from the instance."""
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
