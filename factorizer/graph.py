from typing import List

import networkx as nx


def build_graph(n: int, m: int, B: List[int], E: List[int], R: range) -> nx.DiGraph:
    """Build the graph for the given instance.

    Args:
        n: The width of the grid.
        m: The height of the grid.
        B: The list of start indexes.
        E: The list of end indexes.
        R: Ranges of the belts.
    """
    G = nx.DiGraph()

    # --- NODES ---

    # Add a node for each tile in the grid
    G.add_nodes_from(
        ((x, y) for x in range(n) for y in range(m)),
        grid=True,
    )

    # Add a node for each starting point
    G.add_nodes_from(
        ((-1, b) for b in B),
        grid=False, start=True, end=False,
    )

    # Add a node for each end point
    G.add_nodes_from(
        ((n, e) for e in E),
        grid=False, start=False, end=True,
    )

    # --- EDGES ---

    for r in R:
        is_transport_belt = r == 1
        # Add edges going right
        G.add_edges_from(
            (((x, y), (x + r, y)) for x in range(n - r) for y in range(m)),
            grid=True,
            d="right",
            transport=is_transport_belt,
        )

        # Add edges going left
        G.add_edges_from(
            (((x, y), (x - r, y)) for x in range(r, n) for y in range(m)),
            grid=True,
            d="left",
            transport=is_transport_belt,
        )

        # Add up edges
        G.add_edges_from(
            (((x, y), (x, y + r)) for x in range(n) for y in range(m - r)),
            grid=True,
            d="up",
            transport=is_transport_belt,
        )

        # Add down edges
        G.add_edges_from(
            (((x, y), (x, y - r)) for x in range(n) for y in range(r, m)),
            grid=True,
            d="down",
            transport=is_transport_belt,
        )

    # FIXME: Add splitter edges

    # Start edges
    G.add_edges_from(
        (((-1, b), (0, b)) for b in B),
        grid=False,
        d="right",
        transport=True,
        start=True,
        end=False,
    )

    # End edges
    G.add_edges_from(
        (((n - 1, e), (n, e)) for e in E),
        grid=False,
        d="right",
        transport=True,
        start=False,
        end=True,
    )

    return G
