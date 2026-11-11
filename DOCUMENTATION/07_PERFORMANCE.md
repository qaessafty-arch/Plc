# 07 - Production performance

Three columns are kept strictly apart: what was **calculated**, what was **simulated**, and what was **validated on hardware** (nothing yet).

| Quantity | Theoretical (calculation) | Simulated (model) | Validated |
|---|---|---|---|
| Mechanical cycle limit, reference bag | 1.22 s = 49 bags/min | - | - |
| Rated speed | 40 bags/min (18 % margin) | 39.9 bags/min held by pacing logic, 120 s run, 0 product-in-seal events | not tested |
| Net output at 85 % efficiency [assumed] | 2040 bags/h, 82 kg/h of 40 g chips | - | not tested |
| Weight accuracy at 40 g | - | mean 40.5 g, SD 0.7 g, give-away 1.4 %, 0 % below T - TNE (20 000 dumps, assumed 30 % charge spread, 0.15 g cell noise) | not tested |
| Bag length accuracy | resolution 7.5 µm per encoder count | ±0 mm (ideal belt, no slip modelled) | not tested |
| Film-pull motor | peak 0.47 N.m (37 % of 1.27 N.m), 1273 rpm (42 % of 3000) | - | not tested |
| Elevator capacity | 5100 L/h vs 1600 L/h needed for chips | - | not tested |
| Heater power / warm-up | 1300 W; 5.1-5.8 min by energy balance | 4.9 min to RUNNING, overshoot 4.5 K | not tested |
| Connected / demand power | 4.69 kW / ~3.3 kW | - | not measured |
| Compressed air | 189 NL/min at 0.6 MPa | - | not measured |
| Film consumption | 3.56 g per bag, 7.3 kg/h, one 400 mm roll ≈ 2400 m ≈ 4.3 h | - | not measured |
| Energy + film cost | ≈ 25.8 USD/h ≈ 12.7 USD per 1000 bags (film dominates: 98 %) | - | - |

Sources: `ENGINEERING/03_ENGINEERING_CALCULATIONS.md`, `SIMULATION/RESULTS.md`, `SIMULATION/weigher_results.json`.

## How to read the numbers

* The speed limit is set by the pneumatic jaws (2 x 0.15 s travel + 0.45 s dwell = 62 % of the cycle). Reaching the 80-150 bags/min advertised for high-speed reference machines needs servo-driven jaws with continuous film motion - a different mechanical concept.
* The weight figures depend entirely on the assumed spread of per-head charges and on load-cell noise. They show the principle works with margin; they are not a performance guarantee. The simulation also shows a counter-intuitive effect to check on the real weigher: *too uniform* charges (CV 15 %) reduce the number of usable combinations.
* The bagger cannot detect a wrong weight (simulation scenario S05). Per-bag weight assurance requires the weigher's own reject logic and, for the industrial configuration, a checkweigher.
* Operating cost is dominated by film; a 5 mm shorter bag saves about 2 % of running cost, far more than any energy measure.

## What must be measured to move numbers into the "validated" column

See `TESTING/test_plan.md` section 4 (performance qualification): 3 x 30 min runs per product at rated speed, 100 % weighing of 200 consecutive bags, seal tests, breakage test against a hand-packed control, energy and air metering.
