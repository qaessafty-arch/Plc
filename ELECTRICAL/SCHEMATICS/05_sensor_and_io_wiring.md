# 05 - Sensor wiring, I/O principles and weigher interface

I/O allocation: `AUTOMATION/PLC/io_map.csv`. Terminals: `WIRING/terminal_plan.csv`.

## 24 V DC branches

| Branch | Rating | Feeds |
|---|---|---|
| F10 | 4 A | CPU L+, signal modules L+, HMI, Ethernet switch |
| F11 | 2 A | all sensors (X10 distribution), push-button contacts |
| F12 | 4 A | safety relays K1/K2 -> safe bus -> valves, stack light, interface relays |
| F13 | 2 A | servo and VFD 24 V control supply |

Common alarm contact of the electronic fuse block -> I9.3.

## Standard sensor wiring (3-wire PNP, M12 A-coded)

```
 X10:+ (F11) ── brown (pin 1) ─┐
                               │ sensor
 PLC input  ── black (pin 4) ──┤   PNP NO: 24 V on the input when the target is present
 X10:0V ────── blue  (pin 3) ──┘
```

* All inputs are sourcing sensors into sinking (1M = 0 V) PLC inputs.
* "Fail-safe sense" for stop-type signals: STOP button, VFD healthy, weigher no-fault, cut-out chain, fuse alarm are all normally-closed/energised-when-OK so a broken wire stops the machine.
* B10 registration sensor: shielded cable, separate from valve cables, PLC input filter 0.1 ms, teach on mark/background with the film stationary.
* Cylinder reed switches: 2-wire types must be compatible with the PLC input leakage/current thresholds; prefer 3-wire PNP solid-state switches.
* Thermocouples: `B30+ -> AI0+`, `B30- -> AI0-`, type K extension wire all the way to the module; unused channel 3 measures cabinet air or is short-circuited and disabled.

## Weigher interface X20 (volt-free contacts in both directions)

| Signal | Direction | PLC | Timing |
|---|---|---|---|
| READY | weigher -> bagger | I8.0 | high when a valid combination is waiting |
| DUMP DONE | weigher -> bagger | I8.1 | >= 50 ms pulse after hoppers opened |
| NO FAULT | weigher -> bagger | I8.2 | high = healthy |
| FEED REQUEST | weigher -> bagger | I8.6 | high = top cone needs product (runs elevator) |
| DUMP REQUEST | bagger -> weigher | Q0.6 via relay | 100 ms pulse; weigher must answer within its configured delay |
| RUN ENABLE | bagger -> weigher | Q9.2 via relay, in series with K1 contact | low = weigher stops feeding and dumping |

The weigher keeps its own emergency-stop input; wire a K1 contact pair to it so that one E-stop chain covers the whole line (confirm with the weigher supplier's manual).
