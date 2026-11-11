# Manufacturing guide

Applies to the semi-industrial configuration (welded stainless bagger + bought weigher and elevator). The 3D model and drawings in `CAD/` are **layout level**: before cutting metal, each fabricated part needs a shop drawing with tolerances, weld symbols and surface finish derived from the model. Tolerances below are the design intent for those drawings.

General tolerances: machined parts ISO 2768-mK; welded frames ISO 13920-BF; sheet metal ISO 2768-m with bend ±0.5°.

## Workshop equipment needed

TIG welder (AC/DC not required; DC with argon purge for tube ends), welding table 1500 x 1500 with squares and clamps, cold saw or band saw, pillar drill, lathe (Ø300 x 1000), milling machine with DRO (travel >= 600 mm), surface plate or granite, hand tools, pickling paste and passivation gel, torque wrenches 5-200 N.m, dial indicator with magnetic base, machinist level 0.02 mm/m, feeler gauges, crimping tools for ferrules and M12, multimeter, insulation tester 500 V, loop/earth continuity tester, contact thermometer (reference probe), spring scale 0-100 N, set of certified test weights (for weigher checks). Bought-in services: laser cutting and bending, hardening and grinding of jaws, forming-set manufacture.

## 1. Frame fabrication

| Step | Detail | Acceptance |
|---|---|---|
| Cut SHS 50 x 50 x 2 (1.4301) to the cutting list from the shop drawing; deburr; drill drain/vent holes where tubes will be closed | saw square within 0.5 mm | lengths ±0.5 |
| Tack the two side ladders on the table, then join with cross rails; tack, measure diagonals, then weld in a balanced sequence | TIG, 1.6 mm ER308L filler, short stitches alternating sides | diagonals equal within 1.5 mm; posts plumb 1 mm/m |
| Weld machined pads (10 mm 1.4301) for the jaw-carriage rail (+550) and belt-carriage rail (+1150); skim-mill or shim the pads after welding | - | each pad pair coplanar within 0.2 mm; parallel to the top plate within 0.3 mm |
| Top plate 8 mm with tube opening and two Ø8 H7 dowel holes for the forming set | drill dowel holes after welding, on the mill or with a drill jig | position ±0.05 between dowels |
| Cap all tube ends, grind welds flush in product zone only, pickle and passivate all welds, rinse, dry | - | no heat tint; ferroxyl test negative on product-zone welds |
| Fit feet, level | - | 0.5 mm/m |

Platform: same method with SHS 80 x 80 x 3, deck 5 mm tread plate or perforated sheet, bolted diagonal braces, handrail per ISO 14122-3, four floor anchor plates. Trial-assemble in the shop; match-mark; disassemble for transport if needed.

## 2. Mechanical component manufacturing

| Part | Process | Critical features |
|---|---|---|
| Jaws (2) | mill from tool steel bar (e.g. 1.2312 or 1.2085), drill heater bores Ø10 H7 x 235 (ream; heaters must be a close fit: 0.02-0.05 mm clearance, otherwise they burn out), TC pocket Ø3 x 40 at mid-length 5 mm behind the face, knife slot 2.5 x 30 in the rear jaw; serrate faces (1.5 pitch, 90°) with matching profile so the two jaws mesh; harden 48-52 HRC, grind faces, chemical nickel 15 µm | faces flat 0.02 mm; mesh checked with carbon paper over the full 240 mm |
| Jaw carriages | aluminium 6082, bushing bores Ø(bushing OD) H7 line-bored as a pair | bore spacing ±0.02; jaws parallel to rods within 0.05 |
| Guide rods | bought hard-chrome Ø20 h6, cut and tapped | - |
| Synchroniser | two racks m1.5 + pinion on a needle bearing, or equal-arm lever | backlash < 0.1 mm at the jaw |
| Vertical seal bar | aluminium 6082, heater bore Ø10 H7, PTFE-glass tape cover, pivot bracket | land flat 0.05; radius 0.5 on edges |
| Pull-belt housings | aluminium plates, bearing seats H7, pulleys Ø60 (z per belt pitch) | both units identical: belt contact faces parallel to tube within 0.1 |
| Cross shaft and couplings | 1.4301 shaft Ø15 h7 keyed, two right-angle gear units or twisted timing-belt stages | - |
| Rollers | aluminium tube Ø50 x 3, pressed end caps with 6001-2RS bearings, anodise | TIR 0.1; rotate freely by a 2 g weight on the rim |
| Unwind shaft, chucks, brackets | lathe work, 1.4301 | - |
| Funnel, chutes, covers, crumb trays, cabinet bracket | laser cut 2 mm 1.4301, roll/bend, TIG, polish product side to Ra <= 0.8 | no crevices; continuous welds on product side |
| Forming set | **buy**: give the maker film width, bag width, film structure, lap or fin seal, tube length 690, flange/dowel pattern | maker's test bag supplied |

