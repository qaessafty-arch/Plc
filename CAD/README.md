# CAD

Parametric model written in CadQuery (OpenCASCADE). Regenerate with:

```
pip install cadquery ezdxf matplotlib
python3 CAD/SCRIPTS/build_cad.py        # STEP / STL / manifest
python3 CAD/SCRIPTS/build_drawings.py   # PDF / DXF / PNG drawings
python3 CAD/SCRIPTS/render_views.py      # isometric assembly and exploded views
```

| Folder | Content |
|---|---|
| `SCRIPTS/` | `build_cad.py` (geometry, driven by `/machine_params.py`), `build_drawings.py` (hidden-line projections + dimensions) |
| `ASSEMBLY/` | `SPM-420_assembly.step` (coloured, 22 named parts - open in FreeCAD, SolidWorks, Inventor, Fusion), `.stl`, isometric view `SPM-420_isometric.png/.pdf` |
| `COMPONENTS/` | one `.step` and `.stl` per part, `manifest.json` (envelope, position, material, estimated mass) |
| `EXPLODED/` | exploded arrangement as `.step`, `.stl`, `.png/.pdf` |
| `DRAWINGS/` | `GA-001` general arrangement, `GA-002` floor layout, `CD-000` component sheets, `components/*.dxf` |

**Level of detail:** layout model. Correct: overall proportions, positions, interfaces, envelopes, tube diameter, roller and jaw sizes. Simplified: the forming collar (a real collar is a developed surface made by a specialist), weigher and elevator (supplier envelopes), solid sections instead of hollow tube, no fasteners, bearings, welds or pneumatics. Every sheet is marked PRELIMINARY - NOT FOR MANUFACTURE.

Part prefixes: B bagger, C conveyor, P platform, W weigher, E elevator.
