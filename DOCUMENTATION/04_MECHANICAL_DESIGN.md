# 04 - Mechanical design

Coordinate system (same as CAD): origin on the floor at the forming-tube axis; X to the right of the operator, Y to the rear (film side), Z up. All dimensions mm. Numbers are from `machine_params.py` and are **preliminary** unless stated.

## 1. Choice of dosing principle for fragile snacks

| Principle | How it meters | Accuracy on chips | Gentleness | Speed | Cost | Verdict |
|---|---|---|---|---|---|---|
| Volumetric cup filler | telescopic cups on a turntable | poor: bulk density of chips varies ±15-25 % with breakage, oil, seasoning | poor (shearing at cup edges) | high | low | reject for chips; acceptable for nuts, seeds |
| Auger filler | screw revolutions | n/a | destroys pieces | - | low | reject (powders only) |
| Linear weigher (1-4 heads) | vibratory trickle into a weigh bucket until target | ±2-5 g at 40 g: one chip weighs 1-2.5 g, so the last piece decides | good | 8-25 /min, falls sharply for bulky product | low-medium | educational prototype only |
| **Multihead combination weigher** | 10-14 partial charges, best combination chosen | simulated SD 0.5-0.7 g and ~1.4 % give-away at 40 g for an assumed 30 % charge spread (`SIMULATION/weigher_results.json`) | good with low drop heights, dimpled surfaces, soft-landing hoppers | 40-70 /min (10 head) | high | **selected** |
| Counting / tray filling | piece count by vision or channels | exact count, not weight | very good | low | high | only for stacked biscuits (different machine: flow-wrapper) |

The simulation also quantifies why a 4-head unit is unsuitable: same product, 4 heads -> 4.7 % give-away and no valid combination in ~70 % of cycles.

Rules derived for the weigher specification: 10 heads, 1.6 L hoppers (2.5 L for bags > 100 g of chips), dimpled 304 contact parts, top-cone and linear feeder amplitude per recipe, hopper gates with stepper drive and soft-close profile, collating chute at >= 60° with a PU-lined ring to break the fall, maximum single fall <= 300 mm inside the weigher.

Biscuits and crackers note: random-packed small biscuits/crackers run on this line. **Stacked or oriented biscuits do not** - they need a slug loader and a horizontal flow-wrapper, which is a different machine.

## 2. Line modules

| Item | Module | Make/buy | CAD part |
|---|---|---|---|
| E02 | Infeed hopper 150 L with vibratory tray | buy with elevator or fabricate | `E02_infeed_hopper` |
| E01 | Z-bucket elevator, 1.8 L PP buckets, 0.37 kW, VFD | buy to interface drawing | `E01_z_bucket_elevator` |
| W01 | 10-head multihead weigher with collating chute | buy | `W01_multihead_weigher` |
| P01 | Weigher platform 1900 x 1900, deck +2000, stair, handrail | fabricate | `P01_weigher_platform` |
| B01-B17 | VFFS bagger | design and build | `B01`...`B17` |
| C01 | Take-off conveyor 1800 x 300, inclined | buy or build | `C01_takeoff_conveyor` |

## 3. Bagger sub-assemblies

