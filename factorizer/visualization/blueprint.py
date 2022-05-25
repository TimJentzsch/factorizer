"""See <https://wiki.factorio.com/Blueprint_string_format#Position_object>."""
import base64
import json
import zlib
from typing import Dict, Optional, Tuple

import networkx as nx

from factorizer import D
from factorizer.utils import dir_out_edge, dir_in_edge


def parse_blueprint(blueprint: str) -> Dict:
    """Parse a blueprint string."""
    # Remove the version byte at the start
    blueprint = blueprint[1:]
    # Decode the base64 string
    decoded = base64.b64decode(blueprint.encode("ascii"))
    # Decompress the JSON string
    decompressed = zlib.decompress(decoded).decode()
    # Parse the JSON string to get the data
    return json.loads(decompressed)


def construct_blueprint_data(G: nx.DiGraph, t, u, s, x, y) -> Dict:
    """Construct the blueprint data from a given solution."""
    entities = []
    entity_number = 1

    for v in G.nodes:
        if G.nodes[v]["grid"]:
            if entity := get_entity_at_node(v, G, t, u, s, x, y):
                entities.append(
                    {
                        "entity_number": entity_number,
                        **entity,
                    }
                )
                entity_number += 1

    return {
        "blueprint": {
            "label": G.graph["name"],
            "entities": entities,
            "version": 64424706048,
        }
    }


def convert_to_blueprint(G: nx.DiGraph, t, u, s, x, y) -> str:
    """Convert the given solution to a blueprint string."""
    # Convert the solution to blueprint data
    data = construct_blueprint_data(G, t, u, s, x, y)
    # Convert the blueprint data to JSON
    json_str = json.dumps(data).encode("utf-8")
    # Compress the JSON string with zlib
    compressed = zlib.compress(bytes(json_str), level=9)
    # Encode the compressed JSON in base64
    encoded = base64.b64encode(compressed).decode()
    # Add the 0 version byte at the start
    return "0" + encoded


def get_entity_at_node(v: Tuple, G: nx.DiGraph, t, u, s, x, y) -> Optional[Dict]:
    """Get the Factorio entity at the given node."""
    R_u = G.graph["R_u"]
    (x_coord, y_coord) = v

    # Transport belt
    if t[v].value() == 1:
        for d in D:
            if out_edge := dir_out_edge(G, v, d):
                if y[out_edge] == 1:
                    # Check if this is the output of an underground belt
                    for r in R_u:
                        if in_edge := dir_in_edge(G, v, d, r):
                            (u_pos, _) = in_edge

                            if u[u_pos, d, r].value() == 1:
                                return {
                                    "name": "underground-belt",
                                    "type": "output",
                                    "position": {
                                        "x": x_coord,
                                        "y": y_coord,
                                    },
                                    "direction": direction_to_index(d),
                                }

                    # It's a normal transport belt
                    return {
                        "name": "transport-belt",
                        "position": {
                            "x": x_coord,
                            "y": y_coord,
                        },
                        "direction": direction_to_index(d),
                    }

    # Underground belt (input)
    for d in D:
        for r in R_u:
            if u[v, d, r].value() == 1:
                return {
                    "name": "underground-belt",
                    "type": "input",
                    "position": {
                        "x": x_coord,
                        "y": y_coord,
                    },
                    "direction": direction_to_index(d),
                }

    # Splitter
    if s[v, "left"].value() == 1:
        return {
            "name": "splitter",
            "position": {
                "x": x_coord,
                "y": y_coord - 0.5,
            },
            "direction": direction_to_index("right"),
        }


def direction_to_index(d: str) -> int:
    """Convert a direction to the corresponding index in Factorio."""
    if d == "up":
        return 0
    if d == "right":
        return 2
    if d == "down":
        return 4
    if d == "left":
        return 6
