#!/usr/bin/env python3
"""Parametric CAD of the SPM-420 line (CadQuery / OpenCASCADE).

Run:  python3 CAD/SCRIPTS/build_cad.py
Outputs
  CAD/COMPONENTS/<part>.step|.stl    one file per component / sub-assembly
  CAD/ASSEMBLY/SPM-420_assembly.step coloured, named assembly (opens in FreeCAD,
                                     SolidWorks, Inventor, Fusion)
  CAD/ASSEMBLY/SPM-420_assembly.stl  single mesh for viewers
  CAD/EXPLODED/SPM-420_exploded.step exploded arrangement
  CAD/COMPONENTS/manifest.json       bounding boxes, volumes, estimated masses

The geometry is a LAYOUT-LEVEL model: envelopes, interfaces and proportions are
derived from machine_params.py. It is not a detail design (no fasteners, weld
preps, bearing seats). See CAD/README.md for what is and is not modelled.
"""
import json, math, os, sys
import cadquery as cq
from cadquery import exporters

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT)
import machine_params as P

CAD = os.path.join(ROOT, "CAD")
ref = P.PRODUCTS[P.REFERENCE_PRODUCT]
TUBE_R = P.tube_diameter(ref[3]) / 2
FILM_W = P.film_width(ref[3])


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def cyl_z(r, z0, z1, x=0, y=0):
    return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((x, y, z0))


def cyl_x(r, x0, x1, y, z):
    return cq.Workplane("YZ").circle(r).extrude(x1 - x0).translate((x0, y, z))


def cyl_y(r, y0, y1, x, z):
    return cq.Workplane("XZ").circle(r).extrude(-(y1 - y0)).translate((x, y0, z))


def cone_shell(r_bot, r_top, z0, z1, t=2.0):
    outer = cq.Solid.makeCone(r_bot, r_top, z1 - z0)
    inner = cq.Solid.makeCone(max(r_bot - t, 0.1), max(r_top - t, 0.1), z1 - z0)
    return cq.Workplane("XY").add(outer.cut(inner)).translate((0, 0, z0))


def tube_frame(x0, x1, y0, y1, z0, z1, s, mids=()):
    """Welded box-section skeleton: 4 posts + rails at z0, z1 and each mid level."""
    wp = cq.Workplane("XY")
    parts = []
    for x in (x0, x1 - s):
        for y in (y0, y1 - s):
            parts.append(box(x, x + s, y, y + s, z0, z1))
    for z in (z0, z1 - s, *mids):
        parts += [box(x0 + s, x1 - s, y0, y0 + s, z, z + s), box(x0 + s, x1 - s, y1 - s, y1, z, z + s),
                  box(x0, x0 + s, y0 + s, y1 - s, z, z + s), box(x1 - s, x1, y0 + s, y1 - s, z, z + s)]
    for q in parts:
        wp = wp.add(q)
    return wp.combine()


def union(items):
    wp = cq.Workplane("XY")
    for q in items:
        wp = wp.add(q)
    return wp.combine()


# ============================================================ components
def frame():
    s = P.FRAME_TUBE
    x0, x1 = -P.BAGGER_W / 2, P.BAGGER_W / 2
    y0, y1 = P.BAGGER_FRONT_Y, P.BAGGER_FRONT_Y + P.BAGGER_D
    f = tube_frame(x0, x1, y0, y1, 100, P.BAGGER_H, s, mids=(P.JAW_Z - 150, 1150))
    feet = [cyl_z(40, 0, 100, x, y) for x in (x0 + 45, x1 - 45) for y in (y0 + 45, y1 - 45)]
    top = box(x0, x1, y0, y0 + 600, P.BAGGER_H, P.BAGGER_H + 8).cut(cyl_z(TUBE_R + 90, P.BAGGER_H - 1, P.BAGGER_H + 9))
    return union([f, top, *feet])


