# Final engineering report - SPM-420 snack filling and packaging line

Revision P1, 2026-11-11. Status of the project: **design package at preliminary-design maturity, verified by calculation and software simulation only. No hardware has been built or tested.**

## 1. What was asked and what was delivered

| # | Required deliverable | Delivered as | Maturity |
|---|---|---|---|
| 1 | Reference machine analysis | `DOCUMENTATION/01_REFERENCE_ANALYSIS.md` | inference from title/publisher; **video frames could not be viewed** |
| 2 | Engineering specification | `DOCUMENTATION/02_REQUIREMENTS_SPECIFICATION.md` | requirement IDs, assumptions flagged |
| 3 | Mechanical design | `DOCUMENTATION/04_MECHANICAL_DESIGN.md` + CAD | layout level; shop drawings not made |
| 4 | Footprint and dimensioned layout | `DOCUMENTATION/05_FOOTPRINT_AND_LAYOUT.md`, `CAD/DRAWINGS/GA-001`, `GA-002` (PDF, DXF, PNG) | derived from components; preliminary |
| 5 | Full 3D CAD assembly | `CAD/ASSEMBLY/SPM-420_assembly.step` / `.stl`, 22 named parts | envelopes and interfaces, no fasteners |
| 6 | Component drawings | `CAD/DRAWINGS/CD-000_component_drawings.pdf` (22 sheets) + DXF per part | three views with envelope dimensions only |
| 7 | Electrical architecture | `ELECTRICAL/SCHEMATICS/01_architecture.md` | complete at concept level |
| 8 | Electrical schematics | `ELECTRICAL/SCHEMATICS/02`-`05`, `WIRING/*.csv`, `PANEL/` | design-level; **not ECAD production schematics** |
| 9 | BOM | `ELECTRICAL/BOM/bom.csv` (77 lines, 3 configurations) | 7 order numbers verified, 3 flagged "from memory", rest generic specs |
| 10 | PLC program | `AUTOMATION/PLC/*.scl, *.udt, *.db` | Structured Text source, **not compiled in TIA Portal** |
| 11 | HMI application | `AUTOMATION/HMI/` specification, tag CSV, browser prototype | WinCC project must be built from the spec |
| 12 | Monitoring software | `SOFTWARE/` FastAPI + PostgreSQL schema + React | runs; tested with simulated source; OPC UA path untested on a PLC |
| 13 | Simulation | `SIMULATION/` | 12 scenarios / 49 checks pass; weigher Monte-Carlo |
| 14 | Manufacturing guide | `DOCUMENTATION/MANUFACTURING/manufacturing_guide.md` | process, tolerances, tools |
| 15 | Assembly instructions | `DOCUMENTATION/MANUFACTURING/assembly_instructions.md` | sequence, threading, format change |
| 16 | Safety documentation | `DOCUMENTATION/SAFETY/` | preliminary risk assessment, standards list, LOTO, cleaning |
| 17 | Testing and calibration plan | `DOCUMENTATION/TESTING/` | plan, checklist, calibration, acceptance criteria |
| 18 | Budget | `DOCUMENTATION/REPORTS/budget.md` | estimates only, USD and IQD |
| 19 | Final report | this file | - |

## 2. Design in one page

Line: floor hopper with vibratory tray -> Z-bucket elevator -> 10-head combination weigher on a free-standing platform -> intermittent-motion vertical form-fill-seal bagger (420 mm web, pillow bags 80-200 mm wide, 80-300 mm long) -> inclined take-off conveyor.

* Envelope 4450 x 1900 x 3900 mm; floor area with access 6050 x 4100 mm (24.8 m²); ceiling 4400 mm.
* Bagger: welded 304 frame 1000 x 1300 x 1500; servo-driven twin pull belts (0.4 kW SINAMICS V90 PN); pneumatic horizontal jaws with integrated knife; pneumatic vertical seal bar; three PI-controlled heater zones, 1.3 kW total.
* Control: Siemens S7-1200 CPU 1215C + SM 1223 + thermocouple module, KTP700 HMI, hard-wired safety relays (target PL d), weigher connected by hard-wired handshake, optional read-only monitoring PC.
* Rated 40 bags/min for 40 g chips in a 160 x 230 mm bag; mechanical limit 49 bags/min (calculated).
* Utilities: 400/230 V, 4.7 kW connected; air 0.19 m³/min at 0.6 MPa.
* Budget (estimates): see `budget.md` - three configurations.

## 3. Findings worth the reader's attention

