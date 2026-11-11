# 04 - Motor, drive and heater wiring

All terminal names in this file are (confirm) items: use the current manufacturer manual.

## M1 film-pull servo (T1 SINAMICS V90 PN 6SL3210-5FB10-4UF1 + 1FL6034-2AF21-1AA1)

| Connection | From | To | Cable |
|---|---|---|---|
| Line 1AC 230 V | F4 | T1 L1, L3 (1AC connection per manual) | 3G1.5 mm² |
| Motor power | T1 U V W PE | M1 | MOTION-CONNECT 300 power, 5 m, shield clamped at drive plate |
| Encoder | T1 X8 | M1 encoder | MOTION-CONNECT 300 incremental encoder cable |
| 24 V control | F13 | T1 X6 24 V / M | 2 x 0.75 mm² |
| STO | K1 23-24, 33-34 | T1 STO1, STO+, STO2 | 3 x 0.75 mm² shielded; factory bridges removed |
| PROFINET | switch | T1 X150 P1 | Cat5e industrial, RJ45 |
| Braking | - | internal resistor sufficient (0.6 kg moved mass) | check drive alarm history during commissioning |

Parameters to set (Siemens V-ASSISTANT): control mode speed control with PROFINET (telegram 3) for the S7-1200 technology object, motor ID from the encoder label, stiffness auto-tuning with film threaded, torque limit 200 %, STO acknowledge behaviour.

## M2 elevator and M3 take-off (T2, T3 VFD 1AC 230 V in / 3AC 230 V out)

| Signal | VFD terminal function | PLC |
|---|---|---|
| Run forward | DI1 | Q8.1 (T2), Q8.2 (T3) through K1 enable contact (interface relay) |
| Speed reference | AI 4-20 mA | QW64 (T2), QW66 (T3) |
| Fault relay (NO, closed = healthy) | RO | I8.7 (T2), I9.0 (T3) |

Motor data: 230/400 V motors connected in **delta** for the 3 x 230 V drive output; set nameplate current, 50 Hz, ramp 2 s up / 1 s down, minimum 15 Hz for self-ventilated gearmotors, electronic thermal overload on, current limit 150 % so that a jam trips the drive (alarm 24 / 25) before the gearbox is damaged. Elevator: add a shear pin or torque limiter on the chain drive.

## Heaters

```
L2 ─ F2 ─ KM1 ─┬─ F21 ─ V1 (SSR, zero-cross, 25 A on heat sink) ─ X2:1 ── Z1a 250 W ┐ parallel ── X2:2 ─ N
               │                                                        Z1b 250 W ┘
               ├─ F22 ─ V2 ─ X2:3 ── Z2a + Z2b (2 x 250 W parallel) ── X2:4 ─ N
               └─ F23 ─ V3 ─ X2:5 ── Z3 300 W ── X2:6 ─ N
SSR control: PLC Q0.0 / Q0.1 / Q0.2 (+) ─ SSR A1 ; SSR A2 ─ 0 V
```

* SSRs fail short-circuit more often than open: this is why KM1 (dropped by PLC limit alarm, E-stop and the bimetal chain) exists. Simulation scenario S08 exercises this case.
* SSR dissipation ≈ 1.2 W per ampere: 3 SSRs ≈ 7 W, mount on a common heat sink at the top of the plate.
* Moving jaws: heater and thermocouple leads in a small drag chain with strain relief at both ends; glass-silk or PTFE insulated, minimum bend radius 10 x diameter; plug connectors at the jaw so a jaw can be swapped without opening the cabinet.
