import pulp
from output import doc_from_solution, string_from_solution
from contants import *

# - VARIABLES ----------------------------------------------------

v = {}
for x, y in V:
    for e in E:
        # Use entity e for node (x, y)?
        v[x, y, e] = pulp.LpVariable(f"v[{x},{y},{e}]", cat="Binary")

a = {}
for x1, y1, x2, y2 in A:
    # Use arc (x1, y1) => (x2, y2)?
    a[x1, y1, x2, y2] = pulp.LpVariable(
        f"a[{x1},{y1},{x2},{y2}]", cat="Binary")

# - MODEL --------------------------------------------------------

model = pulp.LpProblem("facotizer", pulp.LpMinimize)

# Minimize cost
model += pulp.lpSum(v[x, y, e] * C[e] for x, y in V for e in E)

# - CONSTRAINTS --------------------------------------------------

# for x in range(1, X_COUNT - 1):
#     model += a[x, 3, x + 1, 3] == 1

for x, y in V:
    # Place inputs and outputs
    if (x, y) in I:
        model += v[x, y, "I"] == 1
    else:
        model += v[x, y, "I"] == 0
    if (x, y) in O:
        model += v[x, y, "O"] == 1
    else:
        model += v[x, y, "O"] == 0

for y in Y:
    # Leave input and output space free of entities
    for e in E:
        if e != "I":
            model += v[0, y, e] == 0
    for e in E:
        if e != "O":
            model += v[X_COUNT + 1, y, e] == 0

for x, y in V:
    # Each node can have at most one entity
    model += pulp.lpSum(v[x, y, e] for e in E) <= 1

for x, y in V:
    # An arc must enter each entity
    model += pulp.lpSum(a[x, y, x2, y2] for x2, y2 in reachable(x, y)
                        ) == pulp.lpSum(v[x, y, e] for e in E if e not in ["O", "S", "T"])
    # An arc must leave each entity
    model += pulp.lpSum(a[x1, y1, x, y] for x1, y1 in reachable(x, y)
                        ) == pulp.lpSum(v[x, y, e] for e in E if e not in ["I", "S", "T"])

for x, y in V:
    for x2, y2 in underground_reachable(x, y):
        # Only underground belts can use long arcs
        model += a[x, y, x2, y2] <= v[x, y, "U"]

for x, y in V:
    for x2, y2 in reachable(x, y):
        # Exit from underground belts
        model += v[x, y, "U"] + a[x, y, x2, y2] <= 1 + v[x2, y2, "V"]

for x1, y1, x2, y2 in A:
    # Only go in one direction
    model += pulp.lpSum(a[x1, y1, x2, y2] + a[x2, y2, x1, y1]) <= 1

for x, y in V:
    for e in ["U", "V"]:
        # Do not bend underground belts
        model += pulp.lpSum(a[x, y, x2, y2] for x2, y2 in reachable_horz(x, y)) + (1 - v[x, y, e]) >= pulp.lpSum(a[x1, y1, x, y] for x1, y1 in reachable_horz(x, y))
        model += pulp.lpSum(a[x, y, x2, y2] for x2, y2 in reachable_vert(x, y)) + (1 - v[x, y, e]) >= pulp.lpSum(a[x1, y1, x, y] for x1, y1 in reachable_vert(x, y))

for x, y in V:
    # Connect splitter segments
    if y - 1 in Y:
        model += v[x, y, "S"] == v[x, y - 1, "T"]
        model += a[x, y, x, y - 1] >= v[x, y, "S"]
    else:
        model += v[x, y, "S"] == 0
    if y + 1 in Y:
        model += v[x, y, "T"] == v[x, y + 1, "S"]
        model += a[x, y, x, y + 1] >= v[x, y, "T"]
    else:
        model += v[x, y, "T"] == 0

# Use a splitter
# model += pulp.lpSum(v[x, y, "S"] for x, y in V) >= 1

# - SOLVE MODEL --------------------------------------------------

model.solve()

# - OUTPUT -------------------------------------------------------

print("Solution:\n")

if model.status != 1:
    print("INFEASABLE!")
else:
    nodes = []
    for x, y in V:
        for e in E:
            if v[x, y, e].value() == 1:
                nodes.append((x, y, e))

    arcs = []
    for x1, y1, x2, y2 in A:
        if a[x1, y1, x2, y2].value() == 1:
            arcs.append((x1, y1, x2, y2))

    print(string_from_solution(nodes))
    doc_from_solution(nodes, arcs)
