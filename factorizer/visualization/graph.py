import os.path
from typing import Tuple

import networkx as nx
import matplotlib.pyplot as plt
from pulp import LpProblem

from factorizer import D, F_s


def build_solution_graph(G: nx.DiGraph, problem: LpProblem, t, u, s, x, y) -> nx.DiGraph:
    """Build a graph from the solution of the problem."""
    n = G.graph["n"]
    m = G.graph["m"]
    R_u: range = range(1, G.graph["R"] + 1)

    H = nx.DiGraph(name=G.graph["name"])
    pos = {}
    labels = {}

    for x in range(1, n):
        for y in range(1, m):
            v = (x, y)
            pos[v] = v
            labels[v] = _get_node_label(v, R_u, t, u, s)

            H.add_node((x, y))

    nx.set_node_attributes(H, pos, "pos")
    nx.set_node_attributes(H, labels, "labels")

    return H


def _get_node_label(v: Tuple[int, int], R_u: range, t, u, s) -> str:
    """Get the label for the given node v."""
    for d in D:
        if t[v, d].value() == 1:
            return f"t_{d[0]}"

    for d in D:
        for r in R_u:
            if u[v, d, r].value() == 1:
                return f"u_{d[0]},{r}"

    for f in F_s:
        if s[v, f].value() == 1:
            return f"s_{f[0]}"

    return ""


def save_solution_graph(H: nx.DiGraph, output_dir: str) -> None:
    """Save the solution graph to an image."""
    # Draw the graph
    nx.draw_networkx(
        H,
        pos=nx.get_node_attributes(H, "pos"),
        labels=nx.get_node_attributes(H, "labels"),
        with_labels=True
    )

    path = os.path.join(output_dir, "solution_graph.png")

    # Save it to an image
    plt.savefig(path, format="PNG")
