import os.path
from typing import Tuple

import networkx as nx
import matplotlib.pyplot as plt

from factorizer import D, F_s


def build_solution_graph(G: nx.DiGraph, t, u, s, x, y) -> nx.DiGraph:
    """Build a graph from the solution of the problem."""
    n = G.graph["n"]
    m = G.graph["m"]
    R_u: range = range(1, G.graph["R"] + 1)

    H = nx.DiGraph(**G.graph)

    # --- NODES ---

    node_labels = {}

    # Grid nodes
    for i in range(n):
        for j in range(m):
            v = (i, j)
            node_labels[v] = _get_node_label(v, R_u, t, u, s)

            H.add_node(v)

    # Start nodes
    for b in G.graph["B"]:
        v = (-1, b)
        node_labels[v] = "B"

        H.add_node(v)

    # End nodes
    for e in G.graph["E"]:
        v = (n, e)
        node_labels[v] = "E"

        H.add_node(v)

    pos = {v: v for v in H.nodes}

    nx.set_node_attributes(H, pos, "pos")
    nx.set_node_attributes(H, node_labels, "node_labels")

    # --- EDGES ---

    edge_labels = {}

    for a in G.edges:
        flows = {}

        for b in G.graph["B"]:
            flows[b] = x[a, b].value()

        if sum(flows.values()) > 0:
            label = "/".join([str(int(f)) for f in flows.values()])
            edge_labels[a] = label

            H.add_edge(*a)

    nx.set_edge_attributes(H, edge_labels, "edge_labels")

    return H


def _get_node_label(v: Tuple[int, int], R_u: range, t, u, s) -> str:
    """Get the label for the given node v."""
    if t[v].value() == 1:
        return f"t"

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
    pos = nx.get_node_attributes(H, "pos")
    node_labels = nx.get_node_attributes(H, "node_labels")
    edge_labels = nx.get_edge_attributes(H, "edge_labels")

    n = H.graph["n"]
    m = H.graph["m"]
    factor = 0.75
    size = (n * factor, m * factor)

    plt.figure(2, figsize=size, dpi=200)
    plt.axis("off")

    # Draw the graph
    nx.draw_networkx(
        H,
        pos=pos,
        labels=node_labels,
        with_labels=True,
        node_size=50,
        font_size=7,
    )
    nx.draw_networkx_edge_labels(
        H,
        pos=pos,
        edge_labels=edge_labels,
        font_size=7,
    )

    path = os.path.join(output_dir, "solution_graph.png")

    # Save it to an image
    plt.savefig(path, format="PNG", bbox_inches="tight")
    plt.close()