## 3. Conveyor assembly

Take-off conveyor: frame 1.4301, PU belt 300 wide (blue, food grade), drive drum with 0.18 kW gearmotor, tail drum with tracking screws; set belt tension to the belt maker's elongation mark; track by 10 min run in both loaded/unloaded condition; fit nip guards at both drums. Elevator: assemble per supplier manual; chain tension, bucket tipping cam position, torque limiter setting to supplier values; check every bucket pivots freely.

## 4. Feeding mechanism assembly

Position the platform to the layout (datum = tube axis; scribe X and Y lines on the floor). Anchor platform (4 x M12 chemical anchors), fit braces. Lift the weigher onto the deck (crane or forklift with spreader - remove hoppers first; mass per supplier), level the weigher base to 0.2 mm/m with its own feet. Fit collating chute; centre the chute outlet on the tube axis with a plumb line through the deck opening: ±3 mm. Place elevator; align discharge spout over the weigher cone centre ±10 mm; fit the PU drop liner; no part of the elevator may touch the weigher (vibration and weighing error).

## 5. Film system installation

Fit side plates, rollers, dancer and unwind brackets. Align: stretch a string or use a laser line from the roll centre to the collar centre; every roller square to this line within 0.2 mm across its face (feeler gauge against a square on the side plate) and level 0.1 mm/m. Fit forming set on its dowels. Fit pull-belt units: equal gap to the tube both sides (shim), belts parallel to the tube axis within 0.1 mm over 250 mm. Thread film per the threading diagram; set dancer spring so the web tension is 5-15 N (spring scale on a loop of film).

## 6. Sealing mechanism installation

Slide the jaw cartridge onto the +550 rail; set the jaw closing plane on the tube axis ±0.5 mm (both jaws touch a Ø20 test pin on the axis simultaneously). Jaw parallelism: carbon-paper print at 0.2 MPa - even over the full length; shim the rear jaw mount if needed. Knife: protrusion past the jaw face 1.5-2.0 mm when fired, fully inside when retracted; anvil slot clearance 0.3 mm. Install heaters with high-temperature anti-seize, thermocouples spring-loaded to the pocket bottom, bimetal cut-outs screwed to each bar. Vertical bar: land parallel to the tube within 0.05 mm (print test); silicone-rubber or PTFE backing strip on the tube as supplied by the former maker.

## 7. Electrical cabinet construction

Follow `ELECTRICAL/PANEL/panel_layout.md` and the released ECAD schematics. Sequence: mounting plate drilling -> ducts and DIN rails -> devices -> PE bar and bonding -> power wiring (black/light-blue, 1.5-4 mm², ferrules) -> 24 V wiring (dark blue, 0.75 mm²) -> safety circuits (two channels in separate cores, never in one multicore with the valve outputs unshielded) -> labels. Torque every terminal to the maker's value and mark with paint. Tests before energising: point-to-point check against the schematic, PE continuity, insulation resistance 500 V DC >= 1 MΩ power circuits to PE (disconnect drives/PSU as their manuals require), then staged power-up circuit by circuit.

## 8. Sensor installation

Mount per `AUTOMATION/PLC/io_map.csv`; set sensing distances from the data sheets; route M12 leads in the left conduit; teach the contrast sensor on the actual film; set cylinder switches so "closed" switches 1-2 mm before the mechanical end; label every sensor with its tag (B1...).

## 9. Motor installation

Servo on the gearbox with the supplied clamp hub (degrease, tighten to spec); check the cross shaft turns freely by hand; connect pre-assembled cables; conveyor and elevator gearmotors per supplier manuals, direction checked in MANUAL mode at 15 Hz first.

## 10-12. PLC, HMI and software installation

PLC: `AUTOMATION/PLC/README.md` (hardware configuration, import, compile, download; set IP addresses; activate OPC UA server and licence). HMI: build the 14 screens from `AUTOMATION/HMI/HMI_SPECIFICATION.md`, import tags and alarm texts from the CSV files, set user groups. Monitoring software: `SOFTWARE/README.md` (Docker Compose on a PC with two network cards).

## 13-15. Calibration, safety validation, production testing

`TESTING/calibration.md`, `TESTING/commissioning_checklist.md`, `TESTING/test_plan.md`. The machine must not run product for sale before the safety validation section is signed.
