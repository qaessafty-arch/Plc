# 02 - Power distribution

Values from `03_ENGINEERING_CALCULATIONS.md` section 7 (connected 4.69 kW; L1 9.4 A, L2 6.9 A, L3 7.6 A).

```
 L1 L2 L3 N PE   supply cable 5G4 mm2 (confirm prospective short-circuit current on site)
  │  │  │  │  │
 ┌┴──┴──┴──┴┐ │   Q0  main disconnector 4P 25 A, lockable OFF, door-coupled handle (IEC 60204-1 5.3)
 └┬──┬──┬──┬┘ │
 ┌┴──┴──┴──┴┐ │   F0  MCB C16 4P 10 kA   (surge arrester type 2 downstream recommended: unstable grids)
 └┬──┬──┬──┬┘ │
  │  │  │  N──┼────────────── N bar (blue)
  │  │  │     └────────────── PE bar (green/yellow) - star point, 10 mm2 to frame, 6 mm2 to door
  │  │  │
  L1─┬─ F1 C10 2P ───────────── X1:1,2   Weigher cabinet (own supply disconnect + protection inside)
  │  ├─ F6 RCBO B10 30 mA A ─── X1:3,4   Service socket (programming laptop) + cabinet light
  │  └─ F7 C4  1P+N ──────────── X1:5,6   Vibratory feeder controller, date coder
  │
  L2─┬─ F2 C10 1P+N ─ KM1 (3 poles in series/parallel as AC-1) ─┬─ F21 gG 4 A ─ V1 SSR ─ X2:1,2  Z1 500 W
  │  │                                                          ├─ F22 gG 4 A ─ V2 SSR ─ X2:3,4  Z2 500 W
  │  │                                                          └─ F23 gG 2 A ─ V3 SSR ─ X2:5,6  Z3 300 W
  │  └─ F3 C4 1P+N ──── G1 24 V DC 10 A ── F10..F13 electronic branches (see 05)
  │
  L3─┬─ F4 per V90 manual (expected C10 or fuse 6-10 A, confirm) ── T1 servo drive L1/L2(N) ── M1
     └─ F5 C10 1P+N ─┬─ T2 VFD 0.37 kW ── M2 elevator 3x230 V (motor in delta)
                     └─ T3 VFD 0.37 kW ── M3 take-off 0.18 kW 3x230 V
```

## Protection table

| Circuit | Load | I calc. A | Device | Conductor | Notes |
|---|---|---|---|---|---|
| Incoming | 4.69 kW | 9.4 max phase | Q0 25 A, F0 C16 | 5G4 mm² | voltage drop 0.5 % at 30 m |
| Weigher | 1.5 kW | 7.2 | F1 C10 | 3G1.5 mm² | supplier value to confirm |
| Heaters total | 1.3 kW | 5.7 | F2 C10, KM1 | 1.5 mm² | each zone fused separately; SSR needs semiconductor/fast fuse if the SSR maker requires |
| Zone 1 / 2 | 500 W | 2.2 | gG 4 A | 1.0 mm² silicone/PTFE at jaw | high-temperature flexible lead in drag chain |
| Zone 3 | 300 W | 1.3 | gG 2 A | 1.0 mm² | |
| 24 V PSU | 240 W | 1.2 | F3 C4 | 1.5 mm² | inrush: C curve |
| Servo drive | 0.4 kW | 2.9 (peak 3x short) | per manual | 1.5 mm² + shielded motor cable | line filter integrated or external per manual |
| VFDs | 0.55 kW total | 4.9 | F5 C10 | 1.5 mm², shielded motor cables | motor thermal protection by VFD parameter + PTC if fitted |
| Socket | - | - | RCBO 10 A 30 mA | 1.5 mm² | not for production loads |

Residual-current note: if the installation requires an RCD upstream of the machine, drives call for type B / B+ with 300 mA; a 30 mA type A/AC device upstream will nuisance-trip and may be blinded by DC leakage.

## Earthing and EMC

* TN-S: N and PE never joined inside the machine.
* Protective bonding: frame, cabinet, door, mounting plate, platform, elevator, weigher, conveyor frames, each jaw carriage (flexible braid across the moving joint); continuity test <= 0.1 Ω (IEC 60204-1 18.2).
* Heater sheaths are earthed through the jaw; an insulation fault trips the zone fuse. Check insulation resistance of each heater >= 1 MΩ before first power-up (moisture in new cartridge heaters is common).
* Zinc-plated mounting plate; drive and VFD bolted bare-metal; motor cable shields clamped 360° at both ends; motor cables >= 200 mm from signal cables, crossing at 90°.
* Thermocouples: ungrounded junctions, type K extension cable, routed away from heater and motor cables; module in the left (cool, quiet) part of the cabinet.
* 0 V of the 24 V supply bonded to PE at G1 only (PELV); insulation fault then trips a branch fuse instead of causing unintended operation.
* Static: film unwinding charges the web; fit a passive static eliminator (earthed tinsel/carbon brush) before the forming collar.
