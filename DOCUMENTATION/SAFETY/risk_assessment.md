# Preliminary risk assessment (ISO 12100 method)

Status: **design-stage draft**. It must be completed by a competent person on the built machine, with the limits of the machine, all life-cycle phases and reasonably foreseeable misuse reviewed with operators. Risk estimation: S severity (1 reversible, 2 irreversible), F frequency (1 rare, 2 frequent), P possibility of avoidance (1 possible, 2 scarcely) -> required PLr per ISO 13849-1 risk graph.

Limits: trained adult operators; indoor food factory; products per the specification; one operator at the front, one loader at the hopper; cleaning dry (brush/vacuum, wipes) - **no hose-down** in this design.

| # | Hazard / zone | Situation | S F P | PLr | Risk reduction (1 inherent design, 2 safeguarding, 3 information) | Residual risk |
|---|---|---|---|---|---|---|
| 1 | Crushing/burn between sealing jaws (1.7-2.7 kN, 150 °C) | clearing a jam, removing a bag | S2 F2 P2 | e→ **d** accepted with P1 argued (slow, visible, small stroke) - review | 2: interlocked front door (SF2), safe air dump + valve power off; 2: bag-exit tunnel sized to ISO 13857; 3: label | burn from hot jaws after opening: gloves, "HOT" pictogram, HMI shows jaw temperature |
| 2 | Cutting by knife | same | S2 F1 P2 | d | 1: knife inside jaw, fires only with jaws closed (PLC) ; 2: SF2 removes air; blade change with cut-resistant gloves and blade holder | handling of loose blade |
| 3 | Drawing-in at pull belts / film rollers | threading film | S1 F2 P1 | b | 1: belt nip faces the tube, low torque limit in SETUP; 2: inside interlocked guards, threading done with drive stopped; jog only doors closed | finger pinch at dancer (spring force < 15 N) |
| 4 | Vertical seal bar: crush + burn | threading, cleaning | S1 F2 P1 | b | 2: inside guards; bar swings out for threading | hot surface |
| 5 | Hot surfaces > 60 °C (jaws, bar, guards near them) | contact after door opening | S1 F2 P1 | b | 1: thermal barrier plates; 3: pictograms, cool-down time in manual; heaters stay on with door open by design decision - **reconsider if operators are untrained** | burn |
| 6 | Electric shock | cabinet work, damaged heater lead | S2 F1 P2 | - (IEC 60204-1) | lockable disconnector, PELV 24 V, protective bonding incl. jaw braids, heater leads in drag chain, RCD for socket | live incoming terminals: shrouded + label |
| 7 | Fire: film or product residue on jaws; SSR fails short | unattended heating | S2 F1 P2 | c | SF4 bimetal chain + PLC limit 220 °C + contactor (simulation S08: PLC trips at 221 °C before the 250 °C cut-out); heaters off in E-stop; cleaning schedule | smouldering crumbs: extinguisher (CO2) nearby |
| 8 | Fall from weigher platform / stair | cleaning weigher | S2 F2 P1 | - | ISO 14122 handrail 1100, knee rail, toe board, self-closing gate at stair head, non-slip deck | carrying hoppers on the stair: lifting plan |
| 9 | Weigher hoppers and feeders | hand in hopper during run | S1 F2 P1 | b | weigher's own guards/covers; RUN ENABLE removed by K1; maintenance mode disables weigher | pinch at gates (stepper, low force) |
| 10 | Elevator chain/buckets | clearing jam, cleaning | S2 F1 P2 | d | fixed covers (tool to open), inspection hatches interlocked (SF5), torque limiter, jam alarm 24 | reaching in at infeed: grid over hopper outlet |
| 11 | Take-off conveyor nips | bag collection | S1 F2 P1 | b | fixed nip guards at rollers, belt speed < 0.5 m/s, overload trips VFD | - |
| 12 | Stored energy: compressed air | maintenance | S2 F1 P2 | c | lockable shut-off with exhaust, soft-start on re-pressurising, pressure gauge visible | trapped air between flow control and cylinder: vent by procedure |
| 13 | Unexpected start-up | after stop, power return, reset | S2 F1 P2 | d | SF3: reset ≠ start; OB100 clears commands; alarm 30 (simulated S10, S11) | - |
| 14 | Manual handling | film roll ~37 kg at 520 mm, product bags to hopper rim +1250 | S1 F2 P1 | - | roll trolley/lift, loading step or bin tipper; roll weight on label | musculoskeletal |
| 15 | Noise | vibratory feeders, air exhaust, product on steel | S1 F2 P2 | - | silencers on exhausts, PU-lined chutes; measure, declare, hearing protection if > 80 dB(A) | to be measured |
| 16 | Dust / slips / allergens | seasoning dust, oil on floor, product change | S1 F2 P1 | - | extraction hood option at weigher, drip trays, cleaning plan, allergen changeover procedure | plant procedure |
| 17 | Food safety: foreign bodies (knife fragments, bolts, PTFE tape, film), lubricant, pests in idle machine | production | - | - | detectable (blue) plastics, captive fasteners over product zone, knife integrity check per shift, H1 grease, covers when idle, metal detector as CCP (industrial config) | HACCP study by the food business |
| 18 | Software / parameter error (e.g. 0 °C band, wrong recipe) | setter error | S1 F1 P1 | a | limits in HMI and PLC, user levels, recipe locked while running | bad seals → quality loss, not injury |
| 19 | Cyber / remote | monitoring PC compromised | S1 F1 P1 | - | PC is read-only OPC UA client; safety hard-wired; isolated subnet | loss of data only |

Open points for the final assessment: verify stopping/retraction time of jaws against door opening time (ISO 13855 - a guard-locking switch is required if a jaw can still be reached while closing); decide heaters-on-with-door-open policy; platform gate interlock scope; noise measurement.

**Safety interlocks must never be bypassed.** The control system offers no bypass, muting or "service override" function, and this documentation does not describe one.