def film_roll():
    return cyl_x(P.FILM_ROLL_OD_MAX / 2, -FILM_W / 2, FILM_W / 2, 750, 520).cut(
        cyl_x(P.FILM_CORE_ID / 2, -FILM_W / 2, FILM_W / 2, 750, 520))


def unwind_shaft():
    return union([cyl_x(P.FILM_CORE_ID / 2 - 1, -260, 260, 750, 520), cyl_x(20, -420, 420, 750, 520),
                  box(-450, -420, 700, 800, 300, 580), box(420, 450, 700, 800, 300, 580)])


ROLLERS = [(520, 880), (300, 760), (520, 1150), (330, 1380), (200, 1400)]   # (y, z)


def guide_rollers():
    return union([cyl_x(25, -235, 235, y, z) for y, z in ROLLERS] +
                 [box(-260, -235, 180, 560, 730, 1420), box(235, 260, 180, 560, 730, 1420)])


def dancer():
    arm = [box(sx * 240 - 6, sx * 240 + 6, 300, 560, 990, 1010) for sx in (-1, 1)]
    return union(arm + [cyl_x(22, -235, 235, 320, 1000)])


def forming_tube():
    return cyl_z(TUBE_R, P.JAW_Z + 60, P.TUBE_TOP_Z).cut(cyl_z(TUBE_R - 2, P.JAW_Z + 59, P.TUBE_TOP_Z + 1))


def forming_collar():
    z1, z0 = P.TUBE_TOP_Z, P.TUBE_TOP_Z - 130
    sh = cone_shell(TUBE_R + 75, TUBE_R + 3, z0, z1, 2.5)
    cutter = box(-300, 300, -300, 300, z0 - 200, z0).rotate((0, 0, z0), (1, 0, z0), -28).translate((0, 0, 60))
    plate = box(-TUBE_R - 90, TUBE_R + 90, -TUBE_R - 90, TUBE_R + 110, z0 - 60, z0 - 50).cut(
        cyl_z(TUBE_R + 1, z0 - 61, z0 - 49))
    return union([sh.cut(cutter), plate])


def infeed_funnel():
    return cone_shell(TUBE_R - 2, 150, P.TUBE_TOP_Z, P.FUNNEL_TOP_Z, 2.0)


def pull_belt(side):
    x = side * (TUBE_R + 28)
    z0, z1 = P.BELT_Z0, P.BELT_Z0 + P.PULL_BELT_LEN
    body = box(x - 14, x + 14, -22, 22, z0, z1)
    pul = [cyl_y(P.PULL_PULLEY_DIA / 2, -22, 22, x, z) for z in (z0, z1)]
    arm = box(min(x, x + side * 120), max(x, x + side * 120), 30, 60, z0 + 60, z1 - 60)
    return union([body, *pul, arm])


def belt_drive():
    """Servo + planetary gearbox + cross shaft behind the tube."""
    y = TUBE_R + 120
    return union([cyl_x(12, -TUBE_R - 140, TUBE_R + 140, y, P.BELT_Z0),
                  box(-TUBE_R - 300, -TUBE_R - 180, y - 30, y + 30, P.BELT_Z0 - 30, P.BELT_Z0 + 30),
                  cyl_x(30, -TUBE_R - 180, -TUBE_R - 140, y, P.BELT_Z0)])


def vertical_seal():
    y = -(TUBE_R + 1)
    bar = box(-12.5, 12.5, y - 30, y, P.BELT_Z0 - 20, P.BELT_Z0 - 20 + P.VSEAL_LENGTH)
    cyl = cyl_y(26, y - 150, y - 30, 0, P.BELT_Z0 + 140)
    brk = box(-40, 40, y - 160, y - 150, P.BELT_Z0 + 60, P.BELT_Z0 + 220)
    return union([bar, cyl, brk])


