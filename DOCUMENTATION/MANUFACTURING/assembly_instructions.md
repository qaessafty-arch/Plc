# Assembly instructions and format change

## Assembly sequence (site)

| # | Operation | Hold point |
|---|---|---|
| 1 | Mark datum lines on the floor (tube axis), check floor level and loading capacity | floor ±5 mm |
| 2 | Place bagger frame (B01) on its feet, level, do not anchor yet | 0.5 mm/m |
| 3 | Mount cabinet (B15) and operator station (B16) | - |
| 4 | Install film path: unwind (B03), rollers (B04), dancer (B05), sensor bracket | roller alignment record |
| 5 | Install belt carriages (B09/B10) and servo drive (B11) | belt parallelism record |
| 6 | Install jaw cartridge (B13) and vertical seal (B12); pneumatics: air preparation, dump valve, manifold, tubing with flow controls at the cylinders (meter-out) | print tests |
| 7 | Install forming set (B06/B07) and funnel (B08) | tube on axis ±0.5 |
| 8 | Guards and doors (B14), interlock switches | gaps per ISO 13857 measured |
| 9 | Erect platform (P01) around the bagger: **20 mm minimum gap everywhere**, anchor, brace | no contact with bagger |
| 10 | Lift weigher (W01) onto the platform, level, fit chute | chute on axis ±3 |
| 11 | Place elevator (E01) and hopper (E02), anchor, fit discharge liner | no contact with weigher |
| 12 | Place take-off conveyor (C01) | bag drop <= 300 |
| 13 | Field wiring per cable schedule; bonding conductors; air connection | point-to-point test |
| 14 | Anchor the bagger after a first film run confirms alignment | - |
| 15 | Commissioning checklist | signed |

Tightening: stainless fasteners with anti-seize (galling); M6 8 N.m, M8 20 N.m, M10 40 N.m, M12 70 N.m, M16 170 N.m (A2-70, lubricated - confirm against the fastener supplier's table).

Exploded view for orientation: `CAD/EXPLODED/SPM-420_exploded.step` / `.svg`.

## Film threading (machine in SETUP, guards closed for every jog)

1. Load the roll on the shaft, print side per the diagram, centre it with the chucks, close the latches.
2. Lead the web under roller 1, over the dancer roller, over rollers 2-4, past the registration sensor, onto the collar wings.
3. Open the pull belts and swing the vertical bar away. Cut the film end to a point, pull it down around the tube by hand until it is below the belts; overlap the edges for a lap seal (or fin them between the fin wheels, if fitted).
4. Close belts and bar, close the doors, jog forward 300 mm, check tracking: the overlap must stay constant; correct with the tracking roller, never by tilting the collar.
5. Make 5 empty bags (SETUP -> empty bag), check seals and length, then go to AUTO.

## Format change (bag width) - target 15 min

1. Stop, heaters may stay on; mode OFF; open front door (interlock).
2. Remove funnel (lift), release two knobs, lift the forming set out upward; place it on its storage peg (never on the floor: a dented collar is scrap).
3. Fit the new forming set on the dowels; refit funnel.
4. Move both pull-belt units to the new tube diameter using the scale; move the vertical bar stop.
5. Change the film roll to the new web width (2 x bag width + 20 mm); centre it; move the registration sensor if the mark position changed.
6. Select the recipe (bag length, temperatures, speed load automatically); at the weigher select the matching product program.
7. Thread, 5 empty bags, 5 filled bags to the scale, release.

## Wear parts and intervals (to start with; adjust from records in the monitoring software)

| Part | Typical trigger |
|---|---|
| PTFE-glass tape on vertical bar | daily check; replace when glazed or torn |
| Knife | ragged cut; ~0.5-1 million cuts [assumption] |
| Pull belts (pair) | slip marks / length drift; ~1 million bags [assumption] |
| Cartridge heaters | open circuit; keep one set in stock |
| Thermocouples | ±3 K against reference; 6-monthly check |
| Jaw bushings | play > 0.1 mm at jaw face |
| Cylinder seals, valve | cycle time growth (visible as alarm 6/7 margins on the diagnostics screen) |
