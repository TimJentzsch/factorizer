from pylatex import (Document, Command, TikZ, TikZNode,
                     TikZDraw, TikZCoordinate,
                     TikZUserPath, TikZOptions)
from pylatex.utils import NoEscape
from pathlib import Path
from contants import *


def doc_from_solution(nodes, arcs):
    doc = Document('factorizer')

    doc.preamble.append(Command("usepackage", "geometry", [
        "a4paper", "left=2cm", "right=2cm", "top=1cm", "bottom=3cm"]))
    doc.preamble.append(Command("usepackage", "mathabx"))
    doc.preamble.append(Command('title', 'Factorizer'))
    doc.preamble.append(Command('author', 'Tim Jentzsch'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))

    with doc.create(TikZ()) as graph:
        # options for our node
        node_kwargs = {
            'minimum size': '0.7cm'
        }

        node_objs = {}
        for (x, y, e) in nodes:
            node = TikZNode(text=e,
                            handle=f"x{x}y{y}",
                            at=TikZCoordinate(x, y),
                            options=TikZOptions(** node_kwargs))

            # add to tikzpicture
            graph.append(node)
            node_objs[x, y] = node

        for x1, y1, x2, y2 in arcs:
            path = TikZDraw([node_objs[x1, y1], 'edge',
                             node_objs[x2, y2]], options=TikZOptions('->'))
            graph.append(path)

    path = Path(r"output/output.tex")
    path.touch()
    path.write_text(doc.dumps())
    doc.generate_pdf(r'output/output', clean_tex=False)


def string_from_solution(nodes):
    output = ""
    x_numbers = "    "
    for x in X:
        x_numbers += f"{x} "
    x_line = "    "
    for x in X:
        x_line += "--"

    output += f"{x_numbers}\n{x_line}\n"

    for y in reversed(Y):
        line = f"{y} | "
        for x in X:
            hasEntity = False
            for e in E:
                if (x, y, e) in nodes:
                    hasEntity = True
                    line += f"{e} "
            if not hasEntity:
                line += "  "

        output += f"{line} | {y}\n"

    output += f"{x_line}\n{x_numbers}"

    return output
