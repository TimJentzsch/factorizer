import networkx as nx


def dir_out_edge(G: nx.DiGraph, v, d: str, r: int):
    edges = [
        a
        for a in G.out_edges(v)
        if G.edges[a]["d"] == d and G.edges[a]["r"] == r and not G.edges[a]["split"]
    ]

    return edges[0] if len(edges) > 0 else None


def splitter_out_edge(G: nx.DiGraph, v, f: str):
    edge_d = "up" if f == "right" else "down"
    edges = [
        a for a in G.out_edges(v) if G.edges[a]["d"] == edge_d and G.edges[a]["split"]
    ]

    return edges[0] if len(edges) > 0 else None
