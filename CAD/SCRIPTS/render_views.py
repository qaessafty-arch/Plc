#!/usr/bin/env python3
"""Hidden-line isometric views of the assembly and the exploded arrangement.

Run after build_cad.py:  python3 CAD/SCRIPTS/render_views.py
Outputs CAD/ASSEMBLY/SPM-420_isometric.(png|pdf) and CAD/EXPLODED/SPM-420_exploded.(png|pdf),
each from the front-left and the rear-right.
"""
import math, os, sys
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", ".."))
import machine_params as P
import build_cad as B
from build_drawings import project, draw, title_block

CAD = os.path.join(HERE, "..")


def view(az_deg, el_deg):
    """Viewer direction (object -> eye) and screen-x axis for an azimuth measured from -Y."""
    a, e = math.radians(az_deg), math.radians(el_deg)
    n = (math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))
    x = (math.cos(a), math.sin(a), 0.0)          # horizontal, so +Z stays up on the sheet
    return n, x


def sheet(comp, title, number, out):
    fig = plt.figure(figsize=(16.5, 9.5))
    for k, (az, lab) in enumerate(((-35, "from front-left (operator side)"), (145, "from rear-right (film and cabinet side)"))):
        ax = fig.add_axes([0.01 + 0.495 * k, 0.05, 0.485, 0.88])
        draw(ax, project(comp, *view(az, 25)), 0.45)
        ax.set_title(lab, fontsize=9)
    fig.text(0.5, 0.965, f"{P.MACHINE_NAME}  {title}", ha="center", fontsize=12, weight="bold")
    title_block(fig, number, title, "hidden-line isometric, not to scale")
    fig.savefig(out + ".png", dpi=140); fig.savefig(out + ".pdf"); plt.close(fig)
    print("wrote", out + ".png")


if __name__ == "__main__":
    shapes = {n: fn().val() for n, (fn, *_r) in B.PARTS.items()}
    sheet(cq.Compound.makeCompound(list(shapes.values())), "assembly", "GA-003", os.path.join(CAD, "ASSEMBLY", "SPM-420_isometric"))
    moved = [s.moved(cq.Location(cq.Vector(*B.EXPLODE[B.PARTS[n][2]]))) for n, s in shapes.items()]
    sheet(cq.Compound.makeCompound(moved), "exploded view", "GA-004", os.path.join(CAD, "EXPLODED", "SPM-420_exploded"))
