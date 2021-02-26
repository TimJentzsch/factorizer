X_COUNT = 5
Y_COUNT = 5

X = range(0, X_COUNT + 2)
Y = range(1, Y_COUNT + 1)

def reachable(x1, y1):
    "The nodes reachable from the given node"
    leaving = []
    for u in range(1, 4 + 1):
        leaving.append((x1, y1 - u))
        leaving.append((x1, y1 + u))
        leaving.append((x1 - u, y1))
        leaving.append((x1 + u, y1))
    return [(x2, y2) for x2, y2 in leaving if x2 in X and y2 in Y]


def reachable_vert(x1, y1):
    leaving = []
    for u in range(1, 4 + 1):
        leaving.append((x1, y1 - u))
        leaving.append((x1, y1 + u))
    return [(x2, y2) for x2, y2 in leaving if x2 in X and y2 in Y]


def reachable_horz(x1, y1):
    leaving = []
    for u in range(1, 4 + 1):
        leaving.append((x1 - u, y1))
        leaving.append((x1 + u, y1))
    return [(x2, y2) for x2, y2 in leaving if x2 in X and y2 in Y]

def underground_reachable(x1, y1):
    "The nodes reachable from the given node only by an underground belt"
    leaving = []
    for u in range(2, 4 + 1):
        leaving.append((x1, y1 - u))
        leaving.append((x1, y1 + u))
        leaving.append((x1 - u, y1))
        leaving.append((x1 + u, y1))
    return [(x2, y2) for x2, y2 in leaving if x2 in X and y2 in Y]


print(underground_reachable(3, 3))

# Nodes
V = [(x, y) for x in X for y in Y]


# Arcs
A = [(x1, y1, x2, y2) for x1, y1 in V for x2, y2 in reachable(x1, y1)]

# Node entities
#   I = Input
#   O = Output
#   B = Transport Belt
#   U = Underground Belt Entry
#   V = Underground Belt Exit
#   S = Splitter Right
#   T = Splitter Left
E = ["I", "O", "B", "U", "V", "S", "T"]

# Node costs
C = {
    "I": 0,
    "O": 0,
    "B": 3,
    "U": 17.5,
    "V": 17.5,
    "S": 16.75,
    "T": 16.75,
}

# Inputs
INPUTS = [1, 3]
I = [(0, y) for y in INPUTS]

# Outputs
OUTPUTS = [3, 5]
O = [(X_COUNT + 1, y) for y in OUTPUTS]
