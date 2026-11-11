#!/usr/bin/env python3
"""2D drawings from the 3D model (hidden-line projection + dimensions).

Run after build_cad.py:  python3 CAD/SCRIPTS/build_drawings.py
Outputs in CAD/DRAWINGS:
  GA-001_general_arrangement.pdf/.png/.dxf   top, front, side with overall dims
  GA-002_floor_layout.pdf/.png/.dxf          plan with access / clearance zones
  CD-000_component_drawings.pdf              one sheet per component, 3 views + envelope dims
  components/<part>.dxf                      the same views as DXF
All sheets carry the status PRELIMINARY - NOT FOR MANUFACTURE.
"""
import json, os, sys
import cadquery as cq
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import machine_params as P
import build_cad as B

OUT = os.path.join(ROOT, "CAD", "DRAWINGS")
os.makedirs(os.path.join(OUT, "components"), exist_ok=True)
VIEWS = {"TOP": ((0, 0, 1), (1, 0, 0)), "FRONT": ((0, -1, 0), (1, 0, 0)), "SIDE (from right)": ((1, 0, 0), (0, 1, 0))}
STATUS = "PRELIMINARY - NOT FOR MANUFACTURE"


def project(shape, normal, xdir):
    hlr = HLRBRep_Algo()
    hlr.Add(shape.wrapped)
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*normal), gp_Dir(*xdir))))
    hlr.Update(); hlr.Hide()
    hs = HLRBRep_HLRToShape(hlr)
    lines = []
    for comp in (hs.VCompound(), hs.OutLineVCompound(), hs.Rg1LineVCompound()):
        if comp is None or comp.IsNull():
            continue
        BRepLib.BuildCurves3d_s(comp)
        for e in cq.Shape.cast(comp).Edges():
            n = 2 if e.geomType() == "LINE" else 16
            pts = [e.positionAt(i / (n - 1)) for i in range(n)]
            lines.append([(q.x, q.y) for q in pts])
    return lines


def bounds(lines):
    xs = [x for l in lines for x, _ in l]; ys = [y for l in lines for _, y in l]
    return min(xs), max(xs), min(ys), max(ys)


def dim_h(ax, x0, x1, y, txt=None, off=0):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=0.6, color="tab:blue"))
    ax.plot([x0, x0], [y - 40, y + 40], lw=0.4, color="tab:blue"); ax.plot([x1, x1], [y - 40, y + 40], lw=0.4, color="tab:blue")
    ax.text((x0 + x1) / 2, y + 25 + off, txt or f"{abs(x1 - x0):.0f}", ha="center", va="bottom", fontsize=6, color="tab:blue")


def dim_v(ax, y0, y1, x, txt=None):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", lw=0.6, color="tab:blue"))
    ax.plot([x - 40, x + 40], [y0, y0], lw=0.4, color="tab:blue"); ax.plot([x - 40, x + 40], [y1, y1], lw=0.4, color="tab:blue")
    ax.text(x - 25, (y0 + y1) / 2, txt or f"{abs(y1 - y0):.0f}", ha="right", va="center", fontsize=6, color="tab:blue", rotation=90)


def draw(ax, lines, lw=0.35):
    for l in lines:
        ax.plot([q[0] for q in l], [q[1] for q in l], lw=lw, color="k")
    ax.set_aspect("equal"); ax.axis("off")


def title_block(fig, number, title, extra=""):
    fig.text(0.99, 0.012, f"{P.MACHINE_NAME}  |  {number}  |  {title}  |  rev {P.REVISION}  |  units mm  |  {extra}",
             ha="right", fontsize=6.5, family="monospace")
    fig.text(0.01, 0.012, STATUS, ha="left", fontsize=7, color="red", weight="bold")


def dxf_new():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    for n, c in (("OUTLINE", 7), ("DIM", 5), ("ZONE", 3), ("TEXT", 2)):
        doc.layers.add(n, color=c)
    return doc, doc.modelspace()


def dxf_lines(msp, lines, ox=0, oy=0):
    for l in lines:
        msp.add_lwpolyline([(x + ox, y + oy) for x, y in l], dxfattribs={"layer": "OUTLINE"})


