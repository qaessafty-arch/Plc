# Cabinet A0 - layout and thermal check

Enclosure: 1000 (H) x 600 (W) x 300 (D), stainless 1.4301, IP54 minimum (IP65 door seal if the room is washed down), mounted on the right side of the bagger frame (CAD part `B15_electrical_cabinet`). Door: main disconnector handle (interlocked with door), nothing else - the HMI and buttons are on the separate operator station (`B16_hmi_station`) so the cabinet is opened only by electricians.

```
┌──────────────────────────────────────────────────────────┐
│ Q0   F0   F1 F2 F3 F4 F5 F6 F7  │  KM1  V1 V2 V3 (heat   │  row 1: power in, protection, heater switching
│ (top-left incoming, gland below)│        sink, top right)│
├──── wiring duct 60x80 ─────────────────────────────────── ┤
│ G1 24V   F10-F13   K1  K2   KA1..KA8 interface relays     │  row 2: 24 V, safety, relays
├──── wiring duct ───────────────────────────────────────── ┤
│ A1 CPU 1215C | SM1223 | SM1231TC | switch │  T1 V90  T2 T3 │  row 3: PLC left (cool, quiet), drives right
│                                           │  (100 mm free  │         with clearance above/below per manuals
│                                           │   above/below) │
├──── wiring duct ───────────────────────────────────────── ┤
│ X10 X11 X12 X13 X14 X20 X21 (24 V)  ║  X1 X2 X3 (AC) PE   │  row 4: terminals - 24 V left, AC right, divider
└──────────────────────────────────────────────────────────┘
   glands: signal cables bottom-left, power and motor cables bottom-right (EMC clamps on plate)
```

Segregation: AC power and motor cables use the right-hand ducts, 24 V and signals the left; thermocouple pairs go directly to the module without sharing a duct with heater wiring.

## Heat balance (estimate)

| Source | W |
|---|---|
| CPU + modules + HMI supply losses | 20 |
| 24 V PSU (240 W, 90 %) at 40 % load | 11 |
| V90 0.4 kW drive | 25 |
| 2 VFDs | 30 |
| 3 SSRs | 7 |
| Contactors, relays, safety relays | 12 |
| **Total** | **~105** |

Enclosure surface (IEC 60890, wall-mounted on one side): ≈ 1.9 m² effective; stainless steel k ≈ 5.5 W/m²K → ΔT ≈ 105 / (5.5 x 1.9) ≈ **10 K**. With 35 °C ambient the interior is ~45 °C: inside the 50 °C limit of the CPU [verified data sheet value for horizontal mounting: check installed orientation] but with little margin for Iraqi summer conditions (ambient 40-45 °C in unconditioned halls). **Fit a filter fan (≥ 50 m³/h, IP54 filter) or a small cabinet cooler if ambient can exceed 35 °C**, and use the 4th thermocouple channel (cabinet air) for a warning at 45 °C.

## Marking and documentation in the cabinet

Device tags as in the schematics; wire numbers = terminal numbers; warning labels (voltage present with disconnector off on the incoming terminals; multiple supplies if the weigher has its own feeder); schematics pocket in the door; nameplate with supply data, full-load current 9.4 A, largest motor, short-circuit rating, serial number and year (IEC 60204-1 clause 16).
