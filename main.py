import argparse
import math
import os.path
from datetime import datetime
from typing import List

import networkx as nx

from factorizer.graph import build_graph
from factorizer.problem import build_problem

# Maximum range of underground belts
from factorizer.visualization.graph import build_solution_graph, save_solution_graph

R = 5

# Material costs for basic belts
c = {
    "transport": 3,
    # The end piece is modeled as a transport belt, we have to subtract that
    "underground": 17.5 - 3,
    # There are 2 fragments, each one should have half the cost
    "splitter": (7.5 + 16) / 2,
}


def _centered_tiles(grid_height: int, belt_height: int) -> List[int]:
    edge_room = math.floor((grid_height - belt_height) / 2.0)

    return [i for i in range(edge_room, edge_room + belt_height)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Factorio belt balancer")

    parser.add_argument("-b", "--balancer", default="4x4",
                        help="The size of the balanced belts. nxm means n input belts and m output belts.")
    parser.add_argument("-g", "--grid", default="10x4",
                        help="The size of the grid. nxm means a grid n tiles wide and m tiles high.")

    args = parser.parse_args()

    belt_size = args.balancer.split("x")
    belt_n = int(belt_size[0])
    belt_m = int(belt_size[1])

    grid_size = args.grid.split("x")
    grid_n = int(grid_size[0])
    grid_m = int(grid_size[1])

    edge_room_left = (grid_m - belt_m) / 2.0

    B = _centered_tiles(grid_m, belt_n)
    E = _centered_tiles(grid_m, belt_m)

    print("Building graph...")
    start = datetime.now()

    G = build_graph(grid_n, grid_m, B, E, R)

    end_graph = datetime.now()
    dur_graph = (end_graph - start).total_seconds()
    print(f"Built graph ({dur_graph:.2f}s).")

    name = G.graph["name"]
    output_dir = os.path.join("output", name)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Building problem...")

    problem, t, u, s, x, y = build_problem(G, c)

    end_problem = datetime.now()
    dur_problem = (end_problem - end_graph).total_seconds()
    print(f"Built problem ({dur_problem:.2f}s).")

    problem.solve()

    H = build_solution_graph(G, t, u, s, x, y)
    save_solution_graph(H, output_dir)