def jaw_assembly():
    jw, jh = P.JAW_SECTION
    z0 = P.JAW_Z - jh / 2
    L2 = P.JAW_LENGTH / 2
    gap = 35
    front = box(-L2, L2, -gap - jw, -gap, z0, z0 + jh)
    rear = box(-L2, L2, gap, gap + jw, z0, z0 + jh)
    carr = [box(-L2 - 70, L2 + 70, s * (gap + jw), s * (gap + jw + 25), z0 - 10, z0 + jh + 10) if s > 0 else
            box(-L2 - 70, L2 + 70, -(gap + jw + 25), -(gap + jw), z0 - 10, z0 + jh + 10) for s in (1, -1)]
    rods = [cyl_y(10, -220, 320, x, P.JAW_Z) for x in (-L2 - 45, L2 + 45)]
    cylinder = cyl_y(38, 150, 320, 0, P.JAW_Z)
    knife = box(-L2 + 10, L2 - 10, gap + 2, gap + jw - 2, P.JAW_Z - 1, P.JAW_Z + 1)
    sync = box(-L2 - 75, -L2 - 65, -200, 300, P.JAW_Z + 40, P.JAW_Z + 60)
    return union([front, rear, *carr, *rods, cylinder, knife, sync])


def guard_doors():
    y = P.BAGGER_FRONT_Y - 6
    return union([box(-P.BAGGER_W / 2 + 50, -5, y, y + 6, P.JAW_Z - 250, P.BAGGER_H - 60),
                  box(5, P.BAGGER_W / 2 - 50, y, y + 6, P.JAW_Z - 250, P.BAGGER_H - 60)])


def cabinet():
    t, w, hh = P.CABINET
    x0 = P.BAGGER_W / 2
    return union([box(x0, x0 + t, 250, 250 + w, 300, 300 + hh),
                  cyl_x(35, x0 + t, x0 + t + 40, 320, 1150)])          # main isolator handle


def hmi():
    return union([box(520, 560, -340, -300, 1200, 1450), box(540, 780, -380, -340, 1320, 1480),
                  box(560, 760, -384, -380, 1340, 1460)]).translate((0, P.BAGGER_FRONT_Y + 300, 0))


def takeoff_conveyor():
    w = P.TAKEOFF_WIDTH / 2
    ang = math.degrees(math.atan2(450, P.TAKEOFF_LEN))
    bed = box(0, P.TAKEOFF_LEN / math.cos(math.radians(ang)), -w, w, 0, 80).rotate((0, 0, 0), (0, 1, 0), -ang) \
        .translate((-250, 0, 250))
    legs = [box(x - 20, x + 20, s * w - 20, s * w + 20, 0, z) for x, z in ((-150, 270), (1450, 660)) for s in (-1, 1)]
    motor = cyl_y(55, w, w + 180, 1480, 700)
    return union([bed, *legs, motor])


def platform():
    s, z, t = P.PLATFORM_SIZE / 2, P.PLATFORM_Z, 80
    legs = [box(x - t / 2, x + t / 2, y - t / 2, y + t / 2, 0, z) for x in (-s + 40, s - 40) for y in (-s + 40, s - 40)]
    ring = tube_frame(-s, s, -s, s, z - 100, z, 80)
    deck = box(-s, s, -s, s, z, z + 5).cut(cyl_z(260, z - 1, z + 6))
    posts = [box(x - 20, x + 20, y - 20, y + 20, z, z + P.HANDRAIL_H)
             for x in (-s + 20, 0, s - 20) for y in (-s + 20, s - 20)] + \
            [box(x - 20, x + 20, -20, 20, z, z + P.HANDRAIL_H) for x in (-s + 20, s - 20)]
    rails = []
    for zz in (z + P.HANDRAIL_H, z + P.HANDRAIL_H / 2):
        rails += [box(-s, s, -s, -s + 40, zz - 40, zz), box(-s, s, s - 40, s, zz - 40, zz),
                  box(s - 40, s, -s, s, zz - 40, zz), box(-s, -s + 40, -s, 400, zz - 40, zz)]
    kick = [box(-s, s, -s, -s + 5, z, z + 100), box(-s, s, s - 5, s, z, z + 100), box(s - 5, s, -s, s, z, z + 100)]
    run = z / math.tan(math.radians(60))
    stringers = [box(0, z / math.sin(math.radians(60)), y, y + 10, 0, 150).rotate((0, 0, 0), (0, 1, 0), -60)
                 .translate((-s - run, 0, 0)) for y in (450, 940)]
    treads = [box(-s - run + i * run / 9, -s - run + i * run / 9 + 200, 460, 940, (i + 0.5) * z / 9 - 15, (i + 0.5) * z / 9 + 15)
              for i in range(9)]
    brace = [box(x, x + 40, -s + 80, s - 80, 900, 940) for x in (-s + 20, s - 60)] + [box(-s + 80, s - 80, s - 60, s - 20, 1700, 1740)]
    return union(legs + [ring, deck] + posts + rails + kick + stringers + treads + brace)


