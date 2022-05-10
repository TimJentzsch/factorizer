from factorizer.graph import build_graph


def test_build_graph() -> None:
    """Verify that the graph is built properly."""
    n, m = 3, 3
    B = [1]
    E = [1, 2]
    R = range(1, 3)

    G = build_graph(n, m, B, E, R)

    # Standard grid nodes
    for v in [(0, 0), (2, 2), (1, 2)]:
        assert v in G.nodes
        assert G.nodes[v]["grid"] is True

    # Start nodes
    for v in [(-1, 1)]:
        assert v in G.nodes
        assert G.nodes[v]["grid"] is False
        assert G.nodes[v]["start"] is True
        assert G.nodes[v]["end"] is False

    # End nodes
    for v in [(3, 1), (3, 2)]:
        assert v in G.nodes
        assert G.nodes[v]["grid"] is False
        assert G.nodes[v]["start"] is False
        assert G.nodes[v]["end"] is True
