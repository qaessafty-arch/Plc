#!/usr/bin/env python3
"""Exports the assembly for the web viewer: WEB3D/model/spm420.glb (one named node per part,
millimetres, Z up as in the CAD model) and WEB3D/model/parts.json (info for each part)."""
import json, os, sys
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import build_cad as B

OUT = os.path.join(ROOT, "WEB3D", "model")
os.makedirs(OUT, exist_ok=True)
man = json.load(open(os.path.join(ROOT, "CAD", "COMPONENTS", "manifest.json")))
asm = cq.Assembly(name="SPM-420")
jp = B.jaw_parts()
EXTRA = {}                                   # web-only split of the jaw assembly so the jaws can move
for name, (fn, col, grp, (mat, rho)) in B.PARTS.items():
    if name == "B13_jaw_assembly":
        asm.add(jp["fixed"].val(), name=name, color=cq.Color(*col))
        for key, nm in (("front", "B13a_front_jaw"), ("rear", "B13b_rear_jaw")):
            asm.add(jp[key].val(), name=nm, color=cq.Color(*col)); EXTRA[nm] = jp[key].val()
        continue
    asm.add(fn().val(), name=name, color=cq.Color(*col))
asm.export(os.path.join(OUT, "spm420.glb"), exportType="GLTF", tolerance=0.8, angularTolerance=0.35)
LABEL = {
    "B01_main_frame": "Bagger main frame", "B02_film_roll": "Film roll (Ø400, 420 web)", "B03_unwind_shaft": "Film unwind shaft",
    "B04_guide_rollers": "Film guide rollers", "B05_dancer_arm": "Dancer arm", "B06_forming_tube": "Forming / fill tube",
    "B07_forming_collar": "Forming collar", "B08_infeed_funnel": "Infeed funnel", "B09_pull_belt_left": "Pull belt, left",
    "B10_pull_belt_right": "Pull belt, right", "B11_belt_servo_drive": "Pull-belt servo drive", "B12_vertical_seal": "Vertical seal bar",
    "B13_jaw_assembly": "Jaw guide rods, cylinder, synchroniser", "B13a_front_jaw": "Front sealing jaw",
    "B13b_rear_jaw": "Rear sealing jaw + knife", "B14_guard_doors": "Front guard doors", "B15_electrical_cabinet": "Electrical cabinet",
    "B16_hmi_station": "Operator station (HMI)", "B17_film_web": "Film web path", "C01_takeoff_conveyor": "Take-off conveyor",
    "P01_weigher_platform": "Weigher platform + stair", "W01_multihead_weigher": "10-head multihead weigher (envelope)",
    "E01_z_bucket_elevator": "Z-bucket elevator (envelope)", "E02_infeed_hopper": "Infeed hopper + vibratory tray"}
GROUP = {"bagger": "Bagger", "film": "Film system", "former": "Forming", "pull": "Film pull", "seal": "Sealing", "jaw": "Sealing",
         "guard": "Guarding", "cabinet": "Controls", "takeoff": "Discharge", "platform": "Structure", "weigher": "Weighing", "elevator": "Feeding"}
parts = []
for name, (fn, col, grp, (mat, rho)) in B.PARTS.items():
    m = man[name]
    parts.append(dict(id=name, label=LABEL[name], group=GROUP[grp], explode=B.EXPLODE[grp], color=col,
                      material=mat, bbox_mm=m["bbox_mm"], mass_kg=m["est_mass_kg"]))
    if name == "B13_jaw_assembly":
        for nm, shp in EXTRA.items():
            bb = shp.BoundingBox()
            parts.append(dict(id=nm, label=LABEL[nm], group="Sealing", explode=B.EXPLODE["jaw"], color=col, material="tool steel, hardened",
                              bbox_mm=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                              mass_kg=round(shp.Volume() / 1e9 * 7850, 1)))
json.dump(dict(envelope_mm=man["_assembly"]["bbox_mm"], parts=parts), open(os.path.join(OUT, "parts.json"), "w"), indent=1)
print(os.path.getsize(os.path.join(OUT, "spm420.glb")) // 1024, "KB")