def dxf_dim(msp, p1, p2, base, angle=0):
    msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle="EZDXF",
                       override={"dimtxt": 40, "dimasz": 40, "dimexo": 15, "dimexe": 15, "dimdec": 0},
                       dxfattribs={"layer": "DIM"}).render()


def main():
    shapes = {n: fn().val() for n, (fn, *_r) in B.PARTS.items()}
    comp = cq.Compound.makeCompound(list(shapes.values()))
    proj = {v: project(comp, *VIEWS[v]) for v in VIEWS}
    man = json.load(open(os.path.join(ROOT, "CAD", "COMPONENTS", "manifest.json")))

    # ---------------- GA-001
    fig = plt.figure(figsize=(16.5, 11.7))
    axt = fig.add_axes([0.03, 0.52, 0.55, 0.45]); axf = fig.add_axes([0.03, 0.04, 0.55, 0.47]); axs = fig.add_axes([0.60, 0.04, 0.38, 0.47])
    doc, msp = dxf_new()
    offs = {"TOP": (0, 5200), "FRONT": (0, 0), "SIDE (from right)": (6500, 0)}
    for ax, v in ((axt, "TOP"), (axf, "FRONT"), (axs, "SIDE (from right)")):
        draw(ax, proj[v]); x0, x1, y0, y1 = bounds(proj[v])
        ax.set_title(v + " VIEW", fontsize=8, loc="left")
        dim_h(ax, x0, x1, y0 - 220); dim_v(ax, y0, y1, x0 - 220)
        ox, oy = offs[v]; dxf_lines(msp, proj[v], ox, oy)
        dxf_dim(msp, (x0 + ox, y0 + oy), (x1 + ox, y0 + oy), (ox, y0 + oy - 300))
        dxf_dim(msp, (x0 + ox, y0 + oy), (x0 + ox, y1 + oy), (x0 + ox - 300, oy), angle=90)
        msp.add_text(v + " VIEW", height=80, dxfattribs={"layer": "TEXT"}).set_placement((x0 + ox, y1 + oy + 150))
        if v == "FRONT":
            for z, lab in ((P.JAW_Z, "jaw plane"), (P.BAGGER_H, "bagger frame top"), (P.FUNNEL_TOP_Z, "funnel top"),
                           (P.PLATFORM_Z, "platform deck"), (P.PLATFORM_Z + P.HANDRAIL_H, "handrail"),
                           (P.WEIGHER_BASE_Z + P.WEIGHER_HEIGHT, "weigher infeed")):
                ax.plot([x1 + 60, x1 + 420], [z, z], lw=0.4, color="tab:blue")
                ax.text(x1 + 440, z, f"+{z}  {lab}", fontsize=5.5, va="center", color="tab:blue")
                msp.add_text(f"+{z} {lab}", height=45, dxfattribs={"layer": "DIM"}).set_placement((x1 + 100 + ox, z + oy))
            dim_h(ax, -P.BAGGER_W / 2, P.BAGGER_W / 2, 1560, f"bagger {P.BAGGER_W}")
            dim_h(ax, P.ELEV_INFEED_X, 0, y0 - 480, f"infeed to tube axis {-P.ELEV_INFEED_X}")
            dim_h(ax, 0, x1, y0 - 480, f"axis to discharge end {x1:.0f}")
        if v == "TOP":
            dim_h(ax, -P.PLATFORM_SIZE / 2, P.PLATFORM_SIZE / 2, y1 + 150, f"platform {P.PLATFORM_SIZE} sq.")
            dim_v(ax, P.BAGGER_FRONT_Y, P.BAGGER_FRONT_Y + P.BAGGER_D, P.BAGGER_W / 2 + 500, f"bagger {P.BAGGER_D}")
            ax.plot(0, 0, "+", color="red", ms=10); ax.text(30, 30, "datum: forming-tube axis", fontsize=5.5, color="red")
        if v.startswith("SIDE"):
            dim_h(ax, P.BAGGER_FRONT_Y, P.BAGGER_FRONT_Y + P.BAGGER_D, 1560, f"bagger {P.BAGGER_D}")
    ax = fig.add_axes([0.60, 0.55, 0.38, 0.42]); ax.axis("off")
    env = man["_assembly"]
    txt = [f"GENERAL ARRANGEMENT - {P.MACHINE_NAME} snack filling & packaging line", "",
           f"Overall (CAD bounding box): L {env['bbox_mm'][0]} x W {env['bbox_mm'][1]} x H {env['bbox_mm'][2]} mm",
           f"Bagger frame: {P.BAGGER_W} x {P.BAGGER_D} x {P.BAGGER_H} (funnel top +{P.FUNNEL_TOP_Z})",
           f"Estimated dry mass (model, filled sections corrected): ~{env['est_mass_kg']} kg  [ASM]",
           f"Max film web {P.FILM_WIDTH_MAX}, roll OD {P.FILM_ROLL_OD_MAX}, core {P.FILM_CORE_ID}",
           f"Shown tooling: {P.PRODUCTS[P.REFERENCE_PRODUCT][0]}, tube OD {2 * B.TUBE_R:.1f}", "",
           "Items:  B = bagger   W = multihead weigher (10 head)", "        P = platform  E = Z-bucket elevator + hopper",
           "        C = take-off conveyor", "",
           "Weigher and elevator are shown as supplier ENVELOPES;", "replace with certified supplier drawings before release.",
           "Platform and bagger are structurally separate (vibration)."]
    ax.text(0, 1, "\n".join(txt), va="top", fontsize=7.5, family="monospace")
    title_block(fig, "GA-001", "General arrangement", "scale: fit")
    fig.savefig(os.path.join(OUT, "GA-001_general_arrangement.pdf")); fig.savefig(os.path.join(OUT, "GA-001_general_arrangement.png"), dpi=130)
    plt.close(fig); doc.saveas(os.path.join(OUT, "GA-001_general_arrangement.dxf"))

    # ---------------- GA-002 floor layout with zones
    fig, ax = plt.subplots(figsize=(16.5, 11.7)); doc, msp = dxf_new()
    draw(ax, proj["TOP"]); dxf_lines(msp, proj["TOP"])
    x0, x1, y0, y1 = bounds(proj["TOP"])
    front, rear, side = 1200, 1000, 800
    zones = [  # x, y, w, h, colour, label
        (x0 - side, y0 - front, x1 - x0 + 2 * side, y1 - y0 + front + rear, "none", "REQUIRED FLOOR AREA"),
        (-900, y0 - front, 1800, front, "tab:green", "operator working area (HMI, jaw doors) 1200"),
        (-600, y1, 1200, rear, "tab:orange", "film roll change / splice access 1000"),
        (x0 - side, -500, side + 900, 1000, "tab:purple", "product loading (hopper) 800"),
        (x1, -400, side, 800, "tab:cyan", "finished bag collection 800"),
        (P.BAGGER_W / 2 + P.CABINET[0], 250, 800, P.CABINET[1], "tab:red", "cabinet door swing 800"),
        (-P.PLATFORM_SIZE / 2 - 1200, 450, 1200, 500, "tab:brown", "platform stair (emergency egress)"),
    ]
    for zx, zy, zw, zh, col, lab in zones:
        ax.add_patch(Rectangle((zx, zy), zw, zh, fill=col != "none", alpha=0.18 if col != "none" else 1,
                               ec="k" if col == "none" else col, fc=col if col != "none" else "none", lw=1.0, ls="--"))
        ax.text(zx + 30, zy + zh - 40, lab, fontsize=6.5, va="top")
        msp.add_lwpolyline([(zx, zy), (zx + zw, zy), (zx + zw, zy + zh), (zx, zy + zh)], close=True, dxfattribs={"layer": "ZONE"})
        msp.add_text(lab, height=50, dxfattribs={"layer": "TEXT"}).set_placement((zx + 30, zy + zh - 90))
    fx0, fx1, fy0, fy1 = x0 - side, x1 + side, y0 - front, y1 + rear
    dim_h(ax, fx0, fx1, fy0 - 250); dim_v(ax, fy0, fy1, fx0 - 250); dim_h(ax, x0, x1, y1 + rear + 200); dim_v(ax, y0, y1, fx1 + 350)
    dxf_dim(msp, (fx0, fy0), (fx1, fy0), (0, fy0 - 350)); dxf_dim(msp, (fx0, fy0), (fx0, fy1), (fx0 - 350, 0), angle=90)
    ax.text(fx0, fy1 + 500, f"FLOOR LAYOUT   required area {fx1 - fx0:.0f} x {fy1 - fy0:.0f} mm = {(fx1 - fx0) * (fy1 - fy0) / 1e6:.1f} m2,"
            f"  min. clear ceiling {P.WEIGHER_BASE_Z + P.WEIGHER_HEIGHT + 1000} mm.  Emergency stops: HMI station, rear film side, platform, elevator infeed.",
            fontsize=8)
    for ex, ey in ((660, -420), (0, 1010), (700, -800 + 1700), (P.ELEV_INFEED_X + 200, -520)):
        ax.plot(ex, ey, "o", color="red", ms=7, mec="yellow", mew=1.5)
        msp.add_circle((ex, ey), 60, dxfattribs={"layer": "ZONE"})
    ax.set_xlim(fx0 - 500, fx1 + 600); ax.set_ylim(fy0 - 500, fy1 + 700)
    title_block(fig, "GA-002", "Floor layout and access zones", "red dots = E-stop devices")
    fig.savefig(os.path.join(OUT, "GA-002_floor_layout.pdf")); fig.savefig(os.path.join(OUT, "GA-002_floor_layout.png"), dpi=130)
    plt.close(fig); doc.saveas(os.path.join(OUT, "GA-002_floor_layout.dxf"))

    # ---------------- component sheets
    with PdfPages(os.path.join(OUT, "CD-000_component_drawings.pdf")) as pdf:
        for i, (name, shape) in enumerate(shapes.items(), 1):
            fig = plt.figure(figsize=(11.7, 8.3)); doc, msp = dxf_new(); ox = 0
            for k, v in enumerate(VIEWS):
                ax = fig.add_axes([0.03 + 0.32 * k, 0.12, 0.30, 0.74])
                lines = project(shape, *VIEWS[v]); draw(ax, lines, 0.5)
                bx0, bx1, by0, by1 = bounds(lines); m = 0.06 * max(bx1 - bx0, by1 - by0) + 5
                ax.set_title(v, fontsize=8)
                ax.annotate("", (bx0, by0 - m), (bx1, by0 - m), arrowprops=dict(arrowstyle="<->", lw=0.6, color="tab:blue"))
                ax.text((bx0 + bx1) / 2, by0 - 1.2 * m, f"{bx1 - bx0:.1f}", ha="center", va="top", fontsize=7, color="tab:blue")
                ax.annotate("", (bx0 - m, by0), (bx0 - m, by1), arrowprops=dict(arrowstyle="<->", lw=0.6, color="tab:blue"))
                ax.text(bx0 - 1.2 * m, (by0 + by1) / 2, f"{by1 - by0:.1f}", ha="right", va="center", fontsize=7, color="tab:blue", rotation=90)
                ax.set_xlim(bx0 - 3 * m, bx1 + m); ax.set_ylim(by0 - 3 * m, by1 + m)
                dxf_lines(msp, lines, ox - bx0, -by0)
                dxf_dim(msp, (ox, 0), (ox + bx1 - bx0, 0), (ox, -m - 30))
                dxf_dim(msp, (ox, 0), (ox, by1 - by0), (ox - m - 30, 0), angle=90)
                ox += (bx1 - bx0) + 6 * m + 200
            mm = man[name]
            fig.text(0.03, 0.93, f"{name}", fontsize=13, weight="bold")
            fig.text(0.03, 0.895, f"material: {mm['material']}    envelope X x Y x Z: {mm['bbox_mm']} mm    "
                     f"estimated mass ~{mm['est_mass_kg']} kg    position of min corner in assembly: {mm['origin_min']}", fontsize=7.5)
            title_block(fig, f"CD-{i:03d}", name, "layout-level geometry; detail design pending")
            pdf.savefig(fig); plt.close(fig)
            doc.saveas(os.path.join(OUT, "components", name + ".dxf"))
    print("drawings written to", OUT)


if __name__ == "__main__":
    main()
