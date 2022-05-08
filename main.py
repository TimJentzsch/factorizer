from datetime import datetime

from factorizer.graph import build_graph
from factorizer.problem import build_problem

# Maximum range of underground belts
R = 5

# Material costs for basic belts
c = {
    "transport": 3,
    # The end piece is modeled as a transport belt, we have to subtract that
    "underground": 17.5 - 3,
    # There are 2 fragments, each one should have half the cost
    "splitter": (7.5 + 16) / 2,
}

if __name__ == '__main__':
    n = 15
    m = 10

    B = [4, 5]
    E = [4, 5]

    print("Building graph...")
    start = datetime.now()

    G = build_graph(n, m, B, E, R)

    end_graph = datetime.now()
    dur_graph = (end_graph - start).total_seconds()
    print(f"Built graph ({dur_graph:.2f}s).")

    print("Building problem...")

    problem = build_problem(G, c)

    end_problem = datetime.now()
    dur_problem = (end_problem - end_graph).total_seconds()
    print(f"Built problem ({dur_problem:.2f}s).")