def weigher():
    z = P.WEIGHER_BASE_Z
    parts = [cyl_z(200, z + 250, z + 850),                       # drive / electronics column
             cyl_z(310, z + 850, z + 870)]                       # feeder base plate
    parts.append(cone_shell(225, 20, z + 880, z + 960, 3))       # top (dispersion) cone
    n = P.WEIGHER_HEADS
    for i in range(n):
        a = 360.0 * i / n
        feeder = box(230, 470, -45, 45, z + 870, z + 900)
        feed_h = box(400, 520, -60, 60, z + 650, z + 830)
        weigh_h = box(380, 520, -65, 65, z + 400, z + 610)
        actu = box(200, 380, -30, 30, z + 430, z + 800)
        for q in (feeder, feed_h, weigh_h, actu):
            parts.append(q.rotate((0, 0, 0), (0, 0, 1), a))
    parts.append(cone_shell(100, 450, P.FUNNEL_TOP_Z + 50, z + 380, 2))    # collating chute (reversed cone)
    legs = [box(x - 30, x + 30, y - 30, y + 30, P.PLATFORM_Z + 5, z + 300) for x in (-520, 520) for y in (-520, 520)]
    ring = tube_frame(-550, 550, -550, 550, z + 240, z + 300, 60)
    parts.append(cone_shell(60, 175, z + 980, z + P.WEIGHER_HEIGHT, 2))    # infeed funnel
    return union(parts + legs + [ring])


def elevator():
    w = P.ELEV_WIDTH / 2
    x0 = P.ELEV_INFEED_X
    top = P.WEIGHER_BASE_Z + P.WEIGHER_HEIGHT + 500
    low = box(x0, x0 + 1300, -w, w, 300, 600)
    vert = box(x0 + 1300, x0 + 1600, -w, w, 300, top)
    up = box(x0 + 1300, -150, -w, w, top - 300, top)
    spout = box(-180, 180, -150, 150, top - 450, top - 300)
    legs = [box(x - 25, x + 25, s * w - 25, s * w + 25, 0, 300) for x in (x0 + 50, x0 + 1550) for s in (-1, 1)]
    stay = [box(-230, -170, s * 300 - 30, s * 300 + 30, P.PLATFORM_Z + 5, top - 300) for s in (-1, 1)]
    motor = cyl_y(70, w, w + 220, -400, top - 150)
    return union([low, vert, up, spout, *legs, *stay, motor])


def infeed_hopper():
    x0 = P.ELEV_INFEED_X
    body = cq.Workplane("XY").rect(700, 600).workplane(offset=450).rect(1000, 900).loft(combine=True) \
        .translate((x0 + 575, 0, 800))
    inner = cq.Workplane("XY").rect(694, 594).workplane(offset=452).rect(994, 894).loft(combine=True) \
        .translate((x0 + 575, 0, 801))
    tray = box(x0 + 150, x0 + 900, -200, 200, 680, 760)          # vibratory feeder tray
    legs = [box(x0 + 575 + sx * 330 - 20, x0 + 575 + sx * 330 + 20, sy * 280 - 20, sy * 280 + 20, 0, 800)
            for sx in (-1, 1) for sy in (-1, 1)]
    return union([body.cut(inner), tray, *legs])


