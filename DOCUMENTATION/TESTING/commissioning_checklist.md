# Commissioning checklist

Machine no.: ________  Date: ________  Commissioning engineer: ________  Customer witness: ________

## A. Mechanical (power and air isolated)

- [ ] Layout matches GA-002: datum, clearances 1200 front / 1000 rear / 800 ends, ceiling >= 4400
- [ ] Bagger level <= 0.5 mm/m; platform anchored and braced; 20 mm gap bagger-platform everywhere
- [ ] Weigher level <= 0.2 mm/m; chute outlet on tube axis ± 3 mm; elevator not touching weigher
- [ ] Rollers parallel 0.2 mm, turn freely; dancer moves freely; film roll latches closed
- [ ] Forming set seated on dowels; tube on jaw centre ± 0.5 mm; belts parallel 0.1 mm
- [ ] Jaw print test even over 240 mm; knife protrusion 1.5-2.0 mm, retracted fully
- [ ] All guards fitted, fasteners captive over product zone, gaps per ISO 13857 measured and recorded
- [ ] No loose parts, swarf or packaging in hoppers, tube, chutes; product-contact surfaces cleaned

## B. Electrical (IEC 60204-1 clause 18)

- [ ] Wiring checked point-to-point against released schematics
- [ ] PE continuity <= 0.1 Ω to: frame, cabinet door, jaws (both), platform, weigher, elevator, conveyor, motors
- [ ] Insulation resistance >= 1 MΩ at 500 V DC (power circuits to PE); each heater >= 1 MΩ
- [ ] Supply: voltage ____ V L-L, phase sequence, N present; prospective fault level <= device rating
- [ ] Protective devices set/rated per `02_power_distribution.md`; RCD test where fitted
- [ ] 24 V: ____ V; branch fuses F10-F13 set; fuse alarm reaches I9.3
- [ ] Residual voltage after isolation < 60 V within 5 s at drive DC links (or warning label fitted)

## C. Pneumatic

- [ ] Supply 0.6 MPa regulated; pressure switch B1 trips at 0.5 MPa falling
- [ ] No audible leaks; dump valve exhausts system to 0 in < 1 s; soft start works
- [ ] Flow controls set: jaw close ~0.12-0.15 s, open ~0.12-0.15 s (measure on diagnostics screen), no slamming

## D. I/O check (mode OFF, then MANUAL)

- [ ] Every input in `io_map.csv` toggled at the device and seen on the HMI diagnostics screen
- [ ] Every output operated in MANUAL and seen at the device
- [ ] Thermocouples: Z1 ____ Z2 ____ Z3 ____ °C at ambient (within 3 K of each other); open-circuit test raises alarm 13-15
- [ ] Servo: direction (film downward = positive), 100.0 mm jog measured on film = ____ mm
- [ ] VFDs: direction, ramps, fault relay to PLC
- [ ] Weigher handshake: READY, DUMP REQUEST, DUMP DONE, NO FAULT, FEED REQUEST, RUN ENABLE

## E. Safety validation (sign each; any failure = stop)

- [ ] SF1: each E-stop S10 ___ S11 ___ S12 ___ S13 ___ : valves off, air dumped, STO, heaters off, weigher/elevator stop
- [ ] SF1 single-fault tests: one channel opened / shorted -> relay locks out, reset impossible
- [ ] SF2: each door B20 ___ B21 ___ ; jaw retraction time ____ ms vs door access time ____ ms
- [ ] SF3: release/close does not restart; RESET does not start motion; power cycle does not restart (alarm 30)
- [ ] SF4: each bimetal cut-out opens KM1 (simulate by disconnecting; type-test one at temperature)
- [ ] SF5: elevator covers / platform gate
- [ ] KM1 mirror contact mismatch raises alarm 31
- [ ] Knife cannot be fired with jaws open (MANUAL)
- [ ] Hot-surface, voltage, crushing labels fitted; LOTO points labelled and padlockable
- [ ] PL calculation (SISTEMA) completed with actual components and filed

## F. Function without product

- [ ] Film threaded, tracking stable for 50 bags; registration (if printed film) holds ± 1 mm
- [ ] Temperature control: time to band ____ min; overshoot ____ K; stability ± ____ K while cycling
- [ ] 500 empty bags at 20 / 40 / 50 per min: lengths, seals, cut
- [ ] Every alarm in `alarms.csv` provoked once; text, reaction and recovery correct
- [ ] Recipe save/load; user levels; counters; batch target stop
- [ ] Monitoring PC shows state, counters, temperatures, alarms (read-only confirmed: no writable node)

## G. With product

- [ ] Weigher calibrated and product program tuned by the weigher supplier's procedure
- [ ] Fall time measured (video): first piece ____ s, last piece ____ s after the dump request -> dump lead set ____ ms; whole charge lands with jaws closed, >= 40 ms margin at both ends
- [ ] Seal development test T-SEAL-01 done for each film
- [ ] PQ runs per `test_plan.md` section 4; results attached
- [ ] Operators trained (start/stop, threading, format change, cleaning, alarms, E-stop); manual handed over

Deviations and open items: ______________________________________________

Signatures: ____________________  ____________________
