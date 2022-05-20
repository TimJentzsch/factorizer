from typing import List

import networkx as nx


def build_graph(n: int, m: int, B: List[int], E: List[int], R: int) -> nx.DiGraph:
    """Build the graph for the given instance.

    Args:
        n: The width of the grid.
        m: The height of the grid.
        B: The list of start indexes.
        E: The list of end indexes.
        R: Maximum range of underground belts.
    """
    name = f"{len(B)}x{len(E)}-balancer_{n}x{m}-grid"
    print(f"Gname {name}")
    G = nx.DiGraph(name=name, n=n, m=m, R=R, B=B, E=E)

    # --- NODES ---

    # Add a node for each tile in the grid
    G.add_nodes_from(
        ((x, y) for x in range(n) for y in range(m)),
        grid=True,
    )

    # Add a node for each starting point
    G.add_nodes_from(
        ((-1, b) for b in B),
        grid=False,
        split=False,
        start=True,
        end=False,
    )

    # Add a node for each end point
    G.add_nodes_from(
        ((n, e) for e in E),
        grid=False,
        split=False,
        start=False,
        end=True,
    )

    # --- EDGES ---

    for r in range(1, R + 1):
        # Add edges going right
        G.add_edges_from(
            (((x, y), (x + r, y)) for x in range(n - r) for y in range(m)),
            grid=True,
            split=False,
            d="right",
            r=r,
        )

        # Add edges going left
        G.add_edges_from(
            (((x, y), (x - r, y)) for x in range(r, n) for y in range(m)),
            grid=True,
            split=False,
            d="left",
            r=r,
        )

        # Add up edges
        G.add_edges_from(
            (((x, y), (x, y + r)) for x in range(n) for y in range(m - r)),
            grid=True,
            split=False,
            d="up",
            r=r,
        )

        # Add down edges
        G.add_edges_from(
            (((x, y), (x, y - r)) for x in range(n) for y in range(r, m)),
            grid=True,
            split=False,
            d="down",
            r=r,
        )

    # Splitter edges
    for x in range(n - 1):
        for y in range(m):
            if y < m - 1:
                G.add_edge(
                    (x, y),
                    (x + 1, y + 1),
                    grid=True,
                    split=True,
                    d="up",
                    r=1,
                )

            if y > 0:
                G.add_edge(
                    (x, y),
                    (x + 1, y - 1),
                    grid=True,
                    split=True,
                    d="down",
                    r=1,
                )

    # Start edges
    G.add_edges_from(
        (((-1, b), (0, b)) for b in B),
        grid=False,
        split=False,
        d="right",
        r=1,
        start=True,
        end=False,
    )

    # End edges
    G.add_edges_from(
        (((n - 1, e), (n, e)) for e in E),
        grid=False,
        split=False,
        d="right",
        r=1,
        start=False,
        end=True,
    )

    return G