1. **Jaw force is short of the assumed requirement.** Ø63 cylinder gives 1683 N vs 2304 N assumed necessary (SF 0.73). Three remedies are listed in the mechanical design; the decision needs seal trials. The vertical seal cylinder is marginal (SF 1.06).
2. **The bagger cannot detect weight errors** (simulation S05). Weight assurance rests on the weigher and, for anything sold by weight, on a checkweigher.
3. **Speed is capped by pneumatic jaws** at about 49 bags/min for this bag; the 80-150 bags/min of the reference manufacturer's high-speed model requires servo jaws and continuous film motion.
4. **Combination weighing needs charge variety**: the model shows more failed combinations when per-head charges are very uniform, and a 4-head weigher is unusable for 40 g chips (4.7 % give-away, ~70 % skipped cycles).
5. **Simulation found three real sequence defects** before any hardware: a hang in STOPPING after a cycle abort, alarms needing two resets, and the recipe speed not being enforced. All fixed in both the SCL and the model.
6. **Cabinet temperature margin is thin** for unconditioned halls in Iraq (≈ 45 °C inside at 35 °C ambient): a filter fan or cooler is specified.
7. Film is ~98 % of the energy-plus-film running cost; bag length matters more than any energy measure.

## 4. Assumptions and unknowns register

| # | Assumption / unknown | Used in | How to close |
|---|---|---|---|
| A1 | The reference machine is a multihead weigher + VFFS | whole concept | watch the clip with the checklist in the reference analysis |
| A2 | Intended market Iraq, supply 400/230 V 50 Hz TN-S | electrical | site survey; confirm earthing system and voltage stability |
| A3 | Bulk densities of products | bag sizes, elevator | measure each product |
| A4 | Film: 50 µm PP-based laminate, seal 150 °C / 0.45 s / 0.4 MPa | cycle, heaters, jaw force | film supplier data sheet + seal trials (T-SEAL-01) |
| A5 | Film drag 60 N, belt friction allows 6 m/s² | servo sizing, cycle | spring-scale measurement; pull trials |
| A6 | Product string duration 0.35 s, fall without drag | timing | high-speed video per product |
| A7 | Per-head charge CV 30 %, cell noise 0.15 g | weight statistics | weigher supplier trials with the real product |
| A8 | Weigher 1100 dia x 1250, 380 kg, 1.5 kW, 70 wpm; elevator section and head height | layout, loads, footprint | supplier certified drawings and data |
| A9 | Pneumatic travel 0.12-0.15 s, knife force 150 N | cycle | measurement |
| A10 | Thermal model constants (losses, thermocouple lag) | warm-up, PI tuning | commissioning step tests |
| A11 | Section fill factors for mass estimate | mass, floor load | weigh assemblies |
| A12 | Unit prices, exchange rate 1320 IQD/USD, tariff, film price, 85 % efficiency | budget, operating cost | quotations; plant data |
| A13 | Order numbers marked "from memory - confirm" (CPU 1214C, SM 1231 TC, KTP400) | BOM | manufacturer catalogue |
| A14 | Required PL d; door access time longer than jaw retraction | safety concept | final risk assessment, ISO 13855 measurement |
| A15 | National regulatory requirements in Iraq | compliance | COSQC / local conformity body |

## 5. What could not be produced in this environment, and the editable alternative

| Requested | Limitation | Provided instead |
|---|---|---|
| Analysis of the video images | video and thumbnail hosts blocked | analysis from title, publisher catalogue and published machine data, plus a viewing checklist |
| SolidWorks / Inventor / Fusion native files | no such software | CadQuery (Python) parametric source `CAD/SCRIPTS/build_cad.py` + neutral STEP (opens in all of them and in FreeCAD), STL, DXF, PDF |
| Photorealistic Blender render | not attempted | hidden-line isometric SVG of assembly and exploded view; STL for any renderer |
| Detailed manufacturing drawings with tolerances | needs detail design first | component sheets with envelope dimensions; tolerances stated in the manufacturing guide |
| TIA Portal project (.ap17) and WinCC HMI | proprietary, needs TIA Portal | importable SCL/UDT/DB sources, tag and alarm CSVs, HMI specification, browser prototype |
| ECAD schematic set | no ECAD tool | design-level diagrams, protection tables, cable schedule, terminal plan |
| Physical tests, FAT, performance validation | no machine | simulation with explicit limits; full test plan and acceptance criteria |
| Verified prices and purchase links | no quotations; links not invented | estimates labelled as such; source category per line |

## 6. Recommended next steps

1. Confirm A1-A2 and the product/bag list with the project owner; freeze the specification.
2. Request quotations and certified drawings for weigher and elevator (interfaces: chute outlet height +1700, handshake signals, supply).
3. Film and seal trials on a jaw test rig (one jaw pair, one heater controller) - closes the jaw-force question before the frame is built.
4. Detail design of the bagger from the CAD layout (shop drawings), modal check of the platform.
5. Import and compile the PLC sources; build the HMI; bench test PLC + servo + HMI with the I/O simulated.
6. ECAD schematics, SISTEMA calculation, panel build.
7. Build, commission per the checklist, safety validation, performance qualification; then update every "theoretical" number in `07_PERFORMANCE.md` with measured values.
