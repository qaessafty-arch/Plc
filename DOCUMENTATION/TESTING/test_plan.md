# Testing, simulation and acceptance plan

## 1. What has been tested so far (software only)

| Evidence | Tool | Result | What it does NOT show |
|---|---|---|---|
| Sequence logic vs plant model, 12 scenarios, 51 checks | `SIMULATION/run_simulation.py`, `pytest SIMULATION` | all pass (`SIMULATION/RESULTS.md`) | correctness of the SCL text, real actuator times, real thermal behaviour, film behaviour |
| Combination weighing statistics | `SIMULATION/weigher_sim.py` | `weigher_results.json` | real charge distribution, real load-cell dynamics |
| Combination algorithm (C) | gcc host test, 20 000 random cases vs brute force | pass | behaviour on a microcontroller |
| Monitoring backend | 8 pytest API tests (SQLite) + live smoke test with simulated source | pass | PostgreSQL in production, OPC UA against a real CPU |
| Monitoring frontend | production build + browser smoke test (no console errors, no horizontal overflow at 380 px) | pass | usability with operators |
| HMI prototype | browser run through login, all screens, start, E-stop, reset | pass | the real WinCC project |
| CAD | model regenerates, bounding box equals calculated envelope 4450 x 1900 x 3900 | pass | interference check at detail level, manufacturability |

Five sequence defects were found and fixed through simulation before any hardware existed: STOPPING could hang after a cycle abort; alarms needed two RESET presses; recipe speed was not enforced; the weigher dump was sent too late, so the charge landed after the jaws had opened, on an unsupported hot seal; and the speed reported by the PLC was measured over part of the cycle (51.3 shown at a real 40 bags/min). This is the purpose of the model; it is not proof that no defects remain.

## 2. Simulation coverage requested by the brief

| Item | Covered by | Fidelity |
|---|---|---|
| Product movement / feeding | S01, S03 (weigher supply on/off, elevator demand) | logical only - no particle/DEM simulation of chips |
| Weight measurement | weigher_sim (Monte-Carlo), S05 | statistical |
| Film movement | S01 (trapezoid profile, length check), S04 (roll end) | ideal belt; slip is a parameter |
| Bag formation | not simulated (geometry check in calc sheet only) | - |
| Sealing | S02, S08 (first-order thermal model + PI) | lumped; seal strength not modelled |
| Cutting | S01 (knife window inside dwell, bag separation event) | logical |
| Conveyor synchronisation | S06 (jam, overload) | logical |
| Sensor operation | all (sensors derived from plant state), S09 failures | logical |
| PLC sequences | all | Python port of the SCL |
| Fault conditions | S03-S12 | see RESULTS.md |

Not simulated and stated as such: film tracking on the collar, wrinkles, seal strength, chip breakage, product bridging in the tube, vibration coupling into the weigher. These need physical trials.

## 3. Abnormal-scenario tests - repeat on the real machine (site acceptance)

| ID | Scenario | Method on the machine | Expected (acceptance criterion) | Sim. |
|---|---|---|---|---|
| T-AB-01 | Empty product hopper | let the hopper run empty in AUTO | warning 26 then 21, amber lamp, no film pulled, no empty bags, automatic resume on refill | S03 |
| T-AB-02 | Missing film | cut the web / let the roll end | alarm 4, stops with jaws open before the next pull; no restart on RESET alone | S04 |
| T-AB-03 | Incorrect weight | add 10 g to one weigh hopper (weigher test function) or mis-set target | weigher rejects/alarms per its settings; checkweigher (if fitted) rejects; **the bagger alone will not detect it** | S05 |
| T-AB-04 | Jammed conveyor | block the take-off belt; separately hold back 2 bags at the photo-eye | VFD overload -> alarm 25 within 2 s; missing bags -> alarm 22 within 3 bags; jaws open | S06 |
| T-AB-05 | Motor overload | elevator: brake the chain (torque limiter/VFD limit); servo: block the film (belts slip, following error) | alarm 24 (line runs until starved) / alarm 18 or 19, FAULT | S07 |
| T-AB-06 | Excess seal temperature | set SSR output permanently on with a link (electrician, supervised) | alarm 10-12 at 220 °C, KM1 opens; separately verify each bimetal cut-out opens KM1 at 250 ± 15 °C with the PLC limit disabled in a test build | S08 |
| T-AB-07 | Sensor failure | unplug each sensor in turn (list in checklist) | the specific alarm; no movement into an unknown state | S09 |
| T-AB-08 | Power interruption | open Q0 during sealing | all actuators retract; on power return state STOPPED, alarm 30, no motion until RESET + START | S10 |
| T-AB-09 | Emergency stop | press each E-stop during sealing, pulling, idle | jaws open, air dumped (gauge to 0 in < 1 s), servo torque-free, heaters off; release does nothing; RESET does not start | S11 |
| T-AB-10 | Guard door | open each door in each cycle phase | as E-stop for motion; measure jaw retraction time vs door opening time | S12 |
| T-AB-11 | Air failure | close the supply valve while running | alarm 3, FAULT, no half-closed jaw holding film | S12 |

## 4. Qualification stages and acceptance criteria

| Stage | Content | Pass criteria |
|---|---|---|
| IQ - installation | checklist sections A-C | all items signed |
| OQ - function, no product | all modes, all alarms, 500 empty bags at 20/40/50 per min | no unexplained stop; bag length 230 ± 1 mm (n = 50); seal passes leak test (n = 20 per setting) |
| Safety validation | ISO 13849-2 fault injection on SF1-SF5, IEC 60204-1 clause 18 tests | documented, no deviation |
| PQ - with product (per product) | 3 runs x 30 min at rated speed | efficiency >= 85 % (good bags / theoretical); 200 consecutive bags: mean >= nominal, none < nominal - TNE, SD <= 1.0 g at 40 g; 0 leakers in 60; 0 product-in-seal in 200; breakage increase <= 2 % points vs hand-packed control (sieve test); film waste at start <= 5 bags |
| Reliability run | 8 h production | <= 4 stops attributable to the machine, none > 5 min |
| Utilities | energy meter, air flow meter during PQ | within +20 % of calculated values (else update the calculation sheet) |

Any criterion marked as an assumption in the specification (F-07, F-08, F-11) is renegotiated with the project owner after the first PQ, on the basis of measured data.

## 5. Seal development test (T-SEAL-01) - before PQ

For each film: matrix of temperature (5 levels, 10 K steps) x dwell (3 levels) at fixed pressure; 5 bags per cell; evaluate appearance, peel strength (hand peel or tensile tester, ASTM F88 method as reference), leak test. Choose the centre of the window where all bags pass; record in the recipe. Repeat pressure if the window is narrower than ± 10 K. This test also settles the jaw-cylinder question raised in `04_MECHANICAL_DESIGN.md`.