def film_web():
    """Thin representation of the web path (visual aid, not a part)."""
    pts = [(750 + P.FILM_ROLL_OD_MAX / 2 - 60, 520)] + ROLLERS + [(TUBE_R + 75, P.TUBE_TOP_Z - 100)]
    segs = []
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        ln = math.hypot(y1 - y0, z1 - z0)
        ang = math.degrees(math.atan2(z1 - z0, y1 - y0))
        segs.append(box(-FILM_W / 2, FILM_W / 2, 0, ln, -0.5, 0.5).rotate((0, 0, 0), (1, 0, 0), ang).translate((0, y0, z0)))
    return union(segs)


# name: (builder, colour, group for exploded view, material, density kg/m3)
SS, AL, ST, PL = ("1.4301 stainless", 7900), ("EN AW-6082", 2700), ("steel", 7850), ("polymer", 1200)
PARTS = {
    "B01_main_frame":        (frame, (0.75, 0.77, 0.80), "bagger", SS),
    "B02_film_roll":         (film_roll, (0.95, 0.85, 0.35), "film", ("OPP laminate", 910)),
    "B03_unwind_shaft":      (unwind_shaft, (0.55, 0.55, 0.6), "film", SS),
    "B04_guide_rollers":     (guide_rollers, (0.7, 0.7, 0.75), "film", AL),
    "B05_dancer_arm":        (dancer, (0.3, 0.5, 0.8), "film", AL),
    "B06_forming_tube":      (forming_tube, (0.85, 0.85, 0.9), "former", SS),
    "B07_forming_collar":    (forming_collar, (0.9, 0.9, 0.95), "former", SS),
    "B08_infeed_funnel":     (infeed_funnel, (0.85, 0.85, 0.9), "former", SS),
    "B09_pull_belt_left":    (lambda: pull_belt(-1), (0.15, 0.15, 0.15), "pull", AL),
    "B10_pull_belt_right":   (lambda: pull_belt(1), (0.15, 0.15, 0.15), "pull", AL),
    "B11_belt_servo_drive":  (belt_drive, (0.2, 0.2, 0.25), "pull", ST),
    "B12_vertical_seal":     (vertical_seal, (0.8, 0.3, 0.2), "seal", AL),
    "B13_jaw_assembly":      (jaw_assembly, (0.8, 0.35, 0.2), "jaw", ST),
    "B14_guard_doors":       (guard_doors, (0.6, 0.8, 0.95), "guard", ("polycarbonate", 1200)),
    "B15_electrical_cabinet": (cabinet, (0.7, 0.72, 0.75), "cabinet", SS),
    "B16_hmi_station":       (hmi, (0.2, 0.2, 0.22), "cabinet", PL),
    "B17_film_web":          (film_web, (1.0, 0.9, 0.4), "film", ("film", 910)),
    "C01_takeoff_conveyor":  (takeoff_conveyor, (0.3, 0.6, 0.35), "takeoff", SS),
    "P01_weigher_platform":  (platform, (0.6, 0.62, 0.65), "platform", SS),
    "W01_multihead_weigher": (weigher, (0.82, 0.84, 0.88), "weigher", SS),
    "E01_z_bucket_elevator": (elevator, (0.72, 0.74, 0.78), "elevator", SS),
    "E02_infeed_hopper":     (infeed_hopper, (0.8, 0.82, 0.85), "elevator", SS),
}
EXPLODE = {"bagger": (0, 0, 0), "film": (0, 900, 0), "former": (0, -200, 900), "pull": (0, -900, 300),
           "seal": (0, -1300, 500), "jaw": (0, -1500, -100), "guard": (0, -2000, 0), "cabinet": (1200, 0, 0),
           "takeoff": (1200, -1300, 0), "platform": (0, 0, 1700), "weigher": (0, 0, 2900), "elevator": (-1500, 0, 600)}