| # | Sub-assembly | Key data | Material | Mounting / interfaces | Operating requirements |
|---|---|---|---|---|---|
| B01 | Main frame | 1000 x 1300 x 1500; SHS 50 x 50 x 2; rails at +550 (jaw carriage) and +1150 (belt carriage); 8 mm top plate with Ø(tube+180) opening | 1.4301, TIG welded, pickled/passivated, ends capped | 4 x M16 hygienic feet, ±25 mm; **not** bolted to the platform | level 0.5 mm/m; all rails square within 1 mm over the diagonal |
| B02/B03 | Film unwind | roll max Ø400 x 420, 76 mm core, ~37 kg; shaft Ø40 with cone chucks or air shaft; axis at Y +750, Z +520 | shaft 1.4301 | saddle brackets with safety latches on the rear posts; roll loaded from the rear at 520 mm height (trolley) | friction brake or 60 W powered unwind controlled by dancer |
| B04 | Guide rollers | 5 idlers Ø50 x 470 face, ball bearings, TIR <= 0.1 mm | anodised aluminium (not product contact) | between two 6 mm side plates 470 apart | parallel within 0.2 mm over the face; one roller with ±5 mm lateral tracking adjustment |
| B05 | Dancer | pivoting arm, roller Ø44, stroke ~250 mm of web storage; two inductive sensors (high/low) | aluminium | pivot on side plates | web tension 5-15 N adjustable by spring/low-friction cylinder |
| - | Registration sensor bracket | slides ±100 mm along the web, scale engraved | 1.4301 | on side plate between dancer and collar | sensor 9-12 mm from film per sensor data sheet |
| B07 | Forming collar | for the reference bag: tube OD 101.9, collar height ~130, wing angle ~28°; **format part**, one per bag width | 1.4301, 2.5 mm, dimpled or satin for metallised film | located by 2 dowels + 2 hand knobs on the top plate | buy from a former specialist: the developed shape decides film tracking; a home-made collar is the most common cause of wrinkles |
| B06 | Forming / fill tube | OD = 2W/π (101.9 for W 160), wall 2, length 690, bottom end 60 above jaw plane; optional internal N2 lance and air relief flats | 1.4301 tube, inside Ra <= 0.8, longitudinally polished | integral with collar base plate | concentric to belt and jaw centre within 0.5 mm |
| B08 | Infeed funnel | Ø300 top to tube ID, 250 high; capacitive blockage sensor in the wall | 1.4301 2 mm | drops onto the tube top, clamp band | mates with weigher chute with a 30 mm overlap, **no rigid contact** |
| B09/B10 | Pull-belt units | 2 units, belt 20 wide, 250 mm contact, drive pulley Ø60; pressed against the tube by Ø20 compact cylinders (open for threading) | aluminium housings, PU/rubber-faced timing belts | on linear slides on the +1150 rail; lateral adjustment for tube sizes 50-127 | belt pressure 0.15-0.25 MPa, equal both sides |
| B11 | Belt drive | 0.4 kW servo + 5:1 planetary + cross shaft with two right-angle stages (belts mechanically synchronous) | - | servo on the left side outside the product zone | peak 0.47 N.m at motor (37 % of rated), 1273 rpm |
| B12 | Vertical seal | bar 320 x 25, land 10 mm, 300 W cartridge, type K TC, PTFE-glass cover; cylinder Ø40 x 30 | aluminium bar, 1.4301 bracket | front of tube; swings away for threading | 0.2 MPa on the land (calc. SF 1.06 at 0.6 MPa - **marginal**: use Ø50 if seal trials need more pressure) |
| B13 | Jaw assembly | two jaws 240 x 30 x 40, serration 1.5 mm pitch vertical, 2 x 250 W cartridges each, TC + bimetal cut-out each; knife slot in rear jaw, anvil groove in front jaw; 2 guide rods Ø20, 4 bushings; Ø63 x 60 cylinder with rack-and-pinion (or lever) synchroniser so both jaws meet on the tube axis; opening 70 mm | jaws: tool steel hardened 48-52 HRC, nickel plated; carriage aluminium; rods hard chrome | carriage on the +550 rail; whole cartridge removable to the front after 4 screws and 2 plugs | seal force required 2304 N; available 1683 N at 0.6 MPa (SF 0.73) - **see open issue below** |
| - | Knife | serrated 220 mm blade, Ø25 x 20 cylinder, retracted by spring-return valve | hardened stainless | inside rear jaw | fires only with jaws closed (PLC interlock + geometry) |
| B14 | Guards | front double door 6 mm polycarbonate, rear door at film side, fixed side panels; gap to hazards per ISO 13857 | PC + 1.4301 frames | coded interlock switches top edge | bag exit opening: tunnel long enough that the jaws cannot be reached (ISO 13857 table 4) |
| B15 | Cabinet | 1000 x 600 x 300 on the right side, rear half | 1.4301 | 4 x M10 to frame, vibration isolated | door clearance 800 |
| B16 | Operator station | KTP700 + start/stop/reset + E-stop on a swivel arm, front right, 1400 above floor | - | - | - |

### Open mechanical issue found by calculation

The calculation sheet shows the Ø63 jaw cylinder delivers 1683 N against a requirement of 2304 N (0.40 MPa on two 12 mm seal lands, 240 mm long). The requirement is itself an assumption. Options, in order of preference: (1) narrow the seal lands to 2 x 8 mm (typical for snack laminates) -> 1536 N required, SF 1.10; (2) Ø80 cylinder (2714 N, +60 % air for this actuator); (3) toggle linkage with ~3:1 force gain at closure. **Decision deferred to seal trials on the real film** (test T-SEAL-01); the frame rail and carriage are dimensioned for the Ø80 cylinder so that all three options remain open.

## 4. Protecting fragile product

| Location | Measure |
|---|---|
| Infeed hopper | vibratory tray instead of a gate valve; bed depth <= 80 mm |
| Elevator | buckets filled to 60 %; chain speed 0.2 m/s; discharge chute lined with PU, fall <= 250 mm onto the weigher cone |
| Weigher | dimpled plates, low feeder amplitude with longer feed time, soft-close gates, staggered dump (5-20 ms between heads) to lengthen the charge and avoid bridging in the tube |
| Collating chute and funnel | >= 60° walls, no steps; funnel overlaps tube |
| Fill tube | the 1.9 m fall is unavoidable; product lands on film supported by the closed jaws; larger tube than strictly needed is preferred (tube ID >= 1.5 x largest piece) |
| Jaws | product-in-seal is prevented by timing: the dump is requested before the film pull (recipe value "dump lead") so the charge lands on the closed jaws and by an optional stripper/"bag tapper" above the jaws; no mechanical stager for chips |
| Take-off | bag falls <= 300 mm onto an inclined soft belt |

## 5. Maintenance access and adjustability

Feet ±25 mm; jaw cartridge and pull-belt units exchange from the front; forming set lifts out upward after releasing two knobs (funnel removed first, hence the 500 mm overhead clearance); heaters and thermocouples plug-connected at the jaw; film threading path marked on the side plate; all lubrication points (jaw bushings, cross-shaft bearings) outside the product zone with H1 food-grade grease.

## 6. Mass estimate

From the CAD model with section-fill corrections [assumption]: line ≈ 1.3 t (bagger ≈ 0.35 t, platform ≈ 0.27 t, weigher ≈ 0.2-0.4 t per supplier, elevator + hopper ≈ 0.45 t). Per-part values: `CAD/COMPONENTS/manifest.json`.
