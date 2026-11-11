# Cleaning, hygiene and lockout/tagout

## Energy isolation points (LOTO)

| Energy | Isolation device | Location | Verification before work |
|---|---|---|---|
| Electrical 400/230 V | Q0 main disconnector, padlockable in OFF (3 padlock hasp) | cabinet door | try START at HMI (dark) / voltage test on F0 outgoing by electrician |
| Weigher supply (if separately fed) | weigher isolator, padlockable | weigher cabinet | weigher display off |
| Compressed air | lockable shut-off valve with exhaust on the air preparation unit | left side of bagger | gauge at 0; operate a valve manual override |
| Thermal | none (wait) | - | HMI/thermometer: jaws < 50 °C before touching (≈ 30-40 min) |
| Gravity | film roll (latches), weigher hoppers (remove to rack) | - | - |
| Nitrogen (option) | cylinder/line valve, lockable | supply | flowmeter at 0; ventilate - asphyxiation risk in closed rooms |

Procedure: notify -> normal stop -> isolate each energy -> lock and tag (one lock per person) -> dissipate/verify -> work -> remove tools, refit guards -> remove locks (by their owners only) -> restore air slowly, then power -> functional test of E-stop and door interlocks before production.

Tasks that require LOTO: any work inside the jaw area with tools, knife change, heater/thermocouple change, belt change, elevator chain work, cabinet work. Tasks done under interlocked-guard protection only (no LOTO): clearing a bag from the jaws with the door open, threading film, removing crumbs with a brush.

## Hygienic design measures in this design

Stainless 1.4301 frame with capped tubes; product-contact parts listed in `04_MECHANICAL_DESIGN.md`; tool-less removal of funnel, forming set, weigher hoppers and elevator buckets; no painted surfaces or cable trays above open product; cables in closed stainless conduit or sloped wire baskets; cabinet top sloped 15° (add at detail design); drip/crumb tray under the jaws and under the elevator boot.

Not provided (state limits honestly): the machine is **dry-clean only**. Standard drives, sensors (IP65/67) and bearings are not rated for hose-down; the frame has bolted joints and horizontal rails that would hold water.

## Cleaning plan (dry snack plant - adapt to the site HACCP plan)

| Frequency | Task | Method |
|---|---|---|
| Every stop > 10 min | brush crumbs from jaw faces while hot (brass brush, door open, heat gloves) | never steel tools on serrations |
| Each shift | jaw faces, knife slot, vertical bar PTFE cover; photo-eyes; crumb trays; floor | brush, vacuum (ATEX not required for these quantities - verify for fine seasoning dust) |
| Daily / product change | weigher: top cone, feeder pans, feed and weigh hoppers, chute, funnel, fill tube inside; elevator buckets if product/allergen changes | remove parts to a wash room; wash, rinse, **dry completely**, food-grade alcohol wipe; inspect and refit |
| Weekly | pull belts (isopropanol wipe), rollers, dancer, cabinet filter mats, air filter drain | - |
| Monthly | elevator inside, platform deck, under the machine | covers off under LOTO |
| Allergen changeover | full dry clean + visual inspection sign-off + first bags discarded per plant procedure | record in batch record (monitoring software batch notes) |

Cleaning agents: neutral or mild alkaline detergent and potable water for removed parts; no chlorinated cleaners on stainless at temperature; no compressed-air blow-down around open product (spreads allergens and dust) - vacuum instead.
