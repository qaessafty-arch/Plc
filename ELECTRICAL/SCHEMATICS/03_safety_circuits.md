# 03 - Safety-related control circuits

Hard-wired, independent of the standard PLC. Target from the risk assessment (`DOCUMENTATION/SAFETY/risk_assessment.md`): **PL d, category 3** for guard interlocking of the jaw area and for emergency stop. The figures below are a design intent; the achieved PL must be calculated (SISTEMA) with the B10d / PFHd values of the components actually bought, and validated per ISO 13849-2.

## Safety functions

| SF | Trigger | Reaction | Stop category (IEC 60204-1) |
|---|---|---|---|
| SF1 Emergency stop | any of S10-S13 (HMI station, rear film side, platform, elevator hopper) | K1 opens: safe 24 V bus off (valves Y1-Y5 de-energise -> jaws, seal bar, knife retract by spring-return valve), dump valve exhausts the machine, STO to servo, VFD enables removed, heater contactor KM1 drops, weigher enable removed | 0 for pneumatics and heaters; servo STO (uncontrolled stop is acceptable: film mass is negligible) |
| SF2 Guard door interlock | front or rear door opened (B20, B21 coded switches) | K2 opens: safe 24 V bus off, dump valve, STO. Heaters stay on (burn hazard remains guarded by door and labelled) | 0 |
| SF3 Prevention of unexpected start | after SF1/SF2 | manual reset at K1/K2 with monitored reset button S3, then separate START | - |
| SF4 Over-temperature | bimetal cut-outs F20-F22 on each bar (250 °C, manual reset) | series chain opens KM1 coil circuit directly | - (independent of PLC and SSRs) |
| SF5 Platform / elevator | platform gate switch and elevator covers in series with SF2 chain (elevator run enable) | elevator and feeder stop | 0 |

## Circuit (principle)

```
+24 V (F12) ─┬─ S10 ─ S11 ─ S12 ─ S13 ──(ch.1)──► K1 S11-S12 (confirm terminal names in PNOZ s4 manual)
             └─ S10'─ S11'─ S12'─ S13'──(ch.2)──► K1 S21-S22        two-channel, cross-fault detecting
             S3 reset (NO) in series with NC mirror contacts of KM1 and dump-valve monitor ──► K1 S34 (monitored reset)

K1 13-14 ─► K2 supply path / enable chain
K1 23-24 ─► STO1 of T1 (V90)         K1 33-34 ─► STO2 of T1          (dual-channel STO, confirm V90 STO wiring)
K1 41-42 (NC aux) ─► PLC I0.4 inverted status is taken from a spare NO via interface relay (status only)

B20 / B21 coded door switches (2 channels each, in series or on separate inputs) ──► K2 S11-S12 / S21-S22
K2 13-14 ─► "safe 24 V" bus  ──► common of valve outputs Y1, Y2, Y3, Y5  (PLC outputs switch the 0 V/plus side downstream)
K2 23-24 ─► Y0 safety dump valve coil A      K2 33-34 ─► Y0 coil B (redundant dump valve, monitored)
K1 enable AND K2 not required ─► KM1 coil:  +24 V ─ K1(NO) ─ F20 ─ F21 ─ F22 (bimetal NC) ─ PLC Q8.0 ─ KM1 A1
```

Notes
* PLC output modules are supplied from the normal 24 V; only the *load side* of the valve outputs comes from the safe bus, so a stuck PLC output cannot move an actuator after K2 has opened. Check with the Siemens manual that back-feeding of the output group is excluded for the chosen wiring (alternative: switch the valve commons with K2 contacts directly).
* 5/2 valves are monostable (spring return): loss of signal or air returns jaws to OPEN and knife to retracted. Check on the real jaw that gravity/residual pressure cannot close it; add a pilot-operated check valve only where a falling load exists (none here).
* Residual risks kept after stop: hot jaws (> 60 °C for ~30 min), stored air downstream of flow controls (dumped by Y0), film roll inertia.
* Never bridge door switches for cleaning or setting. Jogging with an open door is **not** provided in this design; if a later risk assessment demands it, it needs an enabling device and safely-limited speed, i.e. a different drive concept.

## Preliminary PL estimate (to be replaced by SISTEMA calculation)

| SF | Structure | Sensor | Logic | Actuator | Expected |
|---|---|---|---|---|---|
| SF1 | cat. 3 | E-stop 2 NC, B10d 100 000 (typ.) | PNOZ s4 (PL e capable) | redundant dump valve + STO | PL d |
| SF2 | cat. 3 | coded RFID switch (PL e capable type 4, ISO 14119 high coding) | PNOZ s4 | redundant dump valve + STO | PL d |
| SF4 | cat. 1 (well-tried bimetal) | - | - | KM1 with mirror contact read by PLC (alarm 31) | PL c - back-up to PLC limit alarm |

Series connection of door switches lowers diagnostic coverage (fault masking, ISO/TR 24119): with two frequently used doors use separate inputs or switches with OSSD outputs and diagnostic chaining.
