# Calibration procedures

| # | What | Reference | Method | Tolerance | Interval |
|---|---|---|---|---|---|
| C1 | Film index length | steel rule 500 mm (class II) | SETUP: 10 empty bags at recipe length 200 mm, measure 10-bag strip, divide by 10; correct the axis "distance per revolution" in the technology object (not the recipe) | ± 0.5 mm per bag | commissioning, after belt change |
| C2 | Registration | printed film | adjust "cut offset" until the cut is centred between prints; verify 50 bags | ± 1 mm | each printed film |
| C3 | Temperature channels | calibrated contact thermometer / reference thermocouple in a drilled check pocket in each jaw | compare at 100, 150, 200 °C after 10 min soak; if error > 3 K replace the thermocouple (no software offset unless documented) | ± 3 K | 6 months |
| C4 | PI tuning | - | start from Kp 4 %/K, Ti 60 s; step 130 -> 150 °C; accept overshoot < 5 K, settling < 3 min; or use Siemens PID_Temp auto-tune and transfer values | - | commissioning, after heater change |
| C5 | Air pressure switch / transmitter | test gauge | lower regulator slowly; switch must open at 0.50 ± 0.02 MPa | - | yearly |
| C6 | Jaw timing | HMI diagnostics (close/open times) | adjust meter-out flow controls: 0.12-0.15 s each way, equal for both directions | - | commissioning, after seal kit |
| C7 | Jaw parallelism / pressure | carbon or pressure-indicating film | print at operating pressure, even density | - | after jaw service |
| C8 | Weigher | certified weights (OIML class M1 or better) | supplier procedure: zero, span per head, then 20 dumps checked on a reference scale | weigher specification / legal metrology | 30 days check, yearly verification |
| C9 | Reference bench scale for sampling | certified weights | daily check with one weight near the bag weight | ± 0.1 g | daily |
| C10 | Dump lead | high-speed video (phone 240 fps is sufficient) | film the jaw area through the guard; measure first and last piece arrival relative to the dump request; set dump lead so the first piece lands >= 40 ms after the jaws close and the last >= 40 ms before they open (model: 55 ms for 40 g chips) | both margins >= 40 ms | each new product, after speed or dwell changes |
| C11 | Conveyor / elevator speeds | tachometer or stopwatch over 1 m | set % so the take-off clears one bag per cycle and the elevator duty is 40-70 % | - | commissioning |

Record every calibration in the maintenance log (monitoring software -> Maintenance -> record with description).
