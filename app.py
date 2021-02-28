import pulp
from output import doc_from_solution, string_from_solution
from contants import *

# - VARIABLES ----------------------------------------------------

v = {}
for x, y in V:
    for e in E:
        for d in D:
            # Use entity e for node (x, y) with direction d?
            v[x, y, e, d] = pulp.LpVariable(f"v[{x},{y},{e},{d}]", cat="Binary")

a = {}
for x1, y1, x2, y2 in A:
    # Use arc (x1, y1) => (x2, y2)?
    a[x1, y1, x2, y2] = pulp.LpVariable(
        f"a[{x1},{y1},{x2},{y2}]", cat="Binary")

# - MODEL --------------------------------------------------------

model = pulp.LpProblem("facotizer", pulp.LpMinimize)

# Minimize cost
model += pulp.lpSum(v[x, y, e, d] * C[e] for x, y in V for e in E for d in D)

# - CONSTRAINTS --------------------------------------------------

# - I/O ---

for x, y in V:
    # Place inputs and outputs
    if (x, y) in I:
        model += v[x, y, "I", "E"] == 1
    else:
        model += v[x, y, "I", "E"] == 0
    if (x, y) in O:
        model += v[x, y, "O", "E"] == 1
    else:
        model += v[x, y, "O", "E"] == 0

for y in Y:
    # Leave input and output space free of entities
    for e in E:
        if e != "I":
            for d in D:
                model += v[0, y, e, d] == 0
    for e in E:
        if e != "O":
            for d in D:
                model += v[X_COUNT + 1, y, e, d] == 0

for x, y in I:
    # Leave input nodes
    model += pulp.lpSum(a[x, y, x2, y2] for x2, y2 in reachable(x, y)) == 1
for x, y in O:
    # Enter output nodes
    model += pulp.lpSum(a[x1, y1, x, y]
                        for x1, y1 in reachable(x, y)) == 1

# - GENERAL ---

for x, y in V:
    # Each node can have at most one entity
    model += pulp.lpSum(v[x, y, e, d] for e in E for d in D) <= 1

for x1, y1, x2, y2 in A:
    # An arc must come from an entity
    model += a[x1, y1, x2, y2] <= pulp.lpSum(v[x1, y1, e, d] for e in E for d in D)
    # An arc must go to an entity
    model += a[x1, y1, x2, y2] <= pulp.lpSum(v[x2, y2, e, d] for e in E for d in D)

for x, y in V:
    if (x, y) not in I:
        # If an arc leaves an entity, one must enter it
        model += pulp.lpSum(a[x1, y1, x, y] for x1, y1 in reachable(x, y)) >= pulp.lpSum(a[x, y, x2, y2] for x2, y2 in reachable(x, y)) / len(reachable(x, y))

for x1, y1, x2, y2 in A:
    # Only go in one direction
    model += pulp.lpSum(a[x1, y1, x2, y2] + a[x2, y2, x1, y1]) <= 1

# - BELTS ---

for x, y in V:
    # Only one arc can enter an entity
    model += pulp.lpSum(a[x1, y1, x, y] for x1, y1 in reachable(x, y)) <= 1
    # Only one arc can leave an entity
    model += pulp.lpSum(a[x, y, x2, y2] for x2, y2 in reachable(x, y)) <= 1

# - UNDERGROUND BELTS ---

for x, y in V:
    for x2, y2 in underground_reachable(x, y):
        # Only underground belts can use long arcs
        model += a[x, y, x2, y2] <= pulp.lpSum(v[x, y, "U", d] for d in D)

for x, y in V:
    for x2, y2 in reachable(x, y):
        for d in D:
            # Exit from underground belts
            model += v[x, y, "U", d] + a[x, y, x2, y2] <= 1 + v[x2, y2, "V", d]

# - SPLITTERS ---

for x, y in V:
    for e in ["S", "T", "I", "O"]:
        for d in ["N", "S", "W"]:
            # Only allow splitters and I/O in one direction (for now)
            model += v[x, y, e, d] == 0
            model += v[x, y, e, d] == 0

for x, y in V:
    # Connect splitter segments
    if y - 1 in Y:
        model += v[x, y, "S", "E"] == v[x, y - 1, "T", "E"]
    else:
        model += v[x, y, "S", "E"] == 0
    if y + 1 in Y:
        model += v[x, y, "T", "E"] == v[x, y + 1, "S", "E"]
    else:
        model += v[x, y, "T", "E"] == 0

for x, y in V:
    # Enter each splitter
    if x - 1 in X and y - 1 in Y:
        model += v[x, y, "S", "E"] <= a[x - 1, y, x, y]


# Use a splitter
model += pulp.lpSum(v[x, y, "S", "E"] for x, y in V) >= 1

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

    print("\nGenerating document...")
    doc_from_solution(nodes, arcs)
    print("Done.")