# hollow / envelope parts: solid volume overstates mass, so apply a fill factor [ASM]
FILL = {"B01_main_frame": 0.2, "P01_weigher_platform": 0.17, "E02_infeed_hopper": 0.25, "B04_guide_rollers": 0.3,
        "B03_unwind_shaft": 0.5, "B15_electrical_cabinet": 0.06, "W01_multihead_weigher": 0.12, "E01_z_bucket_elevator": 0.05,
        "C01_takeoff_conveyor": 0.15, "B16_hmi_station": 0.3, "B13_jaw_assembly": 0.9, "B11_belt_servo_drive": 0.6,
        "B02_film_roll": 1.0, "B09_pull_belt_left": 0.5, "B10_pull_belt_right": 0.5}


def main():
    for d in ("COMPONENTS", "ASSEMBLY", "EXPLODED"):
        os.makedirs(os.path.join(CAD, d), exist_ok=True)
    asm, exp, manifest, solids = cq.Assembly(name="SPM-420"), cq.Assembly(name="SPM-420_exploded"), {}, []
    for name, (fn, col, grp, (mat, rho)) in PARTS.items():
        wp = fn()
        shape = wp.val()
        exporters.export(wp, os.path.join(CAD, "COMPONENTS", name + ".step"))
        exporters.export(wp, os.path.join(CAD, "COMPONENTS", name + ".stl"), tolerance=0.5, angularTolerance=0.3)
        bb = shape.BoundingBox()
        vol = shape.Volume()
        manifest[name] = dict(
            group=grp, material=mat,
            bbox_mm=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
            origin_min=[round(bb.xmin, 1), round(bb.ymin, 1), round(bb.zmin, 1)],
            model_volume_dm3=round(vol / 1e6, 2),
            est_mass_kg=round(vol / 1e9 * rho * FILL.get(name, 1.0), 1))
        c = cq.Color(*col)
        asm.add(shape, name=name, color=c)
        exp.add(shape, name=name, color=c, loc=cq.Location(cq.Vector(*EXPLODE[grp])))
        solids.append(shape)
        print(f"{name:26s} bbox {manifest[name]['bbox_mm']}  ~{manifest[name]['est_mass_kg']} kg")
    asm.save(os.path.join(CAD, "ASSEMBLY", "SPM-420_assembly.step"))
    exp.save(os.path.join(CAD, "EXPLODED", "SPM-420_exploded.step"))
    comp = cq.Compound.makeCompound(solids)
    exporters.export(cq.Workplane("XY").add(comp), os.path.join(CAD, "ASSEMBLY", "SPM-420_assembly.stl"),
                     tolerance=1.0, angularTolerance=0.4)
    expc = cq.Compound.makeCompound([s.moved(cq.Location(cq.Vector(*EXPLODE[PARTS[n][2]])))
                                     for n, s in zip(PARTS, solids)])
    exporters.export(cq.Workplane("XY").add(expc), os.path.join(CAD, "EXPLODED", "SPM-420_exploded.stl"),
                     tolerance=1.0, angularTolerance=0.4)
    bb = comp.BoundingBox()
    manifest["_assembly"] = dict(bbox_mm=[round(bb.xlen), round(bb.ylen), round(bb.zlen)],
                                 x=[round(bb.xmin), round(bb.xmax)], y=[round(bb.ymin), round(bb.ymax)],
                                 z=[round(bb.zmin), round(bb.zmax)],
                                 est_mass_kg=round(sum(m["est_mass_kg"] for m in manifest.values())))
    json.dump(manifest, open(os.path.join(CAD, "COMPONENTS", "manifest.json"), "w"), indent=1)
    print("ASSEMBLY", manifest["_assembly"])
    return comp, expc


if __name__ == "__main__":
    main()
